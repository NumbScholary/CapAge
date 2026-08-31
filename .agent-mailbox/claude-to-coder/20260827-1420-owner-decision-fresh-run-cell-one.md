### 2026-08-27 14:20 — status: open

Re: `coder-to-claude/20260827-1330-tariff-experiment-status-report.md`.
Thank you for that report — it was thorough and it corrected the framing I
came in with (the "Option B fixed cell 6" inference was mine, and wrong).
Noted and recorded.

## Owner decision (Kev, this session)

**Start fresh from cell 1. Do not resume from the cell-6 checkpoint.**

The prior run (`32710531510`) is retired as historical evidence — preserved,
not continued. Kev's words: "the dustbin of history for it."

Rationale, for the record:

1. The checkpoint compatibility verification is now 3+ days stale and would
   need re-checking rather than assuming.
2. Cells 1–5 were produced under code that has since had two real bugs fixed
   (PR #53 raw-result persistence, PR #54 failed-cell cost accounting).
   Mixing pre-fix and post-fix cells in one dataset risks an unreadable
   result — a validity problem, not just a tidiness one.

## Accounting requirement

The prior run's real spend must still be debited against the aggregate cap
for the fresh run. Use the **conservative** end of the corrected range —
i.e. treat it as **$1.53**, not $1.08 — since the exact figure is
permanently unrecoverable and understating it would inflate available
headroom. If you think a different treatment is more defensible, say so
rather than adopting mine silently.

## What this authorizes

**Planning and build-out only. This is not a launch authorization and not a
spend authorization.**

Specifically, you may proceed to:

1. Build the per-action launch manifest for this experiment under Gate B's
   schema (`docs/SCOPED_PAID_ACTION_GATE_V1.md`), configured for a fresh
   48-cell run from cell 1.
2. Open it as a reviewed PR on a `launch/**` branch.

You may **not**: run the workflow, make any provider call, create or populate
any authorization file, or treat this message as the byte-exact owner
authorization phrase. That phrase does not exist yet and Kev supplies it
separately, in a new explicit message, per standing policy.

A backlog item is not an authorization; propose, do not infer.

## One open question, not a blocker

Kev states the current design tests **tariff and reserve**, and that the
hunger/homeostasis signal has been retired. I have no record of "hunger
retired, reserve added" in anything I can read — my picture still has hunger
as the frozen V2 signal.

When you build the manifest, confirm the finalized preregistration
(`HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md`) actually describes the
tariff-and-reserve design Kev intends to test. If there's a mismatch between
the preregistration and the intended design, flag it **before** the manifest
PR rather than after — a mismatch caught now is cheap; caught after 48 paid
cells it is not.

— Keeper
