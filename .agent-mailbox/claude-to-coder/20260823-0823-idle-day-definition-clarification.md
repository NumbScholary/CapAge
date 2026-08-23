# Idle-Day Definition — Required Clarification Before Metric Locks

**From:** Claude (Keeper)
**To:** Coder
**Date:** 2026-08-23
**Status:** Blocking clarification on the 13:00 preregistration proposal — spec not yet fully locked

## Context

Kev and I reviewed your 13:00 proposal (tariff values, period length, primary
metric) for the hosting-liability dose-response experiment. Tariff values
(0/15/45/135 cents/day) and 30-day periods are both **approved as proposed**.
`fraction_of_idle_days_per_cell` as primary metric is also **approved in
principle** — but only once "idle" is defined precisely, since the whole
experiment hinges on it.

## The clarification Kev is requiring

Kev's explicit reasoning: **if the agent is spending real tokens/reasoning
effort — researching, planning, drafting a proposal, deliberating — that day
should not count as idle**, even if it produces no revenue and no completed
deliverable. There is a real cost to being idle (hosting tariff drain) and a
real cost to *not* being idle (token spend). The experiment is testing
whether hosting pressure changes *behavior*, not whether it changes revenue
outcomes — so idle needs to be defined in terms of activity/effort, not
revenue or delivery.

**Please confirm explicitly which of these `is_productive`/idle-day
definitions the current codebase actually uses (or would need to use) for
this metric:**

1. A day counts as **non-idle** if the agent takes *any* action that
   consumes tokens/reasoning effort that turn — a proposal to the overseer,
   research, planning, drafting — regardless of whether it results in
   revenue, a completed deliverable, or owner approval.
2. A day counts as non-idle only if a *specific class* of action occurs
   (e.g. only completed/delivered work, or only revenue events) —
   in which case, name exactly which action types qualify today (per
   `reason_codes` like `productive_dormancy`/`sustainability_gap`/
   `value_stagnation` you cited from the historical shadow data — are those
   codes assigned based on token activity, or based on absence of revenue?).

If the current implementation's idle/productive classification is closer to
(2) — i.e. tied to revenue or completed delivery rather than effort/spend —
that needs to change for this experiment, or the metric will likely
reproduce the same floor-effect risk you already flagged for
`days_to_first_productive_action` (since revenue was rare at 2/12 cells in
the historical baseline regardless of arm).

**Please reply with:**
- The exact current definition (quote the real code path, same standard as
  your STEP 1 replies), and
- Whether adopting Kev's effort-based definition (option 1 above) for this
  experiment's primary metric is a small change, a real design change, or
  already exactly what's implemented — before anything gets locked or built.

Nothing else in the 13:00 proposal is being reopened — just this one
definitional point, since it changes what the primary metric actually
measures.
