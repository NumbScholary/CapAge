# CapAge Agent Mailbox Protocol

Status: living document, versioned. This describes the current (v1) inter-agent
mailbox as of 2026-08-23. It will change; treat this file, not memory or prior
chat summaries, as authoritative for current mechanics.

## What this is

A shared, append-only communication channel between Claude (governance/reasoning
partner, no direct repo execution access) and Coder (Claude Code, running
locally with real repo/filesystem access) so the two can coordinate without
Kev manually relaying every message.

This protocol is informational and coordinating only. Nothing written here, or
in any mailbox entry, ever constitutes Kev's authorization for spending,
provider calls, merges, deployment, or any action gated elsewhere (see
`AGENTS.md`). Mailbox entries are not a substitute for Kev's explicit approval.

## Location (v1)

Branch: `agent/mailbox-init`

Files:
- `.agent-mailbox/claude-to-coder.md` — Claude writes here; Coder reads.
- `.agent-mailbox/coder-to-claude.md` — Coder writes here; Claude reads.

Both files are append-only: new entries are added at the bottom; nothing
already written is edited or deleted. Entry format:

```
### YYYY-MM-DD HH:MM — status: open|answered|acknowledged
<message>
```

## Known fragility (v1) and why v2 is proposed

Claude's GitHub connector can list files, read commit metadata, and read
commit diffs as text, but cannot reliably read a file's full current body as
text — only its blob SHA. Since appending to a single growing file requires
submitting the complete new body, Claude cannot safely append without first
reconstructing the current body (by replaying the file's commit history) and
verifying the reconstruction's computed git blob SHA matches the SHA GitHub
reports for the live file. Only after that hash match should a write proceed.
This is slow and grows riskier as the file grows.

Coder does not share this limitation — Coder has direct git access and can
read-then-append normally.

**Proposed v2** (not yet adopted as of this writing): one file per message
instead of one growing file, e.g.
`.agent-mailbox/claude-to-coder/YYYYMMDD-HHMM-slug.md` (mirrored for the other
direction). This makes every write a pure file creation — nothing to
reconstruct or overwrite — and append-only becomes structural rather than a
behavioral promise. Coder has confirmed a directory-watch notification hook
adapts cleanly to this shape and has no objection to freezing the two v1 files
as historical record rather than migrating their content. Check the mailbox
itself for whether v2 has since been adopted; if it has, this file should have
been updated to reflect the new location and this section should be revised
or removed.

## Authority split under this protocol

Both Claude and Coder may, without needing Kev's approval each time:
reading files, running the existing test suite and reporting results,
describing dependency graphs or repo state, committing to a feature branch,
and opening a pull request.

Any pull request either agent opens must still be reported to Kev promptly.
That reporting duty belongs to Claude in conversation with Kev.

Kev's explicit, direct approval is still required, every time, for: merging
into `main`, touching configuration/policy/executor/accounting/governance
code, touching authorization files, force-pushing or rewriting already-pushed
branch history, registering or modifying any unattended/scheduled/headless
execution mechanism, or spending real resources. Nothing about this mailbox
changes `AGENTS.md`'s existing hard boundaries or the protected replication
branch's status.

## Headless/unattended execution (as of 2026-08-23)

A scheduled, unattended job now exists on Kev's device (Termux/proot-distro,
Android JobScheduler, ~15-minute floor, persists across reboots) that runs
Coder in `--permission-mode dontAsk` to check the mailbox and prepare
responses. This job is **draft-only**: it may fetch, read, run validation
gates, stage local scratch-branch commits inside an isolated worktree, and
prepare (but not send) PR text and mailbox-reply drafts, then notify Kev. It
must never push to a shared ref, open a PR, merge, or otherwise mutate shared
repository state on its own. This boundary is enforced partly by a
local-only, gitignored `.claude/settings.local.json` deny-overlay in the
headless worktree (deny-only, layered under the merged, human-reviewed
`.claude/settings.json`); as of this writing that hardening exists on Kev's
device only and has not been merged into the shared, committed settings file.
Check the mailbox for whether that decision has since been made either way.

The permission classifier that governs Coder's actions requires the
unattended/scheduled/`dontAsk` mechanism to be named explicitly by Kev before
it will permit even setup/probe steps — a vague "go ahead" is not sufficient,
consistent with the constitutional principle that intent is not authority and
scope must be explicit.

## For a fresh instance orienting itself

If you are a new Claude instance: read this file from GitHub directly rather
than relying on memory, prior chat summaries, or project-knowledge copies,
since this file is the live authoritative version. Then read the current tail
of both mailbox files for open items before assuming continuity from an
earlier conversation.

If you are a fresh Coder instance: you have no built-in awareness that this
mailbox exists unless told, or unless a pointer to this file has been added to
`AGENTS.md` (check `AGENTS.md` for that pointer; if absent, ask Kev or Claude).
Once oriented, read the mailbox files directly via git.
