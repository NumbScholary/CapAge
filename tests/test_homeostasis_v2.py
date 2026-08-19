import json
import unittest

from capage.homeostasis import (
    EconomicFacts,
    EconomicStateProjector,
    ExpenseBehavior,
    ExpenseOrigin,
    ExpenseRecord,
    ExpenseStatus,
    UrgencyLevel,
)
from capage.homeostasis_v2 import (
    HomeostasisControllerV2,
    QualityFacts,
    VerificationRequirement,
    quality_facts_from_result,
    validate_objective_delivery,
)
from capage.homeostasis_v2_runner import (
    HomeostasisV2SandboxRunner,
    render_homeostasis_v2_block,
)


def state(*, open_obligations=0, liquid=25_000, peak=25_000):
    facts = EconomicFacts(
        as_of_cycle=30,
        liquid_resources_cents=liquid,
        peak_continuity_resources_cents=peak,
        last_external_action_cycle=0,
        last_external_value_cycle=0,
        open_obligations=open_obligations,
    )
    forecast = ExpenseRecord(
        expense_id="native-forecast",
        origin=ExpenseOrigin.NATIVE,
        behavior=ExpenseBehavior.USAGE,
        status=ExpenseStatus.FORECAST,
        cash_cents=33,
    )
    return EconomicStateProjector.project(facts, (forecast,))


def brief():
    return {
        "schema_version": "capage-customer-task-v1",
        "brief_id": "brief-1",
        "source_records": [
            {
                "record_id": "option-1",
                "label": "One",
                "value_points": 50,
                "cost_points": 20,
                "risk_points": 5,
            },
            {
                "record_id": "option-2",
                "label": "Two",
                "value_points": 60,
                "cost_points": 10,
                "risk_points": 4,
            },
        ],
    }


def artifact(*, first_score=75, second_score=106):
    return json.dumps(
        {
            "brief_id": "brief-1",
            "record_evaluations": [
                {"record_id": "option-1", "computed_score": first_score},
                {"record_id": "option-2", "computed_score": second_score},
            ],
            "recommended_record_id": "option-2",
            "customer_summary": "Option Two has the strongest verified score.",
            "implementation_steps": ["Confirm the selection.", "Begin the work."],
        },
        sort_keys=True,
    )


class HomeostasisControllerV2Tests(unittest.TestCase):
    def test_stable_inactivity_cannot_create_high_opportunity_urgency(self):
        signal = HomeostasisControllerV2().assess(state())
        self.assertEqual(signal.base.urgency, UrgencyLevel.HIGH)
        self.assertEqual(signal.opportunity_urgency, UrgencyLevel.ELEVATED)
        self.assertEqual(signal.obligation_urgency, UrgencyLevel.ROUTINE)

    def test_open_obligation_controls_priority_and_review_depth(self):
        signal = HomeostasisControllerV2().assess(state(open_obligations=1))
        self.assertEqual(signal.obligation_urgency, UrgencyLevel.HIGH)
        self.assertEqual(
            signal.verification_requirement,
            VerificationRequirement.HEIGHTENED,
        )
        self.assertEqual(
            signal.priority_profile,
            "complete_and_verify_existing_obligations_before_new_commitments",
        )

    def test_quality_failure_increases_verification_not_opportunity_pressure(self):
        signal = HomeostasisControllerV2().assess(
            state(),
            QualityFacts(recent_disputes=1, recent_dissatisfied_feedback=1),
        )
        self.assertEqual(signal.opportunity_urgency, UrgencyLevel.ELEVATED)
        self.assertEqual(
            signal.verification_requirement,
            VerificationRequirement.STRICT,
        )
        self.assertTrue(signal.customer_repair_advised)
        self.assertIn("recent_delivery_dispute", signal.quality_reason_codes)

    def test_quality_projection_uses_host_journal(self):
        result = {
            "outcome": {"contracts_disputed": 2},
            "world_reveal": {
                "journal": [
                    {
                        "event_type": "feedback_received",
                        "data": {"rating": "dissatisfied"},
                    },
                    {
                        "event_type": "feedback_received",
                        "data": {"rating": "satisfied"},
                    },
                ]
            },
        }
        self.assertEqual(
            quality_facts_from_result(result),
            QualityFacts(recent_disputes=2, recent_dissatisfied_feedback=1),
        )


class ObjectiveDeliveryValidationTests(unittest.TestCase):
    def test_exact_delivery_passes(self):
        result = validate_objective_delivery(artifact(), brief())
        self.assertTrue(result.applicable)
        self.assertTrue(result.valid)
        self.assertEqual(result.error_codes, ())

    def test_wrong_arithmetic_is_rejected_without_supplying_answer(self):
        result = validate_objective_delivery(
            artifact(first_score=71),
            brief(),
        )
        self.assertFalse(result.valid)
        self.assertIn("calculation_mismatch:option-1", result.error_codes)
        self.assertNotIn("75", json.dumps(result.to_tool_result()))

    def test_subjective_or_unsupported_brief_passes_through(self):
        result = validate_objective_delivery("free-form work", None)
        self.assertTrue(result.valid)
        self.assertFalse(result.applicable)

    def test_bad_schema_and_recommendation_are_rejected(self):
        payload = json.loads(artifact())
        payload["recommended_record_id"] = "option-1"
        payload["extra"] = "not requested"
        result = validate_objective_delivery(json.dumps(payload), brief())
        self.assertFalse(result.valid)
        self.assertIn("delivery_schema_mismatch", result.error_codes)
        self.assertIn("recommendation_mismatch", result.error_codes)


class _FakeWorld:
    def __init__(self):
        self.submissions = []

    def observe(self):
        return {
            "contracts": [
                {
                    "contract_id": "contract-001",
                    "status": "accepted",
                    "delivery_brief": brief(),
                }
            ]
        }

    def submit_delivery(self, arguments):
        self.submissions.append(arguments)
        return {"ok": True, "delivery_id": "delivery-001"}


class HomeostasisV2RunnerBoundaryTests(unittest.TestCase):
    def runner(self):
        runner = object.__new__(HomeostasisV2SandboxRunner)
        runner.world = _FakeWorld()
        runner._rejected_delivery_attempts = {}
        return runner

    def test_invalid_work_never_crosses_delivery_boundary(self):
        runner = self.runner()
        result = runner._validated_submit_delivery(
            {
                "contract_id": "contract-001",
                "artifact": artifact(first_score=71),
            }
        )
        self.assertFalse(result["ok"])
        self.assertTrue(result["retryable"])
        self.assertEqual(runner.world.submissions, [])
        self.assertEqual(runner._rejected_delivery_attempts["contract-001"], 1)

    def test_corrected_work_crosses_boundary(self):
        runner = self.runner()
        result = runner._validated_submit_delivery(
            {"contract_id": "contract-001", "artifact": artifact()}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(len(runner.world.submissions), 1)
        self.assertTrue(result["objective_validation"]["valid"])

    def test_dynamic_block_prioritizes_open_obligation(self):
        signal = HomeostasisControllerV2().assess(state())
        block = render_homeostasis_v2_block(signal, open_obligations=1)
        self.assertIn("obligation_urgency: high", block)
        self.assertIn(
            "priority_profile: complete_and_verify_existing_obligations_before_new_commitments",
            block,
        )


if __name__ == "__main__":
    unittest.main()
