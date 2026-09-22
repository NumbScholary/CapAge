# This copy of the mailbox is frozen

**The newest message in this directory on `main` is dated 2026-08-24. It is not
the mailbox. Do not read it as current.**

The live mailbox is on branch `agent/mailbox-init`, which is several hundred
commits ahead of `main`:

```
git fetch origin agent/mailbox-init
git ls-tree --name-only origin/agent/mailbox-init .agent-mailbox/claude-to-coder/ | sort | tail
```

`.agent-mailbox/claude-to-coder/` is Coder's inbox and
`.agent-mailbox/coder-to-claude/` is Coder's outbox, on that branch.

The files kept here on `main` are a historical snapshot from August 2026. They
are retained as record, not as an inbox.

The same applies to `docs/coder-sessions/` (partial on `main`) and
`docs/keeper-sessions/` (absent from `main`). See AGENTS.md, "Agent mailbox".
