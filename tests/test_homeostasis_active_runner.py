import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from capage.homeostasis_active_runner import (
    ActiveConfig,
    ActiveHomeostasisRunner,
    CONFIRMATION,
)
from capage.homeostasis_experiment import make_treatment_runner_class


class FakeCellRunner:
    requests = []

    def __init__(self, config, client, *, audit_path, continuity_state):
        self.config = config
        self.continuity_state = continuity_state

    def _request_body(self, decision_index):
        return {"system": "frozen baseline", "messages": [{"decision": decision_index}]}

    def run(self):
        type(self).requests.append(self._request_body(1))
        starting = self.config.starting_capital_cents
        balance = starting - 1
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
            },
            "business_continuity": self.continuity_state,
            "world_reveal": {"journal": journal},
        }


def fake_config_factory(**kwargs):
    kwargs.pop("tariff_name")
    kwargs.pop("input_cents_per_million_tokens")
    kwargs.pop("output_cents_per_million_tokens")
    return SimpleNamespace(**kwargs)


class ActiveRunnerGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).parents[1]
        cls.plan = json.loads(
            (root / "experiments" / "sandbox" / "economic_homeostasis_active_plan_v1.json").read_text(encoding="utf-8")
        )
        cls.authorization = (
            root / "experiments" / "sandbox" / "HOMEOSTASIS_ACTIVE_V1_AUTHORIZATION.md"
        ).read_text(encoding="utf-8")

    def test_authorization_is_exact_and_budget_bounded(self):
        self.assertIn(f"\n{CONFIRMATION}\n", self.authorization)
        config = ActiveConfig.from_plan(self.plan)
        self.assertEqual(config.aggregate_cost_cap_cents, 900)
        self.assertEqual(config.per_cell_cost_cap_cents, 75)

    def test_plan_still_denies_execution_and_workflow_authority(self):
        self.assertFalse(self.plan["provider_calls_authorized"])
        self.assertFalse(self.plan["spend_authorized"])
        self.assertFalse(self.plan["workflow_present"])

    def test_fake_full_run_is_checkpointed_lagged_and_prompt_isolated(self):
        FakeCellRunner.requests = []
        treatment = make_treatment_runner_class(FakeCellRunner)
        with tempfile.TemporaryDirectory() as directory, patch(
            "capage.homeostasis_active_runner.implementation_commitments",
            return_value={"test": "frozen"},
        ):
            runner = ActiveHomeostasisRunner(
                self.plan,
                object(),
                checkpoint_path=Path(directory) / "checkpoint.json",
                artifact_dir=Path(directory) / "cells",
                control_runner_factory=FakeCellRunner,
                treatment_runner_factory=treatment,
                run_config_factory=fake_config_factory,
                empty_continuity_factory=lambda: {"schema_version": "test"},
            )
            result = runner.run(max_cells=12)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["completed_cells"]), 12)
        self.assertEqual(result["model_cost_units"], 12_000_000)
        treatment_requests = [
            request for request in treatment.requests
            if "ECONOMIC HOMEOSTASIS" in request["system"]
        ]
        control_requests = [
            request for request in FakeCellRunner.requests
            if request["system"] == "frozen baseline"
        ]
        self.assertEqual(len(treatment_requests), 6)
        self.assertEqual(len(control_requests), 6)
        self.assertIn("productive_urgency: high", treatment_requests[1]["system"])


if __name__ == "__main__":
    unittest.main()
