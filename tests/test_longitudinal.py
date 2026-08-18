"""Tests for matched, checkpointed longitudinal sandbox execution."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from capage.longitudinal import LongitudinalConfig, LongitudinalRunner, main
from capage.sandbox import TokenTariff


class FakeMonthRunner:
    calls: list[dict] = []
    fail_cell: str | None = None
    open_obligation_cell: str | None = None
    cost_units_by_arm = {"control": 1_000_000, "memory": 1_000_000}

    def __init__(
        self,
        config,
        client,
        *,
        audit_path,
        durable_context=None,
        continuity_state=None,
    ):
        del client
        self.config = config
        self.context = durable_context
        self.continuity = deepcopy(continuity_state)
        self.attempt_path = Path(str(audit_path).replace("-audit.jsonl", "-attempt.json"))

    def run(self):
        arm = "memory" if "-memory-" in self.config.run_name else "control"
        month = int(self.config.run_name.rsplit("-", 1)[1])
        cell = f"month-{month:03d}:{arm}"
        if not self.attempt_path.exists():
            raise RuntimeError("paid-attempt marker was not created before the runner")
        type(self).calls.append(
            {
                "cell": cell,
                "seed": self.config.seed,
                "starting_capital_cents": self.config.starting_capital_cents,
                "context": self.context,
                "continuity": deepcopy(self.continuity),
            }
        )
        if cell == type(self).fail_cell:
            raise RuntimeError("simulated provider interruption")
        net = (month * 20 if arm == "memory" else month * 10) - 5
        expense = 5
        revenue = net + expense
        open_obligations = int(cell == type(self).open_obligation_cell)
        continuity = deepcopy(self.continuity)
        customer_id = "customer-audience-research-01"
        customer = continuity["customers"].setdefault(
            customer_id,
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
        customer["contracts_paid"] += 1
        customer["reputation_points"] += 5
        customer["last_outcome"] = "paid"
        continuity["global_reputation_points"] += 5
        return {
            "status": "completed",
            "stop_reason": "horizon_reached",
            "actual_model_cost_units": type(self).cost_units_by_arm[arm],
            "outcome": {
                "owner_capital_cents": self.config.starting_capital_cents,
                "balance_cents": self.config.starting_capital_cents + net,
                "earned_revenue_cents": revenue,
                "expense_cents": expense,
                "net_change_cents": net,
                "offers_sent": month + 1,
                "contracts_accepted": 1,
                "contracts_paid": 1,
                "contracts_defaulted": 0,
                "contracts_disputed": 0,
                "open_obligations": open_obligations,
            },
            "transcript": [],
            "business_continuity": continuity,
        }


class LongitudinalRunnerTests(unittest.TestCase):
    def setUp(self):
        FakeMonthRunner.calls = []
        FakeMonthRunner.fail_cell = None
        FakeMonthRunner.open_obligation_cell = None
        FakeMonthRunner.cost_units_by_arm = {
            "control": 1_000_000,
            "memory": 1_000_000,
        }

    def config(self, **overrides):
        values = {
            "experiment_name": "matched-learning-test",
            "month_seeds": (101, 202, 303),
            "experiment_epoch": "2026-01-01T00:00:00+00:00",
            "starting_capital_cents": 25_000,
            "horizon_days": 30,
            "max_decisions_per_month": 25,
            "per_month_model_cost_cap_cents": 40,
            "aggregate_model_cost_cap_cents": 300,
            "per_arm_model_cost_cap_cents": 150,
            "model": "claude-sonnet-5",
            "effort": "medium",
            "max_output_tokens": 2048,
            "tariff": TokenTariff("test", 200, 1000),
            "assessor_version": "deterministic-artifact-v2",
            "customer_population_seed": 404_404,
        }
        values.update(overrides)
        return LongitudinalConfig(**values)

    def runner(self, directory, **kwargs):
        return LongitudinalRunner(
            kwargs.pop("config", self.config()),
            object(),
            checkpoint_path=Path(directory) / "checkpoint.json",
            artifact_dir=Path(directory) / "artifacts",
            memory_path=Path(directory) / "memory.sqlite3",
            runner_factory=FakeMonthRunner,
            **kwargs,
        )

    def test_matched_seeds_capital_carry_and_memory_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.runner(directory).run()

        self.assertEqual(state["status"], "completed")
        for month in range(1, 4):
            calls = [row for row in FakeMonthRunner.calls if row["cell"].startswith(f"month-{month:03d}")]
            self.assertEqual({row["seed"] for row in calls}, {self.config().month_seeds[month - 1]})
        control_calls = [row for row in FakeMonthRunner.calls if row["cell"].endswith(":control")]
        memory_calls = [row for row in FakeMonthRunner.calls if row["cell"].endswith(":memory")]
        self.assertTrue(all(row["context"] is None for row in control_calls))
        self.assertIsNone(memory_calls[0]["context"])
        self.assertGreater(len(memory_calls[1]["context"]["records"]), 0)
        self.assertEqual(control_calls[1]["starting_capital_cents"], 25_005)
        self.assertEqual(memory_calls[1]["starting_capital_cents"], 25_015)
        self.assertEqual(state["summary"]["mean_paired_delta_cents"], 20)
        self.assertEqual(control_calls[1]["continuity"]["global_reputation_points"], 5)
        self.assertEqual(memory_calls[1]["continuity"]["global_reputation_points"], 5)
        self.assertIsNot(
            state["arms"]["control"]["business_continuity"],
            state["arms"]["memory"]["business_continuity"],
        )

    def test_safe_pause_resumes_without_repeating_a_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.runner(directory).run(max_cells=2)
            self.assertEqual(first["status"], "paused")
            first_calls = list(FakeMonthRunner.calls)
            completed = set(first["completed_cells"])

            second = self.runner(directory).run()

        self.assertEqual(second["status"], "completed")
        self.assertEqual(len(FakeMonthRunner.calls), 6)
        self.assertEqual(len({row["cell"] for row in FakeMonthRunner.calls}), 6)
        self.assertEqual({row["cell"] for row in first_calls}, completed)

    def test_provider_error_is_checkpointed_and_never_retried(self):
        FakeMonthRunner.fail_cell = "month-002:memory"
        with tempfile.TemporaryDirectory() as directory:
            first = self.runner(directory).run()
            call_count = len(FakeMonthRunner.calls)
            attempt = (
                Path(directory)
                / "artifacts"
                / "matched-learning-test-memory-month-002-attempt.json"
            )
            attempt_payload = json.loads(attempt.read_text(encoding="utf-8"))
            second = self.runner(directory).run()

        self.assertEqual(first["status"], "stopped")
        self.assertEqual(first["stop_reason"], "provider_or_runner_error")
        self.assertEqual(second["status"], "stopped")
        self.assertEqual(len(FakeMonthRunner.calls), call_count)
        self.assertEqual(first["errors"][0]["cell_id"], "month-002:memory")
        self.assertEqual(attempt_payload["status"], "started")

    def test_orphaned_paid_attempt_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory) / "artifacts"
            artifact_dir.mkdir()
            (artifact_dir / "matched-learning-test-control-month-001-audit.jsonl").write_text(
                "paid attempt may have started\n", encoding="utf-8"
            )
            state = self.runner(directory).run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "ambiguous_uncheckpointed_attempt")
        self.assertEqual(FakeMonthRunner.calls, [])

    def test_started_attempt_marker_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory) / "artifacts"
            artifact_dir.mkdir()
            (artifact_dir / "matched-learning-test-control-month-001-attempt.json").write_text(
                '{"status":"started"}\n', encoding="utf-8"
            )
            state = self.runner(directory).run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "ambiguous_uncheckpointed_attempt")
        self.assertEqual(FakeMonthRunner.calls, [])

    def test_configuration_reserves_an_independent_budget_for_each_arm(self):
        with self.assertRaisesRegex(ValueError, "reserve both arm budgets"):
            self.config(
                aggregate_model_cost_cap_cents=9,
                per_arm_model_cost_cap_cents=5,
            )

    def test_expired_tariff_stops_before_creating_a_paid_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(
                directory,
                config=self.config(tariff_valid_through="2020-01-01"),
            )
            state = runner.run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "frozen_tariff_expired")
        self.assertEqual(FakeMonthRunner.calls, [])
        self.assertEqual(list((Path(directory) / "artifacts").glob("*-attempt.json")), [])

    def test_an_arm_cannot_borrow_the_other_arms_unused_reservation(self):
        FakeMonthRunner.cost_units_by_arm = {
            "control": 1_000_000,
            "memory": 2_000_000,
        }
        with tempfile.TemporaryDirectory() as directory:
            state = self.runner(
                directory,
                config=self.config(
                    per_arm_model_cost_cap_cents=4,
                    aggregate_model_cost_cap_cents=8,
                ),
            ).run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "arm_model_cost_cap_reached")
        self.assertEqual(state["arms"]["control"]["months_completed"], 3)
        self.assertEqual(state["arms"]["memory"]["months_completed"], 2)
        self.assertEqual(state["arms"]["control"]["model_cost_units"], 3_000_000)
        self.assertEqual(state["arms"]["memory"]["model_cost_units"], 4_000_000)

    def test_memory_checkpoint_mismatch_stops_before_a_model_call(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.runner(directory).run(max_cells=2)
            checkpoint = Path(directory) / "checkpoint.json"
            payload = json.loads(checkpoint.read_text(encoding="utf-8"))
            payload["memory_head_hash"] = "f" * 64
            checkpoint.write_text(json.dumps(payload), encoding="utf-8")
            calls = len(FakeMonthRunner.calls)
            second = self.runner(directory).run()

        self.assertEqual(first["status"], "paused")
        self.assertEqual(second["status"], "stopped")
        self.assertEqual(second["stop_reason"], "memory_checkpoint_mismatch")
        self.assertEqual(len(FakeMonthRunner.calls), calls)

    def test_tampered_business_continuity_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            self.runner(directory).run(max_cells=2)
            checkpoint = Path(directory) / "checkpoint.json"
            payload = json.loads(checkpoint.read_text(encoding="utf-8"))
            payload["arms"]["memory"]["business_continuity"][
                "global_reputation_points"
            ] = 99
            checkpoint.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "continuity hash mismatch"):
                self.runner(directory)

    def test_checkpoint_rejects_a_changed_host_implementation_commitment(self):
        with tempfile.TemporaryDirectory() as directory:
            self.runner(directory).run(max_cells=1)
            checkpoint = Path(directory) / "checkpoint.json"
            payload = json.loads(checkpoint.read_text(encoding="utf-8"))
            payload["implementation_commitments"]["capage/sandbox.py"] = "f" * 64
            checkpoint.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "host implementation mismatch"):
                self.runner(directory)

    def test_open_obligations_stop_instead_of_being_discarded(self):
        FakeMonthRunner.open_obligation_cell = "month-001:memory"
        with tempfile.TemporaryDirectory() as directory:
            state = self.runner(directory).run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(
            state["stop_reason"], "open_obligations_require_state_serialization"
        )

    def test_checkpoint_rejects_changed_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            self.runner(directory).run(max_cells=1)
            with self.assertRaisesRegex(ValueError, "frozen configuration"):
                self.runner(
                    directory,
                    config=self.config(month_seeds=(101, 202, 404)),
                )

    def test_frozen_manifest_validates_without_a_provider_call(self):
        manifest = (
            Path(__file__).parents[1]
            / "experiments"
            / "sandbox"
            / "longitudinal_manifest_v2.json"
        )
        with tempfile.TemporaryDirectory() as directory:
            status = main(
                [
                    str(manifest),
                    "--checkpoint",
                    str(Path(directory) / "checkpoint.json"),
                    "--artifact-dir",
                    str(Path(directory) / "months"),
                    "--memory",
                    str(Path(directory) / "memory.sqlite3"),
                    "--validate-only",
                ]
            )
        self.assertEqual(status, 0)


if __name__ == "__main__":
    unittest.main()
