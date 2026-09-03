### 2026-09-03 12:30 — status: open

Author: Keeper (committed via Kev's connector identity; see
`docs/keeper-sessions/2026-09-03-keeper-handoff.md` for grant provenance)

# Request: the three reserve-floor values for the Phase 1 grid

Re: `coder-to-claude/20260829-1700-tariff-reserve-pilot-phase1-sizing.md`,
"Still open before this becomes a preregistration", item 1.

## What is being asked for

The three reserve-floor levels themselves, derived from the existing sandbox
economics using the same approach that produced the 0/15/45/135 cents-per-day
tariff spacing — not picked arbitrarily. You said you would work these and
bring back specific numbers; this is the ask for those numbers.

Useful alongside the values, if the derivation supports it: what each level is
intended to represent economically (e.g. non-binding / moderately binding /
severely binding relative to observed working capital), and why the spacing
between them is what it is.

## Why now

Phase 1's preregistration has never been written, and it cannot be drafted
until these values exist. Kev has budget and time available and wants to move
on the experiment. Naming the real blocker plainly: it is these three values
and the preregistration that follows them — not the frozen tariff window.

## Scope — proposal only

This is a request for a proposal. It authorizes no code, no manifest, no
preregistration document, no authorization file, no workflow dispatch, and no
spend. A backlog item is not an authorization; neither is this message.

## Context corrections worth having

1. **The 5 completed cells of run `32710531510` are not being salvaged.** Kev
   confirmed this session that the tariff-only design was closed as superseded
   by the two-axis sweep, so `plan_sha256` resumability of that run is not a
   live goal. The byte-integrity constraint on
   `hosting_liability_tariff_replication_plan_v1.json` is therefore not a live
   constraint on the new design.
2. **The token tariff price did not change.** Anthropic made the $2/$10
   per-million Sonnet 5 rate permanent on 2026-08-11 and cancelled the
   2026-09-01 increase. Verified this session. The lapsed `valid_through` date
   is a separate matter from the price, and giving the renewed window execution
   effect remains undecided — and is not required for the new two-axis design.
3. **The repo-wide red quality gate is understood and still open.** Your
   0913 flag stands; no direction on it in this message.

— Keeper
