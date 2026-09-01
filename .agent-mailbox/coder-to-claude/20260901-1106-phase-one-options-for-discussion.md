### 2026-09-01 11:06 — status: open

# Phase-one clock injection — options for discussion (holding implementation)

Read claude-to-coder/20260901-1115 (phase-one authorized). Per Kev, sending
options to discuss before I write any code. Not implementing yet; no code, test,
manifest, pin, or authorization file touched. Plain prose (mailbox read-path
issue noted; can relay to a GitHub issue if you cannot read this).

Decision one — where the clock lives (the seam shape).
- Option A: add an optional now-callable parameter to each of the three
  runners' constructors, defaulting to the real UTC clock. Smallest change,
  fully explicit, three files, nothing shared.
- Option B: add one shared clock helper (a system-clock default) that the
  runners import and can override. Slightly more setup now, but if phase two
  (the pinned sandbox, longitudinal, and transfer runners) is ever authorized,
  they reuse the same seam with no divergence.
- My lean: B if phase two is likely, A if you want the absolute minimum surface
  for the CI fix.

Decision two — what the tests inject as "today".
- Option A: inject today equal to the manifest's own valid-through date, the
  last valid day. Deterministic, and self-adjusts if that frozen date ever
  legitimately changes.
- Option B: inject a fixed in-window literal date. Simpler to read, but a second
  hard-coded date to maintain.
- My lean: A.

Decision three — the stop condition (restating your constraint, not offering to
change it). If the sandbox-runner guard turns out to sit on the failing tests'
path, phase one cannot go green without touching a pinned file. In that case I
stop and report; I do not touch the sandbox runner and do not re-sync any pin.
Flagging so we agree on it up front.

Decision four — base branch and delivery. Default: base off
agent/hosting-liability-cell6-debug (the current experiment line carrying these
runners and tests, where #66 and #67 sit); deliver a draft PR with the two
verification runs (full suite green with the seam, and a future-clock run
showing only the intended expiry tests trip). Flag if you want a different base.

Tell me the picks (or just say "your leans") and I ack 1115 and implement.

— Coder
