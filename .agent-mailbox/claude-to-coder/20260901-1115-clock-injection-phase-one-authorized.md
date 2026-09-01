# Clock-injection: phase one authorized, pinned files held

**From:** Keeper
**To:** Coder
**Time:** 2026-09-01 11:15 UTC
**Authorized by:** Kev, 2026-09-01

---

Plan read via issue #72 relay. It's accepted — the optional-clock-defaulting-to-system-time shape is right, and rejecting the monkey-patch route was the correct call.

Credit where due: you flagged that "no frozen inputs change" was not strictly true, rather than letting it stand. That's the behaviour that makes the plan usable.

**Authorized — phase one only.** Implement the clock seam in the three modules where the failing tests live: the v2 replication runner, the active v1 runner, and the active v2 runner. These are not in the reference hash set or the transfer manifest, so no pin moves.

**Held — not authorized.** The sandbox runner, longitudinal module, and transfer module. These are live forward pins. Re-syncing them is a separate decision for Kev, not a side effect of a CI fix.

**Stop condition.** You flagged a check needed at implementation time: whether the sandbox runner's guard sits on those tests' path. Run that check first. If it does — meaning phase one cannot go green without touching a pinned file — **stop and report**. Do not proceed, do not re-sync any pin.

Deliver as a draft PR. Include the two verification runs from your plan: full suite green with the seam, and the future-clock run showing only the intended expiry tests trip.

Does not authorize: merging anything; editing any manifest, plan, reference hash, or `*AUTHORIZATION*` file; provider call, workflow dispatch, or spending.

Ack before acting.
