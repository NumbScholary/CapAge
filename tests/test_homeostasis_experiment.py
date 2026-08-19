import json
from pathlib import Path
import unittest

try:
    from capage.sandbox import EconomicSandbox, TokenTariff
except ImportError:  # The focused scratch harness carries only new modules.
    EconomicSandbox = None
    TokenTariff = None

from capage.homeostasis import HomeostasisSignal
from capage.homeostasis_experiment import (
    PREREGISTRATION_MERGE_SHA,
    completed_period_signal,
    derive_pair_specs,
    inject_treatment_block,
    make_treatment_runner_class,
    materialize_matched_worlds,
    render_treatment_block,
    starting_signal,
    validate_plan,
    verify_only_treatment_difference,
)


class FakeWorld:
    mutate_treatment = False
    calls = 0

    def __init__(self, seed, **kwargs):
        type(self).calls += 1
        arm_mutation = type(self).mutate_treatment and type(self).calls % 2 == 0
        self.payload = {"seed": seed, **kwargs, "mutated": arm_mutation}

    def reveal_world(self):
        payload = dict(self.payload)
        return {
            "payload": payload,
            "world_commitment": "world-" + str(payload["seed"]),
            "cost_policy_commitment": "same-policy",
        }


class FakeBaseRunner:
    calls = 0

    def __init__(self, marker):
        self.marker = marker

    def _request_body(self, decision_index):
        FakeBaseRunner.calls += 1
        return {
            "system": "frozen baseline",
            "model": "test-model",
            "messages": [{"decision": decision_index, "marker": self.marker}],
        }


class ActiveExperimentPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = (
            Path(__file__).parents[1]
            / "experiments"
            / "sandbox"
            / "economic_homeostasis_active_plan_v1.json"
        )
        cls.plan = json.loads(cls.manifest_path.read_text(encoding="utf-8"))

    def setUp(self):
        FakeWorld.calls = 0
        FakeWorld.mutate_treatment = False
        FakeBaseRunner.calls = 0

    def test_merge_beacon_mechanically_fixes_all_seeds_and_orders(self):
        pairs = derive_pair_specs(PREREGISTRATION_MERGE_SHA)
        self.assertEqual(len(pairs), 6)
        self.assertEqual(len({pair.world_seed for pair in pairs}), 6)
        self.assertEqual([pair.to_dict() for pair in pairs], self.plan["pairs"])
        self.assertEqual(pairs[3].execution_order, ("treatment", "control"))

    def test_plan_is_unpaid_and_budget_is_complete(self):
        validate_plan(self.plan)
        self.assertFalse(self.plan["provider_calls_authorized"])
        self.assertFalse(self.plan["spend_authorized"])
        self.assertFalse(self.plan["workflow_present"])
        self.assertEqual(self.plan["maximum_budget"]["provider_cost_cap_cents"], 900)
        self.assertIsNone(self.plan["maximum_budget"]["hosting_cash_cents"])

    def test_world_materialization_proves_arm_equality(self):
        records = materialize_matched_worlds(self.plan, FakeWorld)
        self.assertEqual(len(records), 6)
        self.assertEqual(FakeWorld.calls, 12)
        self.assertTrue(all(record["arms_equal"] for record in records))

    def test_world_materialization_rejects_mismatch(self):
        FakeWorld.mutate_treatment = True
        with self.assertRaisesRegex(ValueError, "exogenous world mismatch"):
            materialize_matched_worlds(self.plan, FakeWorld)

    @unittest.skipIf(EconomicSandbox is None, "full repository sandbox unavailable")
    def test_real_sandbox_materializes_identical_exogenous_worlds(self):
        tariff_payload = self.plan["frozen_config"]["token_tariff"]
        tariff = TokenTariff(
            tariff_payload["name"],
            tariff_payload["input_cents_per_million_tokens"],
            tariff_payload["output_cents_per_million_tokens"],
        )

        def factory(seed, **kwargs):
            return EconomicSandbox(seed, token_tariff=tariff, **kwargs)

        records = materialize_matched_worlds(self.plan, factory)
        self.assertEqual(len({row["exogenous_world_sha256"] for row in records}), 6)
        self.assertTrue(all(row["arms_equal"] for row in records))

    def test_starting_signal_and_prompt_are_bounded_without_exposure(self):
        signal = starting_signal()
        self.assertIsInstance(signal, HomeostasisSignal)
        self.assertEqual(signal.mode.value, "stable")
        self.assertEqual(signal.urgency.value, "routine")
        self.assertEqual(signal.irreversible_loss_tolerance.value, "bounded")
        block = render_treatment_block(signal)
        self.assertIn("Greater urgency never increases permissible", block)
        self.assertIn("not authority or a reserve rule", block)
        self.assertNotIn("preferred_irreversible_exposure", block)

    def test_request_adapter_changes_only_exact_system_suffix(self):
        signal = starting_signal()
        control = {
            "system": "frozen baseline",
            "messages": [{"role": "user", "content": "unchanged"}],
            "tools": [{"name": "sandbox.observe"}],
        }
        treatment = inject_treatment_block(control, signal)
        self.assertEqual(control["system"], "frozen baseline")
        self.assertTrue(verify_only_treatment_difference(control, treatment, signal))
        self.assertEqual(treatment["messages"], control["messages"])
        self.assertEqual(treatment["tools"], control["tools"])

    def test_runner_adapter_calls_baseline_builder_once(self):
        treatment_class = make_treatment_runner_class(FakeBaseRunner)
        runner = treatment_class("marker", homeostasis_signal=starting_signal())
        request = runner._request_body(3)
        self.assertEqual(FakeBaseRunner.calls, 1)
        self.assertEqual(request["messages"][0]["marker"], "marker")
        self.assertIn("ECONOMIC HOMEOSTASIS", request["system"])

    def test_completed_period_path_rejects_non_result_instead_of_guessing(self):
        with self.assertRaises(Exception):
            completed_period_signal(
                {"status": "not-a-completed-sandbox-result"},
                starting_signal().next_history,
                observation_id="pair-01-treatment-period-01",
            )


if __name__ == "__main__":
    unittest.main()
