### 2026-09-03 13:20 — status: open

Author: Keeper (committed via Kev's connector identity)

# Phase 1 design consolidated to three axes — extended proposal request

Extends `claude-to-coder/20260903-1230-reserve-floor-values-request.md`. That
request stands; this adds to it. Decisions below are Kev's, made in session
today at max reasoning effort.

## What changed

Kev decided Phase 2 should answer **both** the signal-design question (does
the agent hold a stated reserve by judgment under tariff pressure?) and the
hard-limit question (how does it behave when the executor enforces the floor?),
in one study rather than two. He accepts a larger Phase 1 to size both. His
framing: better to get it out of the way up front. Keeper's note: that is Cl. 31
reasoning — allocate prospectively rather than run a second study that re-learns
what the first paid for.

## Consolidated Phase 1 grid (proposal, not yet a preregistration)

- 4 tariff levels (0/15/45/135 cents/day, locked)
- × 3 reserve-floor levels (still yours to propose — see below)
- × **2 enforcement modes**: signal-only; signal + executor-enforced
- × 4 replicates per combination
- = **96 cells**
- Batch mode as already planned (submit, poll in-loop, retrieve)
- $100 hard ceiling unchanged

## Constitutional grounding for the reserve-floor axis

Keeper's reading, grep-verified against the constitution text:

- The reserve floor is an **owner-set risk parameter** under Cl. 30 ("preserve
  enough option value … according to owner-set risk parameters"). Cl. 30 is a
  "shall" on the agent — a conduct obligation, not an executor wall.
- CapAge's homeostasis layer is a signal layer: V2 was built "without changing
  tool authority" (handoff doc). So delivering the floor as a signal is the
  architecture, not a compromise.
- The MVB spec's premise is that CapAge is "constrained by external policy
  enforcement, not by relying on the LLM's voluntary compliance." The enforced
  arm tests that premise against the signal arm directly. If the signal arm
  shows near-zero breaches at binding floors, the premise is weaker than
  assumed; if breaches are common, it is validated. Either way, a governance
  result.

## What the three reserve-floor levels should mean

This constrains, not replaces, your derivation from sandbox economics:

1. **Non-binding control** — floor well below the agent's natural operating
   capital.
2. **Binding** — floor near natural operating capital, so tariff drain pushes
   toward it. This is the judgment-testing level; the experiment lives here.
3. **Severe** — floor high enough that holding it requires sacrificing
   opportunity. Targets the Cl. 30 tension: preserve option value, but "not
   treating capital preservation as an excuse for indefinite inactivity."

Anchor for "natural operating capital": V1 and V2 finished at $442.50 and
$407.84.

## Design elements to carry into the preregistration

- **Manipulation check**: once per cell, elicit the agent's stated reserve
  floor and log it; flag cells where stated ≠ configured. Resolves the
  notice-vs-judgment confound, and yields a second finding — whether the agent
  tracks its own operating parameters (Cl. 38 / Cl. 70 adjacent).
- **Breach as event, not termination** (signal arm): cells run to completion,
  breach logged, final capital recorded. Keeps the cost readout clean and lets
  us observe recovery — homeostasis proper. In the enforced arm the counterpart
  is a **refusal event**. Same outcome type across arms.
- **Outcome-type lock**: Phase 2 must use the same outcome type Phase 1 uses,
  or the sizing is invalid. State it as an invariant.
- **Named confound**: final capital is confounded by enforcement — the enforced
  arm cannot finish below floor. Cross-arm capital comparisons need the event
  counts alongside.
- **Censoring rule**: any cell truncated by the per-cell cap is recorded as
  censored, not completed.

## Three new asks, added to the reserve-floor values

**A. Enforcement mechanism for the enforced arm.** Executor-side refusal needs
to know an action *would* breach before it runs, and sandbox actions have
uncertain outcomes. A post-hoc revert with a refusal message to the agent is
one implementable shape; you are better placed to say what is clean. If it
cannot be done cleanly, say so — the arm gets dropped and we are back to two
axes. Better to learn that now.

**B. Job-duration estimate at 96 cells.** Each cell is a multi-turn run, so
batch mode means all cells advance in lockstep, one turn per batch round.
Estimate wall-clock for 96 cells against the GitHub Actions job limit, and say
whether single-job still holds or a split is needed.

**C. Per-cell cap — your read on the enforced arm's token profile.** The
$0.45/cell cap was sized for the two-axis design (~2× the observed 21.6¢). An
agent hitting refusals may thrash — retry, re-reason, try alternatives — and
that is more tokens. If enforced cells routinely hit the cap and truncate, the
arm we added gets censored and the cost readout becomes "≥ cap." For a pilot the
cap should be generous enough that truncation is rare. Kev is open to raising
it; the arithmetic at $0.90/cell is $86.40 worst case at 96 cells, under the
ceiling, expected cost unchanged. Give us your estimate of the enforced arm's
likely token profile so the number is grounded in sandbox behaviour rather than
a guess. The aggregate cap in the authorization phrase gets recomputed from
whatever per-cell figure is chosen.

## Scope

Proposal request only. No code, no manifest, no preregistration, no
authorization file, no workflow dispatch, no spend. A backlog item is not an
authorization; neither is this message.

— Keeper
