"""Tests for PolicyEngine's tool authorization and cost-cap checks."""

from __future__ import annotations

import unittest

from capage.models import ProposedAction
from capage.policy import PolicyEngine


def _action(**overrides: object) -> ProposedAction:
    fields = {
        "action_type": "test",
        "tool_name": "echo",
        "estimated_cost_cents": 0,
    }
    fields.update(overrides)
    return ProposedAction(**fields)  # type: ignore[arg-type]


class PolicyEngineToolAuthorizationTests(unittest.TestCase):
    """No-cap behavior must be unchanged from before this field existed."""

    def test_allowed_tool_with_no_caps_set_is_approved(self) -> None:
        engine = PolicyEngine({"echo"})
        decision = engine.evaluate(_action())
        self.assertTrue(decision.allowed)

    def test_disallowed_tool_is_denied_regardless_of_cost_fields(self) -> None:
        engine = PolicyEngine({"echo"})
        decision = engine.evaluate(_action(tool_name="send_money"))
        self.assertFalse(decision.allowed)
        self.assertIn("not authorized", decision.reason)

    def test_missing_action_type_is_denied_before_cost_is_checked(self) -> None:
        engine = PolicyEngine({"echo"}, per_action_cap_cents=0)
        decision = engine.evaluate(_action(action_type="  ", estimated_cost_cents=1000))
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "Missing action type.")


class PolicyEngineCostValidationTests(unittest.TestCase):
    def test_negative_estimated_cost_is_denied(self) -> None:
        engine = PolicyEngine({"echo"})
        decision = engine.evaluate(_action(estimated_cost_cents=-1))
        self.assertFalse(decision.allowed)
        self.assertIn("cannot be negative", decision.reason)

    def test_non_integer_estimated_cost_is_denied(self) -> None:
        engine = PolicyEngine({"echo"})
        decision = engine.evaluate(_action(estimated_cost_cents=1.5))  # type: ignore[arg-type]
        self.assertFalse(decision.allowed)
        self.assertIn("must be an integer", decision.reason)

    def test_bool_estimated_cost_is_denied(self) -> None:
        # bool is a subclass of int in Python; must be rejected explicitly,
        # matching the same guard pattern used elsewhere in this codebase
        # (e.g. capage.homeostasis._nonnegative_int).
        engine = PolicyEngine({"echo"})
        decision = engine.evaluate(_action(estimated_cost_cents=True))  # type: ignore[arg-type]
        self.assertFalse(decision.allowed)
        self.assertIn("must be an integer", decision.reason)


class PolicyEnginePerActionCapTests(unittest.TestCase):
    def test_estimate_at_the_cap_is_approved(self) -> None:
        engine = PolicyEngine({"echo"}, per_action_cap_cents=500)
        decision = engine.evaluate(_action(estimated_cost_cents=500))
        self.assertTrue(decision.allowed)

    def test_estimate_over_the_cap_is_denied(self) -> None:
        engine = PolicyEngine({"echo"}, per_action_cap_cents=500)
        decision = engine.evaluate(_action(estimated_cost_cents=501))
        self.assertFalse(decision.allowed)
        self.assertIn("per-action cap", decision.reason)

    def test_none_cap_never_denies_on_cost_alone(self) -> None:
        engine = PolicyEngine({"echo"}, per_action_cap_cents=None)
        decision = engine.evaluate(_action(estimated_cost_cents=1_000_000))
        self.assertTrue(decision.allowed)


class PolicyEnginePerRunCapTests(unittest.TestCase):
    def test_running_total_accumulates_across_approved_actions(self) -> None:
        engine = PolicyEngine({"echo"}, per_run_cap_cents=1000)
        self.assertEqual(engine.spent_cents, 0)

        first = engine.evaluate(_action(estimated_cost_cents=400))
        self.assertTrue(first.allowed)
        self.assertEqual(engine.spent_cents, 400)

        second = engine.evaluate(_action(estimated_cost_cents=400))
        self.assertTrue(second.allowed)
        self.assertEqual(engine.spent_cents, 800)

    def test_action_that_would_cross_the_per_run_cap_is_denied(self) -> None:
        engine = PolicyEngine({"echo"}, per_run_cap_cents=1000)
        engine.evaluate(_action(estimated_cost_cents=800))

        decision = engine.evaluate(_action(estimated_cost_cents=300))

        self.assertFalse(decision.allowed)
        self.assertIn("per-run cap", decision.reason)
        # A denied action must not be added to the running total.
        self.assertEqual(engine.spent_cents, 800)

    def test_denied_action_does_not_increment_spent_cents(self) -> None:
        engine = PolicyEngine({"echo"}, per_action_cap_cents=100)
        engine.evaluate(_action(estimated_cost_cents=101))
        self.assertEqual(engine.spent_cents, 0)

    def test_two_independent_engines_track_separate_totals(self) -> None:
        # One PolicyEngine instance is expected to correspond to one run;
        # confirm nothing is shared as class-level mutable state.
        engine_a = PolicyEngine({"echo"}, per_run_cap_cents=1000)
        engine_b = PolicyEngine({"echo"}, per_run_cap_cents=1000)

        engine_a.evaluate(_action(estimated_cost_cents=900))

        self.assertEqual(engine_a.spent_cents, 900)
        self.assertEqual(engine_b.spent_cents, 0)


class ProposedActionDefaultTests(unittest.TestCase):
    def test_estimated_cost_cents_defaults_to_zero(self) -> None:
        action = ProposedAction(action_type="test", tool_name="echo")
        self.assertEqual(action.estimated_cost_cents, 0)


if __name__ == "__main__":
    unittest.main()
