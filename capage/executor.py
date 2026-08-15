"""Trusted execution boundary for CapAge."""

from typing import Any

from capage.models import ProposedAction
from capage.policy import PolicyEngine
from capage.tools import TOOLS


class Executor:
    """Authorizes proposed actions before executing tools."""

    def __init__(self, policy: PolicyEngine) -> None:
        self.policy = policy

    def execute(self, action: ProposedAction) -> dict[str, Any]:
        """Evaluate an action and execute it only if authorized."""

        decision = self.policy.evaluate(action)

        if not decision.allowed:
            return {
                "success": False,
                "action_id": action.action_id,
                "executed": False,
                "reason": decision.reason,
            }

        tool = TOOLS.get(action.tool_name)

        if tool is None:
            return {
                "success": False,
                "action_id": action.action_id,
                "executed": False,
                "reason": "Authorized tool is not implemented.",
            }

        result = tool(action.arguments)

        return {
            "success": True,
            "action_id": action.action_id,
            "executed": True,
            "result": result,
        }
