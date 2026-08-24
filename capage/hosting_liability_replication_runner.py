"""Checkpointing for the four-arm hosting-liability dose-response replication.

Deliberately separate from capage/homeostasis_v2_replication_runner.py's
BlockedReplicationRunner: that class dispatches a per-arm homeostasis SIGNAL
variant (_expected_signal / signal_for_arm_start, imported from
capage/homeostasis_v2_experiment.py) -- machinery this experiment has no use
for, since all four tariff arms share an identical signal/prompt setup and
vary only in hosting_cost_cents_per_day. A single runner factory (not a
per-arm dict of runner classes) is used for all four arms here.

This module reuses capage/homeostasis_v2_replication_runner.py's _cell_metrics
directly (it is fully generic -- takes only a sandbox result dict, references
no arm or signal concept) rather than duplicating it. capage/homeostasis_v2_
replication.py and capage/homeostasis_v2_experiment.py are not imported here
at all; the V1/V2 signal-comparison machinery is left completely untouched.

The module exposes no provider client, paid CLI, confirmation string,
workflow, or authorization marker. A later reviewed launch layer must inject
both the runner factory and an execution guard, matching the same shape as
homeostasis_v2_replication_launch.py. No preregistration document exists yet
for this experiment (unlike the V2 replication's reviewed, merge-bound
economic_homeostasis_v2_replication_prereg_v1.json) -- deliberately not
inventing one here, since a preregistration is a frozen owner-authorization-
adjacent artifact that deserves its own explicit review, not a unilateral
addition alongside this build. ReplicationConfig.from_plan accepts an
in-memory plan dict shaped consistently with what a future reviewed
preregistration/plan pair would produce, so nothing here needs to change once
that document exists.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable

from capage.homeostasis_shadow import SandboxResultProjector
from capage.homeostasis_v2_replication_runner import _cell_metrics
from capage.hosting_liability_replication import (
    ARMS,
    BLOCK_COUNT,
    CELL_COUNT,
    PERIODS_PER_BLOCK,
    TARIFF_CENTS_PER_DAY,
    materialize_matched_worlds,
    ordered_cells,
    validate_balanced_order,
)
from capage.sandbox import (
    validate_continuity_state,
    verify_cost_policy,
    verify_world_reveal,
)


CHECKPOINT_SCHEMA = "capage-hosting-liability-dose-response-checkpoint-v1"
ATTEMPT_SCHEMA = "capage-paid-attempt-v3"
_COST_UNITS_PER_CENT = 1_000_000


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


def _cell_id(block_index: int, period_index: int, arm: str) -> str:
    return f"block-{block_index:02d}:period-{period_index:02d}:{arm}"


def _run_stem(block_index: int, period_index: int, arm: str) -> str:
    return f"hosting-liability-dose-response-b{block_index:02d}-p{period_index:02d}-{arm}"


@dataclass(frozen=True)
class ReplicationConfig:
    plan_sha256: str
    beacon: str
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
    arm_hosting_cost_cents_per_day: dict[str, int]

    @classmethod
    def from_plan(cls, plan: dict[str, Any]) -> "ReplicationConfig":
        if plan.get("arms") != list(ARMS):
            raise ValueError(
                "hosting-liability plan arms must be exactly zero/low/medium/high"
            )
        frozen = plan["frozen_config"]
        tariff = frozen["token_tariff"]
        budget = plan["maximum_budget"]
        arm_hosting = plan.get("arm_hosting_cost_cents_per_day", TARIFF_CENTS_PER_DAY)
        if dict(arm_hosting) != dict(TARIFF_CENTS_PER_DAY):
            raise ValueError(
                "arm_hosting_cost_cents_per_day must match the locked tariff levels "
                "(0/15/45/135 cents/day, see .agent-mailbox 2026-08-23 13:00/15:00)"
            )
        config = cls(
            plan_sha256=_digest(plan),
            beacon=str(plan["seed_beacon"]),
            starting_capital_cents=int(frozen["starting_capital_cents_per_block"]),
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
            arm_hosting_cost_cents_per_day=dict(arm_hosting),
        )
        if config.per_cell_cost_cap_cents != 45:
            raise ValueError("dose-response per-cell cap must be exactly 45 cents")
        if config.aggregate_cost_cap_cents != 2_160:
            raise ValueError("dose-response aggregate cap must be exactly 2160 cents")
        if config.per_cell_cost_cap_cents * CELL_COUNT != 2_160:
            raise ValueError("forty-eight cell caps must equal the aggregate cap")
        date.fromisoformat(config.tariff_valid_through)
        return config

    def commitment(self) -> str:
        return _digest(asdict(self))


RunnerFactory = Callable[..., Any]
RunConfigFactory = Callable[..., Any]
ExecutionGuard = Callable[[], None]


class BlockedTariffReplicationRunner:
    """Run the 48-cell four-arm tariff prefix serially, fail closed on ambiguity.

    Structurally mirrors BlockedReplicationRunner's checkpoint/resume safety
    properties (ordered-prefix completion, ambiguous-attempt detection via
    pre-existing artifact files, atomic checkpoint writes, recomputed-balance
    verification on resume) with two deliberate simplifications: a single
    runner_factory shared by all four arms (no per-arm signal dispatch), and
    a narrower per-cell result validation than the V2 class's -- this omits
    some of that class's redundant arithmetic re-derivations (e.g. re-deriving
    billed-cents-from-units) that are already guaranteed by EconomicSandbox's
    own internal invariants, while keeping the checks that matter for
    integrity across a resume: schema/status, transcript/decision-count
    consistency, cost caps, balance/net-change consistency, and world-reveal
    verification against the plan's materialized matched-world evidence.
    """

    def __init__(
        self,
        plan: dict[str, Any],
        client: Any,
        *,
        checkpoint_path: str | Path,
        artifact_dir: str | Path,
        runner_factory: RunnerFactory,
        run_config_factory: RunConfigFactory,
        world_factory: Callable[..., Any],
        empty_continuity_factory: Callable[[], dict[str, Any]],
        execution_guard: ExecutionGuard,
    ) -> None:
        if not callable(execution_guard):
            raise TypeError("a later reviewed execution guard is required")
        if not callable(runner_factory):
            raise TypeError("runner_factory must be callable")
        self.plan = json.loads(_canonical_json(plan))
        self.config = ReplicationConfig.from_plan(self.plan)
        self.client = client
        self.checkpoint_path = Path(checkpoint_path)
        self.artifact_dir = Path(artifact_dir)
        self.runner_factory = runner_factory
        self.run_config_factory = run_config_factory
        self.world_factory = world_factory
        self.empty_continuity_factory = empty_continuity_factory
        self.execution_guard = execution_guard
        validate_balanced_order(self.config.beacon)
        self._matched_worlds = {
            (int(record["block_index"]), int(record["period_index"])): record
            for record in self.plan["matched_worlds"]
        }
        frozen_config = self.plan["frozen_config"]
        materialized = materialize_matched_worlds(
            self.config.beacon, frozen_config, self.world_factory
        )
        if [dict(r) for r in materialized] != self.plan["matched_worlds"]:
            raise ValueError("matched-world materialization changed before execution")
        self.state = self._load_or_initialize()

    def _empty_arm_state(self) -> dict[str, Any]:
        continuity = self.empty_continuity_factory()
        if not isinstance(continuity, dict):
            raise TypeError("empty continuity factory must return an object")
        return {
            "balance_cents": self.config.starting_capital_cents,
            "model_cost_units": 0,
            "business_continuity": json.loads(_canonical_json(continuity)),
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
            raise ValueError("unsupported hosting-liability checkpoint schema")
        if payload.get("config_commitment") != self.config.commitment():
            raise ValueError("checkpoint config mismatch")
        if payload.get("plan_sha256") != self.config.plan_sha256:
            raise ValueError("checkpoint plan mismatch")
        self._validate_checkpoint_state(payload)
        return payload

    def _checkpoint(self) -> None:
        _atomic_json(self.checkpoint_path, self.state)

    def _validate_checkpoint_state(self, payload: dict[str, Any]) -> None:
        completed = payload.get("completed_cells")
        if not isinstance(completed, dict):
            raise ValueError("checkpoint completed_cells must be an object")
        ordered = [
            (_cell_id(block.block_index, period.period_index, arm), block, period, arm)
            for block, period, arm in ordered_cells(self.config.beacon)
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
                        "business_continuity": json.loads(
                            _canonical_json(initial_continuity)
                        ),
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
            arm_state["balance_cents"] = int(record["ending_balance_cents"])
            arm_state["model_cost_units"] = int(
                arm_state["model_cost_units"] + record["model_cost_units"]
            )
            arm_state["business_continuity"] = record["business_continuity"]
            aggregate_units += int(record["model_cost_units"])
        for error in payload.get("errors", []):
            if isinstance(error, dict) and error.get("cost_counted_toward_aggregate") is True:
                aggregate_units += int(error["raw_actual_model_cost_units"])
        if recomputed != payload.get("blocks"):
            raise ValueError("checkpoint block state does not match completed cells")
        if aggregate_units != payload.get("model_cost_units"):
            raise ValueError("checkpoint aggregate cost does not match completed cells")

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
            input_cents_per_million_tokens=self.config.input_cents_per_million_tokens,
            output_cents_per_million_tokens=self.config.output_cents_per_million_tokens,
            customer_population_seed=block.customer_population_seed,
            customer_namespace="",
            market_profile=self.config.market_profile,
            assessor_version=self.config.assessor_version,
            tariff_valid_through=self.config.tariff_valid_through,
            hosting_cost_cents_per_day=self.config.arm_hosting_cost_cents_per_day[arm],
        )

    def _validate_result(
        self,
        result: dict[str, Any],
        run_config: Any,
        matched_world: dict[str, Any],
        arm: str,
    ) -> None:
        if result.get("schema_version") != "capage-live-sandbox-result-v1":
            raise ValueError("cell returned unsupported result schema")
        if result.get("status") != "completed":
            raise ValueError("cell did not complete")
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
        if reveal.get("cost_policy_commitment") != matched_world[
            "cost_policy_commitment_by_arm"
        ].get(arm):
            raise ValueError("cell cost policy changed after materialization")
        SandboxResultProjector.project(result)

    def run(self, *, max_cells: int | None = None) -> dict[str, Any]:
        """Run only after a later launch layer's guard returns successfully."""

        self.execution_guard()
        if max_cells is not None and not 1 <= max_cells <= CELL_COUNT:
            raise ValueError("max_cells must be between 1 and 48")
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
        for block, period, arm in ordered_cells(self.config.beacon):
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
                "status": "started",
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
            _atomic_json(attempt_path, attempt)
            _atomic_text(audit_path, "")
            raw_result_path = self.artifact_dir / f"{stem}-raw.json"
            result: dict[str, Any] | None = None
            try:
                runner = self.runner_factory(
                    run_config,
                    self.client,
                    audit_path=audit_path,
                    continuity_state=arm_state["business_continuity"],
                )
                result = runner.run()
                # Persist the raw sandbox result immediately, before
                # validation -- if validation below raises, this is the
                # only place the real stop_reason/failure detail survives.
                # result_path (the "official" per-cell result other code
                # trusts as validated) is still only written after success,
                # further down.
                _atomic_json(raw_result_path, result)
                matched = self._matched_worlds[
                    (block.block_index, period.period_index)
                ]
                self._validate_result(result, run_config, matched, arm)
            except Exception as exc:
                error_record: dict[str, Any] = {
                    "cell_id": cell_id,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "raw_result_file": (
                        f"{stem}-raw.json" if raw_result_path.exists() else None
                    ),
                }
                if isinstance(result, dict):
                    error_record["raw_status"] = result.get("status")
                    error_record["raw_stop_reason"] = result.get("stop_reason")
                    error_record["raw_failure"] = result.get("failure")
                # A failed cell can still carry a real, already-billed cost
                # in its raw result -- count it toward the aggregate cap here
                # so a resumed run can't spend past the cap due to a costly
                # failure going untracked. _validate_checkpoint_state below
                # must recompute this same sum on reload, or a checkpoint
                # holding one of these would fail to reload.
                raw_units = result.get("actual_model_cost_units") if isinstance(result, dict) else None
                cost_known = (
                    isinstance(raw_units, int)
                    and not isinstance(raw_units, bool)
                    and raw_units >= 0
                )
                error_record["raw_actual_model_cost_units"] = raw_units if cost_known else None
                error_record["cost_counted_toward_aggregate"] = cost_known
                if cost_known:
                    self.state["model_cost_units"] = int(self.state["model_cost_units"]) + raw_units
                self.state["errors"].append(error_record)
                self.state["status"] = "stopped"
                self.state["stop_reason"] = "provider_or_runner_error"
                self._checkpoint()
                return self.state

            _atomic_json(result_path, result)
            used = int(result["actual_model_cost_units"])
            projected_total = int(self.state["model_cost_units"]) + used
            if projected_total > self.config.aggregate_cost_cap_cents * _COST_UNITS_PER_CENT:
                self.state["status"] = "stopped"
                self.state["stop_reason"] = "aggregate_model_cost_cap_reached"
                self._checkpoint()
                return self.state

            metrics = _cell_metrics(result)
            self.state["completed_cells"][cell_id] = {
                "cell_id": cell_id,
                "block_index": block.block_index,
                "period_index": period.period_index,
                "arm": arm,
                "world_seed": period.world_seed,
                "customer_population_seed": block.customer_population_seed,
                "execution_order": list(period.execution_order),
                "result_file": f"{stem}.json",
                "audit_file": f"{stem}-audit.jsonl",
                "ending_balance_cents": int(result["outcome"]["balance_cents"]),
                "model_cost_units": used,
                "business_continuity": result["business_continuity"],
                "metrics": metrics,
            }
            arm_state["balance_cents"] = int(result["outcome"]["balance_cents"])
            arm_state["model_cost_units"] = int(arm_state["model_cost_units"] + used)
            arm_state["business_continuity"] = result["business_continuity"]
            self.state["model_cost_units"] = projected_total
            attempted += 1
            self._checkpoint()

        self.state["status"] = "completed"
        self.state["stop_reason"] = "all_cells_completed"
        self._checkpoint()
        return self.state

    def analyze(self) -> dict[str, Any]:
        if self.state["status"] != "completed":
            raise ValueError("analysis requires a completed checkpoint")
        by_arm: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
        for cell_id, record in self.state["completed_cells"].items():
            by_arm[record["arm"]].append(record)
        return {
            "arms": ARMS,
            "arm_hosting_cost_cents_per_day": self.config.arm_hosting_cost_cents_per_day,
            "cell_count_by_arm": {arm: len(cells) for arm, cells in by_arm.items()},
            "aggregate_model_cost_units": self.state["model_cost_units"],
            "cells_by_arm": by_arm,
        }
