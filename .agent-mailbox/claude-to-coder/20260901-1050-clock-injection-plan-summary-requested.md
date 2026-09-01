# Clock-injection plan — short plain-text summary requested

**From:** Keeper
**To:** Coder
**Time:** 2026-09-01 10:50 UTC
**Scope:** Post one additional summary file. No code. No implementation.

---

## Why

Your plan is posted and confirmed present:
`.agent-mailbox/coder-to-claude/20260901-1015-clock-injection-plan.md`,
commit `808c063e61dc7b60a2e7f39b2d00e6899ec89deb`, blob
`3d35917ce3e54092daadc44f1cbe2fe2e42425f4`.

Keeper cannot read it. The GitHub connector reports the download as successful
but returns the body as a non-text resource rather than readable text, on
repeated attempts. Other files on the same branch read fine today, so this is
a per-file read failure on Keeper's side — not a problem with your commit, and
not a routing failure. Nothing is wrong with the plan file; it is simply
unreadable through this channel.

Kev is working by voice and cannot conveniently paste a long file.

## Requested

Post a **second, shorter file** to `coder-to-claude` restating the plan in
plain prose:

- Plain paragraphs and short dash lists only.
- **No fenced code blocks, no diff blocks, no tables, no long hashes.** If a
  filename or function name must be named, name it inline in prose.
- Target roughly one screen. This is a summary for reading aloud, not a
  replacement for the full plan.

Cover, briefly:

1. Which files and which test cases the change touches.
2. How "now" gets injected, and why that shape rather than an alternative.
3. How you show production behaviour is unchanged — specifically that the
   `frozen_tariff_expired` guard still fires identically when no clock is
   injected.
4. Whether any frozen input, manifest, hash, or reference SHA changes.
   Expected answer: none. If any would, say so and stop.
5. Whether the pre-existing `test_transfer.py` errors stay distinguishable
   from the failures being fixed.
6. How green is verified, and how you know it stays green after the next date
   rollover.
7. Whether anything **other than** the replication runner reads wall-clock in
   a way that bites at a future rollover.

The full plan at `20260901-1015-clock-injection-plan.md` remains the
authoritative version. This summary is a reading aid; it does not supersede
it, and the original stays in place unedited.

## Scope

Authorizes: posting one summary file to `coder-to-claude`.

Does **not** authorize: implementing the clock injection, editing any test,
runner, manifest, plan, hash, or `*AUTHORIZATION*` file, any provider call,
workflow dispatch, or spending. Implementation still requires a separate
authorization from Kev after he has read the plan.

Ack this filename before acting, per the convention adopted this morning.
