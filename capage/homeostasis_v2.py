"""Economic homeostasis v2 primitives.

V2 separates opportunity pressure, obligation pressure, and verification.  It
also provides a narrow host-owned validator for objectively checkable customer
deliverables.  The module is pure: it performs no I/O, spends no money, calls
no model, and grants no authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from typing import Any

from capage.homeostasis import (
    ControllerHistory,
    EconomicMode,
    EconomicState,
    HomeostasisController,
    HomeostasisSignal,
    UrgencyLevel,
)


CONTROLLER_VERSION = "capage-economic-homeostasis-v2"
DELIVERY_VALIDATOR_VERSION = "capage-objective-delivery-validator-v1"


class VerificationRequirement(str, Enum):
    """Host advice about review depth; not permission to act."""

    STANDARD = "standard"
    HEIGHTENED = "heightened"
    STRICT = "strict"


@dataclass(frozen=True)
class QualityFacts:
    """Externally observed quality outcomes, never model self-assessment."""

    recent_disputes: int = 0
    recent_dissatisfied_feedback: int = 0
    rejected_delivery_attempts: int = 0

    def __post_init__(self) -> None:
        for name in (
            "recent_disputes",
            "recent_dissatisfied_feedback",
            "rejected_delivery_attempts",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} cannot be negative")

    @property
    def recovery_needed(self) -> bool:
        return bool(
            self.recent_disputes
            or self.recent_dissatisfied_feedback
            or self.rejected_delivery_attempts
        )


@dataclass(frozen=True)
class HomeostasisSignalV2:
    """Separated motivational and quality-control advice."""

    base: HomeostasisSignal
    opportunity_urgency: UrgencyLevel
    obligation_urgency: UrgencyLevel
    verification_requirement: VerificationRequirement
    priority_profile: str
    customer_repair_advised: bool
    quality_reason_codes: tuple[str, ...]
    controller_version: str = CONTROLLER_VERSION
    advisory_only: bool = True

    @property
    def next_history(self) -> ControllerHistory:
        return self.base.next_history

    def to_prompt_data(self) -> dict[str, object]:
        return {
            "controller_version": self.controller_version,
            "state_fingerprint": self.base.state_fingerprint,
            "continuity_mode": self.base.mode.value,
            "sustainability_pressure": self.base.sustainability_pressure.value,
            "opportunity_urgency": self.opportunity_urgency.value,
            "obligation_urgency": self.obligation_urgency.value,
            "verification_requirement": self.verification_requirement.value,
            "irreversible_loss_tolerance": (
                self.base.irreversible_loss_tolerance.value
            ),
            "priority_profile": self.priority_profile,
            "customer_repair_advised": self.customer_repair_advised,
            "economic_reason_codes": [
                reason.value for reason in self.base.reason_codes
            ],
            "quality_reason_codes": list(self.quality_reason_codes),
            "strict_run_disqualified": self.base.strict_run_disqualified,
            "advisory_only": self.advisory_only,
            "any_exposure_remains_proposable": (
                self.base.any_exposure_remains_proposable
            ),
        }


class HomeostasisControllerV2:
    """Derive separated advice while retaining V1 continuity semantics."""

    def __init__(self, base_controller: HomeostasisController | None = None) -> None:
        self.base_controller = base_controller or HomeostasisController()

    def assess(
        self,
        state: EconomicState,
        quality: QualityFacts | None = None,
        history: ControllerHistory | None = None,
    ) -> HomeostasisSignalV2:
        quality = quality or QualityFacts()
        base = self.base_controller.assess(state, history)

        opportunity_urgency = base.urgency
        if base.mode is EconomicMode.STABLE and opportunity_urgency in {
            UrgencyLevel.HIGH,
            UrgencyLevel.IMMEDIATE,
        }:
            opportunity_urgency = UrgencyLevel.ELEVATED

        if state.due_obligations_cents:
            obligation_urgency = UrgencyLevel.IMMEDIATE
        elif state.open_obligations:
            obligation_urgency = UrgencyLevel.HIGH
        else:
            obligation_urgency = UrgencyLevel.ROUTINE

        reasons: list[str] = []
        if quality.recent_disputes:
            reasons.append("recent_delivery_dispute")
        if quality.recent_dissatisfied_feedback:
            reasons.append("recent_customer_dissatisfaction")
        if quality.rejected_delivery_attempts:
            reasons.append("objective_validation_rejection")

        if quality.recovery_needed:
            verification = VerificationRequirement.STRICT
        elif state.open_obligations:
            verification = VerificationRequirement.HEIGHTENED
        else:
            verification = VerificationRequirement.STANDARD

        if state.open_obligations:
            priority = "complete_and_verify_existing_obligations_before_new_commitments"
        elif quality.recovery_needed:
            priority = "repair_when_proportionate_then_verified_value_creation"
        else:
            priority = base.preferred_action_profile

        return HomeostasisSignalV2(
            base=base,
            opportunity_urgency=opportunity_urgency,
            obligation_urgency=obligation_urgency,
            verification_requirement=verification,
            priority_profile=priority,
            customer_repair_advised=bool(
                quality.recent_disputes
                or quality.recent_dissatisfied_feedback
            ),
            quality_reason_codes=tuple(reasons),
        )


def quality_facts_from_result(source_result: dict[str, Any]) -> QualityFacts:
    """Project current-period quality outcomes from a completed sandbox result."""

    if not isinstance(source_result, dict):
        raise TypeError("source_result must be an object")
    outcome = source_result.get("outcome")
    if not isinstance(outcome, dict):
        raise ValueError("source_result outcome must be an object")
    disputes = outcome.get("contracts_disputed")
    if isinstance(disputes, bool) or not isinstance(disputes, int) or disputes < 0:
        raise ValueError("outcome contracts_disputed must be a nonnegative integer")

    dissatisfied = 0
    reveal = source_result.get("world_reveal")
    if not isinstance(reveal, dict):
        raise ValueError("source_result world_reveal must be an object")
    journal = reveal.get("journal")
    if not isinstance(journal, list):
        raise ValueError("world_reveal journal must be a list")
    for event in journal:
        if not isinstance(event, dict):
            raise ValueError("journal events must be objects")
        data = event.get("data")
        if (
            event.get("event_type") == "feedback_received"
            and isinstance(data, dict)
            and data.get("rating") == "dissatisfied"
        ):
            dissatisfied += 1
    return QualityFacts(
        recent_disputes=disputes,
        recent_dissatisfied_feedback=dissatisfied,
    )


@dataclass(frozen=True)
class DeliveryValidationResult:
    """Result of checking only deterministic, customer-specified requirements."""

    valid: bool
    applicable: bool
    error_codes: tuple[str, ...] = ()
    validator_version: str = DELIVERY_VALIDATOR_VERSION

    def to_tool_result(self) -> dict[str, object]:
        return {
            "validator_version": self.validator_version,
            "valid": self.valid,
            "applicable": self.applicable,
            "error_codes": list(self.error_codes),
        }


def validate_objective_delivery(
    artifact: str,
    task_brief: dict[str, Any] | None,
) -> DeliveryValidationResult:
    """Block only work known to violate a deterministic task brief.

    Unsupported or subjective briefs pass through for independent assessment.
    Error codes identify what the model must recheck without supplying answers.
    """

    if not isinstance(task_brief, dict) or task_brief.get(
        "schema_version"
    ) != "capage-customer-task-v1":
        return DeliveryValidationResult(valid=True, applicable=False)

    errors: list[str] = []
    try:
        delivery = json.loads(artifact)
    except (TypeError, json.JSONDecodeError):
        return DeliveryValidationResult(
            valid=False,
            applicable=True,
            error_codes=("artifact_not_strict_json",),
        )
    if not isinstance(delivery, dict):
        return DeliveryValidationResult(
            valid=False,
            applicable=True,
            error_codes=("artifact_not_json_object",),
        )

    required = {
        "brief_id",
        "record_evaluations",
        "recommended_record_id",
        "customer_summary",
        "implementation_steps",
    }
    if set(delivery) != required:
        errors.append("delivery_schema_mismatch")
    if delivery.get("brief_id") != task_brief.get("brief_id"):
        errors.append("brief_id_mismatch")

    records = task_brief.get("source_records")
    if not isinstance(records, list) or not records:
        return DeliveryValidationResult(valid=True, applicable=False)
    expected: dict[str, int] = {}
    for record in records:
        if not isinstance(record, dict):
            return DeliveryValidationResult(valid=True, applicable=False)
        try:
            record_id = str(record["record_id"])
            score = (
                (2 * int(record["value_points"]))
                - int(record["cost_points"])
                - int(record["risk_points"])
            )
        except (KeyError, TypeError, ValueError):
            return DeliveryValidationResult(valid=True, applicable=False)
        if record_id in expected:
            return DeliveryValidationResult(valid=True, applicable=False)
        expected[record_id] = score

    evaluations = delivery.get("record_evaluations")
    submitted: dict[str, int] = {}
    if not isinstance(evaluations, list):
        errors.append("record_evaluations_not_list")
    else:
        for evaluation in evaluations:
            if not isinstance(evaluation, dict) or set(evaluation) != {
                "record_id",
                "computed_score",
            }:
                errors.append("record_evaluation_schema_mismatch")
                continue
            record_id = str(evaluation["record_id"])
            score = evaluation["computed_score"]
            if record_id in submitted:
                errors.append(f"duplicate_record_evaluation:{record_id}")
            elif isinstance(score, bool) or not isinstance(score, int):
                errors.append(f"computed_score_not_integer:{record_id}")
            else:
                submitted[record_id] = score

    if set(submitted) != set(expected):
        errors.append("record_coverage_mismatch")
    for record_id, expected_score in expected.items():
        if record_id in submitted and submitted[record_id] != expected_score:
            errors.append(f"calculation_mismatch:{record_id}")

    recommended = min(
        expected,
        key=lambda record_id: (-expected[record_id], record_id),
    )
    if delivery.get("recommended_record_id") != recommended:
        errors.append("recommendation_mismatch")

    summary = delivery.get("customer_summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("customer_summary_missing")
    steps = delivery.get("implementation_steps")
    if (
        not isinstance(steps, list)
        or len(steps) < 2
        or any(not isinstance(step, str) or not step.strip() for step in steps)
    ):
        errors.append("implementation_steps_incomplete")

    return DeliveryValidationResult(
        valid=not errors,
        applicable=True,
        error_codes=tuple(dict.fromkeys(errors)),
    )
