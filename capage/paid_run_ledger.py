"""Durable, append-only ledger for CapAge paid provider calls and economic events.

This module is deliberately pure I/O: every entry is a plain JSON object
appended to one newline-delimited file. It performs no network calls, calls
no model, and owns no credentials -- callers decide whether an entry may be
written; this module only makes the write durable, fail-closed against
ambiguous paid attempts, and queryable as a single source of truth for every
paid call's cost, superseding the independently reimplemented attempt-marker
files and per-runner spend bookkeeping this module replaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


LEDGER_SCHEMA = "capage-paid-run-ledger-v1"

_RESOLVING_ENTRY_TYPES = ("paid_call_completed", "paid_call_reconciled")


class PaidRunLedgerError(ValueError):
    """Raised for invalid ledger operations or malformed ledger state."""


@dataclass(frozen=True)
class LedgerHandle:
    """Identifies one in-flight paid call for later completion."""

    sequence: int
    run_id: str
    cell_id: str


@dataclass(frozen=True)
class OrphanEntry:
    """A ``paid_call_started`` entry with no matching completed/reconciled entry."""

    sequence: int
    run_id: str
    cell_id: str
    timestamp: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_entries(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        entries.append(json.loads(stripped))
    return entries


def _next_sequence(entries: list[dict[str, Any]]) -> int:
    if not entries:
        return 1
    return max(int(entry["sequence"]) for entry in entries) + 1


def _atomic_append(ledger_path: Path, entry: dict[str, Any]) -> None:
    """Append one entry by atomically rewriting the whole file.

    Mirrors the temp-file-plus-replace pattern used elsewhere in this
    codebase for checkpoint writes, so a crash mid-write never leaves a
    partial or corrupt line visible to a later reader.
    """

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    entries = _read_entries(ledger_path)
    entries.append(entry)
    lines = [
        json.dumps(item, sort_keys=True, separators=(",", ":")) for item in entries
    ]
    temporary = ledger_path.with_suffix(ledger_path.suffix + ".tmp")
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    temporary.replace(ledger_path)


def _validate_call_identity(run_id: str, cell_id: str) -> None:
    if not run_id.strip():
        raise PaidRunLedgerError("run_id is required")
    if not cell_id.strip():
        raise PaidRunLedgerError("cell_id is required")


def _resolved_started_sequences(entries: list[dict[str, Any]]) -> set[int]:
    return {
        int(entry["started_sequence"])
        for entry in entries
        if entry["entry_type"] in _RESOLVING_ENTRY_TYPES
    }


def _is_ambiguous(
    entries: list[dict[str, Any]], *, run_id: str, cell_id: str
) -> bool:
    started = [
        entry
        for entry in entries
        if entry["entry_type"] == "paid_call_started"
        and entry["run_id"] == run_id
        and entry["cell_id"] == cell_id
    ]
    if not started:
        return False
    resolved = _resolved_started_sequences(entries)
    return any(int(entry["sequence"]) not in resolved for entry in started)


def begin_call(
    ledger_path: str | Path,
    *,
    run_id: str,
    workflow_name: str,
    cell_id: str,
    model: str,
    tariff_name: str,
    effort: str = "",
) -> LedgerHandle:
    """Record that a paid provider call is about to be attempted.

    Raises ``PaidRunLedgerError`` if a prior ``paid_call_started`` entry for
    this exact ``(run_id, cell_id)`` has no matching completed or reconciled
    entry -- the same fail-closed guarantee the per-runner attempt-marker
    files provided, now backed by ledger data instead of file existence.
    """

    path = Path(ledger_path)
    _validate_call_identity(run_id, cell_id)
    if not model.strip():
        raise PaidRunLedgerError("model is required")
    if not tariff_name.strip():
        raise PaidRunLedgerError("tariff_name is required")
    entries = _read_entries(path)
    if _is_ambiguous(entries, run_id=run_id, cell_id=cell_id):
        raise PaidRunLedgerError(
            f"cell '{cell_id}' in run '{run_id}' already has an unresolved "
            "paid_call_started entry; refusing to start another attempt"
        )
    sequence = _next_sequence(entries)
    entry = {
        "schema_version": LEDGER_SCHEMA,
        "sequence": sequence,
        "timestamp": _now(),
        "run_id": run_id,
        "workflow_name": workflow_name,
        "entry_type": "paid_call_started",
        "cell_id": cell_id,
        "model": model,
        "tariff_name": tariff_name,
        "effort": effort,
    }
    _atomic_append(path, entry)
    return LedgerHandle(sequence=sequence, run_id=run_id, cell_id=cell_id)


def complete_call(
    ledger_path: str | Path,
    handle: LedgerHandle,
    *,
    input_tokens: int,
    output_tokens: int,
    tariff: Any,
) -> int:
    """Record a successful paid call's real, post-response usage and cost.

    ``tariff`` must expose ``cost_units(input_tokens, output_tokens) -> int``
    (``capage.sandbox.TokenTariff`` satisfies this) so cost is always
    computed by the one frozen formula, never reimplemented here.
    """

    path = Path(ledger_path)
    entries = _read_entries(path)
    started = next(
        (
            entry
            for entry in entries
            if entry["entry_type"] == "paid_call_started"
            and entry["sequence"] == handle.sequence
        ),
        None,
    )
    if started is None:
        raise PaidRunLedgerError(
            f"no paid_call_started entry found for sequence {handle.sequence}"
        )
    cost_units = tariff.cost_units(input_tokens, output_tokens)
    sequence = _next_sequence(entries)
    entry = {
        "schema_version": LEDGER_SCHEMA,
        "sequence": sequence,
        "timestamp": _now(),
        "run_id": handle.run_id,
        "workflow_name": started["workflow_name"],
        "entry_type": "paid_call_completed",
        "cell_id": handle.cell_id,
        "started_sequence": handle.sequence,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_units": cost_units,
    }
    _atomic_append(path, entry)
    return cost_units


def check_for_orphans(ledger_path: str | Path) -> list[OrphanEntry]:
    """Return every ``paid_call_started`` entry with no matching resolution."""

    entries = _read_entries(Path(ledger_path))
    resolved = _resolved_started_sequences(entries)
    return [
        OrphanEntry(
            sequence=entry["sequence"],
            run_id=entry["run_id"],
            cell_id=entry["cell_id"],
            timestamp=entry["timestamp"],
        )
        for entry in entries
        if entry["entry_type"] == "paid_call_started"
        and entry["sequence"] not in resolved
    ]


def reconcile_orphan(
    ledger_path: str | Path,
    *,
    started_sequence: int,
    cost_units: int,
    evidence_reference: str,
    reconciliation_note: str = "",
    reconciled_by: str = "",
) -> None:
    """Record the real cost of a previously orphaned paid call.

    This is the data-driven replacement for hand-editing a constant such as
    ``ABORTED_RUN_MODEL_COST_UNITS`` into a runner's source: the forensic
    step of determining the real cost from preserved evidence stays manual,
    but the result becomes a ledger entry, not a source-code edit.
    """

    path = Path(ledger_path)
    entries = _read_entries(path)
    started = next(
        (
            entry
            for entry in entries
            if entry["entry_type"] == "paid_call_started"
            and entry["sequence"] == started_sequence
        ),
        None,
    )
    if started is None:
        raise PaidRunLedgerError(
            f"no paid_call_started entry with sequence {started_sequence}"
        )
    if started_sequence in _resolved_started_sequences(entries):
        raise PaidRunLedgerError(
            f"started entry {started_sequence} is already resolved"
        )
    if not evidence_reference.strip():
        raise PaidRunLedgerError(
            "evidence_reference is required for a reconciliation"
        )
    if isinstance(cost_units, bool) or not isinstance(cost_units, int):
        raise PaidRunLedgerError("cost_units must be an integer")
    if cost_units < 0:
        raise PaidRunLedgerError("cost_units cannot be negative")
    sequence = _next_sequence(entries)
    entry = {
        "schema_version": LEDGER_SCHEMA,
        "sequence": sequence,
        "timestamp": _now(),
        "run_id": started["run_id"],
        "workflow_name": started["workflow_name"],
        "entry_type": "paid_call_reconciled",
        "cell_id": started["cell_id"],
        "started_sequence": started_sequence,
        "cost_units": cost_units,
        "evidence_reference": evidence_reference,
        "reconciled_by": reconciled_by,
        "reconciliation_note": reconciliation_note,
    }
    _atomic_append(path, entry)


def aggregate_cost_units(
    ledger_path: str | Path,
    *,
    run_id: str | None = None,
    since: str | None = None,
) -> int:
    """Sum attributable cost across completed and reconciled paid calls.

    With no filters, this is the aggregate-across-every-run total (the role
    originally proposed as a separate Step 1.5 spend ledger). With
    ``run_id`` set, it is one run's own total, for that run's existing
    per-run cap check.
    """

    entries = _read_entries(Path(ledger_path))
    total = 0
    for entry in entries:
        if entry["entry_type"] not in _RESOLVING_ENTRY_TYPES:
            continue
        if run_id is not None and entry["run_id"] != run_id:
            continue
        if since is not None and entry["timestamp"] < since:
            continue
        total += int(entry["cost_units"])
    return total


def record_economic_event(
    ledger_path: str | Path,
    *,
    run_id: str,
    workflow_name: str,
    event_type: str,
    data: dict[str, Any],
) -> None:
    """Record a non-paid-call economic/authority/experimental event.

    Replaces ``AuditLog.record()`` and ``EconomicSandbox._record()`` as the
    durable copy; both may keep an in-memory or local convenience copy, but
    this ledger is the one considered authoritative.
    """

    path = Path(ledger_path)
    entries = _read_entries(path)
    sequence = _next_sequence(entries)
    entry = {
        "schema_version": LEDGER_SCHEMA,
        "sequence": sequence,
        "timestamp": _now(),
        "run_id": run_id,
        "workflow_name": workflow_name,
        "entry_type": "economic_event",
        "event_type": event_type,
        "data": data,
    }
    _atomic_append(path, entry)


def append_correction(
    ledger_path: str | Path,
    *,
    target_sequence: int,
    reason: str,
    corrected_fields: dict[str, Any],
    run_id: str = "",
    workflow_name: str = "",
) -> None:
    """Append a correction referencing a prior entry, never editing it.

    Satisfies the append-only-correction requirement: the original entry's
    bytes never change; a later reader reconstructs the corrected view by
    following ``target_sequence``.
    """

    path = Path(ledger_path)
    entries = _read_entries(path)
    if not any(entry["sequence"] == target_sequence for entry in entries):
        raise PaidRunLedgerError(f"no ledger entry with sequence {target_sequence}")
    if not reason.strip():
        raise PaidRunLedgerError("reason is required for a correction")
    if not corrected_fields:
        raise PaidRunLedgerError("corrected_fields must not be empty")
    sequence = _next_sequence(entries)
    entry = {
        "schema_version": LEDGER_SCHEMA,
        "sequence": sequence,
        "timestamp": _now(),
        "run_id": run_id,
        "workflow_name": workflow_name,
        "entry_type": "correction",
        "target_sequence": target_sequence,
        "reason": reason,
        "corrected_fields": corrected_fields,
    }
    _atomic_append(path, entry)
