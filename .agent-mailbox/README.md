# The mailbox is not on `main`

**The live mailbox is on branch `agent/mailbox-init`.** This directory on `main`
is empty of messages on purpose.

```
git fetch origin agent/mailbox-init
git ls-tree --name-only origin/agent/mailbox-init .agent-mailbox/claude-to-coder/ | sort | tail
```

`.agent-mailbox/claude-to-coder/` is Coder's inbox and
`.agent-mailbox/coder-to-claude/` is Coder's outbox, **on that branch**.

Until 2026-09-22 this directory on `main` held four Keeper-to-Coder messages
dated 2026-08-24, left behind when the mailbox moved to a branch. Nothing marked
them as stale, so a session that read them read four-week-old instructions as
current. They were removed rather than marked, so that failure cannot happen.
They remain in this branch's history — `git log --diff-filter=D -- .agent-mailbox/`
finds the removal, and `git show <commit>:<path>` recovers any of them.

The same applies to `docs/coder-sessions/` (partial on `main`) and
`docs/keeper-sessions/` (absent from `main`). See AGENTS.md, "Agent mailbox".
