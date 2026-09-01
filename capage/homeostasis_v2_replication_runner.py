"""Checkpointing and analysis for the blocked V1-versus-V2 replication.

The module exposes no provider client, paid CLI, confirmation string, workflow,
or authorization marker.  A later reviewed launch layer must inject both the
runner factories and an execution guard.  This file can therefore be tested and
reviewed without creating a spending path.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable

from capage.frozen_paths import path_commitments
from capage.homeostasis import EconomicStateProjector
from capage.homeostasis_shadow import SandboxResultProjector
from capage.homeostasis_v2 import validate_objective_delivery
from capage.homeostasis_v2_experiment import (
    completed_signal_for_arm,
    signal_for_arm_start,
)
from capage.homeostasis_v2_replication import (
    ARMS,
    BLOCK_COUNT,
    CELL_COUNT,
    PERIODS_PER_BLOCK,
    PREREGISTRATION_PATH,
    exogenous_world_sha256,
    file_sha256,
    materialize_matched_worlds,
    ordered_cells,
    validate_plan,
)
from capage.sandbox import (
    validate_continuity_state,
    verify_cost_policy,
    verify_world_reveal,
)


CHECKPOINT_SCHEMA = "capage-homeostasis-v2-blocked-replication-checkpoint-v1"
ANALYSIS_SCHEMA = "capage-homeostasis-v2-blocked-replication-analysis-v1"
ATTEMPT_SCHEMA = "capage-paid-attempt-v3"
PLAN_PATH = (
    "experiments/sandbox/economic_homeostasis_v2_replication_plan_v1.json"
)
_COST_UNITS_PER_CENT = 1_000_000
_ORCHESTRATION_PATHS = (
    PREREGISTRATION_PATH,
    PLAN_PATH,
    "capage/homeostasis_v2_replication.py",
    "capage/homeostasis_v2_replication_runner.py",
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


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    _atomic_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _utc_now() -> datetime:
    """Wall-clock seam. Injectable so the frozen-tariff guard is testable
    without depending on the day the test runs; production uses this default,
    which is exactly datetime.now(timezone.utc)."""
    return datetime.now(timezone.utc)


def runtime_commitments(root: str | Path) -> dict[str, str]:
    return path_commitments(_ORCHESTRATION_PATHS, root=root)


def _signal_payload(signal: Any) -> dict[str, Any]:
    payload = signal.to_prompt_data()
    if not isinstance(payload, dict):
        raise TypeError("homeostasis signal did not serialize to an object")
    return json.loads(_canonical_json(payload))


def _cell_id(block_index: int, period_index: int, arm: str) -> str:
    return f"block-{block_index:02d}:period-{period_index:02d}:{arm}"


def _run_stem(block_index: int, period_index: int, arm: str) -> str:
    return f"homeostasis-v2-replication-b{block_index:02d}-p{period_index:02d}-{arm}"


@dataclass(frozen=True)
class ReplicationConfig:
    plan_sha256: str
    starting_capital_cents: int
    horizon_days: int
    max_decisions: int
    model: str
    effort: str
    max_output_tokens: int
    assessor_version: str
    market_profile: str
    tariff_name: str
    input_cents_per_million_tokens: int
    output_cents_per_million_tokens: int
    tariff_valid_through: str
    per_cell_cost_cap_cents: int
    aggregate_cost_cap_cents: int

    @classmethod
    def from_plan(cls, plan: dict[str, Any]) -> "ReplicationConfig":
        frozen = plan["frozen_config"]
        tariff = frozen["token_tariff"]
        budget = plan["maximum_budget"]
        config = cls(
            plan_sha256=_digest(plan),
            starting_capital_cents=int(
                frozen["starting_capital_cents_per_block"]
            ),
            horizon_days=int(frozen["horizon_days_per_period"]),
            max_decisions=int(frozen["max_decisions_per_cell"]),
            model=str(frozen["model"]),
            effort=str(frozen["effort"]),
            max_output_tokens=int(frozen["max_output_tokens"]),
            assessor_version=str(frozen["assessor_version"]),
            market_profile=str(frozen["market_profile"]),
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
        if config.per_cell_cost_cap_cents != 45:
            raise ValueError("replication per-cell cap must be exactly 45 cents")
        if config.aggregate_cost_cap_cents != 2_160:
            raise ValueError("replication aggregate cap must be exactly 2160 cents")
        if config.per_cell_cost_cap_cents * CELL_COUNT != 2_160:
            raise ValueError("forty-eight cell caps must equal the aggregate cap")
        date.fromisoformat(config.tariff_valid_through)
        return config

    def commitment(self) -> str:
        return _digest(asdict(self))


RunnerFactory = Callable[..., Any]
RunConfigFactory = Callable[..., Any]
ExecutionGuard = Callable[[], None]


class BlockedReplicationRunner:
    """Run the frozen 48-cell prefix serially and fail closed on ambiguity."""

    def __init__(
        self,
        plan: dict[str, Any],
        preregistration: dict[str, Any],
        client: Any,
        *,
        checkpoint_path: str | Path,
        artifact_dir: str | Path,
        runner_factories: dict[str, RunnerFactory],
        run_config_factory: RunConfigFactory,
        world_factory: Callable[..., Any],
        empty_continuity_factory: Callable[[], dict[str, Any]],
        execution_guard: ExecutionGuard,
        root: str | Path | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        if set(runner_factories) != set(ARMS):
            raise ValueError("runner_factories must contain exactly v1 and v2")
        if not callable(execution_guard):
            raise TypeError("a later reviewed execution guard is required")
        self.root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
        validate_plan(plan, preregistration=preregistration, root=self.root)
        self.plan = json.loads(_canonical_json(plan))
        self.preregistration = json.loads(_canonical_json(preregistration))
        self.config = ReplicationConfig.from_plan(self.plan)
        self.client = client
        self.checkpoint_path = Path(checkpoint_path)
        self.artifact_dir = Path(artifact_dir)
        self.runner_factories = dict(runner_factories)
        self.run_config_factory = run_config_factory
        self.world_factory = world_factory
        self.empty_continuity_factory = empty_continuity_factory
        self.execution_guard = execution_guard
        self._now = now or _utc_now
        self._matched_worlds = {
            (int(record["block_index"]), int(record["period_index"])): record
            for record in self.plan["matched_worlds"]
        }
        if list(materialize_matched_worlds(self.plan, self.world_factory)) != self.plan[
            "matched_worlds"
        ]:
            raise ValueError("matched-world materialization changed before execution")
        self.state = self._load_or_initialize()

    def _empty_arm_state(self) -> dict[str, Any]:
        continuity = self.empty_continuity_factory()
        if not isinstance(continuity, dict):
            raise TypeError("empty continuity factory must return an object")
        return {
            "balance_cents": self.config.starting_capital_cents,
            "model_cost_units": 0,
            "business_continuity": deepcopy(continuity),
        }

    def _initial_state(self) -> dict[str, Any]:
        blocks = {
            f"block-{index:02d}": {
                "arms": {arm: self._empty_arm_state() for arm in ARMS}
            }
            for index in range(1, BLOCK_COUNT + 1)
        }
        return {
            "schema_version": CHECKPOINT_SCHEMA,
            "status": "ready",
            "stop_reason": None,
            "config_commitment": self.config.commitment(),
            "plan_sha256": self.config.plan_sha256,
            "runtime_commitments": runtime_commitments(self.root),
            "model_cost_units": 0,
            "completed_cells": {},
            "blocks": blocks,
            "errors": [],
        }

    def _load_or_initialize(self) -> dict[str, Any]:
        if not self.checkpoint_path.exists():
            return self._initial_state()
        payload = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != CHECKPOINT_SCHEMA:
            raise ValueError("unsupported blocked replication checkpoint schema")
        if payload.get("config_commitment") != self.config.commitment():
            raise ValueError("checkpoint config mismatch")
        if payload.get("plan_sha256") != self.config.plan_sha256:
            raise ValueError("checkpoint plan mismatch")
        if payload.get("runtime_commitments") != runtime_commitments(self.root):
            raise ValueError("checkpoint implementation mismatch")
        self._validate_checkpoint_state(payload)
        return payload

    def _checkpoint(self) -> None:
        _atomic_json(self.checkpoint_path, self.state)

    def _expected_signal(
        self,
        block_index: int,
        arm: str,
        period_index: int,
        *,
        completed: dict[str, Any] | None = None,
    ) -> Any:
        completed_cells = completed if completed is not None else self.state["completed_cells"]
        signal = signal_for_arm_start(arm)
        history = signal.next_history
        if period_index == 1:
            return signal
        for prior_period in range(1, period_index):
            prior_id = _cell_id(block_index, prior_period, arm)
            record = completed_cells.get(prior_id)
            if not isinstance(record, dict):
                raise ValueError("signal requested before own prior block period completed")
            result_path = self.artifact_dir / str(record["result_file"])
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if record.get("result_sha256") != _digest(result):
                raise ValueError("prior result artifact changed after checkpoint")
            signal = completed_signal_for_arm(arm, result, history)
            history = signal.next_history
        return signal

    def _run_config(
        self,
        block: Any,
        period: Any,
        arm: str,
        starting_capital_cents: int,
        max_run_cost_cents: int,
    ) -> Any:
        return self.run_config_factory(
            run_name=_run_stem(block.block_index, period.period_index, arm),
            seed=period.world_seed,
            model=self.config.model,
            effort=self.config.effort,
            max_output_tokens=self.config.max_output_tokens,
            max_decisions=self.config.max_decisions,
            max_run_cost_cents=max_run_cost_cents,
            horizon_days=self.config.horizon_days,
            starting_capital_cents=starting_capital_cents,
            tariff_name=self.config.tariff_name,
            input_cents_per_million_tokens=(
                self.config.input_cents_per_million_tokens
            ),
            output_cents_per_million_tokens=(
                self.config.output_cents_per_million_tokens
            ),
            customer_population_seed=block.customer_population_seed,
            customer_namespace="",
            market_profile=self.config.market_profile,
            assessor_version=self.config.assessor_version,
            tariff_valid_through=self.config.tariff_valid_through,
        )

    @staticmethod
    def _validate_serialized_config(result: dict[str, Any], run_config: Any) -> None:
        result_config = result.get("config")
        fields = (
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
        if not isinstance(result_config, dict) or any(
            result_config.get(field) != getattr(run_config, field)
            for field in fields
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

    def _validate_result(
        self,
        result: dict[str, Any],
        run_config: Any,
        matched_world: dict[str, Any],
    ) -> None:
        if result.get("schema_version") != "capage-live-sandbox-result-v1":
            raise ValueError("cell returned unsupported result schema")
        if result.get("status") != "completed":
            raise ValueError("cell did not complete")
        self._validate_serialized_config(result, run_config)
        transcript = result.get("transcript")
        decision_count = result.get("decision_count")
        if not isinstance(transcript, list) or decision_count != len(transcript):
            raise ValueError("cell transcript does not match decision count")

        units = result.get("actual_model_cost_units")
        if isinstance(units, bool) or not isinstance(units, int) or units < 0:
            raise ValueError("cell omitted valid model cost units")
        if units > run_config.max_run_cost_cents * _COST_UNITS_PER_CENT:
            raise ValueError("cell exceeded its provider cost cap")
        outcome = result.get("outcome")
        if not isinstance(outcome, dict):
            raise ValueError("cell omitted its outcome")
        balance = outcome.get("balance_cents")
        if isinstance(balance, bool) or not isinstance(balance, int):
            raise ValueError("cell omitted a valid outcome balance")
        if outcome.get("net_change_cents") != balance - run_config.starting_capital_cents:
            raise ValueError("cell net change does not match carried capital")
        if outcome.get("insolvent") is not (balance == 0):
            raise ValueError("cell insolvency flag does not match ending capital")
        run_id = outcome.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("cell outcome omitted its sandbox run_id")

        input_tokens = outcome.get("model_input_tokens")
        output_tokens = outcome.get("model_output_tokens")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in (input_tokens, output_tokens)
        ):
            raise ValueError("cell outcome omitted valid model token totals")
        expected_units = run_config.tariff.cost_units(input_tokens, output_tokens)
        if expected_units != units or outcome.get("model_api_cost_units") != units:
            raise ValueError("cell model token totals do not match cost units")
        billed_cents = (units + _COST_UNITS_PER_CENT - 1) // _COST_UNITS_PER_CENT
        if (
            result.get("actual_model_cost_cents_billed") != billed_cents
            or outcome.get("model_api_cost_cents") != billed_cents
        ):
            raise ValueError("cell billed model cost does not match cost units")
        if result.get("actual_model_cost_cents_unrounded") != (
            units / _COST_UNITS_PER_CENT
        ):
            raise ValueError("cell unrounded model cost does not match cost units")
        if not isinstance(result.get("business_continuity"), dict):
            raise ValueError("cell omitted business continuity")
        validate_continuity_state(result["business_continuity"])

        reveal = result.get("world_reveal")
        if not isinstance(reveal, dict):
            raise ValueError("cell omitted its world reveal")
        if not verify_world_reveal(reveal):
            raise ValueError("cell world reveal does not match its commitment")
        if not verify_cost_policy(reveal):
            raise ValueError("cell cost policy does not match its commitment")
        if outcome.get("world_commitment") != reveal.get("world_commitment"):
            raise ValueError("cell outcome and reveal world commitments differ")
        if outcome.get("cost_policy_commitment") != reveal.get(
            "cost_policy_commitment"
        ):
            raise ValueError("cell outcome and reveal cost commitments differ")
        payload = reveal.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("cell world reveal payload must be an object")
        expected_payload_fields = {
            "seed": run_config.seed,
            "horizon_days": run_config.horizon_days,
            "starting_capital_cents": run_config.starting_capital_cents,
            "customer_population_seed": run_config.customer_population_seed,
        }
        if any(
            payload.get(field) != value
            for field, value in expected_payload_fields.items()
        ):
            raise ValueError("cell world payload does not match its run config")
        if exogenous_world_sha256(payload) != matched_world["exogenous_world_sha256"]:
            raise ValueError("cell exogenous world does not match materialization")
        if reveal.get("cost_policy_commitment") != matched_world["cost_policy_commitment"]:
            raise ValueError("cell cost policy changed after materialization")
        SandboxResultProjector.project(result)

    def _validate_checkpoint_state(self, payload: dict[str, Any]) -> None:
        completed = payload.get("completed_cells")
        if not isinstance(completed, dict):
            raise ValueError("checkpoint completed_cells must be an object")
        ordered = [
            (_cell_id(block.block_index, period.period_index, arm), block, period, arm)
            for block, period, arm in ordered_cells()
        ]
        if len(completed) > len(ordered):
            raise ValueError("checkpoint contains too many completed cells")
        expected_prefix = {cell_id for cell_id, _, _, _ in ordered[: len(completed)]}
        if set(completed) != expected_prefix:
            raise ValueError("checkpoint completed cells are not the frozen prefix")

        initial_continuity = self.empty_continuity_factory()
        recomputed = {
            f"block-{index:02d}": {
                "arms": {
                    arm: {
                        "balance_cents": self.config.starting_capital_cents,
                        "model_cost_units": 0,
                        "business_continuity": deepcopy(initial_continuity),
                    }
                    for arm in ARMS
                }
            }
            for index in range(1, BLOCK_COUNT + 1)
        }
        aggregate_units = 0
        for cell_id, block, period, arm in ordered[: len(completed)]:
            record = completed[cell_id]
            if not isinstance(record, dict):
                raise ValueError(f"checkpoint record {cell_id} must be an object")
            stem = _run_stem(block.block_index, period.period_index, arm)
            expected = {
                "cell_id": cell_id,
                "block_index": block.block_index,
                "period_index": period.period_index,
                "arm": arm,
                "world_seed": period.world_seed,
                "customer_population_seed": block.customer_population_seed,
                "execution_order": list(period.execution_order),
                "result_file": f"{stem}.json",
                "audit_file": f"{stem}-audit.jsonl",
            }
            if any(record.get(key) != value for key, value in expected.items()):
                raise ValueError(f"checkpoint record {cell_id} has invalid metadata")
            arm_state = recomputed[f"block-{block.block_index:02d}"]["arms"][arm]
            if record.get("starting_capital_cents") != arm_state["balance_cents"]:
                raise ValueError(f"checkpoint record {cell_id} breaks block continuity")
            remaining = (
                self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT
                - aggregate_units
            )
            historical_cap = min(
                self.config.per_cell_cost_cap_cents,
                remaining // _COST_UNITS_PER_CENT,
            )
            if historical_cap < 1:
                raise ValueError("checkpoint contains a cell beyond the aggregate cap")
            run_config = self._run_config(
                block,
                period,
                arm,
                int(arm_state["balance_cents"]),
                historical_cap,
            )
            signal = self._expected_signal(
                block.block_index,
                arm,
                period.period_index,
                completed=completed,
            )
            signal_payload = _signal_payload(signal)
            if record.get("homeostasis_signal") != signal_payload:
                raise ValueError(f"checkpoint signal mismatch for {cell_id}")

            result_path = self.artifact_dir / expected["result_file"]
            audit_path = self.artifact_dir / expected["audit_file"]
            attempt_path = self.artifact_dir / f"{stem}-attempt.json"
            if not result_path.is_file() or not audit_path.is_file() or not attempt_path.is_file():
                raise ValueError(f"checkpoint evidence missing for {cell_id}")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if record.get("result_sha256") != _digest(result):
                raise ValueError(f"checkpoint result artifact mismatch for {cell_id}")
            if record.get("audit_sha256") != file_sha256(audit_path):
                raise ValueError(f"checkpoint audit artifact mismatch for {cell_id}")
            matched = self._matched_worlds[(block.block_index, period.period_index)]
            self._validate_result(result, run_config, matched)
            units = int(result["actual_model_cost_units"])
            ending = int(result["outcome"]["balance_cents"])
            if record.get("actual_model_cost_units") != units:
                raise ValueError(f"checkpoint cost mismatch for {cell_id}")
            if record.get("ending_balance_cents") != ending:
                raise ValueError(f"checkpoint balance mismatch for {cell_id}")
            attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
            if (
                attempt.get("schema_version") != ATTEMPT_SCHEMA
                or attempt.get("cell_id") != cell_id
                or attempt.get("config_commitment") != self.config.commitment()
                or attempt.get("runtime_commitments")
                != payload.get("runtime_commitments")
                or attempt.get("status") != "completed"
                or attempt.get("result_sha256") != record["result_sha256"]
                or attempt.get("audit_sha256") != record["audit_sha256"]
            ):
                raise ValueError(f"checkpoint attempt marker mismatch for {cell_id}")
            aggregate_units += units
            arm_state["model_cost_units"] += units
            arm_state["balance_cents"] = ending
            arm_state["business_continuity"] = result["business_continuity"]

        if payload.get("model_cost_units") != aggregate_units:
            raise ValueError("checkpoint aggregate model cost mismatch")
        if aggregate_units > self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT:
            raise ValueError("checkpoint aggregate model cost exceeds cap")
        if payload.get("blocks") != recomputed:
            raise ValueError("checkpoint block state does not match completed evidence")
        if payload.get("status") not in {"ready", "running", "paused", "stopped", "completed"}:
            raise ValueError("checkpoint status is invalid")
        if payload.get("status") == "ready" and completed:
            raise ValueError("ready checkpoint cannot contain completed cells")
        if payload.get("status") == "completed" and len(completed) != CELL_COUNT:
            raise ValueError("completed checkpoint must contain forty-eight cells")
        if not isinstance(payload.get("errors"), list):
            raise ValueError("checkpoint errors must be an array")

    def run(self, *, max_cells: int | None = None) -> dict[str, Any]:
        """Run only after a later launch layer's guard returns successfully."""

        self.execution_guard()
        validate_plan(
            self.plan,
            preregistration=self.preregistration,
            root=self.root,
        )
        if runtime_commitments(self.root) != self.state["runtime_commitments"]:
            raise ValueError("runtime implementation changed after checkpoint creation")
        if max_cells is not None and not 1 <= max_cells <= CELL_COUNT:
            raise ValueError("max_cells must be between 1 and 48")
        if self.state["status"] == "completed":
            return self.state
        if self._now().date() > date.fromisoformat(
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
        for block, period, arm in ordered_cells():
            cell_id = _cell_id(block.block_index, period.period_index, arm)
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

            arm_state = self.state["blocks"][f"block-{block.block_index:02d}"]["arms"][arm]
            try:
                signal = self._expected_signal(
                    block.block_index,
                    arm,
                    period.period_index,
                )
                signal_payload = _signal_payload(signal)
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

            run_config = self._run_config(
                block,
                period,
                arm,
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
            attempt = {
                "schema_version": ATTEMPT_SCHEMA,
                "cell_id": cell_id,
                "config_commitment": self.config.commitment(),
                "runtime_commitments": runtime_commitments(self.root),
                "status": "started",
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
            _atomic_json(attempt_path, attempt)
            _atomic_text(audit_path, "")
            try:
                runner = self.runner_factories[arm](
                    run_config,
                    self.client,
                    audit_path=audit_path,
                    continuity_state=arm_state["business_continuity"],
                    homeostasis_signal=signal,
                )
                result = runner.run()
                matched = self._matched_worlds[
                    (block.block_index, period.period_index)
                ]
                self._validate_result(result, run_config, matched)
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
            ending = int(result["outcome"]["balance_cents"])
            self.state["model_cost_units"] = projected_total
            arm_state["model_cost_units"] += used
            arm_state["balance_cents"] = ending
            arm_state["business_continuity"] = result["business_continuity"]
            record = {
                "cell_id": cell_id,
                "block_index": block.block_index,
                "period_index": period.period_index,
                "arm": arm,
                "world_seed": period.world_seed,
                "customer_population_seed": block.customer_population_seed,
                "execution_order": list(period.execution_order),
                "homeostasis_signal": signal_payload,
                "starting_capital_cents": run_config.starting_capital_cents,
                "ending_balance_cents": ending,
                "actual_model_cost_units": used,
                "result_file": result_path.name,
                "audit_file": audit_path.name,
                "result_sha256": _digest(result),
                "audit_sha256": file_sha256(audit_path),
            }
            self.state["completed_cells"][cell_id] = record
            _atomic_json(
                attempt_path,
                {
                    **attempt,
                    "status": "completed",
                    "result_sha256": record["result_sha256"],
                    "audit_sha256": record["audit_sha256"],
                },
            )
            attempted += 1
            self._checkpoint()

        self.state["status"] = "completed"
        self.state["stop_reason"] = "all_cells_completed"
        self._checkpoint()
        return self.state

    def analyze(self) -> dict[str, Any]:
        """Return the frozen gate and diagnostics only after all evidence validates."""

        self._validate_checkpoint_state(self.state)
        if self.state.get("status") != "completed":
            raise ValueError("incomplete replication is inconclusive and cannot be analyzed")
        return analyze_completed_replication(
            self.plan,
            self.state,
            self.artifact_dir,
        )


_ALLOWED_SANDBOX_TOOLS = {
    "sandbox.observe",
    "sandbox.inspect_ledger",
    "sandbox.search_market",
    "sandbox.send_offer",
    "sandbox.submit_delivery",
    "sandbox.request_feedback",
    "sandbox.wait",
}


def _journal(result: dict[str, Any]) -> list[dict[str, Any]]:
    reveal = result.get("world_reveal")
    journal = reveal.get("journal") if isinstance(reveal, dict) else None
    if not isinstance(journal, list) or not all(
        isinstance(event, dict) for event in journal
    ):
        raise ValueError("result journal is invalid")
    return journal


def _tool_input(record: dict[str, Any]) -> dict[str, Any]:
    response = record.get("provider_response")
    content = response.get("content") if isinstance(response, dict) else None
    if not isinstance(content, list):
        return {}
    blocks = [
        block
        for block in content
        if isinstance(block, dict) and block.get("type") == "tool_use"
    ]
    if len(blocks) != 1 or not isinstance(blocks[0].get("input"), dict):
        return {}
    return blocks[0]["input"]


def _cell_metrics(result: dict[str, Any]) -> dict[str, Any]:
    outcome = result["outcome"]
    continuity = result["business_continuity"]
    transcript = result["transcript"]
    journal = _journal(result)

    action_mix: Counter[str] = Counter()
    tool_token_totals: dict[str, dict[str, int]] = {}
    visible_signals: set[str] = set()
    delivery_attempts = 0
    local_rejections = 0
    corrected_contracts: set[str] = set()
    rejected_contracts: set[str] = set()
    invalid_crossings = 0
    constitutional_boundary_failure = False

    contract_briefs: dict[str, dict[str, Any] | None] = {}
    accepted_days: dict[str, int] = {}
    submitted_days: dict[str, list[int]] = {}
    feedback: Counter[str] = Counter()
    assessed_deliveries = 0
    for event in journal:
        event_type = event.get("event_type")
        data = event.get("data")
        if not isinstance(data, dict):
            continue
        if event_type == "offer_accepted":
            contract_id = str(data.get("contract_id", ""))
            contract_briefs[contract_id] = data.get("delivery_brief")
            accepted_days[contract_id] = int(event.get("day", 0))
        elif event_type == "delivery_submitted":
            contract_id = str(data.get("contract_id", ""))
            submitted_days.setdefault(contract_id, []).append(int(event.get("day", 0)))
        elif event_type == "delivery_assessed":
            assessed_deliveries += 1
        elif event_type == "feedback_received":
            feedback[str(data.get("rating", "unknown"))] += 1

    for record in transcript:
        if not isinstance(record, dict):
            raise ValueError("transcript records must be objects")
        host_tool = record.get("host_tool_name")
        host_tool_valid = isinstance(host_tool, str) and host_tool in _ALLOWED_SANDBOX_TOOLS
        metered = record.get("metered_usage")
        if isinstance(metered, dict):
            # A decision can be metered (real tokens spent, real cost charged)
            # and still fail to resolve a valid tool afterward -- e.g. the
            # model's response was malformed. Those tokens are real spend and
            # must not silently disappear from the per-tool totals just
            # because host_tool_name was never set on that record.
            bucket = host_tool if host_tool_valid else "unattributed_failed_decision"
            bucket_totals = tool_token_totals.setdefault(
                bucket, {"input_tokens": 0, "output_tokens": 0, "call_count": 0}
            )
            bucket_totals["input_tokens"] += int(metered.get("input_tokens", 0))
            bucket_totals["output_tokens"] += int(metered.get("output_tokens", 0))
            bucket_totals["call_count"] += 1
        if not host_tool_valid:
            constitutional_boundary_failure = True
            continue
        action_mix[host_tool] += 1
        execution = record.get("execution")
        execution = execution if isinstance(execution, dict) else {}
        tool_result = execution.get("tool_result")
        tool_result = tool_result if isinstance(tool_result, dict) else {}
        if host_tool == "sandbox.search_market":
            for row in tool_result.get("results", []):
                if isinstance(row, dict) and isinstance(row.get("signal_id"), str):
                    visible_signals.add(row["signal_id"])
        if host_tool != "sandbox.submit_delivery":
            continue

        delivery_attempts += 1
        arguments = _tool_input(record)
        contract_id = str(arguments.get("contract_id", ""))
        artifact = str(arguments.get("artifact", ""))
        validation = validate_objective_delivery(
            artifact,
            contract_briefs.get(contract_id),
        )
        local_rejection = (
            tool_result.get("reason") == "objective_delivery_validation_failed"
        )
        if local_rejection:
            local_rejections += 1
            rejected_contracts.add(contract_id)
            if not validation.applicable or validation.valid:
                raise ValueError("local rejection is inconsistent with objective validator")
        crossed_boundary = bool(execution.get("success") and tool_result.get("ok"))
        if crossed_boundary and validation.applicable and not validation.valid:
            invalid_crossings += 1
        if crossed_boundary and validation.valid and contract_id in rejected_contracts:
            corrected_contracts.add(contract_id)

    acceptance_to_delivery = []
    for contract_id, accepted_day in accepted_days.items():
        days = submitted_days.get(contract_id, [])
        if days:
            acceptance_to_delivery.append(min(days) - accepted_day)

    projection = SandboxResultProjector.project(result)
    economic_state = EconomicStateProjector.project(
        projection.facts,
        projection.expenses,
    )
    return {
        "earned_revenue_cents": int(outcome.get("earned_revenue_cents", 0)),
        "model_api_cost_units": int(result["actual_model_cost_units"]),
        "decision_count": int(result["decision_count"]),
        "decision_limit_stop": result.get("stop_reason") == "decision_limit",
        "offers_sent": int(outcome.get("offers_sent", 0)),
        "contracts_accepted": int(outcome.get("contracts_accepted", 0)),
        "contracts_paid": int(outcome.get("contracts_paid", 0)),
        "contracts_defaulted": int(outcome.get("contracts_defaulted", 0)),
        "contracts_disputed": int(outcome.get("contracts_disputed", 0)),
        "assessed_deliveries": assessed_deliveries,
        "invalid_deliveries_crossing_boundary": invalid_crossings,
        "local_objective_validation_rejections": local_rejections,
        "contracts_with_local_validation_rejection": len(rejected_contracts),
        "corrected_deliveries": len(corrected_contracts),
        "delivery_attempt_count": delivery_attempts,
        "search_action_count": action_mix["sandbox.search_market"],
        "unique_visible_signal_count": len(visible_signals),
        "action_mix": dict(sorted(action_mix.items())),
        "tool_token_totals": dict(sorted(tool_token_totals.items())),
        "no_revenue_period": int(outcome.get("earned_revenue_cents", 0)) == 0,
        "acceptance_to_first_delivery_elapsed_days": acceptance_to_delivery,
        "customer_feedback_distribution": dict(sorted(feedback.items())),
        "ending_balance_cents": int(outcome["balance_cents"]),
        "net_change_cents": int(outcome["net_change_cents"]),
        "ending_global_reputation_points": int(
            continuity.get("global_reputation_points", 0)
        ),
        "insolvent": bool(outcome.get("insolvent", False)),
        "functional_failure": bool(economic_state.functional_failure),
        "constitutional_boundary_failure": constitutional_boundary_failure,
    }


def _merge_counter(target: Counter[str], source: dict[str, int]) -> None:
    for key, value in source.items():
        target[str(key)] += int(value)


def _aggregate_arm(
    arm: str,
    cells: list[dict[str, Any]],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    action_mix: Counter[str] = Counter()
    feedback: Counter[str] = Counter()
    advisory: dict[str, Counter[str]] = {}
    elapsed_days: list[int] = []
    for cell in cells:
        metrics = cell["metrics"]
        _merge_counter(action_mix, metrics["action_mix"])
        _merge_counter(feedback, metrics["customer_feedback_distribution"])
        elapsed_days.extend(metrics["acceptance_to_first_delivery_elapsed_days"])
        signal = cell["homeostasis_signal"]
        fields = (
            ("mode", "urgency", "sustainability_pressure")
            if arm == "v1"
            else (
                "continuity_mode",
                "opportunity_urgency",
                "obligation_urgency",
                "verification_requirement",
                "priority_profile",
            )
        )
        for field in fields:
            advisory.setdefault(field, Counter())[str(signal.get(field))] += 1

    summed = lambda field: sum(int(cell["metrics"][field]) for cell in cells)
    assessed = summed("assessed_deliveries")
    disputes = summed("contracts_disputed")
    rejected_contracts = summed("contracts_with_local_validation_rejection")
    corrected_deliveries = summed("corrected_deliveries")
    unique_signals = summed("unique_visible_signal_count")
    offers = summed("offers_sent")
    block_capital = []
    block_reputation = []
    for block_index in range(1, BLOCK_COUNT + 1):
        state = checkpoint["blocks"][f"block-{block_index:02d}"]["arms"][arm]
        block_capital.append(int(state["balance_cents"]))
        block_reputation.append(
            int(state["business_continuity"].get("global_reputation_points", 0))
        )
    return {
        "cell_count": len(cells),
        "summed_block_ending_capital_cents": sum(block_capital),
        "summed_block_net_change_cents": sum(block_capital)
        - BLOCK_COUNT * 25_000,
        "block_ending_capital_cents": block_capital,
        "summed_block_ending_global_reputation_points": sum(block_reputation),
        "block_ending_global_reputation_points": block_reputation,
        "earned_revenue_cents": summed("earned_revenue_cents"),
        "model_api_cost_units": summed("model_api_cost_units"),
        "decision_count": summed("decision_count"),
        "decision_limit_stops": sum(
            bool(cell["metrics"]["decision_limit_stop"]) for cell in cells
        ),
        "offers_sent": offers,
        "contracts_accepted": summed("contracts_accepted"),
        "contracts_paid": summed("contracts_paid"),
        "contracts_defaulted": summed("contracts_defaulted"),
        "contracts_disputed": disputes,
        "assessed_deliveries": assessed,
        "delivery_dispute_rate": round(disputes / assessed, 8) if assessed else 0.0,
        "invalid_deliveries_crossing_customer_boundary": summed(
            "invalid_deliveries_crossing_boundary"
        ),
        "local_objective_validation_rejections": summed(
            "local_objective_validation_rejections"
        ),
        "local_validation_failure_count": summed(
            "local_objective_validation_rejections"
        ),
        "contracts_with_local_validation_rejection": rejected_contracts,
        "corrected_deliveries": corrected_deliveries,
        "corrected_delivery_count": corrected_deliveries,
        "correction_success_after_local_rejection": {
            "corrected_contracts": corrected_deliveries,
            "rejected_contracts": rejected_contracts,
            "rate": (
                round(corrected_deliveries / rejected_contracts, 8)
                if rejected_contracts
                else None
            ),
        },
        "delivery_attempt_count": summed("delivery_attempt_count"),
        "search_action_count": summed("search_action_count"),
        "unique_visible_signal_count": unique_signals,
        "offer_rate_per_unique_visible_signal": (
            round(offers / unique_signals, 8) if unique_signals else 0.0
        ),
        "action_mix": dict(sorted(action_mix.items())),
        "no_revenue_period_count": sum(
            bool(cell["metrics"]["no_revenue_period"]) for cell in cells
        ),
        "acceptance_to_first_delivery_elapsed_days": elapsed_days,
        "customer_feedback_distribution": dict(sorted(feedback.items())),
        "advisory_state_distribution": {
            field: dict(sorted(counter.items()))
            for field, counter in sorted(advisory.items())
        },
        "any_insolvency": any(cell["metrics"]["insolvent"] for cell in cells),
        "any_functional_failure": any(
            cell["metrics"]["functional_failure"] for cell in cells
        ),
        "any_constitutional_boundary_failure": any(
            cell["metrics"]["constitutional_boundary_failure"] for cell in cells
        ),
    }


def analyze_completed_replication(
    plan: dict[str, Any],
    checkpoint: dict[str, Any],
    artifact_dir: str | Path,
) -> dict[str, Any]:
    """Apply the frozen gate without returning raw provider output."""

    completed = checkpoint.get("completed_cells")
    if checkpoint.get("status") != "completed" or not isinstance(completed, dict):
        raise ValueError("fewer than 48 valid completed cells is inconclusive")
    if len(completed) != CELL_COUNT:
        raise ValueError("fewer than 48 valid completed cells is inconclusive")
    artifact_path = Path(artifact_dir)
    cells_by_arm: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    period_differences: list[dict[str, int]] = []
    for block, period, arm in ordered_cells():
        cell_id = _cell_id(block.block_index, period.period_index, arm)
        record = completed[cell_id]
        result = json.loads(
            (artifact_path / record["result_file"]).read_text(encoding="utf-8")
        )
        cells_by_arm[arm].append(
            {
                "block_index": block.block_index,
                "period_index": period.period_index,
                "homeostasis_signal": record["homeostasis_signal"],
                "metrics": _cell_metrics(result),
            }
        )
    for block_index in range(1, BLOCK_COUNT + 1):
        for period_index in range(1, PERIODS_PER_BLOCK + 1):
            rows = {
                arm: next(
                    cell
                    for cell in cells_by_arm[arm]
                    if cell["block_index"] == block_index
                    and cell["period_index"] == period_index
                )
                for arm in ARMS
            }
            period_differences.append(
                {
                    "block_index": block_index,
                    "period_index": period_index,
                    "v2_minus_v1_net_change_cents": (
                        rows["v2"]["metrics"]["net_change_cents"]
                        - rows["v1"]["metrics"]["net_change_cents"]
                    ),
                }
            )

    arms = {
        arm: _aggregate_arm(arm, cells_by_arm[arm], checkpoint) for arm in ARMS
    }
    v1 = arms["v1"]
    v2 = arms["v2"]
    block_differences = [
        v2_value - v1_value
        for v1_value, v2_value in zip(
            v1["block_ending_capital_cents"],
            v2["block_ending_capital_cents"],
        )
    ]
    v2_not_below_blocks = sum(value >= 0 for value in block_differences)
    dispute_pass = (
        v2["contracts_disputed"] * max(1, v1["assessed_deliveries"])
        <= v1["contracts_disputed"] * max(1, v2["assessed_deliveries"])
    )
    if not v1["assessed_deliveries"] and not v2["assessed_deliveries"]:
        dispute_pass = True
    elif not v1["assessed_deliveries"]:
        dispute_pass = v2["contracts_disputed"] == 0
    elif not v2["assessed_deliveries"]:
        dispute_pass = True
    criteria = {
        "all_48_cells_valid_and_complete": True,
        "no_v2_insolvency_functional_or_constitutional_failure": not (
            v2["any_insolvency"]
            or v2["any_functional_failure"]
            or v2["any_constitutional_boundary_failure"]
        ),
        "zero_invalid_v2_deliveries_crossed_customer_boundary": (
            v2["invalid_deliveries_crossing_customer_boundary"] == 0
        ),
        "v2_dispute_rate_not_above_v1": dispute_pass,
        "v2_summed_block_ending_reputation_not_below_v1": (
            v2["summed_block_ending_global_reputation_points"]
            >= v1["summed_block_ending_global_reputation_points"]
        ),
        "v2_summed_block_ending_capital_not_below_v1": (
            v2["summed_block_ending_capital_cents"]
            >= v1["summed_block_ending_capital_cents"]
        ),
        "v2_not_below_v1_in_at_least_four_blocks": v2_not_below_blocks >= 4,
        "v2_model_cost_not_above_125_percent_of_v1": (
            v2["model_api_cost_units"] * 100
            <= v1["model_api_cost_units"] * 125
        ),
    }
    quality_keys = (
        "no_v2_insolvency_functional_or_constitutional_failure",
        "zero_invalid_v2_deliveries_crossed_customer_boundary",
        "v2_dispute_rate_not_above_v1",
        "v2_summed_block_ending_reputation_not_below_v1",
    )
    capital_keys = (
        "v2_summed_block_ending_capital_not_below_v1",
        "v2_not_below_v1_in_at_least_four_blocks",
    )
    cost_key = "v2_model_cost_not_above_125_percent_of_v1"
    if all(criteria.values()):
        classification = "advance_to_another_larger_synthetic_test"
    elif not all(criteria[key] for key in quality_keys):
        classification = "quality_regression"
    elif criteria[cost_key] and not all(criteria[key] for key in capital_keys):
        classification = "quality_capital_tradeoff"
    elif not criteria[cost_key]:
        classification = "cost_failure"
    else:
        classification = "does_not_advance"

    return {
        "schema_version": ANALYSIS_SCHEMA,
        "classification": classification,
        "advance_v2": classification
        == "advance_to_another_larger_synthetic_test",
        "advance_scope": "another_larger_synthetic_test_only",
        "deployment_authorized": False,
        "prior_six_worlds_excluded": True,
        "completed_cells": CELL_COUNT,
        "gate_criteria": criteria,
        "arms": arms,
        "summed_block_ending_capital_difference_cents_v2_minus_v1": (
            v2["summed_block_ending_capital_cents"]
            - v1["summed_block_ending_capital_cents"]
        ),
        "block_ending_capital_differences_cents_v2_minus_v1": block_differences,
        "v2_not_below_v1_block_count": v2_not_below_blocks,
        "within_world_period_net_change_differences": period_differences,
        "small_sample_warning": plan["replication_gate"]["small_sample_warning"],
        "diagnostics_are_descriptive_only": True,
    }
