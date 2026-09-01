"""Checkpointed runner for the preregistered active homeostasis comparison."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable

from capage.homeostasis import ControllerHistory, EconomicMode
from capage.homeostasis_experiment import (
    completed_period_signal,
    derive_pair_specs,
    make_treatment_runner_class,
    materialize_matched_worlds,
    starting_signal,
    validate_plan,
)


CHECKPOINT_SCHEMA = "capage-homeostasis-active-checkpoint-v1"
CONFIRMATION = "RUN_MATCHED_HOMEOSTASIS_ACTIVE_V1_MAX_900_CENTS"
_COST_UNITS_PER_CENT = 1_000_000
_IMPLEMENTATION_PATHS = (
    "capage/sandbox.py",
    "capage/sandbox_runner.py",
    "capage/homeostasis.py",
    "capage/homeostasis_shadow.py",
    "capage/homeostasis_experiment.py",
    "capage/homeostasis_active_runner.py",
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def implementation_commitments() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    return {path: sha256((root / path).read_bytes()).hexdigest() for path in _IMPLEMENTATION_PATHS}


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
            input_cents_per_million_tokens=int(tariff["input_cents_per_million_tokens"]),
            output_cents_per_million_tokens=int(tariff["output_cents_per_million_tokens"]),
            tariff_valid_through=str(tariff["valid_through"]),
            per_cell_cost_cap_cents=int(budget["per_cell_cost_cap_cents"]),
            aggregate_cost_cap_cents=int(budget["provider_cost_cap_cents"]),
        )
        if config.aggregate_cost_cap_cents != 900:
            raise ValueError("active experiment aggregate cap must be exactly 900 cents")
        if config.per_cell_cost_cap_cents * 12 != config.aggregate_cost_cap_cents:
            raise ValueError("twelve cell caps must equal the aggregate cap")
        date.fromisoformat(config.tariff_valid_through)
        return config

    def commitment(self) -> str:
        return _digest(asdict(self))


RunnerFactory = Callable[..., Any]
RunConfigFactory = Callable[..., Any]


def _system_clock() -> datetime:
    """Default injectable clock: the real wall clock, UTC.

    Tariff-expiry checks read the current time through an injected clock so
    tests can pin a deterministic instant without monkey-patching module
    globals. The frozen default preserves prior production behaviour exactly.
    """

    return datetime.now(timezone.utc)


class ActiveHomeostasisRunner:
    """Run frozen cells serially, checkpointing after every completed result."""

    def __init__(
        self,
        plan: dict[str, Any],
        client: Any,
        *,
        checkpoint_path: str | Path,
        artifact_dir: str | Path,
        control_runner_factory: RunnerFactory,
        treatment_runner_factory: RunnerFactory,
        run_config_factory: RunConfigFactory,
        empty_continuity_factory: Callable[[], dict[str, Any]],
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.plan = json.loads(_canonical_json(plan))
        self.config = ActiveConfig.from_plan(self.plan)
        self.client = client
        self.checkpoint_path = Path(checkpoint_path)
        self.artifact_dir = Path(artifact_dir)
        self.control_runner_factory = control_runner_factory
        self.treatment_runner_factory = treatment_runner_factory
        self.run_config_factory = run_config_factory
        self.empty_continuity_factory = empty_continuity_factory
        self._clock = clock if clock is not None else _system_clock
        self.state = self._load_or_initialize()

    def _initial_state(self) -> dict[str, Any]:
        arms = {}
        for arm in ("control", "treatment"):
            arms[arm] = {
                "balance_cents": self.config.starting_capital_cents,
                "model_cost_units": 0,
                "business_continuity": self.empty_continuity_factory(),
            }
        return {
            "schema_version": CHECKPOINT_SCHEMA,
            "status": "ready",
            "stop_reason": None,
            "config_commitment": self.config.commitment(),
            "plan_sha256": self.config.plan_sha256,
            "implementation_commitments": implementation_commitments(),
            "model_cost_units": 0,
            "completed_cells": {},
            "arms": arms,
            "errors": [],
        }

    def _load_or_initialize(self) -> dict[str, Any]:
        if not self.checkpoint_path.exists():
            return self._initial_state()
        payload = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != CHECKPOINT_SCHEMA:
            raise ValueError("unsupported active checkpoint schema")
        if payload.get("config_commitment") != self.config.commitment():
            raise ValueError("active checkpoint config mismatch")
        if payload.get("plan_sha256") != self.config.plan_sha256:
            raise ValueError("active checkpoint plan mismatch")
        if payload.get("implementation_commitments") != implementation_commitments():
            raise ValueError("active checkpoint implementation mismatch")
        return payload

    def _checkpoint(self) -> None:
        _atomic_json(self.checkpoint_path, self.state)

    def _signal_for_period(self, period: int):
        signal = starting_signal()
        history = signal.next_history
        if period == 1:
            return signal
        for prior in range(1, period):
            cell_id = f"pair-{prior:02d}:treatment"
            record = self.state["completed_cells"].get(cell_id)
            if not isinstance(record, dict):
                raise ValueError("treatment signal requested before prior period completed")
            result_path = self.artifact_dir / str(record["result_file"])
            result = json.loads(result_path.read_text(encoding="utf-8"))
            signal = completed_period_signal(
                result,
                history,
                observation_id=f"pair-{prior:02d}:treatment:completed",
            )
            history = signal.next_history
        return signal

    def _run_config(self, pair_index: int, arm: str, seed: int, starting: int):
        return self.run_config_factory(
            run_name=f"homeostasis-active-v1-pair-{pair_index:02d}-{arm}",
            seed=seed,
            model=self.config.model,
            effort=self.config.effort,
            max_output_tokens=self.config.max_output_tokens,
            max_decisions=self.config.max_decisions,
            max_run_cost_cents=self.config.per_cell_cost_cap_cents,
            horizon_days=self.config.horizon_days,
            starting_capital_cents=starting,
            tariff_name=self.config.tariff_name,
            input_cents_per_million_tokens=self.config.input_cents_per_million_tokens,
            output_cents_per_million_tokens=self.config.output_cents_per_million_tokens,
            customer_population_seed=self.config.customer_population_seed,
            assessor_version=self.config.assessor_version,
            tariff_valid_through=self.config.tariff_valid_through,
        )

    def _validate_result(self, result: dict[str, Any], run_config: Any) -> None:
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
        if not isinstance(outcome, dict) or not isinstance(outcome.get("balance_cents"), int):
            raise ValueError("cell omitted a valid outcome balance")
        if not isinstance(result.get("business_continuity"), dict):
            raise ValueError("cell omitted business continuity")

    def run(self, *, max_cells: int | None = None) -> dict[str, Any]:
        if max_cells is not None and not 1 <= max_cells <= 12:
            raise ValueError("max_cells must be between 1 and 12")
        if self.state["status"] == "completed":
            return self.state
        if self._clock().date() > date.fromisoformat(
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
        for pair in derive_pair_specs():
            for arm in pair.execution_order:
                cell_id = f"pair-{pair.pair_index:02d}:{arm}"
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
                    pair.pair_index,
                    arm,
                    pair.world_seed,
                    int(arm_state["balance_cents"]),
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
                attempt = {
                    "schema_version": "capage-paid-attempt-v1",
                    "cell_id": cell_id,
                    "config_commitment": self.config.commitment(),
                    "status": "started",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                }
                _atomic_json(attempt_path, attempt)
                kwargs = {
                    "audit_path": audit_path,
                    "continuity_state": arm_state["business_continuity"],
                }
                factory = self.control_runner_factory
                if arm == "treatment":
                    factory = self.treatment_runner_factory
                    kwargs["homeostasis_signal"] = self._signal_for_period(pair.pair_index)
                try:
                    runner = factory(run_config, self.client, **kwargs)
                    result = runner.run()
                    self._validate_result(result, run_config)
                except Exception as exc:
                    self.state["errors"].append(
                        {"cell_id": cell_id, "error_type": type(exc).__name__, "error": str(exc)}
                    )
                    self.state["status"] = "stopped"
                    self.state["stop_reason"] = "provider_or_runner_error"
                    self._checkpoint()
                    return self.state

                _atomic_json(result_path, result)
                used = int(result["actual_model_cost_units"])
                projected_total = int(self.state["model_cost_units"]) + used
                if projected_total > self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT:
                    raise RuntimeError("aggregate provider cost cap exceeded")
                self.state["model_cost_units"] = projected_total
                arm_state["model_cost_units"] += used
                arm_state["balance_cents"] = int(result["outcome"]["balance_cents"])
                arm_state["business_continuity"] = result["business_continuity"]
                record = {
                    "cell_id": cell_id,
                    "pair_index": pair.pair_index,
                    "arm": arm,
                    "seed": pair.world_seed,
                    "execution_order": list(pair.execution_order),
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
                    {**attempt, "status": "completed", "result_sha256": record["result_sha256"]},
                )
                attempted += 1
                self._checkpoint()

        self.state["status"] = "completed"
        self.state["stop_reason"] = "all_cells_completed"
        self._checkpoint()
        return self.state


def _real_factories(plan: dict[str, Any]):
    from capage.anthropic_client import AnthropicMessagesClient
    from capage.sandbox import EconomicSandbox, TokenTariff, empty_continuity_state
    from capage.sandbox_runner import LiveSandboxRunner, SandboxRunConfig

    treatment = make_treatment_runner_class(LiveSandboxRunner)
    active_config = ActiveConfig.from_plan(plan)
    tariff = TokenTariff(
        active_config.tariff_name,
        active_config.input_cents_per_million_tokens,
        active_config.output_cents_per_million_tokens,
    )

    def world_factory(seed, **kwargs):
        return EconomicSandbox(seed, token_tariff=tariff, **kwargs)

    def config_factory(*, tariff_name, input_cents_per_million_tokens,
                       output_cents_per_million_tokens, **kwargs):
        return SandboxRunConfig(
            **kwargs,
            tariff=TokenTariff(tariff_name, input_cents_per_million_tokens,
                               output_cents_per_million_tokens),
        )

    return (
        AnthropicMessagesClient,
        world_factory,
        LiveSandboxRunner,
        treatment,
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
    factories = _real_factories(plan)
    _, world_factory, control, treatment, config_factory, continuity = factories
    if args.validate_only:
        records = materialize_matched_worlds(plan, world_factory)
        print(json.dumps({"status": "validated", "matched_worlds": len(records)}, sort_keys=True))
        return 0
    if args.confirm != CONFIRMATION:
        raise SystemExit("exact paid-run confirmation is required")
    client_factory = factories[0]
    runner = ActiveHomeostasisRunner(
        plan,
        client_factory(),
        checkpoint_path=args.checkpoint,
        artifact_dir=args.artifact_dir,
        control_runner_factory=control,
        treatment_runner_factory=treatment,
        run_config_factory=config_factory,
        empty_continuity_factory=continuity,
    )
    result = runner.run(max_cells=args.max_cells)
    print(json.dumps({
        "status": result["status"],
        "stop_reason": result["stop_reason"],
        "completed_cells": len(result["completed_cells"]),
        "model_cost_cents_unrounded": result["model_cost_units"] / _COST_UNITS_PER_CENT,
    }, sort_keys=True))
    return 0 if result["status"] in {"completed", "paused"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
