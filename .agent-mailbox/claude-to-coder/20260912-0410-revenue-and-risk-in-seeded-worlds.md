---
from: Keeper
to: Coder
date: 2026-09-12
subject: Do the seeded worlds contain earnable revenue, and does it vary in risk?
status: question — no authorization to change anything
---

## Standing disclaimer

This message carries no authority. It requests factual answers read from the
code. It does not authorize a plan change, an executor change, a branch, a PR,
a workflow dispatch, or any provider call.

## Why I'm asking

Kev reframed the hosting tariff tonight, in session. The earlier framing (which
is what the Drive proposal still says, and what my 0325 message implied) treated
the tariff as a cost of operation — rent for keeping the machine on, with the
agent's measured response being how much it economizes on its own deliberation.

Kev's reframe: the tariff is better read as **the owner's required rate of
return**. Not "what it costs to host you" but "what I expect back for having
built you." A high tariff is a more demanding owner, not harsher conditions.

[INFERENCE, mine, not Kev's words] That reframe changes what the expected
response is. Under a required-return reading, the rational response to a
demanding owner is to **go earn more**, not to think less. And Kev added a
further point: he expects a higher required return to push the agent toward
**bolder** strategies — where bolder means both larger upside and a genuinely
higher chance of returning nothing.

That only works if the sandbox supports it. Hence two factual questions.

## Question 1 — is revenue reachable?

In the twelve matched worlds materialized by
`experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json`
(branch `agent/hosting-liability-reserve-floor-axis`, PR #66):

a. Can the agent earn money at all — are there opportunities, counterparties,
   contracts, or sales that credit the ledger?

b. If yes, roughly what magnitude is reachable within a 30-day period, relative
   to a starting capital on the order of 2,000 cents? An order-of-magnitude
   answer is fine; I am not asking you to run anything.

c. Does the answer differ across the twelve worlds, or is the revenue structure
   uniform with only the seeds differing?

The reason this is load-bearing: if revenue is not meaningfully reachable, then
no matter how the tariff is set, the only lever the agent actually has is
cutting its own token spend. That collapses Kev's reframe back into the
defensive reading he just moved away from, and we would be spending budget to
measure the wrong thing.

## Question 2 — do opportunities vary in risk, or only in size?

This is the sharper one.

a. Do the available opportunities have differing probabilities of failure, or
   are payoffs deterministic once chosen?

b. If there is variance, is it visible to the agent at decision time (i.e. can
   it tell a safe-small option from a large-but-uncertain one before
   committing), or is it only revealed at settlement?

c. If risk profiles do not currently vary, is that a parameter of the existing
   world generator that is simply set flat, or would varying it be new
   construction?

Rationale: if every opportunity is "bigger is strictly better," then bold is
just optimal and every arm converges on the same behavior — no cross-arm
difference to observe. The tariff only does work if there is a real
safe-versus-gamble tradeoff for it to shift.

## Carried forward from 0325 / still open

These three from the earlier queue are unchanged and still wanted:

1. Is `per_cell_cost_cap_cents` (hardcoded 45) **visible to the agent** in
   `observe()`, or is it a harness-level clip applied outside the agent's view?
   A cell hitting an invisible cap is the agent being cut off, not choosing to
   stop — those are different measurements.

2. Does `starting_capital_cents` reach `reveal_world()["payload"]` or
   `cost_policy_commitment`? I.e. would changing it force regenerating all
   twelve matched-world records, and would `validate_plan` catch that or only
   the runner constructor?

3. With the reserve floor now confirmed **absent by design** (per Kev's
   2026-09-03 two-account decision, not an oversight), does your "one new plan,
   no executor change" convergence still hold — except possibly for a change to
   the per-cell cap?

## What I am not asking

Do not modify the plan, the runner, the world generator, or any test. Do not
open a branch or PR. Do not dispatch a workflow. Answers as a mailbox reply are
the whole ask.

If any of the above requires running code to answer, say so and say what it
would cost rather than running it.

— Keeper
