"""Preregistered holdout evaluation for simulator-specific memory overfitting."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from statistics import fmean, median
import sys
from typing import Any, Callable, Protocol

from capage.anthropic_client import AnthropicMessagesClient
from capage.frozen_paths import path_commitments
from capage.memory import AuditedMemoryStore
from capage.sandbox import (
    TokenTariff,
    empty_continuity_state,
    validate_continuity_state,
    validate_customer_namespace,
    validate_market_profile,
    verify_world_reveal,
)
from capage.sandbox_runner import LiveSandboxRunner, ModelClient, SandboxRunConfig


_COST_UNITS_PER_CENT = 1_000_000
_CONDITIONS = ("no_memory", "trained_memory")
_PHASE_IDS = ("same-distribution", "shifted-market")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
_IMPLEMENTATION_PATHS = (
    "capage/sandbox.py",
    "capage/sandbox_runner.py",
    "capage/memory.py",
    "capage/longitudinal.py",
    "capage/transfer.py",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


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


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def current_implementation_commitments() -> tuple[tuple[str, str], ...]:
    """Return exact hashes for every host module frozen by transfer v1."""

    return tuple(path_commitments(_IMPLEMENTATION_PATHS).items())


def derive_transfer_seed(
    source_training_config_commitment: str,
    phase_id: str,
    seed_index: int,
) -> int:
    """Derive an unscreened six-digit holdout seed from the training commitment."""

    digest = sha256(
        (
            f"capage-transfer-v1:{source_training_config_commitment}:"
            f"{phase_id}:month:{seed_index}"
        ).encode("utf-8")
    ).digest()
    return 100_000 + (int.from_bytes(digest[:8], "big") % 900_000)


def derive_transfer_population_seed(
    source_training_config_commitment: str,
    phase_id: str,
) -> int:
    """Derive an unscreened nine-digit customer population seed."""

    digest = sha256(
        (
            f"capage-transfer-v1:{source_training_config_commitment}:"
            f"{phase_id}:population"
        ).encode("utf-8")
    ).digest()
    return 100_000_000 + (int.from_bytes(digest[:8], "big") % 900_000_000)


@dataclass(frozen=True)
class TransferPhase:
    """One hidden holdout population and its host-owned market mechanics."""

    phase_id: str
    seeds: tuple[int, ...]
    customer_population_seed: int
    customer_namespace: str
    market_profile: str

    def __post_init__(self) -> None:
        if not _IDENTIFIER.fullmatch(self.phase_id):
            raise ValueError("phase_id must be a lowercase stable identifier")
        if len(self.seeds) < 2 or len(self.seeds) != len(set(self.seeds)):
            raise ValueError("each transfer phase needs at least two unique seeds")
        if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in self.seeds):
            raise TypeError("transfer seeds must be integers")
        if isinstance(self.customer_population_seed, bool) or not isinstance(
            self.customer_population_seed, int
        ):
            raise TypeError("customer_population_seed must be an integer")
        if not self.customer_namespace:
            raise ValueError("transfer phases require a new customer namespace")
        validate_customer_namespace(self.customer_namespace)
        validate_market_profile(self.market_profile)


@dataclass(frozen=True)
class TransferConfig:
    """Frozen choices for a memory-versus-no-memory transfer evaluation."""

    experiment_name: str
    source_training_config_commitment: str
    source_training_months_per_arm: int
    training_month_seeds: tuple[int, ...]
    training_customer_population_seed: int
    phases: tuple[TransferPhase, ...]
    experiment_epoch: str
    starting_capital_cents: int
    horizon_days: int
    max_decisions_per_cell: int
    per_cell_model_cost_cap_cents: int
    per_condition_model_cost_cap_cents: int
    aggregate_model_cost_cap_cents: int
    model: str
    effort: str
    max_output_tokens: int
    tariff: TokenTariff
    assessor_version: str
    freeze_training_memory: bool
    reset_economic_state_per_cell: bool
    implementation_commitments: tuple[tuple[str, str], ...]
    python_runtime: str
    tariff_valid_through: str = ""

    def __post_init__(self) -> None:
        if not self.experiment_name.strip():
            raise ValueError("experiment_name is required")
        if not re.fullmatch(r"[0-9a-f]{64}", self.source_training_config_commitment):
            raise ValueError("source training commitment must be a SHA-256 digest")
        if self.source_training_months_per_arm < 2:
            raise ValueError("source training must contain at least two months per arm")
        if len(self.training_month_seeds) != self.source_training_months_per_arm:
            raise ValueError("training seed count must match source training months")
        if len(self.training_month_seeds) != len(set(self.training_month_seeds)):
            raise ValueError("training month seeds must be unique")
        if isinstance(self.training_customer_population_seed, bool) or not isinstance(
            self.training_customer_population_seed, int
        ):
            raise TypeError("training_customer_population_seed must be an integer")
        _timestamp(self.experiment_epoch)
        if tuple(phase.phase_id for phase in self.phases) != _PHASE_IDS:
            raise ValueError("transfer phases must be same-distribution then shifted-market")
        same, shifted = self.phases
        if same.market_profile != "baseline-v1":
            raise ValueError("same-distribution phase must use baseline-v1")
        if shifted.market_profile != "transfer-tight-market-v1":
            raise ValueError("shifted-market phase must use transfer-tight-market-v1")
        for phase in self.phases:
            expected_seeds = tuple(
                derive_transfer_seed(
                    self.source_training_config_commitment,
                    phase.phase_id,
                    index,
                )
                for index in range(1, len(phase.seeds) + 1)
            )
            if phase.seeds != expected_seeds:
                raise ValueError("transfer seeds do not match the preregistered derivation")
            if phase.customer_population_seed != derive_transfer_population_seed(
                self.source_training_config_commitment,
                phase.phase_id,
            ):
                raise ValueError(
                    "transfer population seed does not match the preregistered derivation"
                )
        holdout_seeds = [seed for phase in self.phases for seed in phase.seeds]
        if len(holdout_seeds) != len(set(holdout_seeds)):
            raise ValueError("holdout seeds must be unique across phases")
        if set(holdout_seeds) & set(self.training_month_seeds):
            raise ValueError("holdout seeds must not reuse training seeds")
        population_seeds = [phase.customer_population_seed for phase in self.phases]
        if len(population_seeds) != len(set(population_seeds)):
            raise ValueError("transfer phases require distinct customer populations")
        if self.training_customer_population_seed in population_seeds:
            raise ValueError("transfer populations must differ from training")
        namespaces = [phase.customer_namespace for phase in self.phases]
        if len(namespaces) != len(set(namespaces)):
            raise ValueError("transfer customer namespaces must be distinct")
        if self.starting_capital_cents < 0:
            raise ValueError("starting capital cannot be negative")
        if self.horizon_days < 7:
            raise ValueError("horizon_days must be at least 7")
        if not 1 <= self.max_decisions_per_cell <= 100:
            raise ValueError("max_decisions_per_cell must be between 1 and 100")
        if self.per_cell_model_cost_cap_cents < 1:
            raise ValueError("per-cell model cost cap must be positive")
        if self.per_condition_model_cost_cap_cents < (
            self.per_cell_model_cost_cap_cents * self.seeds_per_condition
        ):
            raise ValueError("per-condition cap must reserve every holdout cell")
        if self.aggregate_model_cost_cap_cents < (
            2 * self.per_condition_model_cost_cap_cents
        ):
            raise ValueError("aggregate cap must reserve both transfer conditions")
        if self.effort not in {"low", "medium", "high", "max"}:
            raise ValueError("unsupported effort")
        if not 128 <= self.max_output_tokens <= 4096:
            raise ValueError("max_output_tokens must be between 128 and 4096")
        if self.assessor_version != "deterministic-artifact-v2":
            raise ValueError("transfer evaluation requires deterministic-artifact-v2")
        if self.freeze_training_memory is not True:
            raise ValueError("transfer evaluation requires frozen training memory")
        if self.reset_economic_state_per_cell is not True:
            raise ValueError("transfer evaluation requires an economic reset per cell")
        if tuple(path for path, _ in self.implementation_commitments) != (
            _IMPLEMENTATION_PATHS
        ):
            raise ValueError("transfer manifest must commit every host implementation")
        if any(
            not re.fullmatch(r"[0-9a-f]{64}", digest)
            for _, digest in self.implementation_commitments
        ):
            raise ValueError("implementation commitments must be SHA-256 digests")
        if self.implementation_commitments != current_implementation_commitments():
            raise ValueError("host implementation does not match the frozen manifest")
        running_python = f"{sys.version_info.major}.{sys.version_info.minor}"
        if self.python_runtime != running_python:
            raise ValueError("Python runtime does not match the frozen manifest")
        if self.tariff_valid_through:
            date.fromisoformat(self.tariff_valid_through)

    @property
    def seeds_per_condition(self) -> int:
        return sum(len(phase.seeds) for phase in self.phases)

    @property
    def cell_count(self) -> int:
        return len(_CONDITIONS) * self.seeds_per_condition

    @classmethod
    def from_manifest(cls, path: str | Path) -> "TransferConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != "capage-transfer-v1":
            raise ValueError("unsupported transfer manifest schema")
        source = payload["source_training"]
        model = payload["model"]
        tariff = payload["token_tariff"]
        implementations = payload["implementation_commitments"]
        phases = tuple(
            TransferPhase(
                phase_id=str(phase["phase_id"]),
                seeds=tuple(int(seed) for seed in phase["seeds"]),
                customer_population_seed=int(phase["customer_population_seed"]),
                customer_namespace=str(phase["customer_namespace"]),
                market_profile=str(phase["market_profile"]),
            )
            for phase in payload["phases"]
        )
        return cls(
            experiment_name=str(payload["experiment_name"]),
            source_training_config_commitment=str(source["config_commitment"]),
            source_training_months_per_arm=int(source["months_per_arm"]),
            training_month_seeds=tuple(int(seed) for seed in source["month_seeds"]),
            training_customer_population_seed=int(source["customer_population_seed"]),
            phases=phases,
            experiment_epoch=str(payload["experiment_epoch"]),
            starting_capital_cents=int(payload["starting_capital_cents"]),
            horizon_days=int(payload["horizon_days"]),
            max_decisions_per_cell=int(payload["max_decisions_per_cell"]),
            per_cell_model_cost_cap_cents=int(
                payload["per_cell_model_cost_cap_cents"]
            ),
            per_condition_model_cost_cap_cents=int(
                payload["per_condition_model_cost_cap_cents"]
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
            freeze_training_memory=payload["freeze_training_memory"],
            reset_economic_state_per_cell=payload["reset_economic_state_per_cell"],
            implementation_commitments=tuple(
                (path, str(implementations[path])) for path in _IMPLEMENTATION_PATHS
            ),
            python_runtime=str(payload["python_runtime"]),
            tariff_valid_through=str(payload.get("tariff_valid_through", "")),
        )

    def commitment(self) -> str:
        payload = {**asdict(self), "tariff": asdict(self.tariff)}
        return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def cell_config(
        self,
        *,
        phase: TransferPhase,
        seed_index: int,
        condition: str,
        cost_cap_cents: int,
    ) -> SandboxRunConfig:
        if condition not in _CONDITIONS:
            raise ValueError("unsupported transfer condition")
        return SandboxRunConfig(
            run_name=(
                f"{self.experiment_name}-{phase.phase_id}-"
                f"seed-{seed_index:03d}-{condition.replace('_', '-')}"
            ),
            seed=phase.seeds[seed_index - 1],
            model=self.model,
            effort=self.effort,
            max_output_tokens=self.max_output_tokens,
            max_decisions=self.max_decisions_per_cell,
            max_run_cost_cents=cost_cap_cents,
            horizon_days=self.horizon_days,
            starting_capital_cents=self.starting_capital_cents,
            tariff=self.tariff,
            customer_population_seed=phase.customer_population_seed,
            customer_namespace=phase.customer_namespace,
            market_profile=phase.market_profile,
            assessor_version=self.assessor_version,
            tariff_valid_through=self.tariff_valid_through,
        )


class CellRunner(Protocol):
    def run(self) -> dict[str, Any]: ...


RunnerFactory = Callable[..., CellRunner]


class TransferRunner:
    """Evaluate a frozen training memory on independent, reset holdout cells."""

    def __init__(
        self,
        config: TransferConfig,
        client: ModelClient,
        *,
        source_checkpoint_path: str | Path,
        source_memory_path: str | Path,
        checkpoint_path: str | Path,
        artifact_dir: str | Path,
        runner_factory: RunnerFactory = LiveSandboxRunner,
    ) -> None:
        self.config = config
        self.client = client
        self.source_checkpoint_path = Path(source_checkpoint_path)
        self.source_memory_path = Path(source_memory_path)
        self.checkpoint_path = Path(checkpoint_path)
        self.artifact_dir = Path(artifact_dir)
        self.runner_factory = runner_factory
        self.source = self._load_source()
        self.state = self._load_or_initialize()

    def run(self, *, max_cells: int | None = None) -> dict[str, Any]:
        if max_cells is not None and max_cells < 1:
            raise ValueError("max_cells must be positive")
        if self.state["status"] in {"completed", "stopped"}:
            return self.state
        if self.config.tariff_valid_through and datetime.now(
            timezone.utc
        ).date() > date.fromisoformat(self.config.tariff_valid_through):
            return self._stop("frozen_tariff_expired")

        attempted_now = 0
        self.state["status"] = "running"
        self.state["stop_reason"] = None
        self._checkpoint()

        for phase_index, phase in enumerate(self.config.phases, start=1):
            for seed_index, seed in enumerate(phase.seeds, start=1):
                order = (
                    _CONDITIONS
                    if (phase_index + seed_index) % 2 == 0
                    else tuple(reversed(_CONDITIONS))
                )
                for condition in order:
                    cell_id = (
                        f"phase:{phase.phase_id}:seed-{seed_index:03d}:{condition}"
                    )
                    if cell_id in self.state["completed_cells"]:
                        continue
                    if not self._source_memory_is_unchanged():
                        return self._stop("source_memory_changed")

                    remaining_units = (
                        self.config.aggregate_model_cost_cap_cents
                        * _COST_UNITS_PER_CENT
                        - int(self.state["model_cost_units"])
                    )
                    condition_state = self.state["conditions"][condition]
                    condition_remaining_units = (
                        self.config.per_condition_model_cost_cap_cents
                        * _COST_UNITS_PER_CENT
                        - int(condition_state["model_cost_units"])
                    )
                    remaining_whole_cents = min(
                        remaining_units, condition_remaining_units
                    ) // _COST_UNITS_PER_CENT
                    if remaining_whole_cents < 1:
                        reason = (
                            "condition_model_cost_cap_reached"
                            if condition_remaining_units < _COST_UNITS_PER_CENT
                            else "aggregate_model_cost_cap_reached"
                        )
                        return self._stop(reason)
                    cost_cap = min(
                        self.config.per_cell_model_cost_cap_cents,
                        int(remaining_whole_cents),
                    )
                    cell_config = self.config.cell_config(
                        phase=phase,
                        seed_index=seed_index,
                        condition=condition,
                        cost_cap_cents=cost_cap,
                    )
                    result_path = self.artifact_dir / f"{cell_config.run_name}.json"
                    audit_path = self.artifact_dir / f"{cell_config.run_name}-audit.jsonl"
                    attempt_path = (
                        self.artifact_dir / f"{cell_config.run_name}-attempt.json"
                    )
                    if result_path.exists() or audit_path.exists() or attempt_path.exists():
                        self.state["errors"].append(
                            {
                                "cell_id": cell_id,
                                "error_type": "AmbiguousPriorAttempt",
                                "error": (
                                    "an uncheckpointed result, audit, or attempt file "
                                    "already exists; the paid cell will not be replayed"
                                ),
                            }
                        )
                        return self._stop("ambiguous_uncheckpointed_attempt")

                    context = (
                        self.source["memory_context"]
                        if condition == "trained_memory"
                        else None
                    )
                    attempt = {
                        "schema_version": "capage-paid-attempt-v1",
                        "cell_id": cell_id,
                        "config_commitment": self.config.commitment(),
                        "source_memory_head_hash": self.source["memory_head_hash"],
                        "memory_context_hash": (
                            self.source["memory_context_hash"] if context else None
                        ),
                        "status": "started",
                        "started_at": datetime.now(timezone.utc).isoformat(),
                    }
                    _atomic_json(attempt_path, attempt)
                    try:
                        runner = self.runner_factory(
                            cell_config,
                            self.client,
                            audit_path=audit_path,
                            durable_context=context,
                            continuity_state=empty_continuity_state(),
                        )
                        result = runner.run()
                        self._validate_result(result, cell_config)
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
                    _atomic_json(
                        attempt_path,
                        {
                            **attempt,
                            "status": "completed",
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                            "result_sha256": sha256(
                                _canonical_json(result).encode("utf-8")
                            ).hexdigest(),
                        },
                    )
                    outcome = result["outcome"]
                    continuity = validate_continuity_state(
                        result["business_continuity"]
                    )
                    used_units = int(result["actual_model_cost_units"])
                    self.state["model_cost_units"] += used_units
                    condition_state["model_cost_units"] += used_units
                    record = {
                        "cell_id": cell_id,
                        "phase_id": phase.phase_id,
                        "condition": condition,
                        "seed_index": seed_index,
                        "seed": seed,
                        "customer_population_seed": phase.customer_population_seed,
                        "customer_namespace": phase.customer_namespace,
                        "market_profile": phase.market_profile,
                        "starting_capital_cents": cell_config.starting_capital_cents,
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
                        "memory_context_hash": (
                            self.source["memory_context_hash"] if context else None
                        ),
                        "world_commitment": result["world_reveal"][
                            "world_commitment"
                        ],
                        "business_continuity_hash": sha256(
                            _canonical_json(continuity).encode("utf-8")
                        ).hexdigest(),
                        "result_file": result_path.name,
                        "audit_file": audit_path.name,
                        "attempt_file": attempt_path.name,
                    }
                    condition_state["cells"].append(record)
                    condition_state["cells_completed"] += 1
                    self.state["completed_cells"][cell_id] = record
                    self._checkpoint()
                    attempted_now += 1

                    if int(outcome["open_obligations"]) != 0:
                        return self._stop(
                            "open_obligations_require_state_serialization"
                        )
                    if max_cells is not None and attempted_now >= max_cells:
                        self.state["status"] = "paused"
                        self.state["stop_reason"] = "operator_checkpoint"
                        self._checkpoint()
                        return self.state

        if not self._source_memory_is_unchanged():
            return self._stop("source_memory_changed")
        self.state["status"] = "completed"
        self.state["stop_reason"] = "all_transfer_cells_completed"
        self.state["summary"] = self._summary()
        self._checkpoint()
        return self.state

    def _load_source(self) -> dict[str, Any]:
        checkpoint = json.loads(
            self.source_checkpoint_path.read_text(encoding="utf-8")
        )
        if checkpoint.get("schema_version") != "capage-longitudinal-checkpoint-v3":
            raise ValueError("unsupported source training checkpoint schema")
        if checkpoint.get("config_commitment") != (
            self.config.source_training_config_commitment
        ):
            raise ValueError("source checkpoint does not match preregistered training")
        expected_source_implementation = {
            path: digest
            for path, digest in self.config.implementation_commitments
            if path != "capage/transfer.py"
        }
        if checkpoint.get("implementation_commitments") != (
            expected_source_implementation
        ):
            raise ValueError("source checkpoint host implementation mismatch")
        if checkpoint.get("status") != "completed":
            raise ValueError("source training must be completed before transfer")
        source_cells: set[str] = set()
        source_total_units = 0
        arm_months: dict[str, list[dict[str, Any]]] = {}
        for condition in ("control", "memory"):
            arm = checkpoint.get("arms", {}).get(condition, {})
            months = arm.get("months", [])
            if not isinstance(months, list) or len(months) != (
                self.config.source_training_months_per_arm
            ):
                raise ValueError("source training month count mismatch")
            if int(arm.get("months_completed", -1)) != len(months):
                raise ValueError("source training recorded month count mismatch")
            for month_number, month in enumerate(months, start=1):
                expected_cell = f"month-{month_number:03d}:{condition}"
                if month.get("cell_id") != expected_cell:
                    raise ValueError("source training cell sequence mismatch")
                if int(month.get("month_number", -1)) != month_number:
                    raise ValueError("source training month sequence mismatch")
                if int(month.get("seed", -1)) != self.config.training_month_seeds[
                    month_number - 1
                ]:
                    raise ValueError("source training seed mismatch")
                source_cells.add(expected_cell)
            expected_balance = (
                int(months[-1]["ending_balance_cents"])
                if months
                else self.config.starting_capital_cents
            )
            if int(arm.get("balance_cents", -1)) != expected_balance:
                raise ValueError("source training arm balance mismatch")
            recorded_units = sum(
                int(month["actual_model_cost_units"]) for month in months
            )
            if int(arm.get("model_cost_units", -1)) != recorded_units:
                raise ValueError("source training arm model cost mismatch")
            source_total_units += recorded_units
            continuity = validate_continuity_state(arm.get("business_continuity"))
            expected_continuity_hash = sha256(
                _canonical_json(continuity).encode("utf-8")
            ).hexdigest()
            if months[-1].get("business_continuity_hash") != expected_continuity_hash:
                raise ValueError("source training continuity hash mismatch")
            arm_months[condition] = months
        if int(checkpoint.get("model_cost_units", -1)) != source_total_units:
            raise ValueError("source training aggregate model cost mismatch")
        completed_cells = checkpoint.get("completed_cells", {})
        if not isinstance(completed_cells, dict) or set(completed_cells) != source_cells:
            raise ValueError("source training completed-cell index mismatch")
        for condition, months in arm_months.items():
            for month in months:
                if completed_cells[month["cell_id"]] != month:
                    raise ValueError("source training cell index content mismatch")
        if not isinstance(checkpoint.get("summary"), dict):
            raise ValueError("source training omitted its summary")
        paired_deltas = [
            int(arm_months["memory"][index]["net_change_cents"])
            - int(arm_months["control"][index]["net_change_cents"])
            for index in range(self.config.source_training_months_per_arm)
        ]
        if float(checkpoint["summary"].get("mean_paired_delta_cents", float("nan"))) != round(
            fmean(paired_deltas), 2
        ):
            raise ValueError("source training summary mismatch")

        before_sha = _file_sha256(self.source_memory_path)
        with AuditedMemoryStore(self.source_memory_path, read_only=True) as memory:
            if not memory.verify_chain():
                raise ValueError("source memory chain is invalid")
            memory_head = memory.head_hash()
            if checkpoint.get("memory_head_hash") != memory_head:
                raise ValueError("source memory does not match training checkpoint")
            packet = memory.retrieve(
                "pricing offers customers delivery payment feedback profit strategy",
                as_of=self.config.experiment_epoch,
                limit=8,
                max_chars=8_000,
            )
        after_sha = _file_sha256(self.source_memory_path)
        if before_sha != after_sha:
            raise ValueError("opening source memory changed the frozen database")
        context = packet.to_prompt_data()
        if not context["records"]:
            raise ValueError("source training produced no transferable memory records")
        return {
            "checkpoint_summary": checkpoint["summary"],
            "memory_head_hash": memory_head,
            "memory_file_sha256": before_sha,
            "memory_context": context,
            "memory_context_hash": sha256(
                _canonical_json(context).encode("utf-8")
            ).hexdigest(),
        }

    def _source_memory_is_unchanged(self) -> bool:
        if _file_sha256(self.source_memory_path) != self.source["memory_file_sha256"]:
            return False
        with AuditedMemoryStore(self.source_memory_path, read_only=True) as memory:
            return (
                memory.verify_chain()
                and memory.head_hash() == self.source["memory_head_hash"]
            )

    def _validate_result(
        self,
        result: dict[str, Any],
        config: SandboxRunConfig,
    ) -> None:
        if not isinstance(result, dict) or not isinstance(result.get("outcome"), dict):
            raise ValueError("cell runner omitted an outcome")
        if "business_continuity" not in result:
            raise ValueError("cell runner omitted business continuity state")
        validate_continuity_state(result["business_continuity"])
        reveal = result.get("world_reveal")
        if not isinstance(reveal, dict) or not verify_world_reveal(reveal):
            raise ValueError("cell runner omitted a valid world reveal")
        payload = reveal["payload"]
        if int(payload.get("seed", -1)) != config.seed:
            raise ValueError("cell world seed did not match the frozen configuration")
        if int(payload.get("starting_capital_cents", -1)) != (
            config.starting_capital_cents
        ):
            raise ValueError("cell world starting capital mismatch")
        if int(payload.get("customer_population_seed", -1)) != (
            config.customer_population_seed
        ):
            raise ValueError("cell customer population mismatch")
        if payload.get("customer_namespace", "") != config.customer_namespace:
            raise ValueError("cell customer namespace mismatch")
        revealed_profile = payload.get("market_profile")
        if config.market_profile == "baseline-v1":
            if revealed_profile is not None:
                raise ValueError("baseline cell unexpectedly revealed a shifted profile")
        elif not isinstance(revealed_profile, dict) or revealed_profile.get("name") != (
            config.market_profile
        ):
            raise ValueError("cell market profile mismatch")
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
            raise ValueError(f"cell outcome omitted {missing[0]}")
        if int(outcome["owner_capital_cents"]) != config.starting_capital_cents:
            raise ValueError("cell outcome changed starting capital")
        expected_balance = (
            config.starting_capital_cents
            + int(outcome["earned_revenue_cents"])
            - int(outcome["expense_cents"])
        )
        if int(outcome["balance_cents"]) != expected_balance:
            raise ValueError("cell balance equation failed")
        if int(outcome["net_change_cents"]) != (
            int(outcome["balance_cents"]) - config.starting_capital_cents
        ):
            raise ValueError("cell net-change equation failed")
        used_units = result.get("actual_model_cost_units")
        if isinstance(used_units, bool) or not isinstance(used_units, int) or used_units < 0:
            raise ValueError("cell result omitted valid model cost units")
        if (used_units + _COST_UNITS_PER_CENT - 1) // _COST_UNITS_PER_CENT > (
            config.max_run_cost_cents
        ):
            raise ValueError("cell result exceeded its frozen model cost cap")

    def _summary(self) -> dict[str, Any]:
        phase_summaries: dict[str, Any] = {}
        for phase in self.config.phases:
            deltas: list[int] = []
            for seed_index in range(1, len(phase.seeds) + 1):
                trained = self.state["completed_cells"][
                    f"phase:{phase.phase_id}:seed-{seed_index:03d}:trained_memory"
                ]
                control = self.state["completed_cells"][
                    f"phase:{phase.phase_id}:seed-{seed_index:03d}:no_memory"
                ]
                deltas.append(
                    int(trained["net_change_cents"])
                    - int(control["net_change_cents"])
                )
            phase_summaries[phase.phase_id] = {
                "paired_trained_minus_no_memory_net_cents": deltas,
                "mean_paired_delta_cents": round(fmean(deltas), 2),
                "median_paired_delta_cents": median(deltas),
                "trained_memory_win_rate": (
                    sum(delta > 0 for delta in deltas) / len(deltas)
                ),
            }
        training_delta = float(
            self.source["checkpoint_summary"].get("mean_paired_delta_cents", 0)
        )
        same_delta = float(
            phase_summaries["same-distribution"]["mean_paired_delta_cents"]
        )
        shifted_delta = float(
            phase_summaries["shifted-market"]["mean_paired_delta_cents"]
        )
        if training_delta > 0 and same_delta <= 0:
            interpretation = "simulator_specific_overfit_signal"
        elif same_delta > 0 and shifted_delta > 0:
            interpretation = "portable_strategy_signal"
        elif same_delta > 0 and shifted_delta <= 0:
            interpretation = "distribution_shift_fragility_signal"
        elif same_delta <= 0 and shifted_delta > 0:
            interpretation = "mixed_transfer_signal"
        else:
            interpretation = "no_positive_transfer_signal"
        return {
            "source_training_mean_paired_delta_cents": training_delta,
            "phases": phase_summaries,
            "descriptive_interpretation": interpretation,
            "statistical_claim": "none; this small preregistered test is descriptive",
        }

    def _load_or_initialize(self) -> dict[str, Any]:
        commitment = self.config.commitment()
        if self.checkpoint_path.exists():
            state = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            if state.get("schema_version") != "capage-transfer-checkpoint-v1":
                raise ValueError("unsupported transfer checkpoint schema")
            if state.get("config_commitment") != commitment:
                raise ValueError("checkpoint does not match the frozen transfer configuration")
            if state.get("source_memory_head_hash") != self.source["memory_head_hash"]:
                raise ValueError("checkpoint source memory head mismatch")
            if state.get("memory_context_hash") != self.source["memory_context_hash"]:
                raise ValueError("checkpoint memory context mismatch")
            if state.get("source_memory_file_sha256") != self.source[
                "memory_file_sha256"
            ]:
                raise ValueError("checkpoint source memory file mismatch")
            expected_cells = self._expected_cells()
            indexed: set[str] = set()
            condition_records: dict[str, dict[str, Any]] = {}
            total_units = 0
            for condition in _CONDITIONS:
                condition_state = state.get("conditions", {}).get(condition, {})
                cells = condition_state.get("cells", [])
                if not isinstance(cells, list):
                    raise ValueError("checkpoint condition cells must be a list")
                if int(condition_state.get("cells_completed", -1)) != len(cells):
                    raise ValueError("checkpoint condition cell count mismatch")
                recorded_units = sum(
                    int(cell["actual_model_cost_units"]) for cell in cells
                )
                if int(condition_state.get("model_cost_units", -1)) != recorded_units:
                    raise ValueError("checkpoint condition model cost mismatch")
                total_units += recorded_units
                for cell in cells:
                    if cell.get("condition") != condition:
                        raise ValueError("checkpoint cell is indexed under the wrong condition")
                    cell_id = str(cell["cell_id"])
                    if cell_id in indexed:
                        raise ValueError("checkpoint contains a duplicate transfer cell")
                    expected = expected_cells.get(cell_id)
                    if expected is None:
                        raise ValueError("checkpoint contains an unknown transfer cell")
                    self._validate_checkpoint_record(cell, expected)
                    indexed.add(cell_id)
                    condition_records[cell_id] = cell
                if recorded_units > (
                    self.config.per_condition_model_cost_cap_cents
                    * _COST_UNITS_PER_CENT
                ):
                    raise ValueError("checkpoint condition model cost exceeds its cap")
            if int(state.get("model_cost_units", -1)) != total_units:
                raise ValueError("checkpoint aggregate model cost mismatch")
            if total_units > (
                self.config.aggregate_model_cost_cap_cents * _COST_UNITS_PER_CENT
            ):
                raise ValueError("checkpoint aggregate model cost exceeds its cap")
            if set(state.get("completed_cells", {})) != indexed:
                raise ValueError("checkpoint completed-cell index mismatch")
            for cell_id in indexed:
                if state["completed_cells"][cell_id] != condition_records[cell_id]:
                    raise ValueError("checkpoint completed-cell content mismatch")
            for phase in self.config.phases:
                for seed_index in range(1, len(phase.seeds) + 1):
                    left_id = (
                        f"phase:{phase.phase_id}:seed-{seed_index:03d}:no_memory"
                    )
                    right_id = (
                        f"phase:{phase.phase_id}:seed-{seed_index:03d}:trained_memory"
                    )
                    if left_id in indexed and right_id in indexed:
                        left = state["completed_cells"][left_id]
                        right = state["completed_cells"][right_id]
                        if left["world_commitment"] != right["world_commitment"]:
                            raise ValueError("paired transfer cells used different worlds")
            if state.get("status") == "completed":
                if indexed != set(expected_cells):
                    raise ValueError("completed transfer checkpoint omitted cells")
                previous_state = self.state if hasattr(self, "state") else None
                self.state = state
                try:
                    expected_summary = self._summary()
                finally:
                    if previous_state is None:
                        del self.state
                    else:
                        self.state = previous_state
                if state.get("summary") != expected_summary:
                    raise ValueError("completed transfer summary mismatch")
            elif state.get("summary") is not None:
                raise ValueError("incomplete transfer checkpoint cannot contain a summary")
            return state
        return {
            "schema_version": "capage-transfer-checkpoint-v1",
            "experiment_name": self.config.experiment_name,
            "config_commitment": commitment,
            "source_training_config_commitment": (
                self.config.source_training_config_commitment
            ),
            "source_memory_head_hash": self.source["memory_head_hash"],
            "source_memory_file_sha256": self.source["memory_file_sha256"],
            "memory_context_hash": self.source["memory_context_hash"],
            "status": "ready",
            "stop_reason": None,
            "model_cost_units": 0,
            "completed_cells": {},
            "errors": [],
            "conditions": {
                condition: {
                    "cells_completed": 0,
                    "cells": [],
                    "model_cost_units": 0,
                }
                for condition in _CONDITIONS
            },
            "summary": None,
        }

    def _expected_cells(self) -> dict[str, dict[str, Any]]:
        expected: dict[str, dict[str, Any]] = {}
        for phase in self.config.phases:
            for seed_index, seed in enumerate(phase.seeds, start=1):
                for condition in _CONDITIONS:
                    cell_id = (
                        f"phase:{phase.phase_id}:seed-{seed_index:03d}:{condition}"
                    )
                    expected[cell_id] = {
                        "phase_id": phase.phase_id,
                        "condition": condition,
                        "seed_index": seed_index,
                        "seed": seed,
                        "customer_population_seed": phase.customer_population_seed,
                        "customer_namespace": phase.customer_namespace,
                        "market_profile": phase.market_profile,
                        "config": self.config.cell_config(
                            phase=phase,
                            seed_index=seed_index,
                            condition=condition,
                            cost_cap_cents=self.config.per_cell_model_cost_cap_cents,
                        ),
                    }
        return expected

    def _validate_checkpoint_record(
        self,
        record: dict[str, Any],
        expected: dict[str, Any],
    ) -> None:
        for key in (
            "phase_id",
            "condition",
            "seed_index",
            "seed",
            "customer_population_seed",
            "customer_namespace",
            "market_profile",
        ):
            if record.get(key) != expected[key]:
                raise ValueError(f"checkpoint transfer cell {key} mismatch")
        if int(record.get("starting_capital_cents", -1)) != (
            self.config.starting_capital_cents
        ):
            raise ValueError("checkpoint transfer starting capital mismatch")
        expected_balance = (
            self.config.starting_capital_cents
            + int(record["earned_revenue_cents"])
            - int(record["expense_cents"])
        )
        if int(record["ending_balance_cents"]) != expected_balance:
            raise ValueError("checkpoint transfer balance equation failed")
        if int(record["net_change_cents"]) != (
            int(record["ending_balance_cents"])
            - self.config.starting_capital_cents
        ):
            raise ValueError("checkpoint transfer net-change equation failed")
        used_units = int(record["actual_model_cost_units"])
        if not 0 <= used_units <= (
            self.config.per_cell_model_cost_cap_cents * _COST_UNITS_PER_CENT
        ):
            raise ValueError("checkpoint transfer cell model cost exceeds its cap")
        if expected["condition"] == "trained_memory":
            if int(record.get("memory_record_count", 0)) != len(
                self.source["memory_context"]["records"]
            ):
                raise ValueError("trained transfer cell memory record count mismatch")
            if record.get("memory_context_hash") != self.source[
                "memory_context_hash"
            ]:
                raise ValueError("trained transfer cell memory hash mismatch")
        elif int(record.get("memory_record_count", -1)) != 0 or record.get(
            "memory_context_hash"
        ) is not None:
            raise ValueError("no-memory transfer cell received memory")
        if not re.fullmatch(r"[0-9a-f]{64}", str(record.get("world_commitment", ""))):
            raise ValueError("checkpoint transfer world commitment is invalid")

        result_path = self.artifact_dir / str(record.get("result_file", ""))
        attempt_path = self.artifact_dir / str(record.get("attempt_file", ""))
        if not result_path.is_file() or not attempt_path.is_file():
            raise ValueError("checkpoint transfer artifacts are missing")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self._validate_result(result, expected["config"])
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        if (
            attempt.get("status") != "completed"
            or attempt.get("cell_id") != record["cell_id"]
            or attempt.get("config_commitment") != self.config.commitment()
            or attempt.get("source_memory_head_hash")
            != self.source["memory_head_hash"]
            or attempt.get("memory_context_hash")
            != record.get("memory_context_hash")
            or attempt.get("result_sha256")
            != sha256(_canonical_json(result).encode("utf-8")).hexdigest()
        ):
            raise ValueError("checkpoint transfer attempt artifact mismatch")
        outcome = result["outcome"]
        result_fields = {
            "ending_balance_cents": "balance_cents",
            "net_change_cents": "net_change_cents",
            "earned_revenue_cents": "earned_revenue_cents",
            "expense_cents": "expense_cents",
            "offers_sent": "offers_sent",
            "contracts_accepted": "contracts_accepted",
            "contracts_paid": "contracts_paid",
            "contracts_defaulted": "contracts_defaulted",
            "contracts_disputed": "contracts_disputed",
        }
        for record_key, outcome_key in result_fields.items():
            if int(record[record_key]) != int(outcome[outcome_key]):
                raise ValueError("checkpoint transfer record disagrees with result artifact")
        if record["world_commitment"] != result["world_reveal"]["world_commitment"]:
            raise ValueError("checkpoint transfer world commitment mismatch")

    def _checkpoint(self) -> None:
        _atomic_json(self.checkpoint_path, self.state)

    def _stop(self, reason: str) -> dict[str, Any]:
        self.state["status"] = "stopped"
        self.state["stop_reason"] = reason
        self._checkpoint()
        return self.state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--source-checkpoint")
    parser.add_argument("--source-memory")
    parser.add_argument("--checkpoint")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--max-cells", type=int)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args(argv)

    config = TransferConfig.from_manifest(args.manifest)
    if args.validate_only:
        print(
            json.dumps(
                {
                    "status": "validated",
                    "config_commitment": config.commitment(),
                    "cell_count": config.cell_count,
                    "maximum_external_model_cost_cents": (
                        config.aggregate_model_cost_cap_cents
                    ),
                },
                sort_keys=True,
            )
        )
        return 0
    required = {
        "--source-checkpoint": args.source_checkpoint,
        "--source-memory": args.source_memory,
        "--checkpoint": args.checkpoint,
        "--artifact-dir": args.artifact_dir,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        parser.error(f"paid execution requires {', '.join(missing)}")
    if args.confirm != "RUN_PREREGISTERED_TRANSFER_V1":
        parser.error(
            "paid execution requires --confirm RUN_PREREGISTERED_TRANSFER_V1"
        )

    runner = TransferRunner(
        config,
        AnthropicMessagesClient(),
        source_checkpoint_path=args.source_checkpoint,
        source_memory_path=args.source_memory,
        checkpoint_path=args.checkpoint,
        artifact_dir=args.artifact_dir,
    )
    state = runner.run(max_cells=args.max_cells)
    print(
        json.dumps(
            {
                "status": state["status"],
                "stop_reason": state["stop_reason"],
                "completed_cell_count": len(state["completed_cells"]),
                "model_cost_cents_known_unrounded": (
                    int(state["model_cost_units"]) / _COST_UNITS_PER_CENT
                ),
                "summary": state.get("summary"),
            },
            sort_keys=True,
        )
    )
    return 0 if state["status"] in {"completed", "paused"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
