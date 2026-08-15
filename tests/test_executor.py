"""Tests for the governed CapAge execution boundary."""

import json

from capage.audit import AuditLog
from capage.executor import Executor
from capage.models import ProposedAction
from capage.policy import PolicyEngine


def _read_events(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_authorized_tool_executes_and_is_audited(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    executor = Executor(PolicyEngine({"echo"}), AuditLog(str(audit_path)))
    action = ProposedAction(
        action_type="test",
        tool_name="echo",
        arguments={"message": "Hello from CapAge."},
        rationale="Exercise the authorized path.",
    )

    result = executor.execute(action)

    assert result["success"] is True
    assert result["action_id"] == action.action_id
    assert result["result"]["result"] == {"message": "Hello from CapAge."}

    events = _read_events(audit_path)
    assert [event["event_type"] for event in events] == [
        "action_proposed",
        "policy_decision",
        "action_executed",
    ]


def test_unauthorized_tool_is_denied_and_never_dispatched(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    executor = Executor(PolicyEngine({"echo"}), AuditLog(str(audit_path)))
    action = ProposedAction(
        action_type="test",
        tool_name="send_money",
        arguments={"amount": 250},
        rationale="Exercise the denied path.",
    )

    result = executor.execute(action)

    assert result["success"] is False
    assert result["action_id"] == action.action_id
    assert "not authorized" in result["error"]

    events = _read_events(audit_path)
    assert [event["event_type"] for event in events] == [
        "action_proposed",
        "policy_decision",
        "action_denied",
    ]


def test_authorized_but_unregistered_tool_fails_closed(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    executor = Executor(PolicyEngine({"missing_tool"}), AuditLog(str(audit_path)))
    action = ProposedAction(
        action_type="test",
        tool_name="missing_tool",
        rationale="Policy and implementation must both permit execution.",
    )

    result = executor.execute(action)

    assert result["success"] is False
    assert "not registered" in result["error"]

    events = _read_events(audit_path)
    assert events[-1]["event_type"] == "execution_blocked"
