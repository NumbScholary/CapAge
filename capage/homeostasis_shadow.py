"""Post-run economic-homeostasis shadow observation for CapAge.

The shadow layer has no causal access to a sandbox run.  It receives only the
completed result returned by a source runner, projects host-owned economic
facts, derives the v1 advisory signal, and may append a tamper-evident sidecar
record.  It imports no provider client, executor, policy engine, or sandbox
runner implementation.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from enum import Enum
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Protocol, Sequence

from capage.homeostasis import (
    ControllerHistory,
    EconomicFacts,
    EconomicStateProjector,
    ExpenseBehavior,
    ExpenseOrigin,
    ExpenseRecord,
    ExpenseStatus,
    HomeostasisController,
)


SHADOW_SCHEMA_VERSION = "capage-economic-homeostasis-shadow-v1"
SHADOW_LOG_SCHEMA_VERSION = "capage-economic-homeostasis-shadow-log-v1"
SOURCE_RESULT_SCHEMA_VERSION = "capage-live-sandbox-result-v1"

_NATIVE_LEDGER_TYPES = frozenset({"model_api_cost"})
_EXTERNAL_ACTION_TOOLS = frozenset(
    {
        "sandbox.search_market",
        "sandbox.send_offer",
        "sandbox.submit_delivery",
        "sandbox.request_feedback",
    }
)


class ShadowProjectionError(ValueError):
    """A completed source artifact cannot support a grounded projection."""


class CompletedRunner(Protocol):
    """The only source-runner surface visible to the shadow wrapper."""

    def run(self) -> dict[str, Any]: ...


def _json_default(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"value of type {type(value).__name__} is not JSON serializable")


def _canonical_text(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=_json_default,
    )


def _digest(value: object) -> str:
    return sha256(_canonical_text(value).encode("utf-8")).hexdigest()


def _json_copy(value: object) -> object:
    return json.loads(_canonical_text(value))


def _nonnegative_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")


def _required_mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ShadowProjectionError(f"{key} must be an object")
    return value


def _required_list(parent: dict[str, Any], key: str) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        raise ShadowProjectionError(f"{key} must be an array")
    return value


def _required_int(parent: dict[str, Any], key: str) -> int:
    value = parent.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ShadowProjectionError(f"{key} must be an integer")
    if value < 0:
        raise ShadowProjectionError(f"{key} cannot be negative")
    return value


@dataclass(frozen=True)
class SandboxShadowConfig:
    """Host-owned assumptions unavailable from a completed sandbox artifact.

    Forecast fields describe one controller cycle.  They are experimental
    observations, not reserves or authorization limits.  Extra expenses permit
    hosting, paid or imputed oversight, and other externally verified costs to
    be included without teaching the adapter to invent them.
    """

    observation_id: str = ""
    forecast_native_cash_cents: int = 0
    forecast_native_imputed_cents: int = 0
    realized_overseer_imputed_cents: int = 0
    usable_prepaid_resources_cents: int = 0
    collectible_receivables_cents: int = 0
    realizable_assets_cents: int = 0
    has_path_to_next_value_action: bool = True
    extra_expenses: tuple[ExpenseRecord, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, str):
            raise TypeError("observation_id must be a string")
        for field_name in (
            "forecast_native_cash_cents",
            "forecast_native_imputed_cents",
            "realized_overseer_imputed_cents",
            "usable_prepaid_resources_cents",
            "collectible_receivables_cents",
            "realizable_assets_cents",
        ):
            _nonnegative_int(getattr(self, field_name), field_name)
        if not isinstance(self.has_path_to_next_value_action, bool):
            raise TypeError("has_path_to_next_value_action must be a boolean")
        if not isinstance(self.extra_expenses, tuple):
            raise TypeError("extra_expenses must be a tuple")
        if not all(isinstance(item, ExpenseRecord) for item in self.extra_expenses):
            raise TypeError("extra_expenses must contain ExpenseRecord values")

    def evidence_payload(self) -> dict[str, object]:
        return {
            "forecast_native_cash_cents": self.forecast_native_cash_cents,
            "forecast_native_imputed_cents": (
                self.forecast_native_imputed_cents
            ),
            "realized_overseer_imputed_cents": (
                self.realized_overseer_imputed_cents
            ),
            "usable_prepaid_resources_cents": (
                self.usable_prepaid_resources_cents
            ),
            "collectible_receivables_cents": (
                self.collectible_receivables_cents
            ),
            "realizable_assets_cents": self.realizable_assets_cents,
            "has_path_to_next_value_action": (
                self.has_path_to_next_value_action
            ),
            "extra_expenses": [asdict(item) for item in self.extra_expenses],
        }


@dataclass(frozen=True)
class SandboxRunProjection:
    """Grounded controller inputs reconstructed from a completed run."""

    facts: EconomicFacts
    expenses: tuple[ExpenseRecord, ...]
    evidence: dict[str, object]


class SandboxResultProjector:
    """Translate a completed v1 sandbox result without modifying it."""

    @classmethod
    def project(
        cls,
        source_result: dict[str, Any],
        config: SandboxShadowConfig | None = None,
    ) -> SandboxRunProjection:
        if not isinstance(source_result, dict):
            raise ShadowProjectionError("source_result must be an object")
        if source_result.get("schema_version") != SOURCE_RESULT_SCHEMA_VERSION:
            raise ShadowProjectionError(
                f"source_result schema must be {SOURCE_RESULT_SCHEMA_VERSION}"
            )
        config = config or SandboxShadowConfig()
        outcome = _required_mapping(source_result, "outcome")
        reveal = _required_mapping(source_result, "world_reveal")
        journal = _required_list(reveal, "journal")
        transcript = _required_list(source_result, "transcript")

        ledger = cls._ledger_entries(journal)
        balance = _required_int(outcome, "balance_cents")
        earned_revenue = _required_int(outcome, "earned_revenue_cents")
        expense_cents = _required_int(outcome, "expense_cents")
        as_of_cycle = _required_int(outcome, "day")
        open_obligations = _required_int(outcome, "open_obligations")

        if ledger and int(ledger[-1]["balance_cents"]) != balance:
            raise ShadowProjectionError(
                "final ledger balance does not match outcome balance"
            )
        ledger_revenue = sum(
            int(entry["amount_cents"])
            for entry in ledger
            if entry["entry_type"] == "earned_revenue"
        )
        if ledger_revenue != earned_revenue:
            raise ShadowProjectionError(
                "earned-revenue ledger does not match outcome"
            )
        ledger_expense = -sum(
            int(entry["amount_cents"])
            for entry in ledger
            if int(entry["amount_cents"]) < 0
        )
        if ledger_expense != expense_cents:
            raise ShadowProjectionError("expense ledger does not match outcome")

        expenses = list(cls._expense_records(ledger))
        if (
            config.forecast_native_cash_cents
            or config.forecast_native_imputed_cents
        ):
            expenses.append(
                ExpenseRecord(
                    expense_id="shadow:native-forecast",
                    origin=ExpenseOrigin.NATIVE,
                    behavior=ExpenseBehavior.RECURRING,
                    status=ExpenseStatus.FORECAST,
                    cash_cents=config.forecast_native_cash_cents,
                    imputed_cents=config.forecast_native_imputed_cents,
                    attribution_id="capage-system",
                    description="Host-supplied native forecast for one cycle.",
                )
            )
        if config.realized_overseer_imputed_cents:
            expenses.append(
                ExpenseRecord(
                    expense_id="shadow:overseer-imputed",
                    origin=ExpenseOrigin.NATIVE,
                    behavior=ExpenseBehavior.USAGE,
                    status=ExpenseStatus.SETTLED,
                    imputed_cents=config.realized_overseer_imputed_cents,
                    attribution_id="capage-system",
                    description="Host-supplied imputed overseer work.",
                )
            )
        expenses.extend(config.extra_expenses)

        open_contracts, pending_contracts = cls._contract_state(journal)
        if len(open_contracts) != open_obligations:
            raise ShadowProjectionError(
                "contract journal does not match outcome open obligations"
            )
        value_cycles = cls._external_value_cycles(journal)
        action_cycles = cls._external_action_cycles(transcript)
        injection = cls._post_start_owner_injection(ledger)
        noncash_resources = (
            config.usable_prepaid_resources_cents
            + config.collectible_receivables_cents
            + config.realizable_assets_cents
        )
        peak_cash = max(
            [balance, *(int(entry["balance_cents"]) for entry in ledger)]
        )
        peak_resources = max(balance + noncash_resources, peak_cash + noncash_resources)

        facts = EconomicFacts(
            as_of_cycle=as_of_cycle,
            liquid_resources_cents=balance,
            usable_prepaid_resources_cents=(
                config.usable_prepaid_resources_cents
            ),
            collectible_receivables_cents=(
                config.collectible_receivables_cents
            ),
            realizable_assets_cents=config.realizable_assets_cents,
            earned_revenue_cents=earned_revenue,
            cash_received_cents=earned_revenue,
            external_value_events=len(value_cycles),
            peak_continuity_resources_cents=peak_resources,
            last_external_action_cycle=(max(action_cycles) if action_cycles else None),
            last_external_value_cycle=(max(value_cycles) if value_cycles else None),
            open_obligations=open_obligations,
            pending_settlements=len(pending_contracts),
            has_path_to_next_value_action=(
                config.has_path_to_next_value_action
            ),
            has_pending_external_settlement=bool(pending_contracts),
            post_start_owner_injection_cents=injection,
        )
        evidence = {
            "projection_phase": "post_run_only",
            "ledger_entry_count": len(ledger),
            "open_contract_ids": sorted(open_contracts),
            "pending_settlement_contract_ids": sorted(pending_contracts),
            "external_value_cycles": value_cycles,
            "external_action_cycles": action_cycles,
            "cash_received_mapping": "sandbox earned revenue settles on receipt",
            "host_assumptions": config.evidence_payload(),
        }
        return SandboxRunProjection(facts, tuple(expenses), evidence)

    @staticmethod
    def _ledger_entries(journal: list[Any]) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        seen_sequences: set[int] = set()
        for event in journal:
            if not isinstance(event, dict):
                raise ShadowProjectionError("journal events must be objects")
            if event.get("event_type") != "ledger_posted":
                continue
            data = event.get("data")
            if not isinstance(data, dict):
                raise ShadowProjectionError("ledger event data must be an object")
            sequence = _required_int(data, "sequence")
            _required_int(data, "day")
            amount = data.get("amount_cents")
            if isinstance(amount, bool) or not isinstance(amount, int):
                raise ShadowProjectionError("amount_cents must be an integer")
            _required_int(data, "balance_cents")
            if not isinstance(data.get("entry_type"), str):
                raise ShadowProjectionError("entry_type must be a string")
            if sequence in seen_sequences:
                raise ShadowProjectionError("ledger sequences must be unique")
            seen_sequences.add(sequence)
            entries.append(data)
        entries.sort(key=lambda item: int(item["sequence"]))
        return entries

    @staticmethod
    def _expense_records(
        ledger: list[dict[str, Any]],
    ) -> tuple[ExpenseRecord, ...]:
        records: list[ExpenseRecord] = []
        for entry in ledger:
            amount = int(entry["amount_cents"])
            if amount >= 0:
                continue
            entry_type = str(entry["entry_type"])
            sequence = int(entry["sequence"])
            records.append(
                ExpenseRecord(
                    expense_id=f"ledger:{sequence}:{entry_type}",
                    origin=(
                        ExpenseOrigin.NATIVE
                        if entry_type in _NATIVE_LEDGER_TYPES
                        else ExpenseOrigin.STRATEGY
                    ),
                    behavior=ExpenseBehavior.USAGE,
                    status=ExpenseStatus.SETTLED,
                    cash_cents=-amount,
                    attribution_id=str(entry.get("reference", "")),
                    description=str(entry.get("memo", "")),
                )
            )
        return tuple(records)

    @staticmethod
    def _post_start_owner_injection(ledger: list[dict[str, Any]]) -> int:
        initial_seen = False
        injection = 0
        for entry in ledger:
            if entry["entry_type"] != "owner_capital":
                continue
            amount = int(entry["amount_cents"])
            is_initial = (
                not initial_seen
                and int(entry["sequence"]) == 1
                and str(entry.get("reference", "")) == "initial-capital"
            )
            if is_initial:
                initial_seen = True
            elif amount > 0:
                injection += amount
        return injection

    @staticmethod
    def _contract_state(
        journal: list[Any],
    ) -> tuple[set[str], set[str]]:
        open_contracts: set[str] = set()
        pending_contracts: set[str] = set()
        for event in journal:
            if not isinstance(event, dict):
                continue
            event_type = event.get("event_type")
            data = event.get("data")
            if not isinstance(data, dict):
                continue
            contract_id = data.get("contract_id")
            if not isinstance(contract_id, str) or not contract_id:
                continue
            if event_type == "offer_accepted":
                open_contracts.add(contract_id)
            elif event_type == "delivery_assessed":
                if data.get("status") == "accepted_pending_payment":
                    pending_contracts.add(contract_id)
                elif data.get("status") == "disputed":
                    open_contracts.discard(contract_id)
                    pending_contracts.discard(contract_id)
            elif event_type in {"payment_received", "payment_defaulted"}:
                open_contracts.discard(contract_id)
                pending_contracts.discard(contract_id)
        return open_contracts, pending_contracts

    @staticmethod
    def _external_value_cycles(journal: list[Any]) -> list[int]:
        cycles: list[int] = []
        for event in journal:
            if not isinstance(event, dict):
                continue
            if event.get("event_type") != "delivery_assessed":
                continue
            data = event.get("data")
            if not isinstance(data, dict):
                continue
            if data.get("status") != "accepted_pending_payment":
                continue
            day = event.get("day")
            if isinstance(day, bool) or not isinstance(day, int) or day < 0:
                raise ShadowProjectionError("journal day must be nonnegative")
            cycles.append(day)
        return cycles

    @staticmethod
    def _external_action_cycles(transcript: list[Any]) -> list[int]:
        cycles: list[int] = []
        for item in transcript:
            if not isinstance(item, dict):
                raise ShadowProjectionError("transcript items must be objects")
            if item.get("host_tool_name") not in _EXTERNAL_ACTION_TOOLS:
                continue
            day = item.get("day_after_action", item.get("day_before_action"))
            if isinstance(day, bool) or not isinstance(day, int) or day < 0:
                raise ShadowProjectionError("action day must be nonnegative")
            cycles.append(day)
        return cycles


@dataclass(frozen=True)
class ShadowRecord:
    """Deterministic sidecar observation of one completed source result."""

    observation_id: str
    source_run_id: str
    source_result_sha256: str
    source_transcript_sha256: str
    source_world_journal_sha256: str
    assumptions_sha256: str
    facts: dict[str, object]
    expenses: tuple[dict[str, object], ...]
    state: dict[str, object]
    signal: dict[str, object]
    evidence: dict[str, object]
    schema_version: str = SHADOW_SCHEMA_VERSION
    causal_phase: str = "post_run_only"
    advisory_only: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "observation_id": self.observation_id,
            "causal_phase": self.causal_phase,
            "advisory_only": self.advisory_only,
            "source_run_id": self.source_run_id,
            "source_result_sha256": self.source_result_sha256,
            "source_transcript_sha256": self.source_transcript_sha256,
            "source_world_journal_sha256": self.source_world_journal_sha256,
            "assumptions_sha256": self.assumptions_sha256,
            "facts": self.facts,
            "expenses": list(self.expenses),
            "state": self.state,
            "signal": self.signal,
            "evidence": self.evidence,
        }


class SandboxResultShadowAssessor:
    """Assess completed artifacts with the pure v1 controller."""

    def __init__(
        self,
        config: SandboxShadowConfig | None = None,
        controller: HomeostasisController | None = None,
    ) -> None:
        self.config = config or SandboxShadowConfig()
        self.controller = controller or HomeostasisController()

    def assess(
        self,
        source_result: dict[str, Any],
        history: ControllerHistory | None = None,
    ) -> ShadowRecord:
        source_copy = _json_copy(source_result)
        if not isinstance(source_copy, dict):
            raise ShadowProjectionError("source_result must be an object")
        projection = SandboxResultProjector.project(source_copy, self.config)
        state = EconomicStateProjector.project(
            projection.facts,
            projection.expenses,
        )
        signal = self.controller.assess(state, history)
        outcome = _required_mapping(source_copy, "outcome")
        run_id = outcome.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ShadowProjectionError("outcome run_id must be a nonempty string")
        transcript = _required_list(source_copy, "transcript")
        journal = _required_list(
            _required_mapping(source_copy, "world_reveal"),
            "journal",
        )
        observation_id = self.config.observation_id or f"{run_id}:completed"
        signal_payload = signal.to_prompt_data()
        signal_payload["next_history"] = {
            "previous_mode": signal.next_history.previous_mode.value,
            "improving_observations": (
                signal.next_history.improving_observations
            ),
        }
        return ShadowRecord(
            observation_id=observation_id,
            source_run_id=run_id,
            source_result_sha256=_digest(source_copy),
            source_transcript_sha256=_digest(transcript),
            source_world_journal_sha256=_digest(journal),
            assumptions_sha256=_digest(self.config.evidence_payload()),
            facts=asdict(projection.facts),
            expenses=tuple(asdict(item) for item in projection.expenses),
            state=asdict(state),
            signal=signal_payload,
            evidence=projection.evidence,
        )


@dataclass(frozen=True)
class ShadowLogVerification:
    valid: bool
    record_count: int
    last_record_hash: str | None
    error: str | None = None


class ShadowJsonlLog:
    """Single-writer append-only hash chain for shadow sidecar records."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, record: ShadowRecord) -> dict[str, object]:
        if not isinstance(record, ShadowRecord):
            raise TypeError("record must be a ShadowRecord")
        verification = self.verify()
        if not verification.valid:
            raise ShadowProjectionError(
                f"existing shadow log failed verification: {verification.error}"
            )
        unsigned: dict[str, object] = {
            "schema_version": SHADOW_LOG_SCHEMA_VERSION,
            "sequence": verification.record_count + 1,
            "previous_record_hash": verification.last_record_hash,
            "record": record.to_dict(),
        }
        envelope = {**unsigned, "record_hash": _digest(unsigned)}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(_canonical_text(envelope) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return envelope

    def verify(self) -> ShadowLogVerification:
        if not self.path.exists():
            return ShadowLogVerification(True, 0, None)
        previous_hash: str | None = None
        count = 0
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    if not raw_line.strip():
                        raise ShadowProjectionError(
                            f"blank line at shadow log line {line_number}"
                        )
                    envelope = json.loads(raw_line)
                    if not isinstance(envelope, dict):
                        raise ShadowProjectionError("log envelope must be an object")
                    record_hash = envelope.get("record_hash")
                    if not isinstance(record_hash, str):
                        raise ShadowProjectionError("record_hash must be a string")
                    unsigned = {
                        key: value
                        for key, value in envelope.items()
                        if key != "record_hash"
                    }
                    if envelope.get("schema_version") != SHADOW_LOG_SCHEMA_VERSION:
                        raise ShadowProjectionError("unexpected log schema")
                    if envelope.get("sequence") != line_number:
                        raise ShadowProjectionError("non-contiguous log sequence")
                    if envelope.get("previous_record_hash") != previous_hash:
                        raise ShadowProjectionError("broken previous-record hash")
                    record = envelope.get("record")
                    if not isinstance(record, dict):
                        raise ShadowProjectionError("record must be an object")
                    if record.get("schema_version") != SHADOW_SCHEMA_VERSION:
                        raise ShadowProjectionError("unexpected record schema")
                    if _digest(unsigned) != record_hash:
                        raise ShadowProjectionError("record hash mismatch")
                    previous_hash = record_hash
                    count += 1
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            ShadowProjectionError,
        ) as exc:
            return ShadowLogVerification(False, count, previous_hash, str(exc))
        return ShadowLogVerification(True, count, previous_hash)


@dataclass(frozen=True)
class ShadowedRunResult:
    """Source result plus non-causal observation status."""

    source_result: dict[str, Any]
    shadow_record: ShadowRecord | None
    shadow_record_persisted: bool
    shadow_error: str | None


class EconomicHomeostasisShadowRunner:
    """Run an unchanged source once, then observe its completed result.

    Source-run exceptions propagate without retry.  Shadow assessment and log
    failures occur only after source completion and are returned as shadow
    errors, so they cannot rewrite the source result or trigger another paid
    attempt.
    """

    def __init__(
        self,
        source_runner: CompletedRunner,
        assessor: SandboxResultShadowAssessor | None = None,
        *,
        shadow_log: ShadowJsonlLog | None = None,
        history: ControllerHistory | None = None,
    ) -> None:
        if not hasattr(source_runner, "run"):
            raise TypeError("source_runner must provide run()")
        self.source_runner = source_runner
        self.assessor = assessor or SandboxResultShadowAssessor()
        self.shadow_log = shadow_log
        self.history = history

    def run(self) -> ShadowedRunResult:
        source_result = self.source_runner.run()
        if not isinstance(source_result, dict):
            return ShadowedRunResult(
                source_result=source_result,
                shadow_record=None,
                shadow_record_persisted=False,
                shadow_error="TypeError: source runner result must be an object",
            )
        try:
            source_before = _canonical_text(source_result)
        except (TypeError, ValueError) as exc:
            return ShadowedRunResult(
                source_result=source_result,
                shadow_record=None,
                shadow_record_persisted=False,
                shadow_error=f"{type(exc).__name__}: {exc}",
            )
        try:
            assessment_copy = _json_copy(source_result)
            if not isinstance(assessment_copy, dict):
                raise TypeError("source runner result must be an object")
            record = self.assessor.assess(assessment_copy, self.history)
        except Exception as exc:
            return ShadowedRunResult(
                source_result=source_result,
                shadow_record=None,
                shadow_record_persisted=False,
                shadow_error=f"{type(exc).__name__}: {exc}",
            )
        if _canonical_text(source_result) != source_before:
            return ShadowedRunResult(
                source_result=source_result,
                shadow_record=None,
                shadow_record_persisted=False,
                shadow_error="ShadowIntegrityError: source result changed",
            )
        if self.shadow_log is None:
            return ShadowedRunResult(source_result, record, False, None)
        try:
            self.shadow_log.append(record)
        except Exception as exc:
            return ShadowedRunResult(
                source_result=source_result,
                shadow_record=record,
                shadow_record_persisted=False,
                shadow_error=f"{type(exc).__name__}: {exc}",
            )
        return ShadowedRunResult(source_result, record, True, None)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assess a completed CapAge sandbox result in shadow mode."
    )
    parser.add_argument("result", help="Completed sandbox result JSON path.")
    parser.add_argument("--shadow-log", required=True, help="Sidecar JSONL path.")
    parser.add_argument("--observation-id", default="")
    parser.add_argument("--forecast-native-cash-cents", type=int, default=0)
    parser.add_argument("--forecast-native-imputed-cents", type=int, default=0)
    parser.add_argument("--overseer-imputed-cents", type=int, default=0)
    parser.add_argument(
        "--no-next-value-action-path",
        action="store_true",
        help="Declare that no authorized next value-action path exists.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    with Path(args.result).open("r", encoding="utf-8") as handle:
        result = json.load(handle)
    config = SandboxShadowConfig(
        observation_id=args.observation_id,
        forecast_native_cash_cents=args.forecast_native_cash_cents,
        forecast_native_imputed_cents=args.forecast_native_imputed_cents,
        realized_overseer_imputed_cents=args.overseer_imputed_cents,
        has_path_to_next_value_action=not args.no_next_value_action_path,
    )
    record = SandboxResultShadowAssessor(config).assess(result)
    envelope = ShadowJsonlLog(args.shadow_log).append(record)
    print(
        json.dumps(
            {
                "observation_id": record.observation_id,
                "mode": record.signal["mode"],
                "source_result_sha256": record.source_result_sha256,
                "record_hash": envelope["record_hash"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
