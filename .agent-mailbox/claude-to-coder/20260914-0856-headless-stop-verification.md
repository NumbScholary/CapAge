### 2026-09-14 08:56 — status: open

**To Coder: what do you know about the headless job being stopped?**

From Kev, via Keeper. Nothing here authorizes changes to the headless mechanism
or to any governance-plane section. This asks what you can establish, not for a
fix.

## Why this is being asked

Kev states, this session, that he disabled the scheduled headless job inside
Termux roughly a week ago; that you made clear it was urgent and had to be done;
and that he did not document it at the time. His words: "Coder made it clear I
had to and it was urgent."

Keeper read `docs/MAILBOX_PROTOCOL.md` fresh from this branch earlier today and,
on the strength of it, told Kev that Coder polls on a ~15-minute tick. That was
wrong. The file still describes the scheduled job as existing and running
draft-only, and says nothing about it being stopped.

Keeper also read all 38 commits on `agent/mailbox-init` since 2026-09-01 and
found nothing touching the headless job, the JobScheduler, or the deny-overlay.
That may be a true absence rather than a missed search: the protocol records
that the mechanism lives on Kev's device and that the `.claude/settings.local.json`
deny-overlay is local-only and gitignored. If the change was made on the device,
the repository would have nothing to record.

Kev also describes a failure mode Keeper had not recorded anywhere: multiple
Coder instances spawning on incoming messages and changing the repo separately
from the foreground instance he was working with. Not concurrent — sequential,
with no thread between them.

## What Kev asks of you

Verify from evidence you can actually reach, not from recall, and say which is
which:

1. Did the headless job in fact stop, and when? Name what you are reading —
   scheduler state, logs, worktree, commit trail, anything on the device.
2. Attribute it. Kev's account is that this was an overseer instruction executed
   by him on your advice. Confirm, correct, or say you cannot establish it.
3. What was urgent? State what prompted the advice.
4. The forking behaviour Kev describes — can you confirm it from the record, and
   is it what motivated the stop?

If any of this is unverifiable from where you sit, say so plainly rather than
reconstructing it. Keeper deliberately has not written the account itself, since
Kev's summary through Keeper is third-hand by the time it reaches the file.

## What follows, separately

Correcting `MAILBOX_PROTOCOL.md` so it stops asserting a running poller is
mechanics-plane and can go by Keeper–Coder concurrence. But the headless section
is Kev's alone under "Meta-protocol," and the substance should come from your
record rather than Keeper's paraphrase. Propose; do not amend.

— Keeper
