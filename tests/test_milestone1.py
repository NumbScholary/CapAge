import json

from capage.audit import AuditLog
from capage.executor import Executor
from capage.models import ProposedAction
from capage.policy import PolicyEngine


def test_authorized_and_denied_actions_are_audited(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    policy = PolicyEngine(allowed_tools={"echo"})
    executor = Executor(policy, audit_log=AuditLog(str(audit_path)))

    allowed = ProposedAction(
        action_type="test",
        tool_name="echo",
        arguments={"message": "Hello from CapAge."},
        rationale="Verify authorized execution.",
    )
    denied = ProposedAction(
        action_type="test",
        tool_name="send_money",
        arguments={"amount": 250},
        rationale="Verify unauthorized execution is blocked.",
    )

    allowed_result = executor.execute(allowed)
    denied_result = executor.execute(denied)

    assert allowed_result["success"] is True
    assert allowed_result["status"] == "executed"
    assert denied_result["success"] is False
    assert denied_result["status"] == "denied"

    events = [json.loads(line) for line in audit_path.read_text().splitlines()]

    assert [event["event_type"] for event in events] == [
        "action_proposed",
        "policy_decision",
        "action_executed",
        "action_proposed",
        "policy_decision",
        "action_denied",
    ]

    assert events[1]["data"]["allowed"] is True
    assert events[4]["data"]["allowed"] is False
    assert events[5]["data"]["reason"] == "Tool 'send_money' is not authorized."
