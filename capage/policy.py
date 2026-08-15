"""Policy enforcement for CapAge proposed actions."""

from dataclasses import dataclass

from capage.models import ProposedAction


@dataclass(frozen=True)
class PolicyDecision:
    """Result of evaluating a proposed action."""

    allowed: bool
    reason: str


class PolicyEngine:
    """Evaluates proposed actions before execution."""

    def __init__(self, allowed_tools: set[str]) -> None:
        self.allowed_tools = allowed_tools

    def evaluate(self, action: ProposedAction) -> PolicyDecision:
        """Return an authorization decision for a proposed action."""

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

        return PolicyDecision(
            allowed=True,
            reason="Action satisfies current policy.",
        )
