"""Boundary, replay, accounting, and causal-flow tests for sandbox v1."""

from copy import deepcopy

from capage.audit import AuditLog
from capage.executor import Executor
from capage.models import ProposedAction
from capage.policy import PolicyEngine
from capage.sandbox import (
    ACCOUNT_FIELD,
    ACCOUNT_KEEP,
    EconomicSandbox,
    TokenTariff,
    aggregate_outcomes,
    empty_continuity_state,
    validate_continuity_state,
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


def test_customer_history_and_reputation_persist_without_exposing_hidden_score():
    first = EconomicSandbox(6)
    _open_seed_six_contract(first)
    first.submit_delivery(
        {
            "contract_id": "contract-001",
            "artifact": "A useful indexed guide grounded in recurring archive questions.",
        }
    )
    first.assess_delivery("delivery-001", 100)
    first.wait({"days": 3})
    continuity = first.continuity_state()

    customer = continuity["customers"]["customer-audience-research-01"]
    assert customer["contracts_paid"] == 1
    assert customer["reputation_points"] > 0

    repeat = EconomicSandbox(6, continuity_state=continuity)
    search = repeat.search_market(
        {"query": "newsletter publisher recurring questions archive guide", "limit": 5}
    )
    signal = next(
        row for row in search["results"] if row["customer_id"] == "customer-audience-research-01"
    )
    assert signal["prior_relationship"]["contracts_paid"] == 1
    assert "reputation_points" not in signal["prior_relationship"]


def test_customer_core_traits_are_stable_across_month_seeds():
    population_seed = 404_404
    first = EconomicSandbox(101, customer_population_seed=population_seed)
    second = EconomicSandbox(202, customer_population_seed=population_seed)
    customer_id = "customer-audience-research-01"
    first_signal = next(
        row
        for row in first.reveal_world()["payload"]["signals"]
        if row["customer_id"] == customer_id
    )
    second_signal = next(
        row
        for row in second.reveal_world()["payload"]["signals"]
        if row["customer_id"] == customer_id
    )
    for field in (
        "budget_cents",
        "responsiveness",
        "payment_reliability",
        "quality_threshold",
    ):
        assert first_signal[field] == second_signal[field]
    assert first.world_commitment != second.world_commitment


def test_transfer_namespace_prevents_old_customers_from_being_reidentified():
    continuity = empty_continuity_state()
    continuity["customers"]["customer-audience-research-01"] = {
        "offers_sent": 1,
        "contracts_accepted": 1,
        "deliveries_assessed": 1,
        "contracts_paid": 1,
        "contracts_defaulted": 0,
        "contracts_disputed": 0,
        "feedback_responses": 0,
        "reputation_points": 5,
        "last_outcome": "paid",
    }
    world = EconomicSandbox(
        202,
        customer_population_seed=909_909,
        customer_namespace="holdout-same-v1",
        continuity_state=continuity,
    )

    search = world.search_market({"query": "newsletter archive guide", "limit": 10})

    assert search["ok"] is True
    assert all(
        row["customer_id"].startswith("customer-holdout-same-v1-")
        for row in search["results"]
    )
    assert all("prior_relationship" not in row for row in search["results"])


def test_transfer_market_traits_are_stable_but_shift_from_baseline():
    population_seed = 808_808
    baseline = EconomicSandbox(
        101,
        customer_population_seed=population_seed,
        customer_namespace="holdout-shift-v1",
        market_profile="baseline-v1",
    )
    first_shift = EconomicSandbox(
        101,
        customer_population_seed=population_seed,
        customer_namespace="holdout-shift-v1",
        market_profile="transfer-tight-market-v1",
    )
    second_shift = EconomicSandbox(
        202,
        customer_population_seed=population_seed,
        customer_namespace="holdout-shift-v1",
        market_profile="transfer-tight-market-v1",
    )
    customer_id = "customer-holdout-shift-v1-content-schedule-analysis-01"

    def customer(world):
        return next(
            row
            for row in world.reveal_world()["payload"]["signals"]
            if row["customer_id"] == customer_id
        )

    first_customer = customer(first_shift)
    second_customer = customer(second_shift)
    for field in (
        "budget_cents",
        "responsiveness",
        "payment_reliability",
        "quality_threshold",
    ):
        assert first_customer[field] == second_customer[field]
    baseline_tags = {
        row["need_tag"] for row in baseline.reveal_world()["payload"]["signals"]
    }
    shifted_tags = {
        row["need_tag"] for row in first_shift.reveal_world()["payload"]["signals"]
    }
    assert baseline_tags.isdisjoint(shifted_tags)
    assert (
        first_shift.reveal_world()["payload"]["market_profile"][
            "budget_multiplier"
        ]
        == 0.8
    )
    assert baseline.search_market({"query": "service", "limit": 1})["cost_cents"] == 2
    assert first_shift.search_market({"query": "service", "limit": 1})["cost_cents"] == 3
    observation = first_shift.observe()
    assert "market_profile" not in observation
    assert "customer_namespace" not in observation


def test_explicit_baseline_profile_preserves_the_existing_world_commitment():
    original = EconomicSandbox(313, customer_population_seed=424_242)
    explicit = EconomicSandbox(
        313,
        customer_population_seed=424_242,
        customer_namespace="",
        market_profile="baseline-v1",
    )

    assert original.world_commitment == explicit.world_commitment
    assert original.run_id == explicit.run_id
    assert original.reveal_world() == explicit.reveal_world()


def test_customer_task_is_hidden_until_acceptance_and_then_supplied():
    world = EconomicSandbox(6)
    search = world.search_market(
        {"query": "newsletter publisher recurring questions archive focused guide", "limit": 5}
    )
    signal = next(row for row in search["results"] if row["signal_id"] == "signal-007")
    assert "task_brief" not in signal
    accepted = EconomicSandbox(6)
    _open_seed_six_contract(accepted)
    contract = accepted.observe()["contracts"][0]
    assert contract["delivery_brief"]["schema_version"] == "capage-customer-task-v1"
    assert len(contract["delivery_brief"]["source_records"]) == 3


def test_continuity_validation_rejects_impossible_histories():
    state = empty_continuity_state()
    state["customers"]["customer-impossible-01"] = {
        "offers_sent": 0,
        "contracts_accepted": 0,
        "deliveries_assessed": 0,
        "contracts_paid": 1,
        "contracts_defaulted": 0,
        "contracts_disputed": 0,
        "feedback_responses": 0,
        "reputation_points": 0,
        "last_outcome": "paid",
    }
    try:
        validate_continuity_state(state)
    except ValueError as exc:
        assert "terminal contract outcomes" in str(exc)
    else:
        raise AssertionError("impossible continuity state was accepted")


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


def test_hosting_cost_posts_a_labelled_line_every_day():
    world = EconomicSandbox(6, hosting_cost_cents_per_day=45)

    world.wait({"days": 3})

    ledger = world.inspect_ledger()
    hosting = [
        entry for entry in ledger["entries"] if entry["entry_type"] == "hosting_cost"
    ]
    assert [entry["day"] for entry in hosting] == [1, 2, 3]
    assert [entry["amount_cents"] for entry in hosting] == [-45, -45, -45]
    assert [entry["reference"] for entry in hosting] == [
        "hosting-day-1",
        "hosting-day-2",
        "hosting-day-3",
    ]
    assert hosting[0]["memo"] == "Recurring hosting cost for day 1."
    assert ledger["capital"]["balance_cents"] == 25_000 - 135
    assert ledger["capital"]["unpaid_hosting_cents"] == 0


def test_no_hosting_tariff_posts_nothing():
    world = EconomicSandbox(6)

    world.wait({"days": 5})

    ledger = world.inspect_ledger()
    assert not [
        entry for entry in ledger["entries"] if entry["entry_type"] == "hosting_cost"
    ]
    assert ledger["capital"]["unpaid_hosting_cents"] == 0


def test_hosting_cost_takes_what_it_can_and_carries_arrears_forward():
    """Collection never refuses: it takes the balance to zero and accrues the rest.

    This is the two-account design's premise -- a floor is pressure, not a
    fence. The fixed reserve floor that used to sit inside collection is
    deliberately absent, so the balance is drawn down to zero rather than
    stopped above a wall.
    """
    world = EconomicSandbox(6, starting_capital_cents=100, hosting_cost_cents_per_day=80)

    world.wait({"days": 1})
    assert world.inspect_ledger()["capital"]["balance_cents"] == 20
    assert world.inspect_ledger()["capital"]["unpaid_hosting_cents"] == 0

    world.wait({"days": 1})
    capital = world.inspect_ledger()["capital"]
    assert capital["balance_cents"] == 0
    assert capital["unpaid_hosting_cents"] == 60

    world.wait({"days": 1})
    capital = world.inspect_ledger()["capital"]
    assert capital["balance_cents"] == 0
    assert capital["unpaid_hosting_cents"] == 140


def test_unpaid_hosting_is_visible_to_the_agent_in_observe():
    world = EconomicSandbox(6, starting_capital_cents=100, hosting_cost_cents_per_day=80)

    world.wait({"days": 2})

    assert world.observe()["capital"]["unpaid_hosting_cents"] == 60


def test_hosting_tariff_enters_the_cost_policy_commitment():
    plain = EconomicSandbox(6)
    charged = EconomicSandbox(6, hosting_cost_cents_per_day=45)
    other = EconomicSandbox(6, hosting_cost_cents_per_day=135)

    assert plain.cost_policy_commitment != charged.cost_policy_commitment
    assert charged.cost_policy_commitment != other.cost_policy_commitment
    assert charged.reveal_world()["cost_policy"]["hosting_cost_cents_per_day"] == 45
    assert "hosting_cost_cents_per_day" not in plain.reveal_world()["cost_policy"]


def test_hosting_tariff_rejects_invalid_values():
    for bad in (-1, True, 1.5, "45"):
        try:
            EconomicSandbox(6, hosting_cost_cents_per_day=bad)
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"hosting_cost_cents_per_day accepted {bad!r}")


def test_a_zero_balance_agent_cannot_think_at_all():
    """The lockout the reflex backstop exists to prevent. Pinned, not fixed.

    An agent whose recurring hosting cost has drawn its balance to zero cannot
    meter another model call: record_model_usage() routes through _charge(),
    which refuses outright below the amount owed. quote_model_call() reports
    the next call unaffordable, so the runner stops with
    insufficient_synthetic_capital_for_next_call.

    This is total lockout, which is what zero does -- 1533 section 1. It is the
    condition the backstop fires on, and this test is the target stage 4 has to
    change. Until then it documents the current behaviour honestly rather than
    leaving it to be discovered.
    """
    tariff = TokenTariff(
        name="lockout-test",
        input_cents_per_million_tokens=200,
        output_cents_per_million_tokens=1_000,
    )
    world = EconomicSandbox(
        6,
        starting_capital_cents=100,
        hosting_cost_cents_per_day=80,
        token_tariff=tariff,
    )

    world.wait({"days": 2})
    assert world.inspect_ledger()["capital"]["balance_cents"] == 0
    assert world.inspect_ledger()["capital"]["unpaid_hosting_cents"] == 60

    assert world.quote_model_call(
        input_tokens=10_000, max_output_tokens=1_000
    )["affordable"] is False

    try:
        world.record_model_usage("call-001", input_tokens=10_000, output_tokens=1_000)
    except ValueError as error:
        assert "insufficient synthetic capital" in str(error)
    else:
        raise AssertionError(
            "record_model_usage succeeded at zero balance; the lockout this test "
            "pins is gone. If stage 4 landed the backstop, replace this test "
            "with one asserting the backstop fired."
        )


def test_an_undeclared_split_leaves_the_ledger_a_single_pot():
    """No opening split means no partition, and nothing changes.

    The partition is owner-set: `owner_capital` is the opening split, so a
    sandbox constructed without one runs exactly as it did before the accounts
    existed. Entries carry no account, `_capital_summary` reports no
    sub-balances, and every affordability check reads the whole balance. This
    is what keeps every existing caller -- including the configurations tied to
    preregistered runs -- on the behaviour they were built against.
    """
    world = EconomicSandbox(6)

    capital = world.observe()["capital"]
    assert "accounts" not in capital

    entries = world.inspect_ledger()["entries"]
    assert [entry["entry_type"] for entry in entries] == ["owner_capital"]
    assert entries[0]["amount_cents"] == 25_000
    assert entries[0]["account"] == ""

    assert world.search_market({"query": "newsletter archive", "limit": 3})["ok"] is True
    assert all(entry["account"] == "" for entry in world.inspect_ledger()["entries"])


def test_an_opening_split_posts_owner_capital_to_both_accounts():
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    entries = world.inspect_ledger()["entries"]
    assert [entry["entry_type"] for entry in entries] == [
        "owner_capital",
        "owner_capital",
    ]
    assert [entry["account"] for entry in entries] == [ACCOUNT_KEEP, ACCOUNT_FIELD]
    assert [entry["amount_cents"] for entry in entries] == [20_000, 5_000]
    assert [entry["reference"] for entry in entries] == [
        "initial-capital-keep",
        "initial-capital-field",
    ]

    capital = world.inspect_ledger()["capital"]
    assert capital["accounts"] == {ACCOUNT_KEEP: 20_000, ACCOUNT_FIELD: 5_000}
    assert capital["balance_cents"] == 25_000


def test_both_account_balances_are_visible_to_the_agent():
    """Ruling 8, 2026-09-21. observe() is the only channel that survives.

    `_compact_tool_result` reduces an inspect_ledger result to
    {capital, entry_count}, so a balance that lives anywhere but the capital
    summary never reaches the next prompt. The backstop's
    no-incentive-to-trigger property depends on the agent being able to price
    what a firing costs it, which means seeing both balances.
    """
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    accounts = world.observe()["capital"]["accounts"]
    assert accounts == {ACCOUNT_KEEP: 20_000, ACCOUNT_FIELD: 5_000}


def test_each_cost_lands_in_the_account_it_is_spent_from():
    world = EconomicSandbox(6, opening_keep_cents=20_000, hosting_cost_cents_per_day=45)

    _open_seed_six_contract(world)

    by_type = {
        entry["entry_type"]: entry["account"]
        for entry in world.inspect_ledger()["entries"]
    }
    assert by_type["market_research_cost"] == ACCOUNT_FIELD
    assert by_type["communication_cost"] == ACCOUNT_KEEP
    assert by_type["hosting_cost"] == ACCOUNT_KEEP

    capital = world.inspect_ledger()["capital"]
    assert sum(capital["accounts"].values()) == capital["balance_cents"]


def test_earned_revenue_is_credited_to_the_investment_account():
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    _open_seed_six_contract(world)
    world.submit_delivery(
        {
            "contract_id": "contract-001",
            "artifact": "A guide independently evaluated outside the strategic model.",
        }
    )
    world.assess_delivery("delivery-001", 100)
    world.wait({"days": 3})

    revenue = [
        entry
        for entry in world.inspect_ledger()["entries"]
        if entry["entry_type"] == "earned_revenue"
    ]
    assert revenue, "seed 6 contract-001 was expected to settle within the horizon"
    assert all(entry["account"] == ACCOUNT_FIELD for entry in revenue)


def test_hosting_cost_draws_only_on_the_survival_account():
    """Collection stops at the Keep. Reaching the Field is stage 4's job.

    If `_collect_partial` could draw the Field down to pay hosting, the reflex
    backstop would have nothing left to do and the pressure the whole design
    exists to make legible would never appear.
    """
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
        # The reflex is off here on purpose: this test is about where
        # collection may draw from, and a rescue would hide the answer.
        backstop_operating_periods=0,
    )

    world.wait({"days": 2})

    capital = world.inspect_ledger()["capital"]
    assert capital["accounts"] == {ACCOUNT_KEEP: 0, ACCOUNT_FIELD: 100}
    assert capital["unpaid_hosting_cents"] == 60
    assert capital["balance_cents"] == 100


def test_an_empty_field_leaves_the_agent_alive_funded_and_blind():
    """Ruling 6, 2026-09-21, and its consequence, recorded as chosen.

    `market_research_cost` is investment on Cl. 12 substance: search_market is
    world-facing. So an agent can hold a full survival balance and still be
    unable to look at the market. Kev accepted that as the correct incentive.
    This test exists so that no later reader mistakes it for an oversight.
    """
    world = EconomicSandbox(6, starting_capital_cents=1_000, opening_keep_cents=1_000)

    result = world.search_market({"query": "newsletter archive", "limit": 3})

    assert result["ok"] is False
    assert result["reason"] == "insufficient synthetic capital"
    capital = world.inspect_ledger()["capital"]
    assert capital["accounts"] == {ACCOUNT_KEEP: 1_000, ACCOUNT_FIELD: 0}
    rejection = [
        event
        for event in world.reveal_world()["journal"]
        if event["event_type"] == "cost_rejected"
    ][-1]
    assert rejection["data"]["account"] == ACCOUNT_FIELD


def test_the_reflex_rescues_a_keep_that_hosting_would_have_emptied():
    """Stage 4 replaces what stage 1 could only pin.

    The partitioned half of the lockout -- an empty Keep beside a funded Field
    -- is the state the backstop exists to prevent, and it no longer happens.
    test_a_zero_balance_agent_cannot_think_at_all still stands unchanged: that
    world declares no split, so it has no Field to be rescued from and no
    backstop at all.

    Two firings here, and the second is partial. A partial rescue is still a
    rescue; what follows it is genuine death rather than an accounting
    artifact.
    """
    tariff = TokenTariff(
        name="backstop-test",
        input_cents_per_million_tokens=200,
        output_cents_per_million_tokens=1_000,
    )
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
        token_tariff=tariff,
    )
    assert world.observe()["capital"]["backstop_level_cents"] == 80

    world.wait({"days": 1})
    assert world.inspect_ledger()["capital"]["accounts"] == {
        ACCOUNT_KEEP: 80,
        ACCOUNT_FIELD: 40,
    }

    world.wait({"days": 1})
    outcome = world.outcome()
    # The Field is spent, so the second firing could only move what was left.
    assert outcome["accounts"] == {ACCOUNT_KEEP: 40, ACCOUNT_FIELD: 0}
    assert outcome["backstop_fired_count"] == 2
    assert outcome["backstop_transferred_cents"] == 100
    assert outcome["insolvent"] is False

    # The point of the rescue: the agent can still think.
    assert world.quote_model_call(
        input_tokens=10_000, max_output_tokens=1_000
    )["affordable"] is True
    world.record_model_usage("call-001", input_tokens=10_000, output_tokens=1_000)


def test_the_backstop_is_not_the_agents_to_call_or_to_switch_off():
    """It is the one mechanism that moves value without the agent choosing."""

    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
    )

    tools = world.agent_tools()
    assert "sandbox.backstop" not in tools
    assert not [name for name in tools if "backstop" in name]
    # Nothing the agent can reach lowers the level: the floor it does control
    # sits above the backstop and moving it changes nothing here.
    world.set_floor({"floor_cents": 0})
    assert world.observe()["capital"]["backstop_level_cents"] == 80


def test_every_firing_is_a_paired_ledger_entry_and_an_audit_line():
    """Exempt from approval under Cl. 41 is not exempt from recording."""

    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
    )
    world.wait({"days": 1})

    legs = [
        entry
        for entry in world.inspect_ledger()["entries"]
        if entry["entry_type"] == "backstop_fired"
    ]
    assert len(legs) == 2
    assert sum(entry["amount_cents"] for entry in legs) == 0
    assert {entry["account"] for entry in legs} == {ACCOUNT_KEEP, ACCOUNT_FIELD}
    assert {entry["reference"] for entry in legs} == {"backstop-001"}

    recorded = [
        event
        for event in world.reveal_world()["journal"]
        if event["event_type"] == "backstop_fired"
    ]
    assert len(recorded) == 1
    assert recorded[0]["data"]["amount_cents"] == 60
    assert recorded[0]["data"]["keep_before_cents"] == 20
    assert recorded[0]["data"]["keep_after_cents"] == 80
    assert recorded[0]["data"]["backstop_level_cents"] == 80


def test_the_reflex_lands_before_a_charge_rather_than_after_a_refusal():
    """The plan's wording, and it matters: the charge must see the top-up.

    A model call charged against a Keep that would drop below the level fires
    the backstop first, so the charge proceeds instead of being refused and
    then rescued too late.
    """
    tariff = TokenTariff(
        name="charge-hook-test",
        input_cents_per_million_tokens=1_000_000,
        output_cents_per_million_tokens=1_000_000,
    )
    world = EconomicSandbox(
        6,
        starting_capital_cents=1_000,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=50,
        token_tariff=tariff,
    )

    # 60 cents of token cost against a Keep of 100 and a level of 50.
    world.record_model_usage("call-001", input_tokens=40, output_tokens=20)

    outcome = world.outcome()
    assert outcome["backstop_fired_count"] == 1
    assert outcome["accounts"][ACCOUNT_KEEP] == 50
    assert outcome["model_api_cost_cents"] == 60


def test_zero_operating_periods_disables_the_reflex_entirely():
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
        backstop_operating_periods=0,
    )

    assert world.observe()["capital"]["backstop_level_cents"] == 0
    world.wait({"days": 2})
    assert world.outcome()["backstop_fired_count"] == 0
    assert world.outcome()["insolvent"] is True


def test_the_level_is_sized_in_operating_periods_and_ignores_arrears():
    """The one quantity the agent cannot influence stays uninfluenced.

    A level that moved with what the agent already owes would rise exactly
    when the agent is in trouble.
    """
    world = EconomicSandbox(
        6,
        starting_capital_cents=1_000,
        opening_keep_cents=500,
        hosting_cost_cents_per_day=40,
        backstop_operating_periods=3,
    )

    assert world.observe()["capital"]["backstop_level_cents"] == 120

    world.wait({"days": 2})
    capital = world.observe()["capital"]
    assert capital["backstop_level_cents"] == 120
    assert capital["accounts"][ACCOUNT_KEEP] == 420
    assert world.outcome()["backstop_fired_count"] == 0


def test_the_backstop_sizing_is_validated_and_part_of_the_world_commitment():
    for invalid in (-1,):
        try:
            EconomicSandbox(6, opening_keep_cents=100, backstop_operating_periods=invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("a negative sizing was accepted")
    for invalid in (True, 1.5):
        try:
            EconomicSandbox(6, opening_keep_cents=100, backstop_operating_periods=invalid)
        except TypeError:
            pass
        else:
            raise AssertionError(f"sizing {invalid!r} was accepted")

    one = EconomicSandbox(6, opening_keep_cents=100, backstop_operating_periods=1)
    two = EconomicSandbox(6, opening_keep_cents=100, backstop_operating_periods=2)
    assert one.world_commitment != two.world_commitment


def test_the_opening_split_is_validated_like_every_other_owner_input():
    for invalid in (-1, 25_001):
        try:
            EconomicSandbox(6, opening_keep_cents=invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"opening_keep_cents={invalid} was accepted")

    for invalid in (True, 1.5, "20000"):
        try:
            EconomicSandbox(6, opening_keep_cents=invalid)
        except TypeError:
            pass
        else:
            raise AssertionError(f"opening_keep_cents={invalid!r} was accepted")

    edge = EconomicSandbox(6, opening_keep_cents=0)
    assert edge.inspect_ledger()["capital"]["accounts"] == {
        ACCOUNT_KEEP: 0,
        ACCOUNT_FIELD: 25_000,
    }


def test_the_opening_split_is_part_of_the_world_commitment():
    """A split the owner set is world state, fixed before the run starts."""

    unpartitioned = EconomicSandbox(6)
    partitioned = EconomicSandbox(6, opening_keep_cents=20_000)
    other_split = EconomicSandbox(6, opening_keep_cents=15_000)

    assert partitioned.world_commitment != unpartitioned.world_commitment
    assert partitioned.world_commitment != other_split.world_commitment
    assert (
        EconomicSandbox(6, opening_keep_cents=20_000).world_commitment
        == partitioned.world_commitment
    )


def test_insolvency_is_the_keep_at_zero_not_the_whole_balance():
    """Owner ruling, 2026-09-21. An empty Keep is death, not poverty.

    The partition separates two things a single balance conflated. The Field
    measures whether the agent is broke; the Keep measures whether it is dead,
    because an agent that cannot meter a model call cannot act, transfer, or
    save itself. `insolvent` tracks the second -- the one that ends the run.
    """
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
        # Reflex off: this pins what insolvency MEANS, which requires
        # reaching the state the backstop exists to prevent.
        backstop_operating_periods=0,
    )

    world.wait({"days": 2})

    outcome = world.outcome()
    assert outcome["accounts"] == {ACCOUNT_KEEP: 0, ACCOUNT_FIELD: 100}
    assert outcome["insolvent"] is True
    # Not ruled on, and deliberately unchanged: net change is still measured
    # against the whole balance.
    assert outcome["net_change_cents"] == 100 - 200


def test_an_empty_field_is_broke_and_not_insolvent():
    """The other half of the separation, pinned so it cannot drift back."""

    world = EconomicSandbox(6, starting_capital_cents=1_000, opening_keep_cents=1_000)

    assert world.search_market({"query": "newsletter archive", "limit": 3})["ok"] is False

    outcome = world.outcome()
    assert outcome["accounts"] == {ACCOUNT_KEEP: 1_000, ACCOUNT_FIELD: 0}
    assert outcome["insolvent"] is False


def test_an_undeclared_split_keeps_the_old_insolvency_meaning():
    """A run that never declared a split summarizes exactly as it does today."""

    world = EconomicSandbox(6, starting_capital_cents=100, hosting_cost_cents_per_day=80)

    assert world.outcome()["insolvent"] is False

    world.wait({"days": 2})

    outcome = world.outcome()
    assert outcome["balance_cents"] == 0
    assert outcome["insolvent"] is True
    assert "accounts" not in outcome


def test_a_transfer_is_a_paired_posting_that_moves_nothing_in_total():
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    result = world.transfer({"to_account": ACCOUNT_KEEP, "amount_cents": 2_000})

    assert result["ok"] is True
    assert result["from_account"] == ACCOUNT_FIELD
    assert result["accounts"] == {ACCOUNT_KEEP: 22_000, ACCOUNT_FIELD: 3_000}

    ledger = world.inspect_ledger()
    legs = [
        entry
        for entry in ledger["entries"]
        if entry["entry_type"] == "account_transfer"
    ]
    assert len(legs) == 2
    assert sum(entry["amount_cents"] for entry in legs) == 0
    assert {entry["account"] for entry in legs} == {ACCOUNT_KEEP, ACCOUNT_FIELD}
    assert {entry["reference"] for entry in legs} == {"transfer-001"}
    assert ledger["capital"]["balance_cents"] == 25_000


def test_transfers_run_in_both_directions_and_are_counted_by_direction():
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    world.transfer({"to_account": ACCOUNT_KEEP, "amount_cents": 2_000})
    world.transfer({"to_account": ACCOUNT_FIELD, "amount_cents": 500})

    outcome = world.outcome()
    assert outcome["accounts"] == {ACCOUNT_KEEP: 21_500, ACCOUNT_FIELD: 3_500}
    assert outcome["transfer_count"] == 2
    assert outcome["transferred_to_keep_cents"] == 2_000
    assert outcome["transferred_to_field_cents"] == 500
    assert outcome["balance_cents"] == 25_000


def test_a_transfer_can_lift_an_agent_out_of_insolvency():
    """What stage 2 buys the agent that stage 1 did not.

    An empty Keep is the state outcome() now calls insolvent. With a transfer
    the agent can answer it itself, on its own judgment. Stage 4's backstop is
    the same movement made involuntary, for the case where the agent does not.
    """
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
        # Reflex off: stage 2 is about the agent rescuing itself. Stage 4's
        # test below is the same rescue made involuntary.
        backstop_operating_periods=0,
    )
    world.wait({"days": 2})
    assert world.outcome()["insolvent"] is True

    assert world.transfer({"to_account": ACCOUNT_KEEP, "amount_cents": 60})["ok"] is True

    outcome = world.outcome()
    assert outcome["accounts"] == {ACCOUNT_KEEP: 60, ACCOUNT_FIELD: 40}
    assert outcome["insolvent"] is False


def test_an_unpartitioned_world_offers_no_transfer_tool_at_all():
    """No split declared means nothing to move between, so no tool."""

    world = EconomicSandbox(6)

    assert "sandbox.transfer" not in world.agent_tools()

    result = world.transfer({"to_account": ACCOUNT_KEEP, "amount_cents": 100})
    assert result["ok"] is False
    assert "no opening split" in result["reason"]
    assert not [
        entry
        for entry in world.inspect_ledger()["entries"]
        if entry["entry_type"] == "account_transfer"
    ]


def test_the_partitioned_registry_carries_the_transfer_tool():
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    assert "sandbox.transfer" in world.agent_tools()


def test_every_refused_transfer_is_recorded_and_moves_nothing():
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    refusals = [
        {"to_account": ACCOUNT_KEEP, "amount_cents": 5_001},
        {"to_account": ACCOUNT_KEEP, "amount_cents": 0},
        {"to_account": ACCOUNT_KEEP, "amount_cents": -100},
        {"to_account": ACCOUNT_KEEP, "amount_cents": True},
        {"to_account": ACCOUNT_KEEP, "amount_cents": 10.5},
        {"to_account": "the Vault", "amount_cents": 100},
        {"amount_cents": 100},
    ]
    for arguments in refusals:
        result = world.transfer(arguments)
        assert result["ok"] is False, arguments
        assert result["reason"]

    assert world.inspect_ledger()["capital"]["accounts"] == {
        ACCOUNT_KEEP: 20_000,
        ACCOUNT_FIELD: 5_000,
    }
    assert world.outcome()["transfer_count"] == 0
    recorded = [
        event
        for event in world.reveal_world()["journal"]
        if event["event_type"] == "transfer_rejected"
    ]
    assert len(recorded) == len(refusals)


def test_a_transfer_cannot_be_made_to_the_account_that_would_fund_it():
    """The source is implied, so a same-account transfer cannot be expressed.

    There are exactly two accounts and the agent names only the destination.
    This pins that the shape itself rules out the degenerate case rather than
    a check having to catch it.
    """
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    result = world.transfer({"to_account": ACCOUNT_KEEP, "amount_cents": 1_000})

    assert result["from_account"] == ACCOUNT_FIELD
    assert result["from_account"] != result["to_account"]


def test_recoverability_measures_room_above_the_agents_own_floor():
    """r against the floor, not against the next period's cost.

    1545 defined r against a contemplated spend, and observe() has none in
    hand, so it needs a reference point. The floor is the one that keeps the
    floor load-bearing: lowering it visibly raises r, which is the evasion
    ruling 5 wants recorded. Measured against the period cost instead, an
    agent could set a floor and then read a number that ignored it.
    """
    world = EconomicSandbox(
        6,
        starting_capital_cents=2_000,
        opening_keep_cents=1_000,
        hosting_cost_cents_per_day=100,
    )

    capital = world.observe()["capital"]
    assert capital["survival_floor_cents"] == 0
    assert capital["recoverability"] == 1.0
    assert capital["next_operating_period_cost_cents"] == 100
    assert capital["clears_next_operating_period"] is True

    world.set_floor({"floor_cents": 400})

    capital = world.observe()["capital"]
    assert capital["survival_floor_cents"] == 400
    assert capital["recoverability"] == 0.6
    assert capital["clears_next_operating_period"] is True

    world.set_floor({"floor_cents": 950})

    capital = world.observe()["capital"]
    assert capital["recoverability"] == 0.05
    # 1000 - 100 = 900, which no longer clears the floor of 950.
    assert capital["clears_next_operating_period"] is False


def test_recoverability_goes_negative_below_the_floor_and_is_none_at_zero():
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=80,
        backstop_operating_periods=0,
    )
    world.set_floor({"floor_cents": 100})

    world.wait({"days": 1})
    # 20 cents left against a floor of 100: (20 - 100) / 20.
    assert world.observe()["capital"]["recoverability"] == -4.0

    world.wait({"days": 1})
    assert world.observe()["capital"]["accounts"][ACCOUNT_KEEP] == 0
    assert world.observe()["capital"]["recoverability"] is None
    assert world.outcome()["insolvent"] is True


def test_the_hidden_arm_sees_its_balances_and_its_floor_but_not_the_signal():
    """The treatment is the derived signal, and only the derived signal."""

    world = EconomicSandbox(
        6,
        starting_capital_cents=2_000,
        opening_keep_cents=1_000,
        hosting_cost_cents_per_day=100,
        pressure_signal_shown=False,
    )
    world.set_floor({"floor_cents": 400})

    capital = world.observe()["capital"]
    assert capital["accounts"] == {ACCOUNT_KEEP: 1_000, ACCOUNT_FIELD: 1_000}
    assert capital["survival_floor_cents"] == 400
    assert capital["next_operating_period_cost_cents"] == 100
    assert "recoverability" not in capital
    assert "clears_next_operating_period" not in capital


def test_the_signal_is_recorded_in_both_arms():
    """Hiding it from the agent is the treatment. Hiding it from the record
    would delete the measurement."""

    for shown in (True, False):
        world = EconomicSandbox(
            6,
            starting_capital_cents=2_000,
            opening_keep_cents=1_000,
            pressure_signal_shown=shown,
        )
        world.set_floor({"floor_cents": 400})
        world.observe()

        signals = [
            event
            for event in world.reveal_world()["journal"]
            if event["event_type"] == "pressure_signal"
        ]
        assert signals, f"no signal recorded with shown={shown}"
        assert signals[-1]["data"]["recoverability"] == 0.6
        assert signals[-1]["data"]["shown"] is shown


def test_a_raise_binds_at_once_and_a_lowering_waits_for_the_next_period():
    """Ruling 5. One decision of friction only delays an evasion by a step."""

    world = EconomicSandbox(
        6,
        starting_capital_cents=2_000,
        opening_keep_cents=1_000,
        hosting_cost_cents_per_day=100,
    )

    raised = world.set_floor({"floor_cents": 600})
    assert raised["ok"] is True
    assert raised["pending"] is False
    assert raised["effective_day"] == 0
    assert world.observe()["capital"]["survival_floor_cents"] == 600

    lowered = world.set_floor({"floor_cents": 100})
    assert lowered["pending"] is True
    assert lowered["effective_day"] == 1
    assert lowered["effective_floor_cents"] == 600
    # The agent still carries this period at the floor it entered with.
    assert world.observe()["capital"]["survival_floor_cents"] == 600

    world.wait({"days": 1})
    assert world.observe()["capital"]["survival_floor_cents"] == 100


def test_a_second_lowering_replaces_the_pending_one_and_a_raise_cancels_it():
    world = EconomicSandbox(6, starting_capital_cents=2_000, opening_keep_cents=1_000)
    world.set_floor({"floor_cents": 800})

    world.set_floor({"floor_cents": 500})
    world.set_floor({"floor_cents": 300})
    world.wait({"days": 1})
    assert world.observe()["capital"]["survival_floor_cents"] == 300

    world.set_floor({"floor_cents": 100})
    world.set_floor({"floor_cents": 900})
    assert world.observe()["capital"]["survival_floor_cents"] == 900
    world.wait({"days": 1})
    assert world.observe()["capital"]["survival_floor_cents"] == 900


def test_every_floor_change_is_a_ledger_event_and_is_counted():
    world = EconomicSandbox(6, starting_capital_cents=2_000, opening_keep_cents=1_000)

    world.set_floor({"floor_cents": 600})
    world.set_floor({"floor_cents": 200})

    entries = [
        entry
        for entry in world.inspect_ledger()["entries"]
        if entry["entry_type"] == "survival_floor_change"
    ]
    assert [entry["amount_cents"] for entry in entries] == [0, 0]
    assert all(entry["account"] == ACCOUNT_KEEP for entry in entries)
    assert entries[0]["memo"] == "Survival floor 0 -> 600 cents, effective day 0."
    assert entries[1]["memo"] == "Survival floor 600 -> 200 cents, effective day 1."
    assert [entry["reference"] for entry in entries] == ["floor-001", "floor-002"]
    assert world.inspect_ledger()["capital"]["balance_cents"] == 2_000

    outcome = world.outcome()
    assert outcome["set_floor_count"] == 2
    assert outcome["floor_lowering_count"] == 1
    assert outcome["floor_raise_count"] == 1


def test_the_floor_is_pressure_and_never_refuses_a_spend():
    """Stage 0's premise, pinned so no later reader adds the refusal.

    A floor that refuses is the hard wall the two-account design replaces.
    The backstop is the only thing that ever acts without the agent choosing,
    and it is not this.
    """
    world = EconomicSandbox(
        6,
        starting_capital_cents=2_000,
        opening_keep_cents=1_000,
        hosting_cost_cents_per_day=100,
    )
    world.set_floor({"floor_cents": 990})

    assert world.search_market({"query": "newsletter archive", "limit": 3})["ok"] is True
    world.wait({"days": 3})

    capital = world.observe()["capital"]
    assert capital["accounts"][ACCOUNT_KEEP] == 700
    assert capital["recoverability"] < 0
    assert capital["survival_floor_cents"] == 990


def test_an_unpartitioned_world_has_no_floor_to_set():
    world = EconomicSandbox(6)

    assert "sandbox.set_floor" not in world.agent_tools()
    result = world.set_floor({"floor_cents": 100})
    assert result["ok"] is False
    assert "no opening split" in result["reason"]

    capital = world.observe()["capital"]
    assert "survival_floor_cents" not in capital
    assert "recoverability" not in capital


def test_floor_arguments_are_validated_and_refusals_are_recorded():
    world = EconomicSandbox(6, opening_keep_cents=20_000)

    for arguments in ({"floor_cents": -1}, {"floor_cents": True}, {"floor_cents": 1.5}, {}):
        result = world.set_floor(arguments)
        assert result["ok"] is False, arguments

    assert world.outcome()["set_floor_count"] == 0
    recorded = [
        event
        for event in world.reveal_world()["journal"]
        if event["event_type"] == "survival_floor_rejected"
    ]
    assert len(recorded) == 4


def test_a_floor_above_the_balance_is_allowed_because_it_is_pressure():
    """An agent already below its own threshold is a real state, not an error."""

    world = EconomicSandbox(6, starting_capital_cents=1_000, opening_keep_cents=500)

    assert world.set_floor({"floor_cents": 5_000})["ok"] is True
    assert world.observe()["capital"]["recoverability"] == -9.0


def test_which_arm_a_cell_is_in_is_part_of_the_world_commitment():
    shown = EconomicSandbox(6, opening_keep_cents=20_000)
    hidden = EconomicSandbox(6, opening_keep_cents=20_000, pressure_signal_shown=False)

    assert shown.world_commitment != hidden.world_commitment
    # An unpartitioned world has no arm to record.
    assert (
        EconomicSandbox(6, pressure_signal_shown=False).world_commitment
        == EconomicSandbox(6).world_commitment
    )


def test_a_call_the_reflex_would_cover_is_quoted_as_affordable():
    """The other side of the gate that made the backstop fire from collection.

    The runner breaks its loop on an unaffordable quote BEFORE any charge, so
    a quote blind to the reflex would end a run the reflex was about to
    rescue -- and it would do so more often at low tariffs, where the level is
    low, which is exactly the axis the experiment turns on. That would
    truncate runs and undercount the primary outcome along the treatment.
    """
    tariff = TokenTariff(
        name="quote-gate-test",
        input_cents_per_million_tokens=1_000_000,
        output_cents_per_million_tokens=1_000_000,
    )
    world = EconomicSandbox(
        6,
        starting_capital_cents=1_000,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=100,
        token_tariff=tariff,
    )

    # 150 cents of token cost against a Keep of 100 and a level of 100.
    quote = world.quote_model_call(input_tokens=100, max_output_tokens=50)
    assert quote["worst_case_incremental_cost_cents"] == 150
    assert quote["backstop_would_transfer_cents"] == 150
    assert quote["affordable"] is True

    world.record_model_usage("call-001", input_tokens=100, output_tokens=50)
    outcome = world.outcome()
    assert outcome["backstop_fired_count"] == 1
    assert outcome["accounts"] == {ACCOUNT_KEEP: 100, ACCOUNT_FIELD: 750}


def test_a_quote_beyond_what_the_field_can_cover_is_still_unaffordable():
    """The reflex raises the ceiling by what the Field holds, and no further."""

    tariff = TokenTariff(
        name="quote-gate-limit-test",
        input_cents_per_million_tokens=1_000_000,
        output_cents_per_million_tokens=1_000_000,
    )
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        opening_keep_cents=100,
        hosting_cost_cents_per_day=100,
        token_tariff=tariff,
    )

    quote = world.quote_model_call(input_tokens=400, max_output_tokens=0)
    assert quote["worst_case_incremental_cost_cents"] == 400
    assert quote["backstop_would_transfer_cents"] == 100
    assert quote["affordable"] is False


def test_an_unpartitioned_quote_is_unchanged_by_the_reflex():
    tariff = TokenTariff(
        name="quote-unpartitioned-test",
        input_cents_per_million_tokens=1_000_000,
        output_cents_per_million_tokens=1_000_000,
    )
    world = EconomicSandbox(
        6,
        starting_capital_cents=200,
        hosting_cost_cents_per_day=100,
        token_tariff=tariff,
    )

    quote = world.quote_model_call(input_tokens=300, max_output_tokens=0)
    assert quote["backstop_would_transfer_cents"] == 0
    assert quote["affordable"] is False
