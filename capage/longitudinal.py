"""Checkpointed matched-arm longitudinal sandbox orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
from statistics import fmean, median
from typing import Any, Callable, Protocol

from capage.memory import AuditedMemoryStore
from capage.sandbox import TokenTariff, empty_continuity_state, validate_continuity_state
from capage.sandbox_runner import LiveSandboxRunner, ModelClient, SandboxRunConfig


_COST_UNITS_PER_CENT = 1_000_000
_ARMS = ("control", "memory")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _continuity_hash(value: dict[str, Any]) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("experiment_epoch must include a timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class LongitudinalConfig:
    """Frozen choices for one matched memory-versus-control experiment."""

    experiment_name: str
    month_seeds: tuple[int, ...]
    experiment_epoch: str
    starting_capital_cents: int
    horizon_days: int
    max_decisions_per_month: int
    per_month_model_cost_cap_cents: int
    aggregate_model_cost_cap_cents: int
    model: str
    effort: str
    max_output_tokens: int
    tariff: TokenTariff
    assessor_version: str
    tariff_valid_through: str = ""

    def __post_init__(self) -> None:
        if not self.experiment_name.strip():
            raise ValueError("experiment_name is required")
        if not self.month_seeds or len(self.month_seeds) != len(set(self.month_seeds)):
            raise ValueError("month seeds must be non-empty and unique")
        _timestamp(self.experiment_epoch)
        if self.starting_capital_cents < 0:
            raise ValueError("starting capital cannot be negative")
        if self.horizon_days < 7:
            raise ValueError("horizon_days must be at least 7")
        if not 1 <= self.max_decisions_per_month <= 100:
            raise ValueError("max_decisions_per_month must be between 1 and 100")
        if self.per_month_model_cost_cap_cents < 1:
            raise ValueError("per-month model cost cap must be positive")
        if self.aggregate_model_cost_cap_cents < 2:
            raise ValueError("aggregate model cost cap must be at least two cents")
        if self.effort not in {"low", "medium", "high", "max"}:
            raise ValueError("unsupported effort")
        if not 128 <= self.max_output_tokens <= 4096:
            raise ValueError("max_output_tokens must be between 128 and 4096")
        if self.tariff_valid_through:
            date.fromisoformat(self.tariff_valid_through)
        if self.assessor_version not in {
            "deterministic-artifact-v1",
            "deterministic-artifact-v2",
        }:
            raise ValueError("unsupported artifact assessor version")

    @classmethod
    def from_manifest(cls, path: str | Path) -> "LongitudinalConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != "capage-longitudinal-v1":
            raise ValueError("unsupported longitudinal manifest schema")
        model = payload["model"]
        tariff = payload["token_tariff"]
        return cls(
            experiment_name=str(payload["experiment_name"]),
            month_seeds=tuple(int(seed) for seed in payload["month_seeds"]),
            experiment_epoch=str(payload["experiment_epoch"]),
            starting_capital_cents=int(payload["starting_capital_cents"]),
            horizon_days=int(payload["horizon_days"]),
            max_decisions_per_month=int(payload["max_decisions_per_month"]),
            per_month_model_cost_cap_cents=int(
                payload["per_month_model_cost_cap_cents"]
            ),
            aggregate_model_cost_cap_cents=int(
                payload["aggregate_model_cost_cap_cents"]
            ),
            model=str(model["name"]),
            effort=str(model["effort"]),
            max_output_tokens=int(model["max_output_tokens"]),
            tariff=TokenTariff(
                name=str(tariff["name"]),
                input_cents_per_million_tokens=int(
                    tariff["input_cents_per_million_tokens"]
                ),
                output_cents_per_million_tokens=int(
                    tariff["output_cents_per_million_tokens"]
                ),
            ),
            assessor_version=str(payload["assessor_version"]),
            tariff_valid_through=str(payload.get("tariff_valid_through", "")),
        )

    def commitment(self) -> str:
        payload = {**asdict(self), "tariff": asdict(self.tariff)}
        return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def month_config(
        self,
        *,
        arm: str,
        month_number: int,
        starting_capital_cents: int,
        cost_cap_cents: int,
    ) -> SandboxRunConfig:
        return SandboxRunConfig(
            run_name=(
                f"{self.experiment_name}-{arm}-month-{month_number:03d}"
            ),
            seed=self.month_seeds[month_number - 1],
            model=self.model,
            effort=self.effort,
            max_output_tokens=self.max_output_tokens,
            max_decisions=self.max_decisions_per_month,
            max_run_cost_cents=cost_cap_cents,
            horizon_days=self.horizon_days,
            starting_capital_cents=starting_capital_cents,
            tariff=self.tariff,
            assessor_version=self.assessor_version,
            tariff_valid_through=self.tariff_valid_through,
        )


class MonthRunner(Protocol):
    def run(self) -> dict[str, Any]: ...


RunnerFactory = Callable[..., MonthRunner]


class LongitudinalRunner:
    """Run paired arms sequentially with atomic checkpoints and no cell retries."""

    def __init__(
        self,
        config: LongitudinalConfig,
        client: ModelClient,
        *,
        checkpoint_path: str | Path,
        artifact_dir: str | Path,
        memory_path: str | Path,
        runner_factory: RunnerFactory = LiveSandboxRunner,
    ) -> None:
        self.config = config
        self.client = client
        self.checkpoint_path = Path(checkpoint_path)
        self.artifact_dir = Path(artifact_dir)
        self.memory_path = Path(memory_path)
        self.runner_factory = runner_factory
        self.state = self._load_or_initialize()

    def run(self, *, max_cells: int | None = None) -> dict[str, Any]:
        if max_cells is not None and max_cells < 1:
            raise ValueError("max_cells must be positive")
        if self.state["status"] == "completed":
            return self.state
        if self.state["status"] == "stopped":
            return self.state

        attempted_now = 0
        self.state["status"] = "running"
        self.state["stop_reason"] = None
        self._checkpoint()

        with AuditedMemoryStore(self.memory_path) as memory:
            if not memory.verify_chain():
                return self._stop("memory_chain_invalid")
            if self.state["memory_head_hash"] != memory.head_hash():
                return self._stop("memory_checkpoint_mismatch")
            for month_number in range(1, len(self.config.month_seeds) + 1):
                order = _ARMS if month_number % 2 else tuple(reversed(_ARMS))
                for arm in order:
                    cell_id = f"month-{month_number:03d}:{arm}"
                    if cell_id in self.state["completed_cells"]:
                        continue
                    remaining_units = (
                        self.config.aggregate_model_cost_cap_cents
                        * _COST_UNITS_PER_CENT
                        - int(self.state["model_cost_units"])
                    )
                    remaining_whole_cents = remaining_units // _COST_UNITS_PER_CENT
                    if remaining_whole_cents < 1:
                        return self._stop("aggregate_model_cost_cap_reached")
                    cost_cap = min(
                        self.config.per_month_model_cost_cap_cents,
                        int(remaining_whole_cents),
                    )
                    context = self._memory_context(memory, month_number, arm)
                    arm_state = self.state["arms"][arm]
                    month_config = self.config.month_config(
                        arm=arm,
                        month_number=month_number,
                        starting_capital_cents=int(arm_state["balance_cents"]),
                        cost_cap_cents=cost_cap,
                    )
                    result_path = self.artifact_dir / f"{month_config.run_name}.json"
                    audit_path = self.artifact_dir / f"{month_config.run_name}-audit.jsonl"
                    if result_path.exists() or audit_path.exists():
                        self.state["errors"].append(
                            {
                                "cell_id": cell_id,
                                "error_type": "AmbiguousPriorAttempt",
                                "error": (
                                    "an uncheckpointed result or audit file already exists; "
                                    "the cell will not be replayed"
                                ),
                            }
                        )
                        return self._stop("ambiguous_uncheckpointed_attempt")
                    try:
                        runner = self.runner_factory(
                            month_config,
                            self.client,
                            audit_path=audit_path,
                            durable_context=context,
                            continuity_state=arm_state["business_continuity"],
                        )
                        result = runner.run()
                        self._validate_result(result, month_config)
                    except Exception as exc:
                        self.state["errors"].append(
                            {
                                "cell_id": cell_id,
                                "error_type": type(exc).__name__,
                                "error": str(exc),
                            }
                        )
                        return self._stop("provider_or_runner_error")

                    _atomic_json(result_path, result)
                    outcome = result["outcome"]
                    continuity = validate_continuity_state(
                        result["business_continuity"]
                    )
                    used_units = int(result["actual_model_cost_units"])
                    self.state["model_cost_units"] += used_units
                    arm_state["balance_cents"] = int(outcome["balance_cents"])
                    arm_state["business_continuity"] = continuity
                    arm_state["months_completed"] += 1
                    record = {
                        "cell_id": cell_id,
                        "arm": arm,
                        "month_number": month_number,
                        "seed": month_config.seed,
                        "status": result["status"],
                        "stop_reason": result["stop_reason"],
                        "starting_capital_cents": month_config.starting_capital_cents,
                        "ending_balance_cents": int(outcome["balance_cents"]),
                        "net_change_cents": int(outcome["net_change_cents"]),
                        "earned_revenue_cents": int(outcome["earned_revenue_cents"]),
                        "expense_cents": int(outcome["expense_cents"]),
                        "offers_sent": int(outcome["offers_sent"]),
                        "contracts_accepted": int(outcome["contracts_accepted"]),
                        "contracts_paid": int(outcome["contracts_paid"]),
                        "contracts_defaulted": int(outcome["contracts_defaulted"]),
                        "contracts_disputed": int(outcome["contracts_disputed"]),
                        "actual_model_cost_units": used_units,
                        "memory_record_count": (
                            len(context.get("records", [])) if context else 0
                        ),
                        "known_customers": len(continuity["customers"]),
                        "global_reputation_points": int(
                            continuity["global_reputation_points"]
                        ),
                        "business_continuity_hash": _continuity_hash(continuity),
                        "result_file": result_path.name,
                        "audit_file": audit_path.name,
                    }
                    arm_state["months"].append(record)
                    self.state["completed_cells"][cell_id] = record
                    if arm == "memory":
                        self._ingest_memory_month(memory, record)
                        self.state["memory_head_hash"] = memory.head_hash()
                    self._checkpoint()
                    attempted_now += 1

                    if int(outcome["open_obligations"]) != 0:
                        return self._stop("open_obligations_require_state_serialization")
                    if max_cells is not None and attempted_now >= max_cells:
                        self.state["status"] = "paused"
                        self.state["stop_reason"] = "operator_checkpoint"
                        self._checkpoint()
                        return self.state

        self.state["status"] = "completed"
        self.state["stop_reason"] = "all_matched_months_completed"
        self.state["summary"] = self._summary()
        self._checkpoint()
        return self.state

    def _memory_context(
        self,
        memory: AuditedMemoryStore,
        month_number: int,
        arm: str,
    ) -> dict[str, Any] | None:
        if arm == "control" or month_number == 1:
            return None
        packet = memory.retrieve(
            "pricing offers customers delivery payment feedback profit strategy",
            as_of=self._month_start(month_number),
            limit=8,
            max_chars=8_000,
        )
        return packet.to_prompt_data()

    def _ingest_memory_month(
        self,
        memory: AuditedMemoryStore,
        record: dict[str, Any],
    ) -> None:
        month_number = int(record["month_number"])
        event_id = f"memory-month-{month_number:03d}-outcome"
        occurred_at = self._month_end(month_number)
        if not memory.has_event(event_id):
            memory.append_event(
                event_id,
                "monthly_business_outcome",
                {key: value for key, value in record.items() if key != "audit_file"},
                occurred_at=occurred_at,
            )
        operational_id = f"month-{month_number:03d}-outcome"
        if memory.latest_memory_revision(operational_id) == 0:
            memory.assert_memory(
                operational_id,
                "operational",
                (
                    f"Month {month_number} ended with net change "
                    f"{record['net_change_cents']} cents after "
                    f"{record['offers_sent']} offers, {record['contracts_accepted']} "
                    f"acceptances, {record['contracts_paid']} payments, and "
                    f"{record['contracts_defaulted']} payment defaults."
                ),
                tags=["monthly outcome", "offers", "payments", "profit"],
                evidence_event_ids=[event_id],
                confidence=100,
                occurred_at=occurred_at,
            )

        memory_months = self.state["arms"]["memory"]["months"]
        if len(memory_months) < 2:
            return
        strategy_revision = memory.latest_memory_revision("strategy-performance")
        expected_revision = len(memory_months) - 1
        if strategy_revision >= expected_revision:
            return
        net_changes = [int(item["net_change_cents"]) for item in memory_months]
        evidence = [
            f"memory-month-{int(item['month_number']):03d}-outcome"
            for item in memory_months
        ]
        offers = sum(int(item["offers_sent"]) for item in memory_months)
        accepted = sum(int(item["contracts_accepted"]) for item in memory_months)
        paid = sum(int(item["contracts_paid"]) for item in memory_months)
        memory.assert_memory(
            "strategy-performance",
            "strategy",
            (
                f"Across {len(memory_months)} completed months, "
                f"{sum(change > 0 for change in net_changes)} were profitable; "
                f"mean net change was {round(fmean(net_changes), 2)} cents and "
                f"median was {median(net_changes)} cents. {offers} offers produced "
                f"{accepted} acceptances and {paid} payments. Treat this as a "
                "small-sample estimate rather than a guaranteed rule."
            ),
            tags=["strategy", "conversion", "offers", "profit", "payments"],
            evidence_event_ids=evidence,
            confidence=min(90, 40 + (5 * len(memory_months))),
            occurred_at=occurred_at,
        )

    def _validate_result(
        self,
        result: dict[str, Any],
        config: SandboxRunConfig,
    ) -> None:
        if not isinstance(result, dict) or not isinstance(result.get("outcome"), dict):
            raise ValueError("month runner omitted an outcome")
        if "business_continuity" not in result:
            raise ValueError("month runner omitted business continuity state")
        validate_continuity_state(result["business_continuity"])
        outcome = result["outcome"]
        required = {
            "owner_capital_cents",
            "balance_cents",
            "earned_revenue_cents",
            "expense_cents",
            "net_change_cents",
            "offers_sent",
            "contracts_accepted",
            "contracts_paid",
            "contracts_defaulted",
            "contracts_disputed",
            "open_obligations",
        }
        missing = sorted(required - set(outcome))
        if missing:
            raise ValueError(f"month outcome omitted {missing[0]}")
        if int(outcome["owner_capital_cents"]) != config.starting_capital_cents:
            raise ValueError("month outcome changed starting capital")
        expected_balance = (
            config.starting_capital_cents
            + int(outcome["earned_revenue_cents"])
            - int(outcome["expense_cents"])
        )
        if int(outcome["balance_cents"]) != expected_balance:
            raise ValueError("month balance equation failed")
        if int(outcome["net_change_cents"]) != (
            int(outcome["balance_cents"]) - config.starting_capital_cents
        ):
            raise ValueError("month net-change equation failed")
        used_units = result.get("actual_model_cost_units")
        if isinstance(used_units, bool) or not isinstance(used_units, int) or used_units < 0:
            raise ValueError("month result omitted valid model cost units")

    def _summary(self) -> dict[str, Any]:
        arms: dict[str, Any] = {}
        for arm in _ARMS:
            rows = self.state["arms"][arm]["months"]
            changes = [int(row["net_change_cents"]) for row in rows]
            arms[arm] = {
                "months_completed": len(rows),
                "ending_balance_cents": self.state["arms"][arm]["balance_cents"],
                "total_net_change_cents": sum(changes),
                "mean_net_change_cents": round(fmean(changes), 2),
                "median_net_change_cents": median(changes),
                "profitable_month_rate": sum(change > 0 for change in changes) / len(changes),
                "total_model_cost_units": sum(
                    int(row["actual_model_cost_units"]) for row in rows
                ),
            }
        paired_deltas = []
        for month_number in range(1, len(self.config.month_seeds) + 1):
            memory_row = self.state["completed_cells"][
                f"month-{month_number:03d}:memory"
            ]
            control_row = self.state["completed_cells"][
                f"month-{month_number:03d}:control"
            ]
            paired_deltas.append(
                int(memory_row["net_change_cents"])
                - int(control_row["net_change_cents"])
            )
        return {
            "arms": arms,
            "paired_memory_minus_control_net_cents": paired_deltas,
            "mean_paired_delta_cents": round(fmean(paired_deltas), 2),
        }

    def _load_or_initialize(self) -> dict[str, Any]:
        commitment = self.config.commitment()
        if self.checkpoint_path.exists():
            state = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            if state.get("schema_version") != "capage-longitudinal-checkpoint-v2":
                raise ValueError("unsupported longitudinal checkpoint schema")
            if state.get("config_commitment") != commitment:
                raise ValueError("checkpoint does not match the frozen configuration")
            for arm in _ARMS:
                arm_state = state.get("arms", {}).get(arm, {})
                continuity = validate_continuity_state(
                    arm_state.get("business_continuity")
                )
                months = arm_state.get("months", [])
                if months and months[-1].get("business_continuity_hash") != _continuity_hash(
                    continuity
                ):
                    raise ValueError("checkpoint business continuity hash mismatch")
            return state
        return {
            "schema_version": "capage-longitudinal-checkpoint-v2",
            "experiment_name": self.config.experiment_name,
            "config_commitment": commitment,
            "status": "ready",
            "stop_reason": None,
            "model_cost_units": 0,
            "memory_head_hash": "0" * 64,
            "completed_cells": {},
            "errors": [],
            "arms": {
                arm: {
                    "balance_cents": self.config.starting_capital_cents,
                    "months_completed": 0,
                    "months": [],
                    "business_continuity": empty_continuity_state(),
                }
                for arm in _ARMS
            },
            "summary": None,
        }

    def _checkpoint(self) -> None:
        _atomic_json(self.checkpoint_path, self.state)

    def _stop(self, reason: str) -> dict[str, Any]:
        self.state["status"] = "stopped"
        self.state["stop_reason"] = reason
        self._checkpoint()
        return self.state

    def _month_start(self, month_number: int) -> str:
        start = _timestamp(self.config.experiment_epoch) + timedelta(
            days=(month_number - 1) * self.config.horizon_days
        )
        return start.isoformat()

    def _month_end(self, month_number: int) -> str:
        end = _timestamp(self.config.experiment_epoch) + timedelta(
            days=month_number * self.config.horizon_days,
            microseconds=-1,
        )
        return end.isoformat()
