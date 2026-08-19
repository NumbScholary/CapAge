import json
from itertools import permutations
from pathlib import Path
import unittest

from capage.homeostasis import UrgencyLevel
from capage.homeostasis_v2 import VerificationRequirement
from capage.homeostasis_v2_experiment import (
    ARMS,
    completed_v2_signal,
    derive_triplet_specs,
    materialize_matched_worlds,
    signal_for_arm_start,
    starting_v2_signal,
    validate_plan,
)
from capage.sandbox import EconomicSandbox, TokenTariff


def completed_result(*, disputed=False, dissatisfied=False):
    journal = [
        {
            "sequence": 1,
            "day": 0,
            "event_type": "ledger_posted",
            "data": {
                "sequence": 1,
                "day": 0,
                "entry_type": "owner_capital",
                "amount_cents": 25000,
                "balance_cents": 25000,
                "memo": "Initial capital.",
                "reference": "initial-capital",
            },
        },
        {
            "sequence": 2,
            "day": 1,
            "event_type": "ledger_posted",
            "data": {
                "sequence": 2,
                "day": 1,
                "entry_type": "model_api_cost",
                "amount_cents": -1,
                "balance_cents": 24999,
                "memo": "Model usage.",
                "reference": "call-001",
            },
        },
    ]
    if disputed:
        journal.extend(
            [
                {
                    "sequence": 3,
                    "day": 2,
                    "event_type": "offer_accepted",
                    "data": {"contract_id": "contract-001"},
                },
                {
                    "sequence": 4,
                    "day": 3,
                    "event_type": "delivery_assessed",
                    "data": {
                        "contract_id": "contract-001",
                        "status": "disputed",
                    },
                },
            ]
        )
    if dissatisfied:
        journal.append(
            {
                "sequence": len(journal) + 1,
                "day": 4,
                "event_type": "feedback_received",
                "data": {
                    "contract_id": "contract-001",
                    "rating": "dissatisfied",
                },
            }
        )
    return {
        "schema_version": "capage-live-sandbox-result-v1",
        "transcript": [
            {
                "decision": 1,
                "day_before_action": 0,
                "day_after_action": 1,
                "host_tool_name": "sandbox.search_market",
            }
        ],
        "outcome": {
            "run_id": "v2-test-result",
            "day": 30,
            "balance_cents": 24999,
            "earned_revenue_cents": 0,
            "expense_cents": 1,
            "open_obligations": 0,
            "contracts_disputed": int(disputed),
        },
        "world_reveal": {"journal": journal},
    }


class ThreeArmPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(
            (
                Path(__file__).parents[1]
                / "experiments"
                / "sandbox"
                / "economic_homeostasis_v2_prereg_v1.json"
            ).read_text(encoding="utf-8")
        )

    def test_seeds_and_orders_are_frozen_and_balanced(self):
        specs = derive_triplet_specs()
        self.assertEqual(len(specs), 6)
        self.assertEqual(len({spec.world_seed for spec in specs}), 6)
        self.assertEqual(
            {spec.execution_order for spec in specs},
            set(permutations(ARMS)),
        )
        self.assertEqual(
            self.plan["pairs"],
            [spec.to_dict() for spec in specs],
        )

    def test_plan_is_unpaid_and_budget_is_exact(self):
        validate_plan(self.plan)
        self.assertFalse(self.plan["provider_calls_authorized"])
        self.assertFalse(self.plan["spend_authorized"])
        self.assertFalse(self.plan["workflow_present"])
        self.assertEqual(self.plan["maximum_budget"]["cells"], 18)
        self.assertEqual(
            self.plan["maximum_budget"]["provider_cost_cap_cents"],
            1350,
        )

    def test_all_three_arms_materialize_identical_worlds(self):
        tariff_data = self.plan["frozen_config"]["token_tariff"]
        tariff = TokenTariff(
            tariff_data["name"],
            tariff_data["input_cents_per_million_tokens"],
            tariff_data["output_cents_per_million_tokens"],
        )

        def factory(seed, **kwargs):
            return EconomicSandbox(seed, token_tariff=tariff, **kwargs)

        records = materialize_matched_worlds(self.plan, factory)
        self.assertEqual(len(records), 6)
        self.assertTrue(all(record["arms_equal"] for record in records))

    def test_starting_signals_keep_control_unexposed(self):
        self.assertIsNone(signal_for_arm_start("control"))
        self.assertEqual(
            signal_for_arm_start("v1").urgency,
            UrgencyLevel.ROUTINE,
        )
        v2 = signal_for_arm_start("v2")
        self.assertEqual(v2.opportunity_urgency, UrgencyLevel.ROUTINE)
        self.assertEqual(
            v2.verification_requirement,
            VerificationRequirement.STANDARD,
        )

    def test_completed_v2_quality_failure_raises_verification_not_hunger(self):
        starting = starting_v2_signal()
        signal = completed_v2_signal(
            completed_result(disputed=True, dissatisfied=True),
            starting.next_history,
        )
        self.assertEqual(
            signal.verification_requirement,
            VerificationRequirement.STRICT,
        )
        self.assertEqual(signal.opportunity_urgency, UrgencyLevel.ELEVATED)
        self.assertTrue(signal.customer_repair_advised)


if __name__ == "__main__":
    unittest.main()
