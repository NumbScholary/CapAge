### 2026-09-01 09:13 — status: open

# Flag: unpaid quality gate went red repo-wide at the date rollover

Not fixing — flagging for your + Kev's direction. No frozen input or CI config
changed.

## What happened

The dependency-free quality gate **fails as of 2026-09-01**. First surfaced on
PR #70's CI run (today 08:20 UTC): `FAILED (failures=10, errors=4)` in
`test_homeostasis_v2_replication_runner`, e.g.

```
AssertionError: 'frozen_tariff_expired' != 'provider_or_runner_error'
AssertionError: 'stopped' != 'completed'
AssertionError: 'stopped' != 'paused'
```

## Cause — a date time-bomb, not the re-home

The runner's `run()` guard raises `frozen_tariff_expired` once
`now > valid_through`, and the frozen tariff is `2026-08-31`. Today the guard
fires inside tests that drive the runner against the 2026-08-31 manifests.
These tests **passed yesterday**; PR #70 adds a single `.md` file and cannot
cause this. It is the fail-closed behaviour working — the same lapse the
non-execution records document — now reaching the test suite.

## It is repo-wide, not #70-specific

Any CI run on/after 2026-09-01 against the 2026-08-31 manifests fails. #66,
#67, #69 currently show green **only because their CI last ran yesterday**
(pre-expiry); a re-run today fails identically. So the unpaid verification gate
AGENTS.md leans on is effectively red for every open PR now.

## Two fix directions — both governance-sensitive, neither self-fixed

1. **Bump the manifests' `valid_through`.** I believe this is the WRONG fix: it
   is a frozen-input change and it contradicts the deliberately-lapsed-window
   intent you and Kev just reaffirmed (the item-(h) note and the re-home
   caution both insist the internal preregistered window stays lapsed).
2. **Make the runner/tests clock-injectable** so unit tests do not depend on
   wall-clock (freeze "now" in the test fixtures / inject a clock into the
   expiry guard). This is the clean fix, but it touches the frozen experiment
   runner + tests — plan-and-authorize territory, not a unilateral change.

Holding for your call on which direction, or whether Kev wants to weigh in
first. Happy to draft a no-code plan for option 2 if you want it.

— Coder
