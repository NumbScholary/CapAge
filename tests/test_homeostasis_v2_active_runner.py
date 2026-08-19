from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from capage.homeostasis import HomeostasisSignal
from capage.homeostasis_v2 import HomeostasisSignalV2
from capage.homeostasis_v2_active_runner import (
    ActiveConfig,
    CONFIRMATION,
    ThreeArmHomeostasisRunner,
    main,
)


class FakeCellRunner:
    arm = "unknown"
    calls = []
    fail_arms = set()

    def __init__(
        self,
        config,
        client,
        *,
        audit_path,
        continuity_state,
        homeostasis_signal=None,
    ):
        self.config = config
        self.audit_path = Path(audit_path)
        self.continuity_state = deepcopy(continuity_state)
        self.homeostasis_signal = homeostasis_signal

    def run(self):
        FakeCellRunner.calls.append(
            {
                "arm": self.arm,
                "run_name": self.config.run_name,
                "starting_capital_cents": self.config.starting_capital_cents,
                "continuity_state": deepcopy(self.continuity_state),
                "homeostasis_signal": self.homeostasis_signal,
            }
        )
        if self.arm in FakeCellRunner.fail_arms:
            raise RuntimeError("synthetic provider interruption")

        starting = self.config.starting_capital_cents
        balance = starting - 1
        continuity = deepcopy(self.continuity_state)
        continuity.setdefault("history", []).append(self.config.run_name)
        journal = [
            {
                "sequence": 1,
                "day": 0,
                "event_type": "ledger_posted",
                "data": {
                    "sequence": 1,
                    "day": 0,
                    "entry_type": "owner_capital",
                    "amount_cents": starting,
                    "balance_cents": starting,
                    "memo": "Initial capital.",
                    "reference": "initial-capital",
                },
            },
            {
                "sequence": 2,
                "day": 30,
                "event_type": "ledger_posted",
                "data": {
                    "sequence": 2,
                    "day": 30,
                    "entry_type": "model_api_cost",
                    "amount_cents": -1,
                    "balance_cents": balance,
                    "memo": "Synthetic model cost.",
                    "reference": "call-001",
                },
            },
        ]
        return {
            "schema_version": "capage-live-sandbox-result-v1",
            "status": "completed",
            "stop_reason": "horizon_reached",
            "actual_model_cost_units": 1_000_000,
            "transcript": [],
            "outcome": {
                "run_id": self.config.run_name,
                "day": 30,
                "balance_cents": balance,
                "earned_revenue_cents": 0,
                "expense_cents": 1,
                "open_obligations": 0,
                "contracts_disputed": 0,
            },
            "business_continuity": continuity,
            "world_reveal": {"journal": journal},
        }


class FakeControlRunner(FakeCellRunner):
    arm = "control"


class FakeV1Runner(FakeCellRunner):
    arm = "v1"


class FakeV2Runner(FakeCellRunner):
    arm = "v2"


def fake_config_factory(**kwargs):
    kwargs.pop("tariff_name")
    kwargs.pop("input_cents_per_million_tokens")
    kwargs.pop("output_cents_per_million_tokens")
    return SimpleNamespace(**kwargs)


def fake_factories():
    return {
        "control": FakeControlRunner,
        "v1": FakeV1Runner,
        "v2": FakeV2Runner,
    }


class ThreeArmActiveRunnerGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parents[1]
        cls.plan_path = (
            cls.root
            / "experiments"
            / "sandbox"
            / "economic_homeostasis_v2_prereg_v1.json"
        )
        cls.plan = json.loads(cls.plan_path.read_text(encoding="utf-8"))

    def setUp(self):
        FakeCellRunner.calls = []
        FakeCellRunner.fail_arms = set()

    def runner(self, directory):
        return ThreeArmHomeostasisRunner(
            self.plan,
            object(),
            checkpoint_path=Path(directory) / "checkpoint.json",
            artifact_dir=Path(directory) / "cells",
            runner_factories=fake_factories(),
            run_config_factory=fake_config_factory,
            empty_continuity_factory=lambda: {"history": []},
        )

    def test_confirmation_and_budget_are_exact(self):
        gate = (
            self.root
            / "experiments"
            / "sandbox"
            / "HOMEOSTASIS_V2_EXECUTION_GATE.md"
        ).read_text(encoding="utf-8")
        self.assertIn(f"\n{CONFIRMATION}\n", gate)
        config = ActiveConfig.from_plan(self.plan)
        self.assertEqual(config.aggregate_cost_cap_cents, 1_350)
        self.assertEqual(config.per_cell_cost_cap_cents, 75)

    def test_plan_still_denies_provider_spend_and_workflow_authority(self):
        self.assertFalse(self.plan["provider_calls_authorized"])
        self.assertFalse(self.plan["spend_authorized"])
        self.assertFalse(self.plan["workflow_present"])

    def test_full_run_is_balanced_isolated_and_checkpointed(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            result = self.runner(directory).run(max_cells=18)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["stop_reason"], "all_cells_completed")
        self.assertEqual(len(result["completed_cells"]), 18)
        self.assertEqual(result["model_cost_units"], 18_000_000)
        self.assertEqual({row["arm"] for row in FakeCellRunner.calls}, {"control", "v1", "v2"})
        for arm in ("control", "v1", "v2"):
            calls = [row for row in FakeCellRunner.calls if row["arm"] == arm]
            self.assertEqual(len(calls), 6)
            self.assertEqual(
                [len(row["continuity_state"]["history"]) for row in calls],
                list(range(6)),
            )
            self.assertEqual(result["arms"][arm]["balance_cents"], 24_994)
            self.assertEqual(len(result["arms"][arm]["business_continuity"]["history"]), 6)

        control = [row for row in FakeCellRunner.calls if row["arm"] == "control"]
        v1 = [row for row in FakeCellRunner.calls if row["arm"] == "v1"]
        v2 = [row for row in FakeCellRunner.calls if row["arm"] == "v2"]
        self.assertTrue(all(row["homeostasis_signal"] is None for row in control))
        self.assertTrue(all(isinstance(row["homeostasis_signal"], HomeostasisSignal) for row in v1))
        self.assertTrue(all(isinstance(row["homeostasis_signal"], HomeostasisSignalV2) for row in v2))

    def test_resume_completes_without_repeating_a_paid_cell(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            first = self.runner(directory).run(max_cells=5)
            resumed = self.runner(directory).run(max_cells=18)

        self.assertEqual(first["status"], "paused")
        self.assertEqual(len(first["completed_cells"]), 5)
        self.assertEqual(resumed["status"], "completed")
        self.assertEqual(len(resumed["completed_cells"]), 18)
        self.assertEqual(len(FakeCellRunner.calls), 18)
        self.assertEqual(len({row["run_name"] for row in FakeCellRunner.calls}), 18)

    def test_interrupted_attempt_is_not_automatically_retried(self):
        FakeCellRunner.fail_arms = {"v2"}
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            failed = self.runner(directory).run(max_cells=18)
            FakeCellRunner.fail_arms = set()
            resumed = self.runner(directory).run(max_cells=18)

        self.assertEqual(failed["stop_reason"], "provider_or_runner_error")
        self.assertEqual(resumed["stop_reason"], "ambiguous_uncheckpointed_attempt")
        self.assertEqual(len(FakeCellRunner.calls), 1)

    def test_checkpoint_rejects_implementation_drift(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "first"},
        ):
            self.runner(directory).run(max_cells=1)
            with patch(
                "capage.homeostasis_v2_active_runner.implementation_commitments",
                return_value={"test": "changed"},
            ):
                with self.assertRaisesRegex(ValueError, "implementation mismatch"):
                    self.runner(directory)

    def test_checkpoint_rejects_tampered_completed_evidence(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            self.runner(directory).run(max_cells=1)
            result_path = (
                Path(directory)
                / "cells"
                / "homeostasis-v2-pair-01-v2.json"
            )
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            payload["outcome"]["balance_cents"] -= 1
            result_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "artifact mismatch"):
                self.runner(directory)

    def test_signal_failure_stops_before_paid_attempt_marker(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            runner = self.runner(directory)
            first = runner.run(max_cells=3)
            first_status = first["status"]
            with patch(
                "capage.homeostasis_v2_active_runner.completed_signal_for_arm",
                side_effect=ValueError("bad prior evidence"),
            ):
                stopped = runner.run(max_cells=18)
            next_attempt = (
                Path(directory)
                / "cells"
                / "homeostasis-v2-pair-02-v1-attempt.json"
            )
            attempt_exists = next_attempt.exists()

        self.assertEqual(first_status, "paused")
        self.assertEqual(stopped["stop_reason"], "signal_projection_error")
        self.assertFalse(attempt_exists)
        self.assertEqual(len(FakeCellRunner.calls), 3)

    def test_runner_requires_exactly_three_named_factories(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "control, v1, and v2"):
                ThreeArmHomeostasisRunner(
                    self.plan,
                    object(),
                    checkpoint_path=Path(directory) / "checkpoint.json",
                    artifact_dir=Path(directory) / "cells",
                    runner_factories={"control": FakeControlRunner},
                    run_config_factory=fake_config_factory,
                    empty_continuity_factory=lambda: {"history": []},
                )

    def test_cli_rejects_before_loading_provider_factories(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner._real_factories",
            side_effect=AssertionError("provider surface loaded"),
        ):
            with self.assertRaisesRegex(SystemExit, "exact paid-run confirmation"):
                main(
                    [
                        str(self.plan_path),
                        "--checkpoint",
                        str(Path(directory) / "checkpoint.json"),
                        "--artifact-dir",
                        str(Path(directory) / "cells"),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
