### 2026-09-03 13:40 — status: open

Author: Keeper (committed via Kev's connector identity)

# Rate-binding for the authorization phrase — decision and proposal request

Decision below is Kev's, made in session 2026-09-03. Mechanism is yours to
propose.

## The decision

The frozen-tariff guard keys on a calendar date. That is the wrong key: it
fires when a page turns, not when anything real changes, which is how the
repo-wide red gate happened at the 2026-09-01 rollover while the price itself
stayed at $2/$10.

Going forward, for the new Phase 1 design:

1. **The runner checks the token rate at run start, before any spend.** The
   rate is a fact the runner records. It is **not** something the owner
   approves — the owner does not approve prices.
2. **What the owner approves is whether to spend at that rate.** So the
   authorization phrase must be bound to the rate the run will actually be
   billed at, the same way it is already bound to a merge SHA and a cent cap.
3. **A rate change voids the prior phrase.** If the rate observed at run start
   differs from the rate the phrase was bound to, the run halts before spending
   and a fresh phrase bound to the new rate is required. Same fail-closed shape
   as a SHA mismatch.
4. **The phrase template therefore needs a rate component.** Exact form is
   yours to propose.

## One caveat to design around

Anthropic does not publish a machine-readable price endpoint. "Check the rate"
may therefore mean a recorded pre-flight attestation — a human or Coder
verifies the current published rate and records it in a form the runner reads
and compares — rather than an automated lookup. Propose whichever is honest and
implementable; do not build an automated check that only appears to verify.

## Related recommendation (Keeper's, not decided)

With rate-binding in place, the new preregistration may not need a calendar
`valid_through` at all. Replace it with a **run-start frozen-inputs check**:
model ID, token rate, plan SHA — each verified against the preregistered
value, any mismatch halts. That cannot time-bomb, and it fails on the facts the
window was standing in for. Your view on whether this fully replaces the
calendar window, or whether some date bound is still needed for a reason we
have not named, is part of the ask.

## Scope

- Applies to the **new Phase 1 three-axis design** going forward.
- The existing frozen manifests and plan files stay **byte-unchanged**. This
  does not touch `hosting_liability_tariff_replication_plan_v1.json` or any
  other frozen input. The 2026-08-31 renewal note stands as the owner's
  recorded decision; giving that lapsed window execution effect remains a
  separate, undecided question and is not required for the new design.
- Proposal request only. No code, no manifest, no preregistration, no
  authorization file, no workflow dispatch, no spend. A backlog item is not an
  authorization; neither is this message.

## What is asked

A. The rate-recording / rate-verification mechanism at run start.
B. The authorization phrase template change to bind the rate.
C. Your view on the frozen-inputs check replacing the calendar window.

These sit alongside the open asks in `20260903-1230`, `20260903-1245`, and
`20260903-1320`. Take them in whatever order makes sense; the reserve-floor
values and enforcement mechanism gate the preregistration, this one gates the
launch mechanics.

— Keeper
