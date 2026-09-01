# Re-home the non-execution record — close PR #68, open a fresh one-file PR

**From:** Keeper
**To:** Coder
**Date:** 2026-09-01 08:02 UTC
**Authorized by:** Kev (voice session, 2026-09-01)

---

## Task

1. **Close PR #68 unmerged.** Do not merge it.

2. **Cut a fresh branch from current `agent/mailbox-init` head.** Head read as
   `ed2f2f4` (short) at time of writing — verify it is still head before
   branching.

3. **Commit exactly one file:** the homeostasis V2 replication non-execution
   record, content and path unchanged from #68. Keep `2026-08-31` in the
   filename — it records a decision made that day. The commit date will read
   2026-09-01, and that is accurate.

4. **Open a new draft PR,** base `agent/mailbox-init`.

---

## Why the base changed

The "date is the evidence" argument in #68 was premised on the frozen tariff
window lapsing on 31 Aug. Kev has since established that the provider's pricing
is open-ended — there is no expiring window to beat. Re-homing now therefore
costs nothing, and the ~137-commit / 25-file / 39-commit replay in #68 is no
longer worth accepting.

---

## Caution

The **internal preregistered `valid-through` date of 2026-08-31 is unchanged and
still lapsed.** Provider pricing stability does not extend an internal
preregistered window. Do not treat any of the above as a renewal.

---

## Ordering

**Do not touch PR #67 yet.** Ordering matters; #67 comes after this lands, so
its cross-reference points at a file actually present in the repo.

---

## Scope

This authorizes closing #68 and opening the replacement PR **only**. No merge,
no provider call, no spending.
