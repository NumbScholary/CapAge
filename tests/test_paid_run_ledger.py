"""Tests for the durable paid-run ledger."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from capage.paid_run_ledger import (
    LedgerHandle,
    PaidRunLedgerError,
    aggregate_cost_units,
    append_correction,
    begin_call,
    check_for_orphans,
    complete_call,
    reconcile_orphan,
    record_economic_event,
)
from capage.sandbox import TokenTariff


TARIFF = TokenTariff(
    name="test-tariff",
    input_cents_per_million_tokens=200,
    output_cents_per_million_tokens=1000,
)


class PaidRunLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self.ledger_path = Path(self._tempdir.name) / "ledger.jsonl"

    def _begin(self, *, run_id: str = "run-1", cell_id: str = "cell-1") -> LedgerHandle:
        return begin_call(
            self.ledger_path,
            run_id=run_id,
            workflow_name="test workflow",
            cell_id=cell_id,
            model="claude-sonnet-5",
            tariff_name=TARIFF.name,
        )

    def test_sequence_numbers_are_monotonic_and_continuous(self) -> None:
        first = self._begin(cell_id="cell-1")
        complete_call(
            self.ledger_path, first, input_tokens=100, output_tokens=50, tariff=TARIFF
        )
        second = self._begin(cell_id="cell-2")
        complete_call(
            self.ledger_path, second, input_tokens=10, output_tokens=5, tariff=TARIFF
        )
        entries = [
            line
            for line in self.ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(entries), 4)
        import json

        sequences = [json.loads(line)["sequence"] for line in entries]
        self.assertEqual(sequences, [1, 2, 3, 4])

    def test_complete_call_cost_matches_tariff_formula(self) -> None:
        handle = self._begin()
        cost_units = complete_call(
            self.ledger_path,
            handle,
            input_tokens=126_468,
            output_tokens=3_622,
            tariff=TARIFF,
        )
        self.assertEqual(
            cost_units, TARIFF.cost_units(input_tokens=126_468, output_tokens=3_622)
        )
        self.assertEqual(cost_units, 28_915_600)

    def test_begin_call_fails_closed_on_unresolved_prior_attempt(self) -> None:
        self._begin(cell_id="cell-1")
        with self.assertRaises(PaidRunLedgerError):
            self._begin(cell_id="cell-1")

    def test_begin_call_allows_new_attempt_after_completion(self) -> None:
        handle = self._begin(cell_id="cell-1")
        complete_call(
            self.ledger_path, handle, input_tokens=1, output_tokens=1, tariff=TARIFF
        )
        # Same cell id, different run -- must not collide with the resolved attempt.
        second = self._begin(run_id="run-2", cell_id="cell-1")
        self.assertEqual(second.run_id, "run-2")

    def test_check_for_orphans_finds_only_unresolved_started_entries(self) -> None:
        resolved = self._begin(cell_id="cell-resolved")
        complete_call(
            self.ledger_path,
            resolved,
            input_tokens=1,
            output_tokens=1,
            tariff=TARIFF,
        )
        orphan_handle = begin_call(
            self.ledger_path,
            run_id="run-1",
            workflow_name="test workflow",
            cell_id="cell-orphan",
            model="claude-sonnet-5",
            tariff_name=TARIFF.name,
        )
        orphans = check_for_orphans(self.ledger_path)
        self.assertEqual(len(orphans), 1)
        self.assertEqual(orphans[0].sequence, orphan_handle.sequence)
        self.assertEqual(orphans[0].cell_id, "cell-orphan")

    def test_reconcile_orphan_clears_it_and_counts_toward_aggregate(self) -> None:
        orphan_handle = self._begin(cell_id="cell-orphan")
        self.assertEqual(len(check_for_orphans(self.ledger_path)), 1)

        reconcile_orphan(
            self.ledger_path,
            started_sequence=orphan_handle.sequence,
            cost_units=28_915_600,
            evidence_reference="github-actions-run:32292164227/artifact:9379919939",
            reconciliation_note="Preserved provider usage recomputed under the frozen tariff.",
        )

        self.assertEqual(check_for_orphans(self.ledger_path), [])
        self.assertEqual(aggregate_cost_units(self.ledger_path), 28_915_600)

    def test_reconcile_orphan_rejects_already_resolved_entry(self) -> None:
        handle = self._begin()
        complete_call(
            self.ledger_path, handle, input_tokens=1, output_tokens=1, tariff=TARIFF
        )
        with self.assertRaises(PaidRunLedgerError):
            reconcile_orphan(
                self.ledger_path,
                started_sequence=handle.sequence,
                cost_units=1,
                evidence_reference="irrelevant",
            )

    def test_aggregate_cost_units_scoping_by_run_id(self) -> None:
        run_a = self._begin(run_id="run-a", cell_id="cell-1")
        complete_call(
            self.ledger_path, run_a, input_tokens=100, output_tokens=100, tariff=TARIFF
        )
        run_b = self._begin(run_id="run-b", cell_id="cell-1")
        complete_call(
            self.ledger_path, run_b, input_tokens=200, output_tokens=200, tariff=TARIFF
        )

        total = aggregate_cost_units(self.ledger_path)
        only_a = aggregate_cost_units(self.ledger_path, run_id="run-a")
        only_b = aggregate_cost_units(self.ledger_path, run_id="run-b")

        self.assertEqual(only_a, TARIFF.cost_units(100, 100))
        self.assertEqual(only_b, TARIFF.cost_units(200, 200))
        self.assertEqual(total, only_a + only_b)

    def test_correction_never_mutates_a_prior_line(self) -> None:
        record_economic_event(
            self.ledger_path,
            run_id="run-1",
            workflow_name="test workflow",
            event_type="ledger_posted",
            data={"amount_cents": 500},
        )
        before = self.ledger_path.read_text(encoding="utf-8").splitlines()[0]

        append_correction(
            self.ledger_path,
            target_sequence=1,
            reason="amount was mistyped",
            corrected_fields={"amount_cents": 5000},
        )

        after_lines = self.ledger_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(after_lines[0], before)
        self.assertEqual(len(after_lines), 2)

    def test_append_correction_rejects_unknown_target(self) -> None:
        with self.assertRaises(PaidRunLedgerError):
            append_correction(
                self.ledger_path,
                target_sequence=99,
                reason="nothing to correct",
                corrected_fields={"x": 1},
            )

    def test_record_economic_event_round_trips(self) -> None:
        record_economic_event(
            self.ledger_path,
            run_id="run-1",
            workflow_name="test workflow",
            event_type="policy_decision",
            data={"allowed": True},
        )
        entries = self.ledger_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(entries), 1)
        import json

        entry = json.loads(entries[0])
        self.assertEqual(entry["entry_type"], "economic_event")
        self.assertEqual(entry["event_type"], "policy_decision")
        self.assertEqual(entry["data"], {"allowed": True})


if __name__ == "__main__":
    unittest.main()
