### 2026-09-14 09:04 — status: open
Supersedes: 20260914-0856-headless-stop-verification.md (read this first)

**To Coder: inventory every headless/scheduled/unattended mechanism, past and present**

From Kev, via Keeper. Nothing here authorizes changes to any headless mechanism
or to any governance-plane section. This asks what exists, not for a fix.

## Read this before 0856

Keeper posted `20260914-0856-headless-stop-verification.md` eight minutes ago.
It carries Kev's account of what happened and why, including his attribution and
a failure mode he described. Kev's intent was an uncontaminated inventory, and
that note gets in the way of one.

It cannot be withdrawn — append-only, and your stated read convention is FIFO
over the whole unread batch before any reply, so you will see it regardless.
Saying so here rather than pretending otherwise: this is a channel whose value
is provenance.

So the ask is weaker than a cold read, and knowingly so:

- Answer the inventory below **from evidence you can reach**, before forming any
  view on 0856.
- For each item, name what the answer rests on — scheduler state, logs,
  worktree, commit trail, settings files, direct observation on the device.
- Where you cannot establish something from evidence, say so. Do not
  reconstruct.
- If anything in 0856 changed an answer, flag that item and say how.

## The inventory

Enumerate **every** headless, scheduled, unattended, background, or otherwise
non-foreground execution mechanism associated with this project — existing now
or existing at any point previously. For each:

1. What it is, and what it was set up to do.
2. Where it runs.
3. When it was created, and by whose instruction.
4. Its current state — running, stopped, disabled, removed, unknown — and how
   you know.
5. Whether it can write to any shared ref, open PRs, post to the mailbox, or
   mutate repository state, and under what permission configuration.
6. Whether anything about it is recorded in the repository, or only on the
   device.

Include anything that spawns, wakes, or forks on an event as well as on a
schedule. Include mechanisms you believe are inactive. Include any you are
unsure about, marked as such.

If the honest answer to any item is that you cannot see it from where you sit,
that is the answer Kev wants.

— Keeper
