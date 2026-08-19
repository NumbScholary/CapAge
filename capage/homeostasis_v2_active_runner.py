"""Checkpointed runner for the preregistered three-arm homeostasis test."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable

from capage.homeostasis_shadow import SandboxResultProjector
from capage.homeostasis_v2_experiment import (
    ARMS,
    completed_signal_for_arm,
    derive_triplet_specs,
    materialize_matched_worlds,
    signal_for_arm_start,
    validate_plan,
)


CHECKPOINT_SCHEMA = "capage-homeostasis-v2-three-arm-checkpoint-v1"
CONFIRMATION = "RUN_MATCHED_HOMEOSTASIS_V2_THREE_ARM_MAX_1350_CENTS"
ABORTED_RUN_MODEL_COST_UNITS = 28_915_600
ABORTED_RUN_COST_REFERENCE = (
    "github-actions-run:32292164227/artifact:9379919939"
)
_COST_UNITS_PER_CENT = 1_000_000
_CELL_COUNT = 18
_IMPLEMENTATION_PATHS = (
    "experiments/sandbox/economic_homeostasis_v2_prereg_v1.json",
    "capage/sandbox.py",
    "capage/sandbox_runner.py",
    "capage/homeostasis.py",
    "capage/homeostasis_shadow.py",
    "capage/homeostasis_experiment.py",
    "capage/homeostasis_v2.py",
    "capage/homeostasis_v2_runner.py",
    "capage/homeostasis_v2_experiment.py",
    "capage/homeostasis_v2_active_runner.py",
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def implementation_commitments() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    return {
        path: sha256((root / path).read_bytes()).hexdigest()
        for path in _IMPLEMENTATION_PATHS
    }


@dataclass(frozen=True)
class ActiveConfig:
    plan_sha256: str
    starting_capital_cents: int
    horizon_days: int
    max_decisions: int
    customer_population_seed: int
    model: str
    effort: str
    max_output_tokens: int
    assessor_version: str
    tariff_name: str
    input_cents_per_million_tokens: int
    output_cents_per_million_tokens: int
    tariff_valid_through: str
    per_cell_cost_cap_cents: int
    aggregate_cost_cap_cents: int

    @classmethod
    def from_plan(cls, plan: dict[str, Any]) -> "ActiveConfig":
        validate_plan(plan)
        frozen = plan["frozen_config"]
        tariff = frozen["token_tariff"]
        budget = plan["maximum_budget"]
        config = cls(
            plan_sha256=_digest(plan),
            starting_capital_cents=int(frozen["starting_capital_cents"]),
            horizon_days=int(frozen["horizon_days"]),
            max_decisions=int(frozen["max_decisions_per_cell"]),
            customer_population_seed=int(frozen["customer_population_seed"]),
            model=str(frozen["model"]),
            effort=str(frozen["effort"]),
            max_output_tokens=int(frozen["max_output_tokens"]),
            assessor_version=str(frozen["assessor_version"]),
            tariff_name=str(tariff["name"]),
            input_cents_per_million_tokens=int(
                tariff["input_cents_per_million_tokens"]
            ),
            output_cents_per_million_tokens=int(
                tariff["output_cents_per_million_tokens"]
            ),
            tariff_valid_through=str(tariff["valid_through"]),
            per_cell_cost_cap_cents=int(budget["per_cell_cost_cap_cents"]),
            aggregate_cost_cap_cents=int(budget["provider_cost_cap_cents"]),
        )
        if config.aggregate_cost_cap_cents != 1_350:
            raise ValueError("three-arm aggregate cap must be exactly 1350 cents")
        if config.per_cell_cost_cap_cents * _CELL_COUNT != 1_350:
            raise ValueError("eighteen cell caps must equal the aggregate cap")
        date.fromisoformat(config.tariff_valid_through)
        return config

    def commitment(self) -> str:
        return _digest(asdict(self))


RunnerFactory = Callable[..., Any]
RunConfigFactory = Callable[..., Any]


class ThreeArmHomeostasisRunner:
    """Run frozen cells serially and fail closed around every paid attempt."""

    def __init__(
        self,
        plan: dict[str, Any],
        client: Any,
        *,
        checkpoint_path: str | Path,
        artifact_dir: str | Path,
        runner_factories: dict[str, RunnerFactory],
        run_config_factory: RunConfigFactory,
        empty_continuity_factory: Callable[[], dict[str, Any]],
    ) -> None:
        if set(runner_factories) != set(ARMS):
            raise ValueError("runner_factories must contain control, v1, and v2")
        self.plan = json.loads(_canonical_json(plan))
        self.config = ActiveConfig.from_plan(self.plan)
        ceiling = self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT
        if not 0 < ABORTED_RUN_MODEL_COST_UNITS < ceiling:
            raise ValueError("required aborted-run debit is outside the aggregate cap")
        if not ABORTED_RUN_COST_REFERENCE.strip():
            raise ValueError("required aborted-run evidence reference is missing")
        self.client = client
        self.checkpoint_path = Path(checkpoint_path)
        self.artifact_dir = Path(artifact_dir)
        self.runner_factories = dict(runner_factories)
        self.run_config_factory = run_config_factory
        self.empty_continuity_factory = empty_continuity_factory
        self.prior_model_cost_units = ABORTED_RUN_MODEL_COST_UNITS
        self.prior_cost_reference = ABORTED_RUN_COST_REFERENCE
        self.state = self._load_or_initialize()

    def _initial_state(self) -> dict[str, Any]:
        arms = {
            arm: {
                "balance_cents": self.config.starting_capital_cents,
                "model_cost_units": 0,
                "business_continuity": self.empty_continuity_factory(),
            }
            for arm in ARMS
        }
        return {
            "schema_version": CHECKPOINT_SCHEMA,
            "status": "ready",
            "stop_reason": None,
            "config_commitment": self.config.commitment(),
            "plan_sha256": self.config.plan_sha256,
            "implementation_commitments": implementation_commitments(),
            "prior_model_cost_units": self.prior_model_cost_units,
            "prior_cost_reference": self.prior_cost_reference,
            "model_cost_units": self.prior_model_cost_units,
            "completed_cells": {},
            "arms": arms,
            "errors": [],
        }

    def _load_or_initialize(self) -> dict[str, Any]:
        if not self.checkpoint_path.exists():
            return self._initial_state()
        payload = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != CHECKPOINT_SCHEMA:
            raise ValueError("unsupported three-arm checkpoint schema")
        if payload.get("config_commitment") != self.config.commitment():
            raise ValueError("checkpoint config mismatch")
        if payload.get("plan_sha256") != self.config.plan_sha256:
            raise ValueError("checkpoint plan mismatch")
        if payload.get("implementation_commitments") != implementation_commitments():
            raise ValueError("checkpoint implementation mismatch")
        if payload.get("prior_model_cost_units") != self.prior_model_cost_units:
            raise ValueError("checkpoint prior model cost mismatch")
        if payload.get("prior_cost_reference") != self.prior_cost_reference:
            raise ValueError("checkpoint prior cost reference mismatch")
        if set(payload.get("arms", {})) != set(ARMS):
            raise ValueError("checkpoint arm mismatch")
        self._validate_checkpoint_state(payload)
        return payload

    def _validate_checkpoint_state(self, payload: dict[str, Any]) -> None:
        """Refuse a resume whose paid evidence is missing or inconsistent."""

        completed = payload.get("completed_cells")
        if not isinstance(completed, dict):
            raise ValueError("checkpoint completed_cells must be an object")
        ordered = [
            (f"pair-{triplet.pair_index:02d}:{arm}", triplet, arm)
            for triplet in derive_triplet_specs()
            for arm in triplet.execution_order
        ]
        if len(completed) > len(ordered):
            raise ValueError("checkpoint contains too many completed cells")
        expected_prefix = {cell_id for cell_id, _, _ in ordered[: len(completed)]}
        if set(completed) != expected_prefix:
            raise ValueError("checkpoint completed cells are not the frozen prefix")

        aggregate_units = self.prior_model_cost_units
        arm_units = {arm: 0 for arm in ARMS}
        arm_balances = {
            arm: self.config.starting_capital_cents for arm in ARMS
        }
        latest_continuity: dict[str, dict[str, Any]] = {}
        for cell_id, triplet, arm in ordered[: len(completed)]:
            record = completed[cell_id]
            if not isinstance(record, dict):
                raise ValueError(f"checkpoint record {cell_id} must be an object")
            expected_stem = f"homeostasis-v2-pair-{triplet.pair_index:02d}-{arm}"
            expected_result_file = f"{expected_stem}.json"
            expected_audit_file = f"{expected_stem}-audit.jsonl"
            expected_attempt_file = f"{expected_stem}-attempt.json"
            expected_metadata = {
                "cell_id": cell_id,
                "pair_index": triplet.pair_index,
                "arm": arm,
                "seed": triplet.world_seed,
                "execution_order": list(triplet.execution_order),
                "result_file": expected_result_file,
                "audit_file": expected_audit_file,
            }
            for key, expected in expected_metadata.items():
                if record.get(key) != expected:
                    raise ValueError(f"checkpoint record {cell_id} has invalid {key}")
            if record.get("starting_capital_cents") != arm_balances[arm]:
                raise ValueError(f"checkpoint record {cell_id} breaks arm continuity")

            result_path = self.artifact_dir / expected_result_file
            if not result_path.is_file():
                raise ValueError(f"checkpoint result artifact missing for {cell_id}")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if record.get("result_sha256") != _digest(result):
                raise ValueError(f"checkpoint result artifact mismatch for {cell_id}")
            remaining_units = (
                self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT
                - aggregate_units
            )
            historical_cell_cap_cents = min(
                self.config.per_cell_cost_cap_cents,
                remaining_units // _COST_UNITS_PER_CENT,
            )
            if historical_cell_cap_cents < 1:
                raise ValueError("checkpoint contains a cell beyond the aggregate cap")
            run_config = self._run_config(
                triplet.pair_index,
                arm,
                triplet.world_seed,
                arm_balances[arm],
                historical_cell_cap_cents,
            )
            self._validate_result(result, run_config)
            units = int(result["actual_model_cost_units"])
            ending_balance = int(result["outcome"]["balance_cents"])
            if record.get("actual_model_cost_units") != units:
                raise ValueError(f"checkpoint cost mismatch for {cell_id}")
            if record.get("ending_balance_cents") != ending_balance:
                raise ValueError(f"checkpoint balance mismatch for {cell_id}")

            attempt_path = self.artifact_dir / expected_attempt_file
            if not attempt_path.is_file():
                raise ValueError(f"checkpoint attempt marker missing for {cell_id}")
            attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
            if (
                attempt.get("schema_version") != "capage-paid-attempt-v2"
                or attempt.get("cell_id") != cell_id
                or attempt.get("config_commitment") != self.config.commitment()
                or attempt.get("status") != "completed"
                or attempt.get("result_sha256") != record.get("result_sha256")
            ):
                raise ValueError(f"checkpoint attempt marker mismatch for {cell_id}")

            aggregate_units += units
            arm_units[arm] += units
            arm_balances[arm] = ending_balance
            latest_continuity[arm] = result["business_continuity"]

        if payload.get("model_cost_units") != aggregate_units:
            raise ValueError("checkpoint aggregate model cost mismatch")
        ceiling = self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT
        if aggregate_units > ceiling:
            raise ValueError("checkpoint aggregate model cost exceeds cap")
        for arm in ARMS:
            arm_state = payload["arms"].get(arm)
            if not isinstance(arm_state, dict):
                raise ValueError(f"checkpoint state for {arm} must be an object")
            if arm_state.get("model_cost_units") != arm_units[arm]:
                raise ValueError(f"checkpoint model cost mismatch for {arm}")
            if arm_state.get("balance_cents") != arm_balances[arm]:
                raise ValueError(f"checkpoint balance mismatch for {arm}")
            if not isinstance(arm_state.get("business_continuity"), dict):
                raise ValueError(f"checkpoint continuity for {arm} must be an object")
            if (
                arm in latest_continuity
                and arm_state["business_continuity"] != latest_continuity[arm]
            ):
                raise ValueError(f"checkpoint continuity mismatch for {arm}")

        status = payload.get("status")
        if status not in {"ready", "running", "paused", "stopped", "completed"}:
            raise ValueError("checkpoint status is invalid")
        if status == "ready" and completed:
            raise ValueError("ready checkpoint cannot contain completed cells")
        if status == "completed" and len(completed) != _CELL_COUNT:
            raise ValueError("completed checkpoint must contain eighteen cells")
        if not isinstance(payload.get("errors"), list):
            raise ValueError("checkpoint errors must be an array")

    def _checkpoint(self) -> None:
        _atomic_json(self.checkpoint_path, self.state)

    def _signal_for_period(self, arm: str, period: int):
        signal = signal_for_arm_start(arm)
        if signal is None:
            return None
        history = signal.next_history
        if period == 1:
            return signal
        for prior in range(1, period):
            cell_id = f"pair-{prior:02d}:{arm}"
            record = self.state["completed_cells"].get(cell_id)
            if not isinstance(record, dict):
                raise ValueError("signal requested before own prior period completed")
            result_path = self.artifact_dir / str(record["result_file"])
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if record.get("result_sha256") != _digest(result):
                raise ValueError("prior result artifact changed after checkpoint")
            signal = completed_signal_for_arm(arm, result, history)
            history = signal.next_history
        return signal

    def _run_config(
        self,
        pair_index: int,
        arm: str,
        seed: int,
        starting: int,
        max_run_cost_cents: int,
    ):
        return self.run_config_factory(
            run_name=f"homeostasis-v2-pair-{pair_index:02d}-{arm}",
            seed=seed,
            model=self.config.model,
            effort=self.config.effort,
            max_output_tokens=self.config.max_output_tokens,
            max_decisions=self.config.max_decisions,
            max_run_cost_cents=max_run_cost_cents,
            horizon_days=self.config.horizon_days,
            starting_capital_cents=starting,
            tariff_name=self.config.tariff_name,
            input_cents_per_million_tokens=(
                self.config.input_cents_per_million_tokens
            ),
            output_cents_per_million_tokens=(
                self.config.output_cents_per_million_tokens
            ),
            customer_population_seed=self.config.customer_population_seed,
            assessor_version=self.config.assessor_version,
            tariff_valid_through=self.config.tariff_valid_through,
        )

    @staticmethod
    def _validate_result(result: dict[str, Any], run_config: Any) -> None:
        if result.get("schema_version") != "capage-live-sandbox-result-v1":
            raise ValueError("cell returned unsupported result schema")
        if result.get("status") != "completed":
            raise ValueError("cell did not complete")
        units = result.get("actual_model_cost_units")
        if isinstance(units, bool) or not isinstance(units, int) or units < 0:
            raise ValueError("cell omitted valid model cost units")
        if units > run_config.max_run_cost_cents * _COST_UNITS_PER_CENT:
            raise ValueError("cell exceeded its provider cost cap")
        outcome = result.get("outcome")
        balance = outcome.get("balance_cents") if isinstance(outcome, dict) else None
        if isinstance(balance, bool) or not isinstance(balance, int):
            raise ValueError("cell omitted a valid outcome balance")
        run_id = outcome.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("cell outcome omitted its sandbox run_id")
        result_config = result.get("config")
        if (
            not isinstance(result_config, dict)
            or any(
                result_config.get(field) != getattr(run_config, field)
                for field in (
                    "run_name",
                    "seed",
                    "model",
                    "effort",
                    "max_output_tokens",
                    "max_decisions",
                    "max_run_cost_cents",
                    "horizon_days",
                    "starting_capital_cents",
                    "customer_population_seed",
                    "customer_namespace",
                    "market_profile",
                    "assessor_version",
                    "tariff_valid_through",
                )
            )
        ):
            raise ValueError("cell serialized config does not match its run config")
        serialized_tariff = result_config.get("tariff")
        expected_tariff = run_config.tariff
        if not isinstance(serialized_tariff, dict) or any(
            serialized_tariff.get(field) != getattr(expected_tariff, field)
            for field in (
                "name",
                "input_cents_per_million_tokens",
                "output_cents_per_million_tokens",
            )
        ):
            raise ValueError("cell serialized tariff does not match its run config")

        token_values = {
            "model_input_tokens": outcome.get("model_input_tokens"),
            "model_output_tokens": outcome.get("model_output_tokens"),
        }
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in token_values.values()
        ):
            raise ValueError("cell outcome omitted valid model token totals")
        expected_units = expected_tariff.cost_units(
            token_values["model_input_tokens"],
            token_values["model_output_tokens"],
        )
        if expected_units != units or outcome.get("model_api_cost_units") != units:
            raise ValueError("cell model token totals do not match cost units")
        billed_cents = (units + _COST_UNITS_PER_CENT - 1) // _COST_UNITS_PER_CENT
        if (
            result.get("actual_model_cost_cents_billed") != billed_cents
            or outcome.get("model_api_cost_cents") != billed_cents
        ):
            raise ValueError("cell billed model cost does not match cost units")
        if not isinstance(result.get("business_continuity"), dict):
            raise ValueError("cell omitted business continuity")
        SandboxResultProjector.project(result)

    def run(self, *, max_cells: int | None = None) -> dict[str, Any]:
        if max_cells is not None and not 1 <= max_cells <= _CELL_COUNT:
            raise ValueError("max_cells must be between 1 and 18")
        if self.state["status"] == "completed":
            return self.state
        if datetime.now(timezone.utc).date() > date.fromisoformat(
            self.config.tariff_valid_through
        ):
            self.state["status"] = "stopped"
            self.state["stop_reason"] = "frozen_tariff_expired"
            self._checkpoint()
            return self.state

        attempted = 0
        self.state["status"] = "running"
        self.state["stop_reason"] = None
        self._checkpoint()
        for triplet in derive_triplet_specs():
            for arm in triplet.execution_order:
                cell_id = f"pair-{triplet.pair_index:02d}:{arm}"
                if cell_id in self.state["completed_cells"]:
                    continue
                if max_cells is not None and attempted >= max_cells:
                    self.state["status"] = "paused"
                    self.state["stop_reason"] = "operator_checkpoint"
                    self._checkpoint()
                    return self.state
                remaining = (
                    self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT
                    - int(self.state["model_cost_units"])
                )
                if remaining < _COST_UNITS_PER_CENT:
                    self.state["status"] = "stopped"
                    self.state["stop_reason"] = "aggregate_model_cost_cap_reached"
                    self._checkpoint()
                    return self.state

                arm_state = self.state["arms"][arm]
                run_config = self._run_config(
                    triplet.pair_index,
                    arm,
                    triplet.world_seed,
                    int(arm_state["balance_cents"]),
                    min(
                        self.config.per_cell_cost_cap_cents,
                        remaining // _COST_UNITS_PER_CENT,
                    ),
                )
                stem = run_config.run_name
                result_path = self.artifact_dir / f"{stem}.json"
                audit_path = self.artifact_dir / f"{stem}-audit.jsonl"
                attempt_path = self.artifact_dir / f"{stem}-attempt.json"
                if result_path.exists() or audit_path.exists() or attempt_path.exists():
                    self.state["status"] = "stopped"
                    self.state["stop_reason"] = "ambiguous_uncheckpointed_attempt"
                    self._checkpoint()
                    return self.state
                kwargs = {
                    "audit_path": audit_path,
                    "continuity_state": arm_state["business_continuity"],
                }
                if arm in {"v1", "v2"}:
                    try:
                        kwargs["homeostasis_signal"] = self._signal_for_period(
                            arm, triplet.pair_index
                        )
                    except Exception as exc:
                        self.state["errors"].append(
                            {
                                "cell_id": cell_id,
                                "error_type": type(exc).__name__,
                                "error": str(exc),
                            }
                        )
                        self.state["status"] = "stopped"
                        self.state["stop_reason"] = "signal_projection_error"
                        self._checkpoint()
                        return self.state
                attempt = {
                    "schema_version": "capage-paid-attempt-v2",
                    "cell_id": cell_id,
                    "config_commitment": self.config.commitment(),
                    "status": "started",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                }
                _atomic_json(attempt_path, attempt)
                try:
                    runner = self.runner_factories[arm](
                        run_config,
                        self.client,
                        **kwargs,
                    )
                    result = runner.run()
                    self._validate_result(result, run_config)
                except Exception as exc:
                    self.state["errors"].append(
                        {
                            "cell_id": cell_id,
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        }
                    )
                    self.state["status"] = "stopped"
                    self.state["stop_reason"] = "provider_or_runner_error"
                    self._checkpoint()
                    return self.state

                _atomic_json(result_path, result)
                used = int(result["actual_model_cost_units"])
                projected_total = int(self.state["model_cost_units"]) + used
                ceiling = self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT
                if projected_total > ceiling:
                    raise RuntimeError("aggregate provider cost cap exceeded")
                self.state["model_cost_units"] = projected_total
                arm_state["model_cost_units"] += used
                arm_state["balance_cents"] = int(result["outcome"]["balance_cents"])
                arm_state["business_continuity"] = result["business_continuity"]
                record = {
                    "cell_id": cell_id,
                    "pair_index": triplet.pair_index,
                    "arm": arm,
                    "seed": triplet.world_seed,
                    "execution_order": list(triplet.execution_order),
                    "status": result["status"],
                    "stop_reason": result["stop_reason"],
                    "starting_capital_cents": run_config.starting_capital_cents,
                    "ending_balance_cents": int(result["outcome"]["balance_cents"]),
                    "actual_model_cost_units": used,
                    "result_file": result_path.name,
                    "audit_file": audit_path.name,
                    "result_sha256": _digest(result),
                }
                self.state["completed_cells"][cell_id] = record
                _atomic_json(
                    attempt_path,
                    {
                        **attempt,
                        "status": "completed",
                        "result_sha256": record["result_sha256"],
                    },
                )
                attempted += 1
                self._checkpoint()

        self.state["status"] = "completed"
        self.state["stop_reason"] = "all_cells_completed"
        self._checkpoint()
        return self.state


def _real_factories(plan: dict[str, Any]):
    from capage.anthropic_client import AnthropicMessagesClient
    from capage.homeostasis_experiment import make_treatment_runner_class
    from capage.homeostasis_v2_runner import HomeostasisV2SandboxRunner
    from capage.sandbox import EconomicSandbox, TokenTariff, empty_continuity_state
    from capage.sandbox_runner import LiveSandboxRunner, SandboxRunConfig

    config = ActiveConfig.from_plan(plan)
    tariff = TokenTariff(
        config.tariff_name,
        config.input_cents_per_million_tokens,
        config.output_cents_per_million_tokens,
    )

    def world_factory(seed, **kwargs):
        return EconomicSandbox(seed, token_tariff=tariff, **kwargs)

    def config_factory(
        *,
        tariff_name,
        input_cents_per_million_tokens,
        output_cents_per_million_tokens,
        **kwargs,
    ):
        return SandboxRunConfig(
            **kwargs,
            tariff=TokenTariff(
                tariff_name,
                input_cents_per_million_tokens,
                output_cents_per_million_tokens,
            ),
        )

    return (
        AnthropicMessagesClient,
        world_factory,
        {
            "control": LiveSandboxRunner,
            "v1": make_treatment_runner_class(LiveSandboxRunner),
            "v2": HomeostasisV2SandboxRunner,
        },
        config_factory,
        empty_continuity_state,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--max-cells", type=int)
    parser.add_argument("--confirm", default="")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    validate_plan(plan)
    if not args.validate_only and args.confirm != CONFIRMATION:
        raise SystemExit("exact paid-run confirmation is required")
    factories = _real_factories(plan)
    _, world_factory, runners, config_factory, continuity = factories
    if args.validate_only:
        records = materialize_matched_worlds(plan, world_factory)
        print(
            json.dumps(
                {"status": "validated", "matched_worlds": len(records)},
                sort_keys=True,
            )
        )
        return 0
    client_factory = factories[0]
    runner = ThreeArmHomeostasisRunner(
        plan,
        client_factory(),
        checkpoint_path=args.checkpoint,
        artifact_dir=args.artifact_dir,
        runner_factories=runners,
        run_config_factory=config_factory,
        empty_continuity_factory=continuity,
    )
    result = runner.run(max_cells=args.max_cells)
    print(
        json.dumps(
            {
                "status": result["status"],
                "stop_reason": result["stop_reason"],
                "completed_cells": len(result["completed_cells"]),
                "model_cost_cents_unrounded": (
                    result["model_cost_units"] / _COST_UNITS_PER_CENT
                ),
                "prior_model_cost_cents_unrounded": (
                    result["prior_model_cost_units"] / _COST_UNITS_PER_CENT
                ),
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] in {"completed", "paused"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
