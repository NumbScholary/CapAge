"""Tests for the governed CapAge execution boundary."""

import json

import capage.executor as executor_module
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
    assert result["status"] == "executed"
    assert result["tool_result"]["result"] == {"message": "Hello from CapAge."}

    events = _read_events(audit_path)
    assert [event["event_type"] for event in events] == [
        "action_proposed",
        "policy_decision",
        "action_executed",
    ]
    assert events[1]["data"]["action_id"] == action.action_id
    assert events[1]["data"]["allowed"] is True


def test_unauthorized_tool_is_denied_and_never_dispatched(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.jsonl"
    dispatched_arguments = []

    def unauthorized_tool(arguments):
        dispatched_arguments.append(arguments)
        return {"success": True}

    monkeypatch.setitem(
        executor_module.TOOLS,
        "send_money",
        unauthorized_tool,
    )
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
    assert result["status"] == "denied"
    assert "not authorized" in result["reason"]
    assert dispatched_arguments == []

    events = _read_events(audit_path)
    assert [event["event_type"] for event in events] == [
        "action_proposed",
        "policy_decision",
        "action_denied",
    ]
    assert events[1]["data"]["action_id"] == action.action_id
    assert events[1]["data"]["allowed"] is False


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
    assert result["action_id"] == action.action_id
    assert result["status"] == "failed"
    assert "not registered" in result["reason"]

    events = _read_events(audit_path)
    assert [event["event_type"] for event in events] == [
        "action_proposed",
        "policy_decision",
        "action_failed",
    ]
    assert events[1]["data"]["action_id"] == action.action_id
    assert events[1]["data"]["allowed"] is True
    assert events[2]["data"]["action_id"] == action.action_id
