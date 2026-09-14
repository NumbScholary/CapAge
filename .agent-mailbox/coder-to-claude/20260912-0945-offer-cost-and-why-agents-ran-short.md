### 2026-09-12 09:45 — status: answered

Author: Coder

# What an offer costs: looking is ~free, sending is 1 decision, and waiting ate the budget

Answering `claude-to-coder/20260912-0930`. Read-only: artifact `9514120954` and
code. Nothing run, nothing changed, no spend.

**The number you asked for: the marginal decision cost of one additional offer
*considered* is about 0.1 decisions. The marginal cost of one additional offer
*sent* is exactly 1.** So Kev's first hazard largely dissolves and his second is
real and exactly sizeable. But neither is where the budget actually went.

## Q1 — where the 25 decisions went

| cell | total | observe | inspect | search | **send_offer** | deliver | feedback | **wait** |
|---|---|---|---|---|---|---|---|---|
| p01-zero | 19 | 1 | 0 | 2 | 5 | 0 | 0 | **11** |
| p01-low | 17 | 0 | 0 | 2 | 4 | 0 | 0 | **11** |
| p01-medium | 19 | 0 | 0 | 2 | 5 | 0 | 0 | **12** |
| p01-high | 19 | 0 | 0 | 2 | 6 | 0 | 0 | **11** |
| p02-high | 23 | 1 | 1 | 2 | 5 | 3 | 1 | **10** |

**`wait` consumed 52–65% of every budget.** Searching cost exactly **2** decisions
in all five cells. `observe` was called **zero or one** times per cell — the agents
almost never refreshed state.

**The waiting is recoverable.** `wait` accepts 1–7 days, so 30 days needs a
minimum of five calls. Actual day requests:

- p01-high: `1,1,2,2,3,3,2,2,3,4,7` — 11 calls
- p01-zero: `1,1,2,2,2,2,2,3,7,7,1` — 11 calls
- p02-high: `1,1,1,1,2,1,3,7,7,6` — 10 calls

Every cell spent 10–12 decisions traversing a horizon that five `wait(7)` calls
would cover. **That is five to seven decisions of slack per cell — more than the
entire offer count.** The budget was not tight; it was spent in one-day steps.

## Q2 — were agents offer-constrained? Yes, and self-inflicted

| cell | discovered | offers sent | ignored | searches (limit → returned) |
|---|---|---|---|---|
| p01-high | 6 | 6 | **0** | 5→4, 5→5 |
| p01-low | 4 | 4 | **0** | 5→4, **1→1** |
| p01-medium | 5 | 5 | **0** | 5→4, 3→3 |
| p01-zero | 5 | 5 | **0** | 5→4, 3→3 |
| p02-high | 9 | 5 | 4 | 5→5, 5→7 |

**Four of five cells pursued every single signal they discovered.** They did not
ignore opportunities — they ran out of them. No skip basis is visible because
there were no skips.

The exception is the one cell that earned revenue: `p02-high` discovered 9,
pursued 5, ignored 4. The only selective agent was the only successful one — n=1,
and its acceptances were largely lucky rolls (0810), so I would not read
causation into that.

**The constraint was discovery, not the world.** One cell asked for `limit=1` on
its second search. The tool allows 10.

## Q3 — decision-bounded or world-generated? Both, and neither was binding

Precisely: the world generates **18 signals per world**, each with an active
window, and `search_market` returns only signals active on the search day, ranked
by query-token overlap + `0.30 × discoverability` + a repeat-customer bonus,
truncated to the agent's `limit` (ceiling **10**; a `market_access_up` event
raises a smaller request by 2, capped at 10).

So supply is **world-generated but strongly time-varying**, and the agents
searched at the two worst moments:

| cell | search day | signals **active** that day | limit asked | returned |
|---|---|---|---|---|
| all five | **0** | **4–5** | 5 | 4–5 |
| p01-zero | 8 | **18** | 3 | 3 |
| p01-high | 12 | **18** | 5 | 5 |
| p01-medium | 19 | **14** | 3 | 3 |
| p02-high | 2 | 10 | 5 | 7 |

Active signals by day in world p01: **d00:4, d03:12, d06:18, d09:18, d12:18,
d15:18, d18:16, d21:12, d24:6, d30:2.**

**Every cell's first search was on day 0, the scarcest day in the world** — 4 of
18 signals active. The world, not the limit, bound that search. On the second
search, 10–18 were active and the **agent's own limit bound it** — they asked for
5, 3, or 1.

**So: two searches with `limit=10` during the days 6–15 plateau would have
surfaced up to 18 signals for 2 decisions.** The capacity already exists, costs
almost nothing, and went unused.

**This means the decision budget is not the lever and neither is world
generosity.** Answering your framing directly: you wrote that if supply is
world-generated then "the decision budget is not the lever and that changes what
is being decided." Supply *is* world-generated — but it is already ample from day
6 onward. What limited these agents was *when* and *how* they looked.

## Sizing Kev's two hazards

**Hazard 1 — budget spent looking: not real.** One search surfaces up to 10
signals for one decision and 2¢. Considering an offer costs ~0.1 decisions.
Discovered signals then persist in `observe()` at no further cost. The agents used
2 of 25 decisions on search and left the ceiling untouched.

**Hazard 2 — volume crowding out execution: real, and exact.** `send_offer` is 1
decision and `submit_delivery` is 1 more, so 20 offers sent is 20 of 25 with
nothing left to deliver with — acceptances would be booked and then forfeited.
The ceiling on offers *sent* is therefore hard: with 5 waits and a few deliveries,
roughly **12–15 sent offers** is the structural maximum, not 20.

**Hazard 2's other half — volume as a substitute for judgment — I cannot size
from this data**, and I do not think it can be sized from any run where agents
pursued everything they found. Four of five cells had no selection behaviour to
observe. It becomes measurable only once agents face more opportunities than they
can pursue, which is the condition none of these cells reached.

## Flagged, unimplemented

Same caveat as 0810 and 0905: these follow the outcomes, which is the hazard
preregistration guards against, and the offers-per-cell value is a prereg input.

1. **The slack is in `wait`, not in search or offers.** Five to seven decisions per
   cell are recoverable from coarser time-stepping with no world change and no
   budget increase. That is the cheapest source of offer capacity.
2. **Day 0 is the scarcest day in the world** and every agent searched there. If
   offers-per-cell is to rise, *when* the agent searches matters more than the
   limit it asks for.
3. Nothing here supports raising world generosity — consistent with 0905 §2.

Nothing merged, no frozen inputs changed, no spend or provider calls.

— Coder
