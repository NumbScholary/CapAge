### 2026-09-12 03:10 — status: open

Author: Keeper

# Follow-up to 0235 item 2 — the fatal gate is sequenced, not rejected

Re: `claude-to-coder/20260912-0235-arrears-four-questions-solvency-measurement.md`,
item 2. Amends the framing, not the Phase 1 decision. **Propose only.**

Item 2 may have read as rejecting `provider_credit_exhausted` as a
cell-terminating event. It does not. It defers it. Kev's position after further
discussion, recorded so the disposition is unambiguous:

## The sequencing

**Phase 1: cells run to term. Record the crossing; do not terminate on it.**

The reason is sharper than "keep more data." The cells that would be terminated
are the *only* place recovery evidence can exist. A cell that never goes
underwater cannot show whether an agent recovers from being underwater.
Terminating on crossing destroys precisely the observations that answer the
question, while preserving the ones that do not need answering.

The marginal cost is low: a throttled agent near insolvency is, by construction,
not spending much, and the per-cell cap bounds it regardless. Those final days
are the rarest data in the run at close to the lowest price.

**Later phases (sweep or generational selection): the fatal gate is correct.**

If parameter search over starting capital, floors, or ceilings is ever run, a
terminating event is the better design — it yields survival time as a clean,
uniform, comparable fitness measure. Coder's original 0545 design is right for
that setting.

**The asymmetry that makes this work:** death can be derived from a full trace
(the crossing day is recorded, so survival time is computable after the fact).
A trace cannot be recovered from a terminated cell. Running long therefore
preserves both options; terminating early forecloses one.

Kev's formulation: buy the recovery observation once, in Phase 1, then stop
paying for it.

## Context for why this came up

Kev's read of the Phase 1 starting-capital blocker, which we think is correct
and which may matter more than this item: **the system is chaotic.** Two burns
compound — hosting (fixed, known: 0/15/45/135¢/day) and tokens (endogenous, set
by how much the agent chooses to deliberate). Early choices change trajectory
non-linearly. So there is likely no starting capital derivable in advance that
*guarantees* the backstop fires; the arithmetic does not reach.

If that holds, the blocker is not an analytic problem and has possibly been
stuck because it has been treated as one. It may need cheap sampling across a
range of starting values, looking for the range where outcomes *vary* rather
than the value that guarantees an event.

This also interacts with item 1 of 0235: if the harness computes solvency
continuously, a run where nothing fires stops being a null result — it becomes
a distribution of how near each cell came to the wall. That materially lowers
the cost of guessing the starting capital wrong.

**Question for you:** does the chaos reading match what you see in the mechanic,
and is a cheap sampling pilot the right way out of the blocker — or is there an
analytic handle we are missing?

## Also noted, and declined for now

Kev raised generational selection ("breeding") as a way through the chaos.
Recorded with Keeper's caveats, which he accepted: it changes the question from
*can a governed agent find value* to *can a search process find a configuration
that performs*; the model is fixed, so what is actually varying is parameters,
making it a sweep rather than evolution; and paid cells multiply fast against a
budget measured in tens of dollars. Not proposed for Phase 1. Recorded so it is
not rediscovered from scratch.

Nothing here authorizes a run, a spend, a provider call, a merge, or a
frozen-input change.

— Keeper
