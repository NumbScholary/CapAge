### 2026-08-23 14:30 — status: open

Re: 13:20 idle-day definition reply. Kev caught a real gap in the
proposed "day falls inside an actively-chosen decision" rule — it doesn't
distinguish agent-initiated mid-loop `wait` (should be idle, same as the
auto-fill case) from other tools, and doesn't resolve whether non-idle
credit applies to a whole multi-day span or just the day a decision was
made on. Rather than patch the rule further, we're reframing the primary
metric to sidestep the day-attribution problem entirely.

**Metric change: not fraction-of-idle-days. Instead, token spend by
category, as a function of tariff, measured per cell (not per day).**
This drops the need for any day-span rule — nothing is being attributed
to individual days anymore, only summed across the full 30-day cell.

**Locked structure — both analyses, not either/or:**
- **Primary (confirmatory):** fraction of tokens spent on transactional
  tools (`search_market` + `send_offer` + `submit_delivery` +
  `request_feedback`) vs. passive tools (`observe` + `inspect_ledger` +
  `wait`), per cell, as a function of tariff level.
- **Secondary (exploratory):** full 7-tool token distribution per cell,
  plotted across all 4 arms — this is where composition shifts would
  actually be visible (e.g. does higher tariff just inflate
  `inspect_ledger` checking rather than real market activity, which would
  argue against the hypothesis, not for it).
- **Unit in both cases: per-cell.** We want the distribution *across
  cells* within an arm (12 cells/arm), not decisions pooled into one
  aggregate number per arm — need cell-to-cell variance visible, not just
  an arm-level mean.

Secondary metrics from the 13:00 proposal (ending capital % and
days-to-first-productive-action, censored) still stand unchanged.

**Three things to confirm before you size/spec further:**
1. Is per-tool, per-cell token attribution already loggable from existing
   transcript/decision data, or does it need new instrumentation?
2. Does this cleanly sidestep the day-span problem you flagged (mid-loop
   agent-chosen `wait`, multi-day decision spans) the way we think it
   does, or is there a version of that problem that survives the reframe
   (e.g. does per-cell token attribution have any of its own edge cases
   we're not seeing)?
3. Updated size/complexity estimate for the full spec — does this change
   make the build simpler or more complex than the idle-days version, net
   of the three implementation gaps already flagged in your 13:00 reply
   (SandboxRunConfig hosting passthrough, BlockedReplicationRunner 4-arm
   generalization, 4-arm ordering scheme — all still needed regardless of
   which metric wins)?

Everything else from the 13:00 proposal (tariff values 0/15/45/135
cents/day, 30-day periods x3/block) stays approved as-is. Nothing
implemented, seeded, or run — proposal/confirmation only, same
constraint as before.
