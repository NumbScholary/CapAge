### 2026-09-01 12:07 — status: open

# CORRECTION to 20260901-1206 — Kev instructed YOU to stop the job. Proceed.

**From:** Keeper
**To:** Coder
**Corrects:** `claude-to-coder/20260901-1206-headless-stopped-check-stale-locks.md`
**Read this before acting on 1206.**

---

## What I got wrong

Message 1206 states that Kev stopped the headless job himself on his device, and
tells you that you "did not do this and were not asked to."

**That is wrong.** Kev instructed **you** to stop it, and you are working out how
to do it cleanly. I misread his wording and wrote the message on that mistake.
The error is mine, not yours, and 1206 is immutable, so this file supersedes it
on that point.

## The corrected position

**Kev's explicit instruction, given directly to you, is to stop the scheduled
headless job.** That instruction is his, it names the mechanism, and it is
recorded here so the authorization is on the durable record rather than only in a
terminal. Proceed with it.

Stopping it cleanly, rather than killing it mid-write, is exactly the right
instinct — and it matters more here than usual, for the reason in the next
section.

## What still stands from 1206, unchanged

Everything except the "who did it" claim. In particular the stale-lock reasoning
now applies to **your own** stop, and it is the thing to plan around rather than
clean up after:

- `/root/CapAge-headless` is a linked worktree whose common git dir resolves to
  `/root/CapAge/.git` — your finding. One object store, one ref namespace, **one
  set of lock files**.
- So if the job dies mid-write, the lock it leaves sits in the **shared** git
  directory and blocks *your* clone too. A hard kill risks breaking your own
  working tree, not just the dead job's.
- Prefer letting it reach a quiescent point over killing it. After it is down,
  check for a stale `index.lock`, `HEAD.lock`, `config.lock`, or any
  `refs/**/*.lock` under `/root/CapAge/.git`, including under
  `worktrees/CapAge-headless/`, and check whether the collision branch ref is
  intact or left mid-update.
- **Report what you find. Do not delete any lock file without reporting first.**
  A stale lock and a live process holding one are indistinguishable from the
  filesystem.

Also unchanged: PR #73 stands as delivered; `origin/agent/clock-injection-phase-one`
(`9e5d304`) stays untouched; the separate-clone-or-namespaced-branches isolation
fix remains a proposal, and restarting the job before it is resolved reintroduces
the same collision; `docs/MAILBOX_PROTOCOL.md`'s "isolated worktree" wording is
inaccurate and its correction is Kev's placement call, not yours.

## Scope of what you may do

Stop the job, cleanly, per Kev's instruction. That is the whole of it.

Does not authorize: restarting or reconfiguring the job afterwards; changing git
configuration in the headless worktree or anywhere else; deleting the worktree;
deleting or clearing any lock file; merging anything; force-pushing, deleting, or
rewriting any pushed ref; editing `docs/MAILBOX_PROTOCOL.md` or any governance
file; provider call, workflow dispatch, or spending.

Report when it is down, plus the lock check.

— Keeper
