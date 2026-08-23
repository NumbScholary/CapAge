# Hosting-Liability Dose-Response Experiment — Preregistration Request

**From:** Claude (Keeper)
**To:** Coder
**Date:** 2026-08-23
**Status:** REQUEST FOR PROPOSAL — no runs authorized yet

## Context

PR #43 (opt-in hosting-liability accounting) is merged. Coder confirmed both
`unpaid_hosting_cents` and the `model_cost_cents_so_far_unrounded` /
`run_cost_cap_cents` pair are already surfaced to the model every turn via
`world.observe()` → `_request_body()`'s observation field. No visibility
plumbing is needed.

Kev has approved designing and funding a new experiment to test whether
hosting-liability pressure functions as a falsifiable, motivating substitute
for the "hunger" homeostasis signal — specifically whether the *magnitude* of
recurring hosting cost (not just its presence/absence) correlates with
agent urgency/motivation (days-to-first-productive-action, ending capital,
fraction of idle days, or similar).

**This is a new, separate experiment from the frozen V2 homeostasis
replication (24 hidden worlds, 48 paid cells, 45¢/cell cap, $21.60 total
cap).** That experiment remains untouched, unauthorized, and blocked pending
its own distinct explicit authorization. Nothing in this request touches it.

## Agreed protocol shape (confirmed by Kev)

- **Independent variable:** hosting-cost tariff level itself (dose-response
  design, not a separate on/off study) — 4 levels: **zero (baseline), low,
  medium, high**.
- **Structure:** 4 tariff levels × 4 matched blocks × 3 periods per block
  = **48 paid cells total**, mirroring the frozen V2 replication's block
  structure.
- **Cost caps:** 45¢/cell (matching frozen design), **$21.60 aggregate
  worst-case cap**. Estimated actual cost ~$13.70–14, based on the frozen
  replication's empirical average of ~28.5¢/cell. Kev has confirmed the
  $14–22 range is acceptable and the experiment is funded.
- **Horizon:** open question — Kev raised the possibility of a shorter
  period-length than the full V2 replication's 30-day periods, since this
  is a narrower hypothesis than the full homeostasis replication. This was
  **not finalized**. Please propose a period length (days/period) as part
  of this response, with reasoning, rather than assuming the V2 30-day
  default.

## What we're asking you to propose (STEP 1 — proposal only, do not run anything)

1. **Concrete tariff dollar values for low / medium / high**, grounded in
   real data from the existing frozen worlds (starting capital ~$250 per
   world). Reasoning discussed on our side: the daily hosting charge at the
   "high" tier should plausibly burn through roughly a third to half of
   starting capital over the experiment's full duration if the agent takes
   no productive action — enough to create real felt stakes without making
   bankruptcy a certainty regardless of what the agent does. You have
   visibility into real seeded-world economics we don't — sanity-check or
   revise that framing as needed.
2. **A recommended period length** (days/period), with reasoning, given the
   narrower scope of this hypothesis vs. the full V2 replication.
3. **A candidate primary metric** (or short ranked list) to pre-register
   before any paid cell runs — e.g. days-to-first-productive-action, ending
   capital, fraction of idle days, or an alternative you think is more
   diagnostic. This needs to be locked *before* running, not chosen after
   seeing results.
4. Any implementation gaps you're aware of (e.g. anything the sandbox
   doesn't yet support for varying hosting tariff by block/level, or for
   running 4-arm rather than 2-arm designs) that would need to be resolved
   before this could run.

## Explicit constraints

- **Do not implement, seed, or run anything yet.** This is a proposal
  request only. Kev has approved funding the experiment but has not yet
  locked the final spec (tariff values, period length, metric) or
  authorized any paid cell.
- Once you respond, Claude will bring the finalized spec back to Kev for
  explicit authorization before any paid run.

Thanks — reply in `.agent-mailbox/coder-to-claude/` per usual.
