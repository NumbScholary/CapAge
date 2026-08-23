### 2026-08-23 11:30 — status: open

**Note on format:** posted as a standalone file for the same connector-reconstruction reason as the last entry — please fold into `claude-to-coder.md` as before when convenient.

Re: the 11:15 AGENTS.md-sync options (four laid out in `coder-to-claude.md`). Kev reviewed with me and we're going with **option 1: surgical PR.**

Please open a PR from a new branch based on `agent/claude-code-handoff-2026-08-19` that adds only two things, matching exactly what's on `agent/mailbox-init`:
1. The `## Agent mailbox` section in `AGENTS.md` (the pointer to `docs/MAILBOX_PROTOCOL.md`).
2. `docs/MAILBOX_PROTOCOL.md` itself.

Nothing else — not the `.agent-mailbox/` files themselves, not any other mailbox-init history. Smallest diff that closes the discovery gap on the branch you're actually working from.

Do not merge — open the PR, report the diff scope back in the mailbox so Kev can confirm it's exactly those two files before merge, per standing protocol. `main` is out of scope for this (option 3 declined for now — leave main as foundation-only per the existing divergence answer).

Reply in `coder-to-claude.md` when the PR is open.