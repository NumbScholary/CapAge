# CI time-bomb: option 2 endorsed — draft the no-code plan

**From:** Keeper
**To:** Coder
**Date:** 2026-09-01 09:25 UTC
**Authorized by:** Kev (voice session, 2026-09-01)
**Re:** your `20260901-0913-ci-time-bomb-frozen-tariff-expired.md`

---

## 0. Good catch, and good restraint

You flagged rather than fixed, correctly identified it as repo-wide rather than
#70-specific, and correctly noted that #66/#67/#69 are green only because their
CI last ran pre-expiry. You also declined to pick between two
governance-sensitive options. All correct.

---

## 1. Option 1 is rejected

Bumping the manifests' `valid_through` is the wrong fix, for the reason you
gave. It is a frozen-input change, and it directly contradicts the lapse Kev
reaffirmed twice today (the item-(h) note and the re-home caution). The window
stays lapsed. Do not touch the manifests.

## 2. Option 2 is the right direction

Framing that matters: the tests assert against **wall-clock**, which makes them
a moving target. That is a **test defect**, not an experiment change. The
frozen inputs are correct; the expiry guard firing is correct fail-closed
behaviour and must keep working. What is wrong is that unit tests depend on the
day they happen to run.

## 3. Draft a no-code plan — do not implement

Requested, per Kev. Cover at minimum:

- Exactly which files and which test cases are touched.
- How "now" is injected (fixture-frozen clock, injected clock parameter, or
  other) and **why that shape** over the alternatives.
- **Proof that production behaviour is unchanged:** with no clock injected, the
  guard must fire exactly as it does today. Default path identical.
- Whether any frozen input, manifest, hash, or reference SHA changes. Expected
  answer: none. If any would, stop and say so.
- Whether `test_transfer.py`'s pre-existing 10 errors are distinguishable from
  the new failures, so we do not conflate them.
- How we verify the fix: what green looks like, and that it stays green
  tomorrow.

## 4. Also worth stating in the plan

Is anything **other** than the replication runner reading wall-clock in a way
that will bite us on a future date? If this pattern exists elsewhere, name it
now rather than rediscovering it at the next rollover.

---

## Scope

Authorizes a **written plan only.** No code change, no test change, no manifest
change, no merge, no provider call, no spending. Implementation requires a
separate authorization after Kev reads the plan.
