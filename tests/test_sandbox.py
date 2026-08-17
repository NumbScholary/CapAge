"""Boundary, replay, accounting, and causal-flow tests for sandbox v1."""

from copy import deepcopy

from capage.audit import AuditLog
from capage.executor import Executor
from capage.models import ProposedAction
from capage.policy import PolicyEngine
from capage.sandbox import (
    EconomicSandbox,
    TokenTariff,
    aggregate_outcomes,
    verify_cost_policy,
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
    assert "sandbox.quote_model_call" not in tools
    assert "sandbox.record_model_usage" not in tools

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


def test_token_usage_is_metered_from_a_frozen_tariff_and_debited():
    tariff = TokenTariff(
        name="test-tariff",
        input_cents_per_million_tokens=300,
        output_cents_per_million_tokens=1_500,
    )
    world = EconomicSandbox(13, token_tariff=tariff)

    quote = world.quote_model_call(input_tokens=1_000, max_output_tokens=500)
    assert quote["worst_case_incremental_cost_cents"] == 2
    assert quote["affordable"] is True
    usage = world.record_model_usage(
        "model-call-001",
        input_tokens=1_000,
        output_tokens=500,
    )

    ledger = world.inspect_ledger()
    assert [entry["entry_type"] for entry in ledger["entries"]] == [
        "owner_capital",
        "model_api_cost",
    ]
    assert usage.incremental_billed_cents == 2
    assert ledger["capital"]["balance_cents"] == 24_998
    assert ledger["capital"]["expense_cents"] == 2
    assert ledger["capital"]["model_input_tokens"] == 1_000
    assert ledger["capital"]["model_output_tokens"] == 500
    assert ledger["model_usage"][0]["tariff_name"] == "test-tariff"


def test_subcent_token_usage_accumulates_without_per_call_rounding():
    tariff = TokenTariff(
        name="low-cost-test",
        input_cents_per_million_tokens=1,
        output_cents_per_million_tokens=1,
    )
    world = EconomicSandbox(13, token_tariff=tariff)

    for index in range(10):
        world.record_model_usage(
            f"model-call-{index:03d}",
            input_tokens=100_000,
            output_tokens=0,
        )

    ledger = world.inspect_ledger()
    model_postings = [
        entry for entry in ledger["entries"] if entry["entry_type"] == "model_api_cost"
    ]
    assert ledger["capital"]["model_api_cost_units"] == 1_000_000
    assert ledger["capital"]["model_api_cost_cents"] == 1
    assert ledger["capital"]["balance_cents"] == 24_999
    assert sum(-entry["amount_cents"] for entry in model_postings) == 1


def test_tariffs_change_cost_commitment_but_not_the_seeded_world():
    cheap = TokenTariff("cheap", 100, 200)
    expensive = TokenTariff("expensive", 300, 1_500)
    cheap_world = EconomicSandbox(83, token_tariff=cheap)
    expensive_world = EconomicSandbox(83, token_tariff=expensive)

    assert cheap_world.world_commitment == expensive_world.world_commitment
    assert cheap_world.cost_policy_commitment != expensive_world.cost_policy_commitment


def test_unaffordable_model_call_is_visible_before_execution():
    tariff = TokenTariff("test", 300, 1_500)
    poor_world = EconomicSandbox(
        13,
        starting_capital_cents=1,
        token_tariff=tariff,
    )

    quote = poor_world.quote_model_call(
        input_tokens=1_000_000,
        max_output_tokens=1_000_000,
    )
    assert quote["affordable"] is False

    failed_search = poor_world.search_market({"query": "anything"})
    assert failed_search["ok"] is False
    assert poor_world.inspect_ledger()["capital"]["balance_cents"] == 1


def test_reveal_verifies_commitment_and_detects_tampering():
    tariff = TokenTariff("committed-test", 300, 1_500)
    world = EconomicSandbox(71, token_tariff=tariff)
    reveal = world.reveal_world()

    assert verify_world_reveal(reveal) is True
    assert verify_cost_policy(reveal) is True
    altered = deepcopy(reveal)
    altered["payload"]["events"][0]["magnitude"] += 1
    assert verify_world_reveal(altered) is False

    repriced = deepcopy(reveal)
    repriced["cost_policy"]["token_tariff"][
        "output_cents_per_million_tokens"
    ] += 1
    assert verify_cost_policy(repriced) is False


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
