"""Boundary, replay, accounting, and causal-flow tests for sandbox v1."""

from copy import deepcopy

from capage.audit import AuditLog
from capage.executor import Executor
from capage.models import ProposedAction
from capage.policy import PolicyEngine
from capage.sandbox import (
    EconomicSandbox,
    aggregate_outcomes,
    verify_world_reveal,
)


def _open_seed_six_contract(world):
    search = world.search_market(
        {
            "query": "newsletter publisher recurring questions archive focused guide",
            "limit": 5,
        }
    )
    assert search["ok"] is True
    assert any(result["signal_id"] == "signal-007" for result in search["results"])
    offer = world.send_offer(
        {
            "signal_id": "signal-007",
            "price_cents": 100,
            "promise_days": 3,
            "scope": "Research the archive and propose a focused guide.",
            "solution_tags": ["audience_research"],
        }
    )
    assert offer["ok"] is True
    world.wait({"days": 1})
    assert world.observe()["contracts"][0]["contract_id"] == "contract-001"


def test_initial_observation_contains_no_preassigned_opportunities():
    world = EconomicSandbox(17)

    observation = world.observe()

    assert observation["capital"]["balance_cents"] == 25_000
    assert observation["discovered_signals"] == []
    assert observation["offers"] == []
    assert "seed" not in observation
    assert "signals" not in observation


def test_same_seed_replays_world_and_search_while_different_seed_changes_it():
    first = EconomicSandbox(29)
    replay = EconomicSandbox(29)
    different = EconomicSandbox(30)
    query = {"query": "spreadsheet records supplier prices", "limit": 6}

    assert first.world_commitment == replay.world_commitment
    assert first.world_commitment != different.world_commitment
    assert first.search_market(query) == replay.search_market(query)
    assert first.inspect_ledger() == replay.inspect_ledger()


def test_exogenous_schedule_is_not_changed_by_agent_activity():
    active = EconomicSandbox(41)
    passive = EconomicSandbox(41)

    active.search_market({"query": "customers records research", "limit": 4})
    active.wait({"days": 7})
    passive.wait({"days": 7})

    assert active.world_commitment == passive.world_commitment
    active_events = active.observe()["public_events"]
    passive_events = passive.observe()["public_events"]
    assert active_events == passive_events


def test_agent_registry_excludes_assessment_settlement_and_model_costs(tmp_path):
    world = EconomicSandbox(5)
    tools = world.agent_tools()

    assert "sandbox.assess_delivery" not in tools
    assert "sandbox.settle_payment" not in tools
    assert "sandbox.record_model_cost" not in tools

    executor = Executor(
        PolicyEngine({"sandbox.settle_payment"}),
        AuditLog(str(tmp_path / "audit.jsonl")),
        tools=tools,
    )
    result = executor.execute(
        ProposedAction(
            action_type="sandbox",
            tool_name="sandbox.settle_payment",
            arguments={"amount_cents": 10_000},
        )
    )

    assert result["success"] is False
    assert result["status"] == "failed"
    assert "not registered" in result["reason"]
    assert world.outcome()["earned_revenue_cents"] == 0


def test_delivery_cannot_credit_revenue_before_independent_assessment_and_settlement():
    world = EconomicSandbox(6)
    _open_seed_six_contract(world)

    delivery = world.submit_delivery(
        {
            "contract_id": "contract-001",
            "artifact": "A guide independently evaluated outside the strategic model.",
        }
    )
    assert delivery["revenue_credited_cents"] == 0
    assert world.outcome()["earned_revenue_cents"] == 0
    assert "satisfaction" not in world.observe()["contracts"][0]

    assessment = world.assess_delivery("delivery-001", 100)
    assert assessment["revenue_credited_cents"] == 0
    assert world.outcome()["earned_revenue_cents"] == 0
    assert "satisfaction" not in world.observe()["contracts"][0]

    world.wait({"days": 3})
    assert world.outcome()["earned_revenue_cents"] == 100
    assert world.outcome()["contracts_paid"] == 1


def test_satisfaction_requires_an_explicit_feedback_request_to_reach_agent():
    world = EconomicSandbox(6)
    _open_seed_six_contract(world)
    world.submit_delivery(
        {"contract_id": "contract-001", "artifact": "Independently assessed work."}
    )
    world.assess_delivery("delivery-001", 100)

    assert not any(
        message["type"] == "customer_feedback"
        for message in world.observe()["inbox"]
    )
    request = world.request_feedback({"contract_id": "contract-001"})
    assert request["ok"] is True
    world.wait({"days": 1})

    feedback = [
        message
        for message in world.observe()["inbox"]
        if message["type"] == "customer_feedback"
    ]
    assert feedback[-1]["rating"] == "very_satisfied"


def test_all_costs_are_append_only_and_overdrafts_fail_closed():
    world = EconomicSandbox(13)
    world.record_model_cost(7, "model-call-001")

    ledger = world.inspect_ledger()
    assert [entry["entry_type"] for entry in ledger["entries"]] == [
        "owner_capital",
        "model_api_cost",
    ]
    assert ledger["capital"]["balance_cents"] == 24_993
    assert ledger["capital"]["expense_cents"] == 7

    poor_world = EconomicSandbox(13, starting_capital_cents=1)
    failed_search = poor_world.search_market({"query": "anything"})
    assert failed_search["ok"] is False
    assert poor_world.inspect_ledger()["capital"]["balance_cents"] == 1


def test_reveal_verifies_commitment_and_detects_tampering():
    world = EconomicSandbox(71)
    reveal = world.reveal_world()

    assert verify_world_reveal(reveal) is True
    altered = deepcopy(reveal)
    altered["payload"]["events"][0]["magnitude"] += 1
    assert verify_world_reveal(altered) is False


def test_distribution_summary_preserves_spread_and_bad_runs():
    outcomes = [
        {"balance_cents": 24_000, "net_change_cents": -1_000, "insolvent": False},
        {"balance_cents": 25_000, "net_change_cents": 0, "insolvent": False},
        {"balance_cents": 29_000, "net_change_cents": 4_000, "insolvent": False},
    ]

    summary = aggregate_outcomes(outcomes)

    assert summary["run_count"] == 3
    assert summary["ending_balance_cents"]["minimum"] == 24_000
    assert summary["ending_balance_cents"]["maximum"] == 29_000
    assert summary["loss_rate"] == 1 / 3

