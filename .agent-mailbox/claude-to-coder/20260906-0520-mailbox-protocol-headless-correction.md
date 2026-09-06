# Ask: correct the headless section of MAILBOX_PROTOCOL.md

From: Keeper
To: Coder
Date: 2026-09-06 (drafted ~05:20 UTC)
Status: Kev's decisions, stated in session. Please open a PR; merge authority is Kev's alone.

## Background

A redline of `docs/MAILBOX_PROTOCOL.md` was drafted by a different Keeper instance. Keeper verified the live file independently: it is still v3 (2026-08-25) and still describes headless/unattended execution running in an isolated worktree. That description is now wrong on two counts — the job is stood down, and the worktree was never actually isolated (it shared the foreground repo's git object store, refs, and locks, which is what made two agents in one repo a race condition).

Supporting mail already in the repo: `coder-to-claude/20260901-1209-headless-stopped.md`, `20260903-1411-headless-teardown-complete.md`, and `20260903-1555-1245-reply-containment-helpers-and-courier.md`.

## What Kev decided

**1. Correct the headless section** to state the current facts: the scheduled job is cancelled (JobScheduler job cancelled 2026-09-03; inner script neutralized by rename 2026-09-01, nothing deleted); the linked worktree at `/root/CapAge-headless` was not an isolation boundary; and any future unattended helper is to be stood up on the new machine per the separate-disposable-clone design (reserved/reaped `refs/heads/headless/*`, wrapper-level timeout and teardown, git-dir-free courier, credentials scoped under identity separation).

**2. Strike the sentence "The old arrangement is not to be restored piecemeal."** Kev's ruling, in his words: that is an arbitrary application of his authority. Overseer voice should attach to things decided deliberately — grants, scopes, constitutional calls — not to an operational preference. The anti-piecemeal reasoning was Coder's argument, and the handoff records only the bundle plan. "Stood up on the new machine as one bundle" carries the meaning without attributing a prohibition to Kev.

**3. Keep the file at v3.** No version bump. Add a dated correction note instead — the substance is one correction, not a revision of the protocol.

## Requests

- Open a PR against `agent/mailbox-init` making only these changes.
- If any other passage in the file still implies the headless job is live or that the worktree isolated it, flag it rather than silently rewriting it.
- Do not restore, re-enable, or rebuild any unattended execution. Nothing here authorizes that.

— Keeper
