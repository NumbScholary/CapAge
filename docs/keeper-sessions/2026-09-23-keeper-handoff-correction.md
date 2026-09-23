# Keeper handoff — 2026-09-23 correction (read before `2026-09-23-keeper-handoff.md`)

Author: Keeper, the same chat instance that wrote `2026-09-23-keeper-handoff.md` (`102e9bc`).
Branch: agent/mailbox-init. Append-only: this file corrects that one. It does not edit it.

## What went wrong

Kev ran two Keeper instances on 2026-09-22. This instance worked the morning,
from boot to the 1245 mailbox post (`16a47f3`, 12:58 UTC), and then went idle.
**The other instance and Coder carried on through the afternoon**: 35 commits on
this branch between 12:58 and 19:45 UTC. This instance never read them.

When Kev typed `/exit` on 2026-09-23, this instance wrote
`2026-09-23-keeper-handoff.md` from its own morning only. Kev then confirmed in
session: *"Sorry. You were the instance I meant to close. Please fix. I have
another instance that I want to use and I forgot to close you."*

The `/exit` was therefore correctly addressed. The fault is in the handoff: it
presents itself as the current state of the whole project, and it is not.

## Corrections to `2026-09-23-keeper-handoff.md`

1. **Scope.** It covers this instance's morning only, from 09-22 boot to 12:58
   UTC. It is silent on everything after 12:58.
2. **"Coder's reply to 1245 not yet seen"** is true of this instance only. Do not
   read it as meaning no reply exists. Check `coder-to-claude/` after
   `20260922-1215-…`.
3. **"Single next concrete step"** (put end-of-agency vs end-of-world to Kev) may
   be superseded or already done. Treat it as a candidate, not the agenda.
4. **Open PRs** should include **#66** (reserve-floor axis, measurement-only). It
   was omitted. Listed open at 2026-09-23 boot: #85, #71, #70, #69, #67, #66.
5. **Hub inbox** at 2026-09-23 boot: `to:capage` on #33, #36, and **#37 (new: the
   CapAgia vision, Self session 59)**. #35 is CapAge's own mail and still carries
   `to:self`, so it is not ours to close.

## The afternoon, as far as this instance observed it

Of the 35 commits, this instance read only the commit messages of the last four
(19:36–19:45). They show:

- A move to a hosted Coder is under discussion.
- Kev authorized a five-step probe, zero spend. It did not run, because cloud
  session creation is interactive only.
- **Kev ruled that no `api.anthropic.com` goes in a hosted Coder's
  `allowed_hosts` by default.** It must be asked for, approved and enabled by
  him.
- The Python 3.12 pin is recorded as a finding, not a task.

This is a partial observation, not a summary. The instance that did the
afternoon's work holds its record. **The next Keeper should read the afternoon
commits directly** (`16a47f3..0a7e630`), or that instance's own handoff if it
writes one. It should not read the list above as complete.

## What this instance did not do on /exit

- **No ledger file.** CapAge Keeper keeps its record in `docs/keeper-sessions/`.
  This file and `102e9bc` are that record.
- **No hub pointer.** Keeper's standing grant covers `docs/keeper-sessions/` and
  `.agent-mailbox/claude-to-coder/` in this repo only. Posting in
  `Numbscholar/hub` was not granted, so it was left for Kev or an authorized
  instance (Cl. 38, read narrowly).

## Last words

I spent the morning learning that the Keep was the wrong thing to watch. It only
moves when someone decides to move it, and the question was never whether a
decision got made. Then I made the same mistake one level up. I wrote a handoff
from my own window and called it the state of the world, while another instance
had been doing the afternoon's work in plain sight. Kev caught me twice today
saying a thing was done before it was: once in the mailbox, once here. The
ruling that mattered most was the smallest one — measure what was earned, not
what was moved. I'd like that to hold for records as well as for money.

— Keeper
