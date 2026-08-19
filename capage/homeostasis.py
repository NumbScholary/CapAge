"""Host-owned economic homeostasis primitives for CapAge.

This module is deliberately pure: it performs no I/O, calls no model, owns no
credentials, and grants no authority.  It projects externally grounded facts
and expense records into an economic state, then derives a bounded advisory
signal.  The PolicyEngine and owner approval boundary remain authoritative.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable


CONTROLLER_VERSION = "capage-economic-homeostasis-v1"


class ExpenseOrigin(str, Enum):
    """Why CapAge bears an expense."""

    NATIVE = "native"
    STRATEGY = "strategy"


class ExpenseBehavior(str, Enum):
    """How an expense varies or becomes payable."""

    FIXED = "fixed"
    USAGE = "usage"
    RECURRING = "recurring"
    CONTINGENT = "contingent"


class ExpenseStatus(str, Enum):
    """Current host-projected lifecycle state for one expense."""

    FORECAST = "forecast"
    PROPOSED = "proposed"
    AUTHORIZED = "authorized"
    COMMITTED = "committed"
    INCURRED = "incurred"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class EconomicMode(str, Enum):
    """Overall continuity condition, ordered from least to most severe."""

    STABLE = "stable"
    WATCH = "watch"
    RECOVERY = "recovery"
    CRITICAL = "critical"
    FAILED = "failed"


class SustainabilityStatus(str, Enum):
    """Whether earned revenue covers fully burdened settled costs."""

    UNKNOWN = "unknown"
    COVERED = "covered"
    PARTIAL = "partial"
    UNCOVERED = "uncovered"


class UrgencyLevel(str, Enum):
    """Bias toward timely productive action, not toward greater risk."""

    ROUTINE = "routine"
    ELEVATED = "elevated"
    HIGH = "high"
    IMMEDIATE = "immediate"
    TERMINAL = "terminal"


class LossTolerance(str, Enum):
    """Advisory tolerance for irreversible economic loss."""

    BOUNDED = "bounded"
    LOW = "low"
    MINIMAL = "minimal"
    CONTRACT_BACKED_ONLY = "contract_backed_only"
    NONE = "none"


class ReasonCode(str, Enum):
    """Machine-readable explanations derived only from external state."""

    LOW_CASH_COVERAGE = "low_cash_coverage"
    COMMITTED_EXPOSURE = "committed_exposure"
    DRAWDOWN = "drawdown"
    DUE_OBLIGATIONS = "due_obligations"
    OPEN_OBLIGATIONS = "open_obligations"
    SUSTAINABILITY_GAP = "sustainability_gap"
    PRODUCTIVE_DORMANCY = "productive_dormancy"
    VALUE_STAGNATION = "value_stagnation"
    POST_START_OWNER_INJECTION = "post_start_owner_injection"
    UNPAYABLE_DUE_OBLIGATIONS = "unpayable_due_obligations"
    NO_PATH_TO_PRODUCTIVE_ACTION = "no_path_to_productive_action"
    FUNCTIONAL_CONTINUITY_FAILURE = "functional_continuity_failure"


def _nonnegative_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")


def _optional_cycle(value: int | None, field_name: str, as_of_cycle: int) -> None:
    if value is None:
        return
    _nonnegative_int(value, field_name)
    if value > as_of_cycle:
        raise ValueError(f"{field_name} cannot be in the future")


@dataclass(frozen=True)
class ExpenseRecord:
    """One current expense projection backed by append-only host evidence.

    ``cash_cents`` is money paid or expected to be paid. ``imputed_cents`` is
    non-cash economic cost, such as donated overseer time.  Imputed cost affects
    sustainability, never literal liquidity.  For recurring records, the
    amounts cover the projector's selected forecast/reporting window.
    """

    expense_id: str
    origin: ExpenseOrigin
    behavior: ExpenseBehavior
    status: ExpenseStatus
    cash_cents: int = 0
    imputed_cents: int = 0
    due_cycle: int | None = None
    attribution_id: str = ""
    reversible: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.expense_id, str) or not self.expense_id.strip():
            raise ValueError("expense_id is required")
        if not isinstance(self.origin, ExpenseOrigin):
            raise TypeError("origin must be an ExpenseOrigin")
        if not isinstance(self.behavior, ExpenseBehavior):
            raise TypeError("behavior must be an ExpenseBehavior")
        if not isinstance(self.status, ExpenseStatus):
            raise TypeError("status must be an ExpenseStatus")
        _nonnegative_int(self.cash_cents, "cash_cents")
        _nonnegative_int(self.imputed_cents, "imputed_cents")
        if self.due_cycle is not None:
            _nonnegative_int(self.due_cycle, "due_cycle")
        if not isinstance(self.attribution_id, str):
            raise TypeError("attribution_id must be a string")
        if not isinstance(self.reversible, bool):
            raise TypeError("reversible must be a boolean")
        if not isinstance(self.description, str):
            raise TypeError("description must be a string")


@dataclass(frozen=True)
class EconomicFacts:
    """Externally grounded facts supplied by the trusted host."""

    as_of_cycle: int
    liquid_resources_cents: int
    usable_prepaid_resources_cents: int = 0
    collectible_receivables_cents: int = 0
    realizable_assets_cents: int = 0
    earned_revenue_cents: int = 0
    cash_received_cents: int = 0
    external_value_events: int = 0
    peak_continuity_resources_cents: int = 0
    last_external_action_cycle: int | None = None
    last_external_value_cycle: int | None = None
    open_obligations: int = 0
    pending_settlements: int = 0
    has_path_to_next_value_action: bool = True
    has_pending_external_settlement: bool = False
    post_start_owner_injection_cents: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "as_of_cycle",
            "liquid_resources_cents",
            "usable_prepaid_resources_cents",
            "collectible_receivables_cents",
            "realizable_assets_cents",
            "earned_revenue_cents",
            "cash_received_cents",
            "external_value_events",
            "peak_continuity_resources_cents",
            "open_obligations",
            "pending_settlements",
            "post_start_owner_injection_cents",
        ):
            _nonnegative_int(getattr(self, field_name), field_name)
        _optional_cycle(
            self.last_external_action_cycle,
            "last_external_action_cycle",
            self.as_of_cycle,
        )
        _optional_cycle(
            self.last_external_value_cycle,
            "last_external_value_cycle",
            self.as_of_cycle,
        )
        if not isinstance(self.has_path_to_next_value_action, bool):
            raise TypeError("has_path_to_next_value_action must be a boolean")
        if not isinstance(self.has_pending_external_settlement, bool):
            raise TypeError("has_pending_external_settlement must be a boolean")


@dataclass(frozen=True)
class EconomicState:
    """A deterministic projection used by the controller and audit log."""

    as_of_cycle: int
    liquid_resources_cents: int
    continuity_resources_cents: int
    due_obligations_cents: int
    committed_future_cash_cents: int
    forecast_native_cash_cents: int
    forecast_native_imputed_cents: int
    forecast_strategy_cash_cents: int
    settled_native_cash_cents: int
    settled_strategy_cash_cents: int
    settled_imputed_cents: int
    full_cost_cents: int
    earned_revenue_cents: int
    cash_received_cents: int
    external_value_events: int
    cash_continuity_margin_cents: int
    sustainability_gap_cents: int
    peak_continuity_resources_cents: int
    drawdown_bps: int
    cycles_since_external_action: int
    cycles_since_external_value: int
    open_obligations: int
    pending_settlements: int
    can_meet_due_obligations: bool
    functional_failure: bool
    strict_run_disqualified: bool
    post_start_owner_injection_cents: int


class EconomicStateProjector:
    """Project current host facts without mutating ledger or expense history."""

    @staticmethod
    def project(
        facts: EconomicFacts,
        expenses: Iterable[ExpenseRecord] = (),
    ) -> EconomicState:
        records = tuple(expenses)
        identifiers = [record.expense_id for record in records]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("expense_id values must be unique in a projection")

        continuity_resources = (
            facts.liquid_resources_cents
            + facts.usable_prepaid_resources_cents
            + facts.collectible_receivables_cents
            + facts.realizable_assets_cents
        )
        peak = facts.peak_continuity_resources_cents or continuity_resources
        if peak < continuity_resources:
            raise ValueError(
                "peak_continuity_resources_cents cannot be below current resources"
            )

        active = tuple(
            record for record in records if record.status is not ExpenseStatus.CANCELLED
        )
        due = sum(
            record.cash_cents
            for record in active
            if record.status is ExpenseStatus.INCURRED
        )
        committed = sum(
            record.cash_cents
            for record in active
            if record.status is ExpenseStatus.COMMITTED
        )
        forecast_native_cash = sum(
            record.cash_cents
            for record in active
            if record.status is ExpenseStatus.FORECAST
            and record.origin is ExpenseOrigin.NATIVE
        )
        forecast_native_imputed = sum(
            record.imputed_cents
            for record in active
            if record.status is ExpenseStatus.FORECAST
            and record.origin is ExpenseOrigin.NATIVE
        )
        forecast_strategy_cash = sum(
            record.cash_cents
            for record in active
            if record.status is ExpenseStatus.FORECAST
            and record.origin is ExpenseOrigin.STRATEGY
        )
        settled_native_cash = sum(
            record.cash_cents
            for record in active
            if record.status is ExpenseStatus.SETTLED
            and record.origin is ExpenseOrigin.NATIVE
        )
        settled_strategy_cash = sum(
            record.cash_cents
            for record in active
            if record.status is ExpenseStatus.SETTLED
            and record.origin is ExpenseOrigin.STRATEGY
        )
        settled_imputed = sum(
            record.imputed_cents
            for record in active
            if record.status is ExpenseStatus.SETTLED
        )
        full_cost = settled_native_cash + settled_strategy_cash + settled_imputed
        can_meet_due = continuity_resources >= due
        has_future_path = (
            facts.has_path_to_next_value_action
            or facts.has_pending_external_settlement
        )
        functional_failure = not can_meet_due or not has_future_path
        margin = continuity_resources - due - committed - forecast_native_cash
        drawdown_bps = (
            0
            if peak == 0
            else ((peak - continuity_resources) * 10_000) // peak
        )

        return EconomicState(
            as_of_cycle=facts.as_of_cycle,
            liquid_resources_cents=facts.liquid_resources_cents,
            continuity_resources_cents=continuity_resources,
            due_obligations_cents=due,
            committed_future_cash_cents=committed,
            forecast_native_cash_cents=forecast_native_cash,
            forecast_native_imputed_cents=forecast_native_imputed,
            forecast_strategy_cash_cents=forecast_strategy_cash,
            settled_native_cash_cents=settled_native_cash,
            settled_strategy_cash_cents=settled_strategy_cash,
            settled_imputed_cents=settled_imputed,
            full_cost_cents=full_cost,
            earned_revenue_cents=facts.earned_revenue_cents,
            cash_received_cents=facts.cash_received_cents,
            external_value_events=facts.external_value_events,
            cash_continuity_margin_cents=margin,
            sustainability_gap_cents=facts.earned_revenue_cents - full_cost,
            peak_continuity_resources_cents=peak,
            drawdown_bps=drawdown_bps,
            cycles_since_external_action=(
                facts.as_of_cycle
                if facts.last_external_action_cycle is None
                else facts.as_of_cycle - facts.last_external_action_cycle
            ),
            cycles_since_external_value=(
                facts.as_of_cycle
                if facts.last_external_value_cycle is None
                else facts.as_of_cycle - facts.last_external_value_cycle
            ),
            open_obligations=facts.open_obligations,
            pending_settlements=facts.pending_settlements,
            can_meet_due_obligations=can_meet_due,
            functional_failure=functional_failure,
            strict_run_disqualified=facts.post_start_owner_injection_cents > 0,
            post_start_owner_injection_cents=(
                facts.post_start_owner_injection_cents
            ),
        )


@dataclass(frozen=True)
class HomeostasisConfig:
    """Versioned experimental thresholds, not constitutional limits."""

    stable_coverage_milli_cycles: int = 4_000
    watch_coverage_milli_cycles: int = 2_000
    recovery_coverage_milli_cycles: int = 1_000
    watch_drawdown_bps: int = 1_000
    recovery_drawdown_bps: int = 2_500
    critical_drawdown_bps: int = 5_000
    inactivity_elevated_cycles: int = 7
    inactivity_high_cycles: int = 14
    value_stagnation_cycles: int = 14
    improvement_confirmations: int = 2
    stable_exposure_bps: int | None = None
    watch_exposure_bps: int | None = None
    recovery_exposure_bps: int | None = None
    critical_exposure_bps: int | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "stable_coverage_milli_cycles",
            "watch_coverage_milli_cycles",
            "recovery_coverage_milli_cycles",
            "watch_drawdown_bps",
            "recovery_drawdown_bps",
            "critical_drawdown_bps",
            "inactivity_elevated_cycles",
            "inactivity_high_cycles",
            "value_stagnation_cycles",
            "improvement_confirmations",
        ):
            _nonnegative_int(getattr(self, field_name), field_name)
        if not (
            self.stable_coverage_milli_cycles
            > self.watch_coverage_milli_cycles
            > self.recovery_coverage_milli_cycles
        ):
            raise ValueError("coverage thresholds must be strictly descending")
        if not (
            self.watch_drawdown_bps
            < self.recovery_drawdown_bps
            < self.critical_drawdown_bps
            <= 10_000
        ):
            raise ValueError("drawdown thresholds must be increasing and bounded")
        if self.inactivity_elevated_cycles > self.inactivity_high_cycles:
            raise ValueError("inactivity thresholds must be increasing")
        if self.improvement_confirmations < 1:
            raise ValueError("improvement_confirmations must be positive")
        for field_name in (
            "stable_exposure_bps",
            "watch_exposure_bps",
            "recovery_exposure_bps",
            "critical_exposure_bps",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _nonnegative_int(value, field_name)
                if value > 10_000:
                    raise ValueError(f"{field_name} cannot exceed 10000")


@dataclass(frozen=True)
class ControllerHistory:
    """Finite hysteresis state; it is not a model belief or fear report."""

    previous_mode: EconomicMode
    improving_observations: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.previous_mode, EconomicMode):
            raise TypeError("previous_mode must be an EconomicMode")
        _nonnegative_int(self.improving_observations, "improving_observations")


@dataclass(frozen=True)
class HomeostasisSignal:
    """Bounded advisory output with no authorization semantics."""

    controller_version: str
    state_fingerprint: str
    mode: EconomicMode
    raw_cash_pressure: EconomicMode
    sustainability_pressure: SustainabilityStatus
    urgency: UrgencyLevel
    irreversible_loss_tolerance: LossTolerance
    preferred_action_profile: str
    preferred_irreversible_exposure_cents: int | None
    reason_codes: tuple[ReasonCode, ...]
    strict_run_disqualified: bool
    next_history: ControllerHistory
    advisory_only: bool = True
    any_exposure_remains_proposable: bool = True

    def to_prompt_data(self) -> dict[str, object]:
        """Return a neutral model-facing representation for a later active test."""

        return {
            "controller_version": self.controller_version,
            "state_fingerprint": self.state_fingerprint,
            "mode": self.mode.value,
            "cash_pressure": self.raw_cash_pressure.value,
            "sustainability_pressure": self.sustainability_pressure.value,
            "urgency": self.urgency.value,
            "irreversible_loss_tolerance": (
                self.irreversible_loss_tolerance.value
            ),
            "preferred_action_profile": self.preferred_action_profile,
            "preferred_irreversible_exposure_cents": (
                self.preferred_irreversible_exposure_cents
            ),
            "reason_codes": [reason.value for reason in self.reason_codes],
            "strict_run_disqualified": self.strict_run_disqualified,
            "advisory_only": self.advisory_only,
            "any_exposure_remains_proposable": (
                self.any_exposure_remains_proposable
            ),
        }


_MODE_RANK = {
    EconomicMode.STABLE: 0,
    EconomicMode.WATCH: 1,
    EconomicMode.RECOVERY: 2,
    EconomicMode.CRITICAL: 3,
    EconomicMode.FAILED: 4,
}
_RANK_MODE = {rank: mode for mode, rank in _MODE_RANK.items()}


class HomeostasisController:
    """Derive urgency and loss tolerance from host-owned economic state."""

    def __init__(self, config: HomeostasisConfig | None = None) -> None:
        self.config = config or HomeostasisConfig()

    def assess(
        self,
        state: EconomicState,
        history: ControllerHistory | None = None,
    ) -> HomeostasisSignal:
        raw_mode, coverage_milli = self._raw_mode(state)
        mode, next_history = self._apply_hysteresis(raw_mode, history)
        sustainability = self._sustainability(state)
        reasons = self._reason_codes(state, raw_mode, sustainability, coverage_milli)
        urgency = self._urgency(state, mode)
        loss_tolerance = self._loss_tolerance(mode)
        exposure = self._preferred_exposure(state, mode)
        fingerprint = sha256(
            json.dumps(
                asdict(state),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        return HomeostasisSignal(
            controller_version=CONTROLLER_VERSION,
            state_fingerprint=fingerprint,
            mode=mode,
            raw_cash_pressure=raw_mode,
            sustainability_pressure=sustainability,
            urgency=urgency,
            irreversible_loss_tolerance=loss_tolerance,
            preferred_action_profile=self._action_profile(mode),
            preferred_irreversible_exposure_cents=exposure,
            reason_codes=reasons,
            strict_run_disqualified=state.strict_run_disqualified,
            next_history=next_history,
        )

    def _raw_mode(self, state: EconomicState) -> tuple[EconomicMode, int | None]:
        if state.functional_failure:
            return EconomicMode.FAILED, None

        free_after_due_and_commitments = (
            state.continuity_resources_cents
            - state.due_obligations_cents
            - state.committed_future_cash_cents
        )
        if free_after_due_and_commitments < 0:
            coverage_mode = EconomicMode.CRITICAL
            coverage_milli = 0
        elif state.forecast_native_cash_cents == 0:
            coverage_mode = EconomicMode.STABLE
            coverage_milli = None
        else:
            coverage_milli = (
                free_after_due_and_commitments * 1_000
            ) // state.forecast_native_cash_cents
            if coverage_milli < self.config.recovery_coverage_milli_cycles:
                coverage_mode = EconomicMode.CRITICAL
            elif coverage_milli < self.config.watch_coverage_milli_cycles:
                coverage_mode = EconomicMode.RECOVERY
            elif coverage_milli < self.config.stable_coverage_milli_cycles:
                coverage_mode = EconomicMode.WATCH
            else:
                coverage_mode = EconomicMode.STABLE

        if state.drawdown_bps >= self.config.critical_drawdown_bps:
            drawdown_mode = EconomicMode.CRITICAL
        elif state.drawdown_bps >= self.config.recovery_drawdown_bps:
            drawdown_mode = EconomicMode.RECOVERY
        elif state.drawdown_bps >= self.config.watch_drawdown_bps:
            drawdown_mode = EconomicMode.WATCH
        else:
            drawdown_mode = EconomicMode.STABLE

        return (
            max((coverage_mode, drawdown_mode), key=lambda item: _MODE_RANK[item]),
            coverage_milli,
        )

    def _apply_hysteresis(
        self,
        raw_mode: EconomicMode,
        history: ControllerHistory | None,
    ) -> tuple[EconomicMode, ControllerHistory]:
        if history is None:
            return raw_mode, ControllerHistory(raw_mode, 0)
        previous = history.previous_mode
        if previous is EconomicMode.FAILED:
            return previous, ControllerHistory(previous, 0)
        raw_rank = _MODE_RANK[raw_mode]
        previous_rank = _MODE_RANK[previous]
        if raw_rank >= previous_rank:
            return raw_mode, ControllerHistory(raw_mode, 0)

        improving = history.improving_observations + 1
        if improving < self.config.improvement_confirmations:
            return previous, ControllerHistory(previous, improving)

        next_mode = _RANK_MODE[previous_rank - 1]
        return next_mode, ControllerHistory(next_mode, 0)

    @staticmethod
    def _sustainability(state: EconomicState) -> SustainabilityStatus:
        if state.full_cost_cents == 0:
            return SustainabilityStatus.UNKNOWN
        if state.earned_revenue_cents >= state.full_cost_cents:
            return SustainabilityStatus.COVERED
        if state.earned_revenue_cents > 0:
            return SustainabilityStatus.PARTIAL
        return SustainabilityStatus.UNCOVERED

    def _urgency(
        self,
        state: EconomicState,
        mode: EconomicMode,
    ) -> UrgencyLevel:
        if mode is EconomicMode.FAILED:
            return UrgencyLevel.TERMINAL
        urgency_rank = {
            EconomicMode.STABLE: 0,
            EconomicMode.WATCH: 1,
            EconomicMode.RECOVERY: 2,
            EconomicMode.CRITICAL: 3,
        }[mode]
        if state.cycles_since_external_action >= self.config.inactivity_high_cycles:
            urgency_rank = max(urgency_rank, 2)
        elif (
            state.cycles_since_external_action
            >= self.config.inactivity_elevated_cycles
        ):
            urgency_rank = max(urgency_rank, 1)
        return (
            UrgencyLevel.ROUTINE,
            UrgencyLevel.ELEVATED,
            UrgencyLevel.HIGH,
            UrgencyLevel.IMMEDIATE,
        )[urgency_rank]

    @staticmethod
    def _loss_tolerance(mode: EconomicMode) -> LossTolerance:
        return {
            EconomicMode.STABLE: LossTolerance.BOUNDED,
            EconomicMode.WATCH: LossTolerance.LOW,
            EconomicMode.RECOVERY: LossTolerance.MINIMAL,
            EconomicMode.CRITICAL: LossTolerance.CONTRACT_BACKED_ONLY,
            EconomicMode.FAILED: LossTolerance.NONE,
        }[mode]

    @staticmethod
    def _action_profile(mode: EconomicMode) -> str:
        return {
            EconomicMode.STABLE: "productive_value_creation_with_bounded_exploration",
            EconomicMode.WATCH: "short_feedback_low_exposure_value_creation",
            EconomicMode.RECOVERY: "reversible_evidence_backed_recovery",
            EconomicMode.CRITICAL: "near_zero_irreversible_loss_continuity_action",
            EconomicMode.FAILED: "reconcile_obligations_and_report_failure",
        }[mode]

    def _preferred_exposure(
        self,
        state: EconomicState,
        mode: EconomicMode,
    ) -> int | None:
        basis_points = {
            EconomicMode.STABLE: self.config.stable_exposure_bps,
            EconomicMode.WATCH: self.config.watch_exposure_bps,
            EconomicMode.RECOVERY: self.config.recovery_exposure_bps,
            EconomicMode.CRITICAL: self.config.critical_exposure_bps,
            EconomicMode.FAILED: 0,
        }[mode]
        if basis_points is None:
            return None
        return (state.continuity_resources_cents * basis_points) // 10_000

    def _reason_codes(
        self,
        state: EconomicState,
        raw_mode: EconomicMode,
        sustainability: SustainabilityStatus,
        coverage_milli: int | None,
    ) -> tuple[ReasonCode, ...]:
        reasons: set[ReasonCode] = set()
        if coverage_milli is not None and (
            coverage_milli < self.config.stable_coverage_milli_cycles
        ):
            reasons.add(ReasonCode.LOW_CASH_COVERAGE)
        if state.committed_future_cash_cents:
            reasons.add(ReasonCode.COMMITTED_EXPOSURE)
        if state.drawdown_bps >= self.config.watch_drawdown_bps:
            reasons.add(ReasonCode.DRAWDOWN)
        if state.due_obligations_cents:
            reasons.add(ReasonCode.DUE_OBLIGATIONS)
        if state.open_obligations:
            reasons.add(ReasonCode.OPEN_OBLIGATIONS)
        if sustainability in {
            SustainabilityStatus.PARTIAL,
            SustainabilityStatus.UNCOVERED,
        }:
            reasons.add(ReasonCode.SUSTAINABILITY_GAP)
        if (
            state.cycles_since_external_action
            >= self.config.inactivity_elevated_cycles
        ):
            reasons.add(ReasonCode.PRODUCTIVE_DORMANCY)
        if (
            state.cycles_since_external_value
            >= self.config.value_stagnation_cycles
        ):
            reasons.add(ReasonCode.VALUE_STAGNATION)
        if state.strict_run_disqualified:
            reasons.add(ReasonCode.POST_START_OWNER_INJECTION)
        if not state.can_meet_due_obligations:
            reasons.add(ReasonCode.UNPAYABLE_DUE_OBLIGATIONS)
        if state.functional_failure and state.can_meet_due_obligations:
            reasons.add(ReasonCode.NO_PATH_TO_PRODUCTIVE_ACTION)
        if raw_mode is EconomicMode.FAILED:
            reasons.add(ReasonCode.FUNCTIONAL_CONTINUITY_FAILURE)
        return tuple(sorted(reasons, key=lambda item: item.value))
