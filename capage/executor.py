"""Governed execution boundary for CapAge proposed actions."""

from dataclasses import asdict
from typing import Any

from capage.audit import AuditLog
from capage.models import ProposedAction
from capage.policy import PolicyEngine
from capage.tools import TOOLS


class Executor:
    """Authorize, execute, and audit proposed CapAge actions.

    The executor is the trusted boundary between agent intent and tool
    execution. A ProposedAction never executes merely because it exists:
    every action is evaluated by the policy engine first.
    """

    def __init__(
        self,
        policy: PolicyEngine,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.policy = policy
        self.audit_log = audit_log or AuditLog()

    def execute(self, action: ProposedAction) -> dict[str, Any]:
        """Evaluate an action, execute it if authorized, and record the result."""

        self.audit_log.record("action_proposed", asdict(action))

        decision = self.policy.evaluate(action)
        self.audit_log.record(
            "policy_decision",
            {
                "action_id": action.action_id,
                "allowed": decision.allowed,
                "reason": decision.reason,
            },
        )

        if not decision.allowed:
            result = {
                "success": False,
                "action_id": action.action_id,
                "status": "denied",
                "reason": decision.reason,
            }
            self.audit_log.record("action_denied", result)
            return result

        tool = TOOLS.get(action.tool_name)
        if tool is None:
            result = {
                "success": False,
                "action_id": action.action_id,
                "status": "failed",
                "reason": f"Authorized tool '{action.tool_name}' is not registered.",
            }
            self.audit_log.record("action_failed", result)
            return result

        try:
            tool_result = tool(action.arguments)
        except Exception as exc:
            result = {
                "success": False,
                "action_id": action.action_id,
                "status": "failed",
                "reason": f"Tool execution failed: {type(exc).__name__}: {exc}",
            }
            self.audit_log.record("action_failed", result)
            return result

        result = {
            "success": True,
            "action_id": action.action_id,
            "status": "executed",
            "tool_result": tool_result,
        }
        self.audit_log.record("action_executed", result)
        return result
