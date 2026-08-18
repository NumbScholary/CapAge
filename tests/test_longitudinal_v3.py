"""Tests for outcome-complete longitudinal v3 memory."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from capage.longitudinal_v3 import LongitudinalV3Config, LongitudinalV3Runner
from capage.memory import AuditedMemoryStore
from capage.sandbox import TokenTariff


class FakeV3MonthRunner:
    calls: list[dict] = []

    def __init__(
        self,
        config,
        client,
        *,
        audit_path,
        durable_context=None,
        continuity_state=None,
    ):
        del client, audit_path
        self.config = config
        self.context = durable_context
        self.continuity = deepcopy(continuity_state)

    def run(self) -> dict:
        arm = "memory" if "-memory-" in self.config.run_name else "control"
        month = int(self.config.run_name.rsplit("-", 1)[1])
        type(self).calls.append(
            {"arm": arm, "month": month, "context": deepcopy(self.context)}
        )
        customer = self.continuity["customers"].setdefault(
            "customer-generic-01",
            {
                "offers_sent": 0,
                "contracts_accepted": 0,
                "deliveries_assessed": 0,
                "contracts_paid": 0,
                "contracts_defaulted": 0,
                "contracts_disputed": 0,
                "feedback_responses": 0,
                "reputation_points": 0,
                "last_outcome": "",
            },
        )
        customer["offers_sent"] += 1
        customer["contracts_accepted"] += 1
        customer["deliveries_assessed"] += 1
        customer["contracts_disputed"] += 1
        customer["reputation_points"] -= 1
        customer["last_outcome"] = "delivery_disputed"
        self.continuity["global_reputation_points"] -= 1
        return {
            "status": "completed",
            "stop_reason": "horizon_reached",
            "actual_model_cost_units": 1,
            "outcome": {
                "owner_capital_cents": self.config.starting_capital_cents,
                "balance_cents": self.config.starting_capital_cents - 1,
                "earned_revenue_cents": 0,
                "expense_cents": 1,
                "net_change_cents": -1,
                "offers_sent": 1,
                "contracts_accepted": 1,
                "contracts_paid": 0,
                "contracts_defaulted": 0,
                "contracts_disputed": 1,
                "open_obligations": 0,
                "mean_customer_satisfaction": 25.0,
            },
            "transcript": [
                {
                    "host_assessment": {
                        "assessor_version": "deterministic-artifact-v2",
                        "quality_score": 45,
                        "factors": {"generic_accuracy": 10},
                        "result": {
                            "contract_id": "contract-001",
                            "delivery_id": "delivery-001",
                            "status": "disputed",
                        },
                    }
                }
            ],
            "business_continuity": self.continuity,
        }


class LongitudinalV3Tests(unittest.TestCase):
    def setUp(self):
        FakeV3MonthRunner.calls = []

    def config(self) -> LongitudinalV3Config:
        return LongitudinalV3Config(
            experiment_name="outcome-complete-test",
            month_seeds=(101, 202, 303),
            experiment_epoch="2026-01-01T00:00:00+00:00",
            starting_capital_cents=25_000,
            horizon_days=30,
            max_decisions_per_month=25,
            per_month_model_cost_cap_cents=40,
            aggregate_model_cost_cap_cents=300,
            per_arm_model_cost_cap_cents=150,
            model="claude-sonnet-5",
            effort="medium",
            max_output_tokens=2_048,
            tariff=TokenTariff("test", 200, 1_000),
            assessor_version="deterministic-artifact-v2",
            customer_population_seed=404_404,
        )

    def runner(self, directory: str) -> LongitudinalV3Runner:
        return LongitudinalV3Runner(
            self.config(),
            object(),
            checkpoint_path=Path(directory) / "checkpoint.json",
            artifact_dir=Path(directory) / "artifacts",
            memory_path=Path(directory) / "memory.sqlite3",
        )

    @staticmethod
    def result(
        *,
        status: str,
        quality_score: int,
        factors: dict[str, int],
        satisfaction: float | None,
    ) -> dict:
        return {
            "outcome": {"mean_customer_satisfaction": satisfaction},
            "transcript": [
                {
                    "host_assessment": {
                        "assessor_version": "deterministic-artifact-v2",
                        "quality_score": quality_score,
                        "factors": factors,
                        "result": {
                            "contract_id": "contract-001",
                            "delivery_id": "delivery-001",
                            "status": status,
                        },
                    }
                }
            ],
        }

    @staticmethod
    def record(
        month_number: int,
        *,
        result_file: str,
        paid: int = 0,
        defaulted: int = 0,
        disputed: int = 0,
        reputation: int = 0,
    ) -> dict:
        return {
            "cell_id": f"month-{month_number:03d}:memory",
            "arm": "memory",
            "month_number": month_number,
            "seed": month_number * 100,
            "status": "completed",
            "stop_reason": "horizon_reached",
            "starting_capital_cents": 25_000,
            "ending_balance_cents": 24_990,
            "net_change_cents": -10,
            "earned_revenue_cents": 0,
            "expense_cents": 10,
            "offers_sent": 3,
            "contracts_accepted": 1,
            "contracts_paid": paid,
            "contracts_defaulted": defaulted,
            "contracts_disputed": disputed,
            "actual_model_cost_units": 1_000_000,
            "memory_record_count": 0,
            "known_customers": 1,
            "global_reputation_points": reputation,
            "business_continuity_hash": "0" * 64,
            "result_file": result_file,
            "audit_file": "audit.jsonl",
            "attempt_file": "attempt.json",
        }

    def ingest(
        self,
        runner: LongitudinalV3Runner,
        memory: AuditedMemoryStore,
        record: dict,
        result: dict,
    ) -> None:
        runner.artifact_dir.mkdir(parents=True, exist_ok=True)
        result_path = runner.artifact_dir / record["result_file"]
        result_path.write_text(json.dumps(result), encoding="utf-8")
        runner.state["arms"]["memory"]["months"].append(record)
        runner._ingest_memory_month(memory, record)

    def test_dispute_quality_and_reputation_survive_projection_and_retrieval(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            record = self.record(
                1,
                result_file="month-001.json",
                disputed=1,
                reputation=-18,
            )
            result = self.result(
                status="disputed",
                quality_score=35,
                factors={"calculation_accuracy": 20, "record_coverage": 15},
                satisfaction=24.5,
            )
            with AuditedMemoryStore(runner.memory_path) as memory:
                self.ingest(runner, memory, record, result)
                context = runner._memory_context(memory, 2, "memory")

        self.assertEqual(record["reputation_delta"], -18)
        self.assertEqual(record["mean_customer_satisfaction"], 24.5)
        self.assertIsNotNone(context)
        text = "\n".join(item["content"] for item in context["records"])
        self.assertIn("scored delivery delivery-001 at 35/100", text)
        self.assertIn("calculation_accuracy=20", text)
        self.assertIn("delivery was disputed", text.lower())
        self.assertIn("-18 points", text)
        self.assertGreaterEqual(context["critical_incident_count"], 1)

    def test_payment_default_is_not_mislabeled_as_delivery_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            record = self.record(
                1,
                result_file="month-001.json",
                defaulted=1,
                reputation=12,
            )
            result = self.result(
                status="accepted_pending_payment",
                quality_score=100,
                factors={"calculation_accuracy": 30, "record_coverage": 15},
                satisfaction=100.0,
            )
            with AuditedMemoryStore(runner.memory_path) as memory:
                self.ingest(runner, memory, record, result)
                active = memory.active_memories(as_of=runner._month_start(2))

        delivery = next(item for item in active if "delivery-001-assessment" in item.memory_id)
        monthly = next(item for item in active if item.memory_id == "month-001-outcome")
        self.assertIn("passed assessment and was accepted", delivery.content)
        self.assertNotIn("delivery was disputed", delivery.content.lower())
        self.assertIn("1 customer payment defaults after accepted delivery", monthly.content)
        self.assertIn("0 delivery disputes", monthly.content)

    def test_dispute_without_host_assessment_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            record = self.record(
                1,
                result_file="month-001.json",
                disputed=1,
                reputation=-18,
            )
            runner.artifact_dir.mkdir(parents=True, exist_ok=True)
            (runner.artifact_dir / record["result_file"]).write_text(
                json.dumps(
                    {
                        "outcome": {"mean_customer_satisfaction": 20.0},
                        "transcript": [],
                    }
                ),
                encoding="utf-8",
            )
            runner.state["arms"]["memory"]["months"].append(record)
            with AuditedMemoryStore(runner.memory_path) as memory:
                with self.assertRaisesRegex(ValueError, "missing host assessment"):
                    runner._ingest_memory_month(memory, record)

                self.assertEqual(memory.active_memories(as_of=runner._month_start(2)), ())

    def test_critical_incident_is_forced_into_context_despite_lexical_noise(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            record = self.record(
                1,
                result_file="month-001.json",
                disputed=1,
                reputation=-7,
            )
            result = self.result(
                status="disputed",
                quality_score=41,
                factors={"reasoning_consistency": 5},
                satisfaction=30.0,
            )
            with AuditedMemoryStore(runner.memory_path) as memory:
                self.ingest(runner, memory, record, result)
                for index in range(20):
                    event_id = f"noise-{index:03d}"
                    memory.append_event(
                        event_id,
                        "synthetic_noise",
                        {"index": index},
                        occurred_at=runner._month_end(1),
                    )
                    memory.assert_memory(
                        f"noise-{index:03d}",
                        "operational",
                        (
                            "Pricing offers customers payments profit strategy "
                            f"routine observation {index}."
                        ),
                        tags=["pricing", "offers", "payments", "strategy"],
                        evidence_event_ids=[event_id],
                        confidence=100,
                        occurred_at=runner._month_end(1),
                    )
                context = runner._memory_context(memory, 2, "memory")

        ids = [item["memory_id"] for item in context["records"]]
        self.assertIn("month-001-delivery-001-assessment", ids)
        self.assertLess(ids.index("month-001-delivery-001-assessment"), 4)

    def test_strategy_tracks_failure_classes_satisfaction_and_sample_size(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            first = self.record(
                1,
                result_file="month-001.json",
                disputed=1,
                reputation=-8,
            )
            second = self.record(
                2,
                result_file="month-002.json",
                defaulted=1,
                reputation=-5,
            )
            with AuditedMemoryStore(runner.memory_path) as memory:
                self.ingest(
                    runner,
                    memory,
                    first,
                    self.result(
                        status="disputed",
                        quality_score=40,
                        factors={"record_coverage": 5},
                        satisfaction=20.0,
                    ),
                )
                self.ingest(
                    runner,
                    memory,
                    second,
                    self.result(
                        status="accepted_pending_payment",
                        quality_score=95,
                        factors={"record_coverage": 15},
                        satisfaction=90.0,
                    ),
                )
                active = memory.active_memories(as_of=runner._month_start(3))

        strategy = next(item for item in active if item.memory_id == "strategy-performance")
        self.assertIn("Across 2 completed months", strategy.content)
        self.assertIn("1 were disputed", strategy.content)
        self.assertIn("1 customers defaulted after accepted delivery", strategy.content)
        self.assertIn("2 monthly satisfaction observations", strategy.content)
        self.assertIn("-5 points", strategy.content)
        self.assertIn("small-sample", strategy.content)

    def test_control_arm_never_receives_durable_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            with AuditedMemoryStore(runner.memory_path) as memory:
                memory.append_event(
                    "control-isolation-evidence",
                    "test",
                    {"value": 1},
                    occurred_at=runner._month_end(1),
                )
                memory.assert_memory(
                    "control-isolation-memory",
                    "operational",
                    "A record that must remain unavailable to the control arm.",
                    tags=["critical incident"],
                    evidence_event_ids=["control-isolation-evidence"],
                    confidence=100,
                    occurred_at=runner._month_end(1),
                )
                context = runner._memory_context(memory, 2, "control")

        self.assertIsNone(context)

    def test_parent_run_path_persists_projection_and_injects_it_next_month(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = LongitudinalV3Runner(
                self.config(),
                object(),
                checkpoint_path=Path(directory) / "checkpoint.json",
                artifact_dir=Path(directory) / "artifacts",
                memory_path=Path(directory) / "memory.sqlite3",
                runner_factory=FakeV3MonthRunner,
            )
            state = runner.run()

        self.assertEqual(state["status"], "completed")
        first_record = state["completed_cells"]["month-001:memory"]
        self.assertEqual(first_record["mean_customer_satisfaction"], 25.0)
        self.assertEqual(first_record["reputation_delta"], -1)
        memory_calls = [row for row in FakeV3MonthRunner.calls if row["arm"] == "memory"]
        control_calls = [row for row in FakeV3MonthRunner.calls if row["arm"] == "control"]
        self.assertIsNone(memory_calls[0]["context"])
        self.assertGreaterEqual(memory_calls[1]["context"]["critical_incident_count"], 1)
        self.assertTrue(all(row["context"] is None for row in control_calls))

    def test_v3_checkpoint_is_separate_and_implementation_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            self.assertEqual(
                runner.state["schema_version"], "capage-longitudinal-checkpoint-v4"
            )
            self.assertEqual(
                runner.state["memory_projection_version"], "outcome-complete-v3"
            )
            runner._checkpoint()
            checkpoint = Path(directory) / "checkpoint.json"
            payload = json.loads(checkpoint.read_text(encoding="utf-8"))
            payload["implementation_commitments"]["capage/longitudinal_v3.py"] = (
                "f" * 64
            )
            checkpoint.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "host implementation mismatch"):
                self.runner(directory)

    def test_v3_manifest_schema_is_required(self):
        payload = {
            "schema_version": "capage-longitudinal-v3",
            "experiment_name": "manifest-test",
            "month_seeds": [11, 22],
            "experiment_epoch": "2026-01-01T00:00:00+00:00",
            "starting_capital_cents": 25_000,
            "horizon_days": 30,
            "max_decisions_per_month": 25,
            "per_month_model_cost_cap_cents": 40,
            "aggregate_model_cost_cap_cents": 200,
            "per_arm_model_cost_cap_cents": 100,
            "model": {
                "name": "claude-sonnet-5",
                "effort": "medium",
                "max_output_tokens": 2_048,
            },
            "token_tariff": {
                "name": "test",
                "input_cents_per_million_tokens": 200,
                "output_cents_per_million_tokens": 1_000,
            },
            "assessor_version": "deterministic-artifact-v2",
            "customer_population_seed": 404_404,
        }
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            config = LongitudinalV3Config.from_manifest(manifest)
            payload["schema_version"] = "capage-longitudinal-v2"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "v3 manifest schema"):
                LongitudinalV3Config.from_manifest(manifest)

        self.assertEqual(config.month_seeds, (11, 22))


if __name__ == "__main__":
    unittest.main()
