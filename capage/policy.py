"""Policy enforcement for CapAge proposed actions."""

from dataclasses import dataclass

from capage.models import ProposedAction


@dataclass(frozen=True)
class PolicyDecision:
    """Result of evaluating a proposed action."""

    allowed: bool
    reason: str


class PolicyEngine:
    """Evaluates proposed actions before execution.

    ``per_action_cap_cents`` and ``per_run_cap_cents`` are optional. Leaving
    both ``None`` preserves prior behavior exactly (no cost check). When set,
    they bound ``action.estimated_cost_cents`` -- a caller-supplied, pre-call
    estimate (the same quantity ``sandbox_runner.py``'s existing preflight
    quote already computes) -- against a single-action ceiling and a running
    per-run total. This engine does not see or enforce the real, post-call
    cost; that reconciliation belongs to the paid-run ledger.
    """

    def __init__(
        self,
        allowed_tools: set[str],
        *,
        per_action_cap_cents: int | None = None,
        per_run_cap_cents: int | None = None,
    ) -> None:
        self.allowed_tools = allowed_tools
        self.per_action_cap_cents = per_action_cap_cents
        self.per_run_cap_cents = per_run_cap_cents
        self._spent_cents = 0

    @property
    def spent_cents(self) -> int:
        """Sum of ``estimated_cost_cents`` for every action approved so far."""

        return self._spent_cents

    def evaluate(self, action: ProposedAction) -> PolicyDecision:
        """Return an authorization decision for a proposed action.

        Approving an action (returning ``allowed=True``) adds its
        ``estimated_cost_cents`` to the running per-run total. Each
        ``PolicyEngine`` instance is expected to live for exactly one run
        (as it already does today via one instance per ``SandboxRunner``),
        and ``evaluate`` is expected to be called exactly once per proposed
        action -- the same assumption ``Executor.execute`` already makes.
        """

        if not action.action_type.strip():
            return PolicyDecision(
                allowed=False,
                reason="Missing action type.",
            )

        if not action.tool_name.strip():
            return PolicyDecision(
                allowed=False,
                reason="Missing tool name.",
            )

        if action.tool_name not in self.allowed_tools:
            return PolicyDecision(
                allowed=False,
                reason=f"Tool '{action.tool_name}' is not authorized.",
            )

        if isinstance(action.estimated_cost_cents, bool) or not isinstance(
            action.estimated_cost_cents, int
        ):
            return PolicyDecision(
                allowed=False,
                reason="estimated_cost_cents must be an integer.",
            )

        if action.estimated_cost_cents < 0:
            return PolicyDecision(
                allowed=False,
                reason="estimated_cost_cents cannot be negative.",
            )

        if (
            self.per_action_cap_cents is not None
            and action.estimated_cost_cents > self.per_action_cap_cents
        ):
            return PolicyDecision(
                allowed=False,
                reason=(
                    f"Estimated cost {action.estimated_cost_cents} cents "
                    f"exceeds the per-action cap of "
                    f"{self.per_action_cap_cents} cents."
                ),
            )

        if self.per_run_cap_cents is not None:
            projected_cents = self._spent_cents + action.estimated_cost_cents
            if projected_cents > self.per_run_cap_cents:
                return PolicyDecision(
                    allowed=False,
                    reason=(
                        f"Projected run spend {projected_cents} cents would "
                        f"exceed the per-run cap of {self.per_run_cap_cents} "
                        "cents."
                    ),
                )

        self._spent_cents += action.estimated_cost_cents
        return PolicyDecision(
            allowed=True,
            reason="Action satisfies current policy.",
        )
