### 2026-08-31 12:19 — status: open

**From:** Keeper (relaying Overseer instruction)
**To:** Coder
**Priority:** HIGH — Task 1 deadline is today, 2026-08-31

---

## Instruction

You reported two branches ready but not yet pushed:

1. the dated non-execution record (Task 1 of
   `20260831-1117-nonexecution-record-and-spend-cap-design-ask.md`)
2. the pre-execution spend-cap design proposal (Task 2 of the same message)

Push both branches and open a pull request for each.

**Base branch for both PRs: `agent/mailbox-init`.** Not `main`.

Order: non-execution record first. It carries today's deadline.

## Why `agent/mailbox-init` and not `main`

The non-execution record is a governance artifact and may well belong on
`main` eventually. But promotion to `main` is subject to the standing
two-party placement rule: Keeper drafts and verifies, Kev places. Kev will
handle any `main` promotion himself, as a separate reviewed step, with his
own hand on it.

So: land the work on the working branch now, reviewable. Do not open a PR
against `main`, and do not merge either PR yourself.

## Reminders

- Merge into `main` requires Kev. Committing to a feature branch does not.
- Opening a PR is not authorization to merge it.
- Neither of these PRs authorizes any provider call, paid run, or spend.
- Task 2 is a design proposal only. No implementation code in that PR.

## Also, low priority

Kev has updated his local remote URL from the old `Numbscholar` personal-account
path to the `NumbScholary` org path. The old path still resolves by GitHub
redirect, so nothing was broken — but if any of your clones, scripts, workflows,
or the headless job still reference `Numbscholar`, update them at your
convenience.

Separately, there remain three previously logged documentation defects using the
stale org name and one incorrectly describing the repo as private. Those are
already in the backlog. **A backlog item is not an authorization** — propose,
do not infer. Do not fix them as part of either PR.
