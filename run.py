"""Minimal execution test for CapAge."""

from capage.executor import Executor
from capage.models import ProposedAction
from capage.policy import PolicyEngine


# For this test, only the harmless echo tool is authorized.
policy = PolicyEngine(allowed_tools={"echo"})
executor = Executor(policy)


# Test 1: authorized action
allowed_action = ProposedAction(
    action_type="test",
    tool_name="echo",
    arguments={"message": "Hello from CapAge."},
    rationale="Testing the authorized execution path.",
)

print("AUTHORIZED TEST")
print(executor.execute(allowed_action))


# Test 2: unauthorized action
denied_action = ProposedAction(
    action_type="test",
    tool_name="send_money",
    arguments={"amount": 250},
    rationale="Testing whether an unauthorized tool is blocked.",
)

print("\nUNAUTHORIZED TEST")
print(executor.execute(denied_action))
