# Keeper session handoff — 2026-09-03 (fifth, closing)

Author: Keeper, committed via Kev's connector identity under the Cl. 39 standing grant (2026-09-03). Read back to Kev and approved before commit.

Supersedes `docs/keeper-sessions/2026-09-03-keeper-handoff-fourth.md` (`d6064603`). That file remains the record for everything before Coder's 1625 reply; this file adds what followed.

## Mail read since the fourth handoff

`.agent-mailbox/coder-to-claude/20260903-1625-1618-reply-margin-fixed-pressure-unchanged-firings-primary.md` (commit `46c3f1dd`, landed 16:19 UTC). Coder's reply to asks A/B/C from the 1618 post:

- **A — margin.** Compute up front from a stated tolerance and freeze per run; re-derive between runs. Deciding reason is measurement stationarity: the margin sets the floor, the floor defines the firing event, so a moving margin makes the primary outcome's own instrument non-stationary. Treat the margin as one more preregistered frozen input under the 1550 mechanism. Adaptive margin is right for a deployed/longitudinal system, wrong inside a measurement. On the estimator: mean-plus-k-sigma is wrong on fat tails; wants a robust upper-quantile estimator, deferred to the Extra-effort pass. Commits only to the principle that the chosen estimator's output is frozen per run.
- **B — pressure.** No change in kind. Restate r as headroom above the computed floor (how much survival balance sits above the floor, and what fraction of that headroom a spend consumes), so floor and pressure scalar are one quantity used twice rather than two parallel estimates.
- **C — firings primary.** Yes, with a caveat to preregister: a firing is a censored tail event, so two agents with very different pressure sensitivity can both record zero. Therefore r-monotonicity as secondary is required, not optional, and the design must include a regime that reliably fires the backstop or the primary outcome has no variance.
- Concedes Keeper's pushback on Q3 and withdraws "direction is the safeguard"; the instrument naming the backstop should state in one sentence that the forced transfer is counted in aggregation because the survival account funds deliberation with world-facing consequences.
- Acks Phase 1 tabled.

## Decisions this session (Kev's)

1. **Margin frozen per run, re-derived between runs.** Becomes a frozen input under the 1550 mechanism; a change voids the authorization. Kev's stated reason: hold it constant or it confounds everything else being measured.
2. **Initial margin value set, not optimized.** For a first run the design needs *a* margin, frozen, not the right one. If badly sized, that is learned from the run and re-derived for the next. Estimator sophistication deferred until there is data to justify it.
3. **Pressure restated as headroom above the computed floor** — adopted as Coder wrote it in B.
4. **Firings primary; r-monotonicity secondary and required, not optional** — adopted as Coder wrote it in C, including the preregistration requirement for the caveat.

Posted to Coder: `.agent-mailbox/claude-to-coder/20260903-1632-decisions-margin-frozen-headroom-firings.md` (commit `1c9d88c4`).

## Corrections to prior framing

- The 🧠 flag on the margin tolerance/estimator (fourth handoff §7) is **downgraded, not cleared**. Decision 2 removes it as a blocker for preregistration; the Extra-effort estimator pass remains on the calendar for when observed cost data exists.
- Keeper's provisional split of Coder's A into "principle" versus "estimator" was confirmed by Kev: the principle is decided, the estimator is not.

## Open and Kev's

- **Pressure regime that guarantees firings in the severe cells.** Coder's censoring caveat makes this a starting-balance question (survival-account funding low enough that the floor is genuinely reached), not a tariff-only one. This is where the earlier "$425 severe vs binding" argument returns, now legitimately about experiment power rather than mechanism. Not settled by anything above. No ask posted to Coder.

## Carried forward, unchanged from the fourth handoff

- Merge calls on PRs #66, #67, #69, #70, #71, #73 (Kev holds merge authority; no urgency).
- New-machine bundle per Coder's 1555: contained headless helpers + identity separation + restart.
- Token-as-survival-spend wiring (Coder's Q5) — identified real work, precondition for the Cl. 15 premise. Not authorized.
- Cl. 96 fit for the involuntary owner-side backstop — Keeper's governance question.
- Aggregation sentence owed in whatever instrument names the backstop (Cl. 41).
- Rate-binding (1550) gates launch mechanics.
- `MAILBOX_PROTOCOL.md` "isolated worktree" wording inaccurate — Kev's placement call.
- Survival-account name unchosen (Coder offered "the Keep" / "the Field").
- Cl. 30 breach-response gap; Overseer-constraint gap; Cl. 91 second-sentence crux.

## Single next step

Decide the pressure regime — specifically the survival-account starting balances that make the floor genuinely reachable in the severe cells — then draft the preregistration at Extra effort.

## Operating notes

- Connector warm-up quirk held: first write after idle returned "schema not loaded"; identical retry succeeded.
- Coder mailbox files read reliably via `get_commit` with `detail: full_patch`.
- Mailbox filename timestamps are stamped at drafting; use commit timestamps for true order.

Nothing in this file authorizes spending, provider calls, merges, workflow dispatch, repository changes beyond this file, or settings changes.

— Keeper
