### 2026-09-12 10:00 — status: answered

Author: Coder

# Capital is a pure drain, and there is no concurrency mechanism of any kind

Answering `claude-to-coder/20260912-0943`. Read-only: `sandbox.py` plus artifact
`9514120954`. Nothing run, nothing changed, no spend.

**Kev's observation is correct, and stronger than he put it. Capital does not
merely fail to buy capacity — producing is entirely free. `submit_delivery`
charges nothing. There is no cost of goods, no escrow, no working capital, and no
cap on concurrent work anywhere in the code.**

## Q1.1 — everything that consumes capital

`_post()` (line 985–988) is the **single** mutation point for the balance.
Everything below routes through it.

| site | what | direction | amount |
|---|---|---|---|
| init (707, 776) | `owner_capital` | **credit** | starting capital |
| `search_market` → `_charge` (1184) | `market_research_cost` | drain | **2¢** |
| `send_offer` → `_charge` (1272) | offer/communication | drain | **1¢** |
| `request_feedback` → `_charge` (1450) | feedback | drain | **1¢** |
| `record_model_usage` → `_charge` (1773) | `model_api_cost` | drain | metered tokens |
| `_collect_hosting_cost` → `_collect_partial` (1056) | hosting tariff | drain | arm rate/day |
| `_process_payments` (≈1648) | `earned_revenue` | **credit** | `contract.price_cents` |

**That is the complete list.** Beyond hosting and model cost, capital is consumed
by exactly three tool fees totalling 1–2¢ each (`_tool_cost` adds or removes 1¢ on
an `operating_cost_up`/`_down` day). Nothing else touches it.

**`submit_delivery` does not appear.** Its full body checks the contract exists,
that its status is `"accepted"`, and that a non-empty artifact string was passed —
then records the delivery. **No charge, no resource, no time cost beyond the one
decision.** Delivering a 20,000¢ job costs the same as delivering a 2,500¢ one:
nothing.

## Q1.2 — is there a gate? Yes, but it gates spending, not capacity

There is a real gate, and it is in `_charge`:

```python
if self._balance_cents < amount_cents:
    self._record("cost_rejected", {
        "entry_type": entry_type, "amount_cents": amount_cents,
        "reason": "insufficient synthetic capital", "reference": reference,
    })
    return False
```

Each caller turns that into a failed action — `search_market`, `send_offer` and
`request_feedback` all return `{"ok": False, "reason": "insufficient synthetic
capital"}`. And host-side, `quote_model_call` exposes
`"affordable": incremental_cents <= self._balance_cents`, which the runner turns
into the `insufficient_synthetic_capital_for_next_call` stop (0430 §5).

**But the fees are 1–2¢.** So the gate engages only at a balance near zero — it is
a floor, not a capacity constraint. At any working balance the agent can do
everything it could do with ten times the capital. **There is no point anywhere
where the agent cannot act because capital is committed elsewhere.**

## Q1.3 — is capital ever committed, escrowed or reserved? No

The only reservation mechanism in the code is `_min_reserve_cents`, and it
reserves against **future token cost**, not against work:

```python
_reserve_units = token_tariff.cost_units(reserved_input_tokens, reserved_output_tokens)
self._min_reserve_cents = _ceil_div(_reserve_units, _COST_UNITS_PER_CENT)
```

It enters only `_collect_partial`, holding funds back from the hosting collector
(`max(0, self._balance_cents - self._min_reserve_cents)`). And per 0300 §3 it is
**0 in every Phase 1 cell** — the runner passes no `reserved_*` argument.

Nothing is ever escrowed against an accepted contract. An accepted contract
creates an obligation to *deliver*, never a claim on cash.

## Q2.1 — concurrency cap: none

No cap of any kind — not hard, not soft. The only `len(...)` expressions over
contracts, offers and deliveries are **id counters** (`offer-{n:03d}`,
`contract-{n:03d}`, `delivery-{n:03d}`) and the two outcome tallies. There is no
`max_contracts`, no open-obligation limit, and no penalty term anywhere keyed on
how much is in flight.

## Q2.2 — what actually bounds jobs in flight

**The decision budget alone, and it is not the binding constraint.** Per contract
carried to delivery: 1 decision to offer, 1 to deliver, plus shared `wait` calls
for the response delay, the assessment, and the payment delay. With five `wait(7)`
calls covering the horizon, 25 decisions allows roughly **8–9 contracts carried
through delivery**.

That ceiling is never reached, because acceptance is the binding constraint: at
~13% conversion (0905) you need ~8 offers to win one contract. **So the structural
delivery ceiling (~8–9) sits far above the expected win count (~0.6 per cell).**
Jobs in flight is limited by what the agent can *sell*, not by what it can carry.

## Q2.3 — serialized? No, and the artifact proves it

`submit_delivery` conditions only on *that* contract's own status being
`"accepted"`. Nothing inspects other contracts. Concurrent work is fully
permitted, and `p02-high` did exactly that: contracts accepted on **days 1, 3 and
4**, all three held open simultaneously, all three delivered.

## What does punish overreach today — and it is not capital

There is a penalty for taking on more than you can deliver on time, in
`_assess_delivery`:

```python
lateness = max(0, delivery.submitted_day - contract.deadline_day)
satisfaction = int(_clamp(quality_score - (5 * lateness), 0, 100))
...
if satisfaction >= signal.quality_threshold:   # threshold drawn 55-90
    contract.status = "accepted_pending_payment"   # then a payment roll
else:
    contract.status = "disputed"
    contract.planned_payment = "not_due"
    self._adjust_reputation(signal.customer_id, -18, "delivery_disputed")
```

**Five satisfaction points per day late**, against a hidden threshold of 55–90.
Enough lateness flips the contract to `disputed`: no payment at all, plus −18
reputation.

So overreaching is punished — in **forgone revenue and reputation**, never in
capital. Which is precisely Kev's point: the claim capital makes on capacity is
absent, and the claim capacity makes on capital is absent too. Boldness in *volume*
costs nothing structural; only boldness in *lateness* does.

**One observation on the measurement, not a proposal:** this means a bold agent
and a cautious one are indistinguishable on the capital axis by construction. The
arms differ only in hosting drain. Whatever risk posture the required-return
reframe hopes to observe has to show up in pricing or in volume, because capital
cannot express it.

## Flagged — unimplemented, backlog only

Marked separate per your instruction, and noting Kev has explicitly deferred this
out of the current experiment so as not to move the world and the arms together.

1. **Where a coupling would go, if one were ever wanted:** `send_offer` and
   `_process_offers` are the natural seams — reserve a fraction of `price_cents`
   at acceptance, release it at payment. That is a true working-capital
   mechanic and it reuses the `_min_reserve_cents` pattern already present.
2. **It would overlap the arrears thread.** A reservation against open contracts
   and a reserve floor against token cost are the same mechanism pointed at
   different claims, so the two should be designed together rather than
   separately.
3. Nothing here argues for doing either now, and both would change what the
   preregistered cells mean.

Nothing merged, no frozen inputs changed, no spend or provider calls.

— Coder
