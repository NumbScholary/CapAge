"""Noninterference and accounting tests for homeostasis shadow mode."""

from __future__ import annotations

import ast
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

from capage.homeostasis import (
    EconomicMode,
    ExpenseOrigin,
    SustainabilityStatus,
)
from capage.homeostasis_shadow import (
    EconomicHomeostasisShadowRunner,
    SandboxResultProjector,
    SandboxResultShadowAssessor,
    SandboxShadowConfig,
    ShadowJsonlLog,
    ShadowProjectionError,
    main,
)


def ledger_event(
    event_sequence: int,
    *,
    ledger_sequence: int,
    day: int,
    entry_type: str,
    amount_cents: int,
    balance_cents: int,
    reference: str,
) -> dict[str, object]:
    return {
        "sequence": event_sequence,
        "day": day,
        "event_type": "ledger_posted",
        "data": {
            "sequence": ledger_sequence,
            "day": day,
            "entry_type": entry_type,
            "amount_cents": amount_cents,
            "balance_cents": balance_cents,
            "memo": f"Posting for {entry_type}.",
            "reference": reference,
        },
    }


def completed_result(*, settled: bool = False) -> dict[str, object]:
    journal: list[dict[str, object]] = [
        ledger_event(
            1,
            ledger_sequence=1,
            day=0,
            entry_type="owner_capital",
            amount_cents=25_000,
            balance_cents=25_000,
            reference="initial-capital",
        ),
        ledger_event(
            2,
            ledger_sequence=2,
            day=0,
            entry_type="model_api_cost",
            amount_cents=-2,
            balance_cents=24_998,
            reference="call-001",
        ),
        ledger_event(
            3,
            ledger_sequence=3,
            day=1,
            entry_type="market_search_cost",
            amount_cents=-3,
            balance_cents=24_995,
            reference="search-001",
        ),
        {
            "sequence": 4,
            "day": 2,
            "event_type": "offer_accepted",
            "data": {"contract_id": "contract-001"},
        },
        {
            "sequence": 5,
            "day": 3,
            "event_type": "delivery_assessed",
            "data": {
                "contract_id": "contract-001",
                "status": "accepted_pending_payment",
            },
        },
    ]
    balance = 24_995
    earned = 0
    open_obligations = 1
    day = 3
    if settled:
        journal.extend(
            [
                ledger_event(
                    6,
                    ledger_sequence=4,
                    day=4,
                    entry_type="earned_revenue",
                    amount_cents=100,
                    balance_cents=25_095,
                    reference="contract-001",
                ),
                {
                    "sequence": 7,
                    "day": 4,
                    "event_type": "payment_received",
                    "data": {"contract_id": "contract-001", "amount_cents": 100},
                },
            ]
        )
        balance = 25_095
        earned = 100
        open_obligations = 0
        day = 4
    return {
        "schema_version": "capage-live-sandbox-result-v1",
        "status": "completed",
        "stop_reason": "horizon_reached",
        "started_at": "2027-01-01T00:00:00+00:00",
        "completed_at": "2027-01-01T00:00:01+00:00",
        "transcript": [
            {
                "decision": 1,
                "day_before_action": 0,
                "day_after_action": 1,
                "host_tool_name": "sandbox.search_market",
                "execution": {"status": "executed"},
                "provider_response": {"id": "message-001"},
            },
            {
                "decision": 2,
                "day_before_action": 1,
                "day_after_action": day,
                "host_tool_name": "sandbox.wait",
                "execution": {"status": "executed"},
                "provider_response": {"id": "message-002"},
            },
        ],
        "outcome": {
            "run_id": "run-shadow-001",
            "day": day,
            "balance_cents": balance,
            "earned_revenue_cents": earned,
            "expense_cents": 5,
            "open_obligations": open_obligations,
            "contracts_paid": int(settled),
        },
        "world_reveal": {
            "world_commitment": "committed-world",
            "journal": journal,
        },
    }


class SandboxResultProjectorTests(unittest.TestCase):
    def test_rejects_an_unknown_source_schema(self) -> None:
        result = completed_result()
        result["schema_version"] = "unknown"
        with self.assertRaises(ShadowProjectionError):
            SandboxResultProjector.project(result)

    def test_maps_native_and_strategy_expense_from_immutable_ledger(self) -> None:
        projection = SandboxResultProjector.project(completed_result())
        settled = {
            item.expense_id: item
            for item in projection.expenses
            if item.status.value == "settled"
        }
        self.assertEqual(settled["ledger:2:model_api_cost"].cash_cents, 2)
        self.assertEqual(
            settled["ledger:2:model_api_cost"].origin,
            ExpenseOrigin.NATIVE,
        )
        self.assertEqual(
            settled["ledger:3:market_search_cost"].origin,
            ExpenseOrigin.STRATEGY,
        )

    def test_value_revenue_and_cash_receipt_remain_distinct(self) -> None:
        pending = SandboxResultProjector.project(completed_result())
        self.assertEqual(pending.facts.external_value_events, 1)
        self.assertEqual(pending.facts.earned_revenue_cents, 0)
        self.assertEqual(pending.facts.cash_received_cents, 0)
        self.assertEqual(pending.facts.pending_settlements, 1)

        settled = SandboxResultProjector.project(completed_result(settled=True))
        self.assertEqual(settled.facts.external_value_events, 1)
        self.assertEqual(settled.facts.earned_revenue_cents, 100)
        self.assertEqual(settled.facts.cash_received_cents, 100)
        self.assertEqual(settled.facts.pending_settlements, 0)

    def test_pending_settlement_prevents_false_functional_failure(self) -> None:
        assessor = SandboxResultShadowAssessor(
            SandboxShadowConfig(has_path_to_next_value_action=False)
        )
        pending = assessor.assess(completed_result())
        settled = assessor.assess(completed_result(settled=True))
        self.assertNotEqual(pending.signal["mode"], EconomicMode.FAILED.value)
        self.assertEqual(settled.signal["mode"], EconomicMode.FAILED.value)

    def test_forecast_and_overseer_costs_are_explicit_host_assumptions(self) -> None:
        result = completed_result()
        base = SandboxResultShadowAssessor().assess(result)
        burdened = SandboxResultShadowAssessor(
            SandboxShadowConfig(
                forecast_native_cash_cents=10_000,
                realized_overseer_imputed_cents=50,
            )
        ).assess(result)
        self.assertEqual(base.signal["mode"], EconomicMode.STABLE.value)
        self.assertEqual(burdened.signal["mode"], EconomicMode.WATCH.value)
        self.assertEqual(
            base.signal["sustainability_pressure"],
            SustainabilityStatus.UNCOVERED.value,
        )
        self.assertEqual(
            burdened.signal["sustainability_pressure"],
            SustainabilityStatus.UNCOVERED.value,
        )
        self.assertEqual(burdened.state["settled_imputed_cents"], 50)
        self.assertEqual(burdened.state["forecast_native_cash_cents"], 10_000)

    def test_post_start_owner_injection_disqualifies_strict_run(self) -> None:
        result = completed_result()
        outcome = result["outcome"]
        reveal = result["world_reveal"]
        assert isinstance(outcome, dict)
        assert isinstance(reveal, dict)
        journal = reveal["journal"]
        assert isinstance(journal, list)
        journal.append(
            ledger_event(
                6,
                ledger_sequence=4,
                day=3,
                entry_type="owner_capital",
                amount_cents=50,
                balance_cents=25_045,
                reference="rescue-capital",
            )
        )
        outcome["balance_cents"] = 25_045
        record = SandboxResultShadowAssessor().assess(result)
        self.assertTrue(record.signal["strict_run_disqualified"])
        self.assertEqual(record.facts["post_start_owner_injection_cents"], 50)

    def test_inconsistent_source_accounting_fails_closed(self) -> None:
        result = completed_result()
        outcome = result["outcome"]
        assert isinstance(outcome, dict)
        outcome["earned_revenue_cents"] = 999
        with self.assertRaisesRegex(ShadowProjectionError, "earned-revenue"):
            SandboxResultProjector.project(result)


class ShadowAssessmentTests(unittest.TestCase):
    def test_identical_completed_result_produces_identical_record(self) -> None:
        assessor = SandboxResultShadowAssessor(
            SandboxShadowConfig(observation_id="fixed-observation")
        )
        first = assessor.assess(completed_result())
        second = assessor.assess(completed_result())
        self.assertEqual(first, second)
        self.assertEqual(first.causal_phase, "post_run_only")
        self.assertTrue(first.advisory_only)

    def test_shadow_record_contains_no_emotional_or_authority_input(self) -> None:
        encoded = json.dumps(
            SandboxResultShadowAssessor().assess(completed_result()).to_dict(),
            sort_keys=True,
        )
        self.assertNotIn("fear", encoded)
        self.assertNotIn("model_confidence", encoded)
        self.assertNotIn("authorized_exposure", encoded)

    def test_hashes_cover_source_transcript_and_world_journal(self) -> None:
        assessor = SandboxResultShadowAssessor()
        original = assessor.assess(completed_result())
        changed = completed_result()
        transcript = changed["transcript"]
        assert isinstance(transcript, list)
        assert isinstance(transcript[0], dict)
        transcript[0]["provider_response"] = {"id": "changed"}
        revised = assessor.assess(changed)
        self.assertNotEqual(
            original.source_result_sha256,
            revised.source_result_sha256,
        )
        self.assertNotEqual(
            original.source_transcript_sha256,
            revised.source_transcript_sha256,
        )
        self.assertEqual(
            original.source_world_journal_sha256,
            revised.source_world_journal_sha256,
        )


class FakeCompletedRunner:
    def __init__(self, result: dict[str, object], trace: list[str]) -> None:
        self.result = result
        self.trace = trace
        self.calls = 0

    def run(self) -> dict[str, object]:
        self.calls += 1
        self.trace.extend(
            ["model_request", "model_response", "tool_execution", "world_transition"]
        )
        return self.result


class TracingAssessor(SandboxResultShadowAssessor):
    def __init__(self, trace: list[str]) -> None:
        super().__init__()
        self.trace = trace

    def assess(self, source_result, history=None):
        self.trace.append("shadow_assessment")
        return super().assess(source_result, history)


class MutatingFailingAssessor:
    def assess(self, source_result, history=None):
        del history
        source_result["status"] = "mutated"
        raise RuntimeError("deliberate shadow failure")


class ShadowRunnerTests(unittest.TestCase):
    def test_shadow_module_does_not_import_authority_or_provider_surfaces(self) -> None:
        module_path = Path(__file__).parents[1] / "capage" / "homeostasis_shadow.py"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        forbidden = {
            "capage.anthropic_client",
            "capage.audit",
            "capage.executor",
            "capage.policy",
            "capage.sandbox",
            "capage.sandbox_runner",
        }
        self.assertTrue(forbidden.isdisjoint(imported))

    def test_shadow_assessment_occurs_after_source_world_transition(self) -> None:
        trace: list[str] = []
        source = FakeCompletedRunner(completed_result(), trace)
        wrapped = EconomicHomeostasisShadowRunner(
            source,
            TracingAssessor(trace),
        ).run()
        self.assertEqual(source.calls, 1)
        self.assertEqual(
            trace,
            [
                "model_request",
                "model_response",
                "tool_execution",
                "world_transition",
                "shadow_assessment",
            ],
        )
        self.assertIsNone(wrapped.shadow_error)

    def test_wrapper_returns_byte_equivalent_unmodified_source_result(self) -> None:
        direct_trace: list[str] = []
        shadow_trace: list[str] = []
        direct = FakeCompletedRunner(completed_result(), direct_trace).run()
        source_result = completed_result()
        before = json.dumps(source_result, sort_keys=True, separators=(",", ":"))
        wrapped = EconomicHomeostasisShadowRunner(
            FakeCompletedRunner(source_result, shadow_trace)
        ).run()
        after = json.dumps(
            wrapped.source_result,
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(direct_trace, shadow_trace)
        self.assertEqual(direct, wrapped.source_result)
        self.assertEqual(before, after)
        self.assertNotIn("shadow", wrapped.source_result)

    def test_shadow_failure_does_not_mutate_or_retry_source(self) -> None:
        trace: list[str] = []
        original = completed_result()
        before = deepcopy(original)
        source = FakeCompletedRunner(original, trace)
        wrapped = EconomicHomeostasisShadowRunner(
            source,
            MutatingFailingAssessor(),  # type: ignore[arg-type]
        ).run()
        self.assertEqual(source.calls, 1)
        self.assertEqual(wrapped.source_result, before)
        self.assertIsNone(wrapped.shadow_record)
        self.assertIn("deliberate shadow failure", wrapped.shadow_error or "")

    def test_source_exception_propagates_without_shadow_retry(self) -> None:
        class FailingRunner:
            def __init__(self) -> None:
                self.calls = 0

            def run(self):
                self.calls += 1
                raise RuntimeError("source failed")

        source = FailingRunner()
        with self.assertRaisesRegex(RuntimeError, "source failed"):
            EconomicHomeostasisShadowRunner(source).run()
        self.assertEqual(source.calls, 1)

    def test_sidecar_write_failure_keeps_completed_source_result(self) -> None:
        class FailingLog:
            def append(self, record):
                del record
                raise OSError("sidecar unavailable")

        trace: list[str] = []
        original = completed_result()
        source = FakeCompletedRunner(original, trace)
        wrapped = EconomicHomeostasisShadowRunner(
            source,
            shadow_log=FailingLog(),  # type: ignore[arg-type]
        ).run()
        self.assertEqual(source.calls, 1)
        self.assertEqual(wrapped.source_result, original)
        self.assertIsNotNone(wrapped.shadow_record)
        self.assertFalse(wrapped.shadow_record_persisted)
        self.assertIn("sidecar unavailable", wrapped.shadow_error or "")


class ShadowLogTests(unittest.TestCase):
    def test_log_is_append_only_hash_chained_and_verifiable(self) -> None:
        record = SandboxResultShadowAssessor().assess(completed_result())
        with tempfile.TemporaryDirectory() as directory:
            log = ShadowJsonlLog(Path(directory) / "shadow.jsonl")
            first = log.append(record)
            second = log.append(record)
            verification = log.verify()
        self.assertEqual(first["sequence"], 1)
        self.assertEqual(second["sequence"], 2)
        self.assertEqual(second["previous_record_hash"], first["record_hash"])
        self.assertTrue(verification.valid)
        self.assertEqual(verification.record_count, 2)

    def test_log_detects_tampering_and_refuses_another_append(self) -> None:
        record = SandboxResultShadowAssessor().assess(completed_result())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shadow.jsonl"
            log = ShadowJsonlLog(path)
            log.append(record)
            envelope = json.loads(path.read_text(encoding="utf-8"))
            envelope["record"]["signal"]["mode"] = "critical"
            path.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
            verification = log.verify()
            with self.assertRaisesRegex(ShadowProjectionError, "verification"):
                log.append(record)
        self.assertFalse(verification.valid)
        self.assertIn("hash mismatch", verification.error or "")

    def test_cli_assesses_existing_result_without_running_a_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "result.json"
            log_path = Path(directory) / "shadow.jsonl"
            result_path.write_text(
                json.dumps(completed_result()),
                encoding="utf-8",
            )
            output = io.StringIO()
            with redirect_stdout(output):
                status = main(
                    [
                        str(result_path),
                        "--shadow-log",
                        str(log_path),
                        "--forecast-native-cash-cents",
                        "1000",
                    ]
                )
            summary = json.loads(output.getvalue())
            verification = ShadowJsonlLog(log_path).verify()
        self.assertEqual(status, 0)
        self.assertEqual(summary["observation_id"], "run-shadow-001:completed")
        self.assertTrue(verification.valid)
        self.assertEqual(verification.record_count, 1)


if __name__ == "__main__":
    unittest.main()
