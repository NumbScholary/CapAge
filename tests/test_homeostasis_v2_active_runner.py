from copy import deepcopy
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from capage.homeostasis import HomeostasisSignal
from capage.homeostasis_v2 import HomeostasisSignalV2
from capage.homeostasis_v2_active_runner import (
    ABORTED_RUN_COST_REFERENCE,
    ABORTED_RUN_MODEL_COST_UNITS,
    ActiveConfig,
    CONFIRMATION,
    ThreeArmHomeostasisRunner,
    main,
)
from capage.sandbox import TokenTariff


def _manifest_clock(plan):
    # Freeze "now" to the manifest's own token_tariff valid-through date (the last
    # valid day) so the frozen-tariff guard runs deterministically, independent of
    # the wall-clock day the test executes. Derived from the same manifest the
    # runner reads, so these tests do not validate the manifest date itself.
    valid_through = plan["frozen_config"]["token_tariff"]["valid_through"]
    frozen = datetime.fromisoformat(valid_through).replace(tzinfo=timezone.utc)
    return lambda: frozen


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
                "max_run_cost_cents": self.config.max_run_cost_cents,
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
        config_fields = (
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
        serialized_config = {
            field: getattr(self.config, field) for field in config_fields
        }
        serialized_config["tariff"] = {
            "name": self.config.tariff.name,
            "input_cents_per_million_tokens": (
                self.config.tariff.input_cents_per_million_tokens
            ),
            "output_cents_per_million_tokens": (
                self.config.tariff.output_cents_per_million_tokens
            ),
        }
        return {
            "schema_version": "capage-live-sandbox-result-v1",
            "status": "completed",
            "stop_reason": "horizon_reached",
            "actual_model_cost_units": 1_000_000,
            "actual_model_cost_cents_unrounded": 1.0,
            "actual_model_cost_cents_billed": 1,
            "config": serialized_config,
            "transcript": [],
            "outcome": {
                "run_id": f"world-{self.config.run_name}",
                "day": 30,
                "balance_cents": balance,
                "earned_revenue_cents": 0,
                "expense_cents": 1,
                "model_api_cost_cents": 1,
                "model_api_cost_units": 1_000_000,
                "model_input_tokens": 5_000,
                "model_output_tokens": 0,
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
    tariff_name = kwargs.pop("tariff_name")
    input_rate = kwargs.pop("input_cents_per_million_tokens")
    output_rate = kwargs.pop("output_cents_per_million_tokens")
    kwargs.setdefault("customer_namespace", "")
    kwargs.setdefault("market_profile", "baseline-v1")
    kwargs["tariff"] = TokenTariff(tariff_name, input_rate, output_rate)
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
            now=_manifest_clock(self.plan),
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
        aborted_record = (
            self.root
            / "experiments"
            / "sandbox"
            / "HOMEOSTASIS_V2_ABORTED_RUN_32292164227.md"
        ).read_text(encoding="utf-8")
        self.assertIn("28,915,600 cost units", aborted_record)
        self.assertIn("9379919939", aborted_record)
        tariff = self.plan["frozen_config"]["token_tariff"]
        self.assertEqual(
            ABORTED_RUN_MODEL_COST_UNITS,
            126_468 * tariff["input_cents_per_million_tokens"]
            + 3_622 * tariff["output_cents_per_million_tokens"],
        )

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
        self.assertEqual(
            result["model_cost_units"],
            ABORTED_RUN_MODEL_COST_UNITS + 18_000_000,
        )
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

    def test_prior_failed_attempt_cost_is_debited_from_aggregate_cap(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            result = self.runner(directory).run(max_cells=18)
            with patch(
                "capage.homeostasis_v2_active_runner.ABORTED_RUN_MODEL_COST_UNITS",
                ABORTED_RUN_MODEL_COST_UNITS + 1,
            ):
                with self.assertRaisesRegex(ValueError, "prior model cost mismatch"):
                    self.runner(directory)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(
            result["prior_model_cost_units"], ABORTED_RUN_MODEL_COST_UNITS
        )
        self.assertEqual(result["prior_cost_reference"], ABORTED_RUN_COST_REFERENCE)
        self.assertEqual(
            result["model_cost_units"],
            ABORTED_RUN_MODEL_COST_UNITS + 18_000_000,
        )

    def test_prior_cost_can_reduce_a_cell_cap_and_prevent_overspend(self):
        prior = 1_349_000_000
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ), patch(
            "capage.homeostasis_v2_active_runner.ABORTED_RUN_MODEL_COST_UNITS",
            prior,
        ), patch(
            "capage.homeostasis_v2_active_runner.ABORTED_RUN_COST_REFERENCE",
            "test-near-ceiling",
        ):
            result = self.runner(directory).run(max_cells=18)

        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["stop_reason"], "aggregate_model_cost_cap_reached")
        self.assertEqual(result["model_cost_units"], 1_350_000_000)
        self.assertEqual(len(result["completed_cells"]), 1)
        self.assertEqual(FakeCellRunner.calls[0]["starting_capital_cents"], 25_000)
        self.assertEqual(FakeCellRunner.calls[0]["max_run_cost_cents"], 1)

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

    def test_result_binds_full_config_not_internal_world_id(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            runner = self.runner(directory)
            config = runner._run_config(1, "v2", 123, 25_000, 75)
            result = FakeV2Runner(
                config,
                object(),
                audit_path=Path(directory) / "audit.jsonl",
                continuity_state={"history": []},
            ).run()
            self.assertNotEqual(result["outcome"]["run_id"], config.run_name)
            runner._validate_result(result, config)

            result["config"]["seed"] += 1
            with self.assertRaisesRegex(ValueError, "serialized config"):
                runner._validate_result(result, config)

    def test_result_rejects_token_cost_accounting_mismatch(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_v2_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            runner = self.runner(directory)
            config = runner._run_config(1, "v2", 123, 25_000, 75)
            result = FakeV2Runner(
                config,
                object(),
                audit_path=Path(directory) / "audit.jsonl",
                continuity_state={"history": []},
            ).run()
            result["outcome"]["model_input_tokens"] += 1
            with self.assertRaisesRegex(ValueError, "token totals"):
                runner._validate_result(result, config)

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
