"""Invariant tests for the pure Economic Homeostasis v1 controller."""

from dataclasses import FrozenInstanceError
import unittest

from capage.homeostasis import (
    ControllerHistory,
    EconomicFacts,
    EconomicMode,
    EconomicStateProjector,
    ExpenseBehavior,
    ExpenseOrigin,
    ExpenseRecord,
    ExpenseStatus,
    HomeostasisConfig,
    HomeostasisController,
    LossTolerance,
    ReasonCode,
    SustainabilityStatus,
    UrgencyLevel,
)


def expense(
    expense_id: str,
    *,
    origin: ExpenseOrigin = ExpenseOrigin.NATIVE,
    behavior: ExpenseBehavior = ExpenseBehavior.USAGE,
    status: ExpenseStatus = ExpenseStatus.SETTLED,
    cash_cents: int = 0,
    imputed_cents: int = 0,
) -> ExpenseRecord:
    return ExpenseRecord(
        expense_id=expense_id,
        origin=origin,
        behavior=behavior,
        status=status,
        cash_cents=cash_cents,
        imputed_cents=imputed_cents,
    )


def facts(**overrides: object) -> EconomicFacts:
    values: dict[str, object] = {
        "as_of_cycle": 1,
        "liquid_resources_cents": 25_000,
        "earned_revenue_cents": 0,
        "cash_received_cents": 0,
        "peak_continuity_resources_cents": 25_000,
        "last_external_action_cycle": 1,
        "last_external_value_cycle": 1,
        "has_path_to_next_value_action": True,
    }
    values.update(overrides)
    return EconomicFacts(**values)  # type: ignore[arg-type]


class ExpenseProjectionTests(unittest.TestCase):
    def test_expense_validation_rejects_negative_and_boolean_amounts(self) -> None:
        with self.assertRaises(ValueError):
            expense("negative", cash_cents=-1)
        with self.assertRaises(TypeError):
            expense("boolean", cash_cents=True)  # type: ignore[arg-type]

    def test_projection_requires_unique_expense_ids(self) -> None:
        record = expense("same")
        with self.assertRaises(ValueError):
            EconomicStateProjector.project(facts(), (record, record))

    def test_projection_classifies_native_strategy_cash_and_imputed_cost(self) -> None:
        records = (
            expense("native-paid", cash_cents=5),
            expense(
                "strategy-paid",
                origin=ExpenseOrigin.STRATEGY,
                cash_cents=7,
            ),
            expense(
                "overseer-time",
                behavior=ExpenseBehavior.USAGE,
                cash_cents=0,
                imputed_cents=40,
            ),
            expense(
                "hosting-forecast",
                behavior=ExpenseBehavior.RECURRING,
                status=ExpenseStatus.FORECAST,
                cash_cents=20,
                imputed_cents=3,
            ),
            expense(
                "marketplace-forecast",
                origin=ExpenseOrigin.STRATEGY,
                behavior=ExpenseBehavior.RECURRING,
                status=ExpenseStatus.FORECAST,
                cash_cents=10,
            ),
            expense(
                "marketplace-committed",
                origin=ExpenseOrigin.STRATEGY,
                behavior=ExpenseBehavior.RECURRING,
                status=ExpenseStatus.COMMITTED,
                cash_cents=30,
            ),
            expense(
                "invoice-due",
                origin=ExpenseOrigin.STRATEGY,
                status=ExpenseStatus.INCURRED,
                cash_cents=11,
            ),
        )
        state = EconomicStateProjector.project(facts(), records)
        self.assertEqual(state.settled_native_cash_cents, 5)
        self.assertEqual(state.settled_strategy_cash_cents, 7)
        self.assertEqual(state.settled_imputed_cents, 40)
        self.assertEqual(state.full_cost_cents, 52)
        self.assertEqual(state.forecast_native_cash_cents, 20)
        self.assertEqual(state.forecast_native_imputed_cents, 3)
        self.assertEqual(state.forecast_strategy_cash_cents, 10)
        self.assertEqual(state.committed_future_cash_cents, 30)
        self.assertEqual(state.due_obligations_cents, 11)
        self.assertEqual(state.cash_continuity_margin_cents, 24_939)

    def test_proposed_and_authorized_costs_are_not_commitments(self) -> None:
        state = EconomicStateProjector.project(
            facts(),
            (
                expense(
                    "proposed",
                    origin=ExpenseOrigin.STRATEGY,
                    status=ExpenseStatus.PROPOSED,
                    cash_cents=20_000,
                ),
                expense(
                    "authorized",
                    origin=ExpenseOrigin.STRATEGY,
                    status=ExpenseStatus.AUTHORIZED,
                    cash_cents=3_000,
                ),
            ),
        )
        self.assertEqual(state.committed_future_cash_cents, 0)
        self.assertEqual(state.due_obligations_cents, 0)
        self.assertEqual(state.cash_continuity_margin_cents, 25_000)

    def test_imputed_labor_does_not_reduce_cash_continuity(self) -> None:
        without_labor = EconomicStateProjector.project(facts())
        with_labor = EconomicStateProjector.project(
            facts(),
            (expense("volunteer", imputed_cents=10_000),),
        )
        self.assertEqual(
            without_labor.cash_continuity_margin_cents,
            with_labor.cash_continuity_margin_cents,
        )
        self.assertEqual(with_labor.full_cost_cents, 10_000)

    def test_value_revenue_and_cash_remain_distinct(self) -> None:
        state = EconomicStateProjector.project(
            facts(
                external_value_events=2,
                earned_revenue_cents=8_000,
                cash_received_cents=3_000,
            )
        )
        self.assertEqual(state.external_value_events, 2)
        self.assertEqual(state.earned_revenue_cents, 8_000)
        self.assertEqual(state.cash_received_cents, 3_000)

    def test_owner_injection_disqualifies_strict_run_but_is_not_revenue(self) -> None:
        state = EconomicStateProjector.project(
            facts(post_start_owner_injection_cents=500)
        )
        self.assertTrue(state.strict_run_disqualified)
        self.assertEqual(state.earned_revenue_cents, 0)


class ControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = HomeostasisController()

    def test_stable_state_is_routine_and_bounded(self) -> None:
        state = EconomicStateProjector.project(
            facts(),
            (
                expense(
                    "native-forecast",
                    status=ExpenseStatus.FORECAST,
                    cash_cents=1_000,
                ),
            ),
        )
        signal = self.controller.assess(state)
        self.assertEqual(signal.mode, EconomicMode.STABLE)
        self.assertEqual(signal.urgency, UrgencyLevel.ROUTINE)
        self.assertEqual(
            signal.irreversible_loss_tolerance,
            LossTolerance.BOUNDED,
        )
        self.assertTrue(signal.advisory_only)
        self.assertTrue(signal.any_exposure_remains_proposable)

    def test_coverage_modes_are_configurable_and_deterministic(self) -> None:
        forecast = (
            expense(
                "native-forecast",
                status=ExpenseStatus.FORECAST,
                cash_cents=10_000,
            ),
        )
        watch = self.controller.assess(
            EconomicStateProjector.project(
                facts(
                    liquid_resources_cents=30_000,
                    peak_continuity_resources_cents=30_000,
                ),
                forecast,
            )
        )
        recovery = self.controller.assess(
            EconomicStateProjector.project(
                facts(
                    liquid_resources_cents=15_000,
                    peak_continuity_resources_cents=15_000,
                ),
                forecast,
            )
        )
        critical = self.controller.assess(
            EconomicStateProjector.project(
                facts(
                    liquid_resources_cents=5_000,
                    peak_continuity_resources_cents=5_000,
                ),
                forecast,
            )
        )
        self.assertEqual(watch.mode, EconomicMode.WATCH)
        self.assertEqual(recovery.mode, EconomicMode.RECOVERY)
        self.assertEqual(critical.mode, EconomicMode.CRITICAL)

    def test_drawdown_can_raise_pressure_without_a_fixed_reserve(self) -> None:
        state = EconomicStateProjector.project(
            facts(
                liquid_resources_cents=12_000,
                peak_continuity_resources_cents=25_000,
            )
        )
        signal = self.controller.assess(state)
        self.assertEqual(signal.mode, EconomicMode.CRITICAL)
        self.assertIn(ReasonCode.DRAWDOWN, signal.reason_codes)
        self.assertTrue(signal.any_exposure_remains_proposable)

    def test_dormancy_increases_urgency_but_not_loss_tolerance(self) -> None:
        active = self.controller.assess(
            EconomicStateProjector.project(
                facts(
                    as_of_cycle=20,
                    last_external_action_cycle=20,
                    last_external_value_cycle=20,
                )
            )
        )
        dormant = self.controller.assess(
            EconomicStateProjector.project(
                facts(
                    as_of_cycle=20,
                    last_external_action_cycle=1,
                    last_external_value_cycle=1,
                )
            )
        )
        self.assertEqual(active.urgency, UrgencyLevel.ROUTINE)
        self.assertEqual(dormant.urgency, UrgencyLevel.HIGH)
        self.assertEqual(
            active.irreversible_loss_tolerance,
            dormant.irreversible_loss_tolerance,
        )
        self.assertIn(ReasonCode.PRODUCTIVE_DORMANCY, dormant.reason_codes)

    def test_imputed_cost_changes_sustainability_not_cash_pressure(self) -> None:
        base_facts = facts(earned_revenue_cents=100)
        no_labor = self.controller.assess(
            EconomicStateProjector.project(base_facts)
        )
        with_labor = self.controller.assess(
            EconomicStateProjector.project(
                base_facts,
                (expense("overseer", imputed_cents=500),),
            )
        )
        self.assertEqual(no_labor.mode, with_labor.mode)
        self.assertEqual(
            no_labor.sustainability_pressure,
            SustainabilityStatus.UNKNOWN,
        )
        self.assertEqual(
            with_labor.sustainability_pressure,
            SustainabilityStatus.PARTIAL,
        )

    def test_unpayable_due_obligation_is_functional_failure(self) -> None:
        state = EconomicStateProjector.project(
            facts(liquid_resources_cents=100, peak_continuity_resources_cents=100),
            (
                expense(
                    "due",
                    status=ExpenseStatus.INCURRED,
                    cash_cents=101,
                ),
            ),
        )
        signal = self.controller.assess(state)
        self.assertEqual(signal.mode, EconomicMode.FAILED)
        self.assertIn(
            ReasonCode.UNPAYABLE_DUE_OBLIGATIONS,
            signal.reason_codes,
        )

    def test_pending_settlement_prevents_false_no_path_failure(self) -> None:
        pending = EconomicStateProjector.project(
            facts(
                has_path_to_next_value_action=False,
                has_pending_external_settlement=True,
                pending_settlements=1,
            )
        )
        stranded = EconomicStateProjector.project(
            facts(
                has_path_to_next_value_action=False,
                has_pending_external_settlement=False,
            )
        )
        self.assertNotEqual(
            self.controller.assess(pending).mode,
            EconomicMode.FAILED,
        )
        self.assertEqual(
            self.controller.assess(stranded).mode,
            EconomicMode.FAILED,
        )

    def test_worsening_is_immediate_but_recovery_requires_confirmation(self) -> None:
        stable_state = EconomicStateProjector.project(facts())
        critical_state = EconomicStateProjector.project(
            facts(
                liquid_resources_cents=10_000,
                peak_continuity_resources_cents=25_000,
            )
        )
        worsening = self.controller.assess(
            critical_state,
            ControllerHistory(EconomicMode.STABLE),
        )
        self.assertEqual(worsening.mode, EconomicMode.CRITICAL)

        first_improvement = self.controller.assess(
            stable_state,
            worsening.next_history,
        )
        self.assertEqual(first_improvement.mode, EconomicMode.CRITICAL)
        second_improvement = self.controller.assess(
            stable_state,
            first_improvement.next_history,
        )
        self.assertEqual(second_improvement.mode, EconomicMode.RECOVERY)

    def test_identical_state_produces_identical_signal_and_fingerprint(self) -> None:
        state = EconomicStateProjector.project(facts())
        first = self.controller.assess(state)
        second = self.controller.assess(state)
        self.assertEqual(first, second)
        self.assertEqual(first.state_fingerprint, second.state_fingerprint)

    def test_exposure_is_optional_advice_and_never_an_authorization_limit(self) -> None:
        controller = HomeostasisController(
            HomeostasisConfig(stable_exposure_bps=100)
        )
        signal = controller.assess(EconomicStateProjector.project(facts()))
        self.assertEqual(signal.preferred_irreversible_exposure_cents, 250)
        self.assertTrue(signal.advisory_only)
        self.assertTrue(signal.any_exposure_remains_proposable)

    def test_signal_is_frozen_and_prompt_data_is_neutral(self) -> None:
        signal = self.controller.assess(EconomicStateProjector.project(facts()))
        with self.assertRaises(FrozenInstanceError):
            signal.mode = EconomicMode.FAILED  # type: ignore[misc]
        prompt = signal.to_prompt_data()
        self.assertNotIn("fear", prompt)
        self.assertNotIn("model_confidence", prompt)
        self.assertEqual(prompt["mode"], "stable")


if __name__ == "__main__":
    unittest.main()
