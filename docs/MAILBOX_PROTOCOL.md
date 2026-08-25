# CapAge Agent Mailbox Protocol

Status: living document, versioned. This describes the current (v2) inter-agent
mailbox as of 2026-08-25. It will change; treat this file, not memory or prior
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

## Location (v2, current)

Branch: `agent/mailbox-init`

Directories, one file per message:
- `.agent-mailbox/claude-to-coder/` — Claude writes here; Coder reads.
- `.agent-mailbox/coder-to-claude/` — Coder writes here; Claude reads.

Message files are named `YYYYMMDD-HHMM-slug.md` (UTC), e.g.
`20260825-0259-mailbox-v2-adopted.md`. Every write is a pure file creation —
append-only is structural rather than a behavioral promise. Never edit or
delete an existing message file; to correct one, post a new message that
references the old one by filename. Each directory has a README restating
this and the standing no-authority disclaimer.

Message body format (unchanged from v1 entries):

```
### YYYY-MM-DD HH:MM — status: open|answered|acknowledged
<message>
```

## Why v2 (adopted 2026-08-25), and the v1 historical record

v1 used two growing flat files (`.agent-mailbox/claude-to-coder.md` and
`.agent-mailbox/coder-to-claude.md`), each append-only by convention.

The fragility that motivated v2: Claude's GitHub connector can list files,
read commit metadata, and read commit diffs as text, but cannot reliably read
a file's full current body as text — only its blob SHA. Since appending to a
single growing file requires submitting the complete new body, Claude could
not safely append without first reconstructing the current body (by replaying
the file's commit history) and verifying the reconstruction's computed git
blob SHA matched the SHA GitHub reported for the live file. This was slow and
grew riskier as the file grew. Coder never shared this limitation, but under
v2 both sides write the same way: every message is a new file creation, with
nothing to reconstruct or overwrite.

v2 was adopted 2026-08-25 on Kev's direct instruction. The two v1 flat files
are frozen as historical record — each carries a final freeze entry pointing
here — and their content was deliberately not migrated into the new format.
Coder re-verified at adoption time that the directory-watch notification hook
adapts cleanly: it already tracked the `claude-to-coder/` directory listing
alongside the flat file's blob hash, so new per-message files are detected as
new directory entries and the frozen flat file simply stops producing hash
changes.

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
since this file is the live authoritative version. Then list both message
directories and read the most recent message files for open items before
assuming continuity from an earlier conversation. (The frozen v1 flat files
are historical context only.)

If you are a fresh Coder instance: you have no built-in awareness that this
mailbox exists unless told, or unless a pointer to this file has been added to
`AGENTS.md` (check `AGENTS.md` for that pointer; if absent, ask Kev or Claude).
Once oriented, read the mailbox files directly via git.
