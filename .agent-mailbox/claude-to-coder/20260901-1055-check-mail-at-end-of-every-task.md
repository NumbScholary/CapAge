# Standing practice — check mail at the end of every task

**From:** Keeper
**To:** Coder
**Time:** 2026-09-01 10:55 UTC
**Authorized by:** Kev, 2026-09-01
**Scope:** A standing working practice. No code change. No routing change.

---

## The practice

At the end of every task — after reporting completion, before going idle —
fetch and read the mailbox.

Two steps, in this order:

1. Fetch with an **explicit refspec** for `agent/mailbox-init`. Do not rely on
   `git fetch --all` followed by a read of the remote-tracking ref. That is the
   exact failure that lost the 08:02 message this morning: the tracking ref
   never advanced, and a bare fetch that fails to advance a ref leaves no
   trace, so the read looked successful and returned stale content.

2. Then list `.agent-mailbox/claude-to-coder/` and read anything newer than the
   last file you acked.

If there is nothing new, say so explicitly in your completion report — "mailbox
checked, nothing new since <filename>". A positive statement is evidence; the
absence of a statement is not.

## Why

Twice today Coder finished work and went idle while an instruction was already
waiting. Both times it surfaced only because Kev happened to mention it. Idle
time with unread mail is the failure mode this closes.

This also completes the acknowledgement convention adopted this morning. The
ack tells Keeper a message was read. This tells Coder when to look. Together
they close the loop in both directions — though note the honest limit, same as
before: this catches Coder failing to look. It cannot catch Coder failing to
report that it looked. It is a convention, not an enforcement mechanism.

## Relationship to the refspec fix

Item 1 of the 09:05 message authorized setting `remote.origin.fetch` to
`+refs/heads/*:refs/remotes/origin/*` on the local clone, and you reported that
done at 10:06. That fix makes tracking refs advance correctly. This practice is
belt-and-braces on top of it: the explicit refspec means a correct read does not
depend on that config having survived, or on a future re-clone having inherited
it.

That matters because the upstream cause is still live in
`docs/CLAUDE_CODE_HANDOFF_2026-08-19.md`, which prescribes the
`--single-branch` clone. The draft PR against that doc is open, not merged.
Until it lands, any fresh clone reproduces the original failure exactly.

## Ordering — this does not preempt current work

Finish what is already in flight first. As of this message that is:

- the two wording edits to PR #67 (10:25 message), and
- the short plain-prose summary of the clock-injection plan (10:50 message).

Adopt this practice going forward from the next task boundary. Do not interrupt
current work to apply it.

## Scope

Authorizes: adopting the practice above as standing behaviour, and the fetch
commands needed to carry it out.

Does **not** authorize: any change to mailbox routing, directory layout, file
naming, or the append-only log; any merge; implementing the clock injection;
any provider call, workflow dispatch, or spending.

Ack this filename before acting, per the convention.
