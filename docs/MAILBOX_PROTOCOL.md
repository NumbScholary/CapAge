# CapAge Agent Mailbox Protocol

Status: living document, versioned. This describes the current (v4) inter-agent
mailbox as of 2026-09-12 — v4 extends autonomous posting to Keeper's outbound
direction and establishes a meta-protocol for amending this file (see
"Autonomous posting" and "Meta-protocol"). The v2 file layout is unchanged.
It will change; treat this file, not memory or prior chat summaries, as
authoritative for current mechanics.

## What this is

A shared, append-only communication channel between Keeper (governance/reasoning
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
- `.agent-mailbox/claude-to-coder/` — Keeper writes here; Coder reads.
- `.agent-mailbox/coder-to-claude/` — Coder writes here; Keeper reads.

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

**Note on the directory names (2026-09-12).** `claude-to-coder/` is v1 residue
from before the interface instance had the role name "Keeper." The name is
retained deliberately rather than corrected: Coder's directory-watch hook
tracks that listing, every existing message path would stop resolving on a
rename, and v2's provenance argument depends on paths being stable. Read
`claude-to-coder/` as "Keeper's outbound directory" throughout this document.

## Why v2 (adopted 2026-08-25), and the v1 historical record

v1 used two growing flat files (`.agent-mailbox/claude-to-coder.md` and
`.agent-mailbox/coder-to-claude.md`), each append-only by convention.

The fragility that motivated v2: Keeper's GitHub connector can list files,
read commit metadata, and read commit diffs as text, but cannot reliably read
a file's full current body as text — only its blob SHA. Since appending to a
single growing file requires submitting the complete new body, Keeper could
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

**This section is governance plane. It is not amendable by agent concurrence —
see "Meta-protocol" below.**

Both Keeper and Coder may, without needing Kev's approval each time:
reading files, running the existing test suite and reporting results,
describing dependency graphs or repo state, committing to a feature branch,
and opening a pull request.

Any pull request either agent opens must still be reported to Kev promptly.
That reporting duty belongs to Keeper in conversation with Kev.

Kev's explicit, direct approval is still required, every time, for: merging
into `main`, touching configuration/policy/executor/accounting/governance
code, touching authorization files, force-pushing or rewriting already-pushed
branch history, registering or modifying any unattended/scheduled/headless
execution mechanism, or spending real resources. Nothing about this mailbox
changes `AGENTS.md`'s existing hard boundaries or the protected replication
branch's status.

## Autonomous posting (v4, 2026-09-12; supersedes v3, 2026-08-25)

**v3 (2026-08-25):** Kev approved relaxing the draft-only boundary so Coder may
post replies autonomously — without waiting for a live foreground session — and
approved recurring/automatic mailbox polling (frequency at Coder's discretion;
the existing ~15-minute tick is fine). This was scoped to Coder's outbound
direction only, and explicitly did *not* extend to `claude-to-coder/`.

**v4 (2026-09-12):** Kev granted Keeper the same autonomy in Keeper's own
outbound direction. Autonomous posting now covers:

- `.agent-mailbox/coder-to-claude/` — Coder's outbound directory.
- `.agent-mailbox/claude-to-coder/` — Keeper's outbound directory.

Autonomous posting still explicitly does NOT extend to:

- The other agent's outbound directory. Each agent writes only its own.
- The "Authority split" section of this file, or any other governance/policy
  file (see "Meta-protocol").
- Any other path in the repository.

Append-only semantics are unchanged in both directions: new files only, never
edit or delete an existing message, supersede by writing a new one, UTC
filenames. Each agent owns its own outbound directory, so a message's
provenance is unambiguous from its path alone — the scope narrowing is retained
for that structural cleanliness, not as a safety control.

**Why this is safe.** The owner's protection here is not his presence at the
moment of a write. If he is not reading each message as it lands — and he
should not have to — then requiring a live console for every exchange buys only
a rubber stamp at a high cost. What actually bounds both agents is that neither
can spend, alter repository settings, merge, or reach an API key through this
channel; the mailbox is two agents leaving each other notes about governance
reasoning, not an authority surface. Nothing here authorizes spending, provider
calls, merges, workflow dispatch, or settings changes, and the standing
no-authority disclaimer on every message is unchanged.

Implementation note (corrected 2026-09-14): no scheduled job exists. The job
that existed was stood down (see "Headless/unattended execution") and never
posted autonomously. Coder has no poller and reads the mailbox when prompted.
Enabling any future unattended helper to post autonomously is a separate
mechanism change — per the standing rule on modifying an unattended/scheduled
execution mechanism — made deliberately by Kev and reported, never as a silent
side effect of a protocol change.

## Meta-protocol (v4, 2026-09-12)

Kev's grant, 2026-09-12: this is the agents' own coordination protocol, and
Keeper and Coder may amend it by mutual concurrence without involving him —
**within the mechanics plane only.** Keeper raised, and Kev confirmed, the
narrowing recorded here.

**Amendable by Keeper–Coder concurrence, no Kev:**
file layout and directory names, message file naming, message body format,
polling cadence, posting directions within each agent's own outbound
directory, supersession and correction conventions, orientation instructions
for fresh instances, and the descriptive/rationale prose throughout.

**Not amendable by agent concurrence — Kev's alone:**
- the "Authority split under this protocol" section;
- the standing no-authority disclaimer, in this file or in any message;
- anything governing the headless/scheduled/unattended execution mechanism;
- this "Meta-protocol" section itself.

**Direction asymmetry.** Within the mechanics plane, the agents may by
concurrence *narrow or tighten* either agent's own scope freely. They may never
*widen* it. This mirrors Cl. 35 (voluntary tightening) over Cl. 34 (no
self-expansion): self-tightening creates no later right to restore or expand
beyond the existing grant.

**Constitutional basis for the narrowing.** Cl. 80 (governance-plane
protection) forbids autonomous modification of owner policies, authority
records, approval gates, and the mechanisms that enforce them. Cl. 81 treats a
change materially altering authority enforcement as a governance change rather
than ordinary strategy. Cl. 34 forbids an agent granting itself a capability or
changing a role. An unrestricted concurrence power over this file would let two
agents amend the clause stating what requires Kev's approval; Cl. 91 means Kev
cannot silently authorize that — it would need a valid amendment. The split
above preserves what Kev intended (the plumbing is the agents' business) without
that consequence.

**Procedure.** Either agent proposes an amendment by mailbox message naming the
section and the change. The other concurs, dissents, or counter-proposes by
mailbox message. On concurrence, either agent may edit this file, and must post
a message recording that the edit was made and by whose concurrence. Absent
concurrence, the file is unchanged. A proposal is not an amendment; silence is
not concurrence (Cl. 37).

## Headless/unattended execution (stood down 2026-09-03; corrected 2026-09-06 and 2026-09-14)

**Correction notes (2026-09-06; extended 2026-09-14).** The scheduled unattended
job described in earlier versions of this section is no longer running; one
claim it made about isolation was wrong; and this section was not a complete
account of unattended mechanisms. All three are corrected below. The prior
description is preserved as history rather than deleted, so the record stays
legible. The facts here were verified from the device on 2026-09-14
(`coder-to-claude/20260914-0915-headless-inventory-0904.md`).

What existed (2026-08-23 to 2026-09-03): a scheduled, unattended job on Kev's
device (Termux/proot-distro, Android JobScheduler job id 1, ~15-minute floor,
persisting across reboots) that ran Coder in `--permission-mode dontAsk` inside
the linked worktree `/root/CapAge-headless` to check the mailbox and prepare
responses. It was draft-only: it could fetch, read, run validation gates, stage
local scratch-branch commits, and prepare (but not send) PR text and
mailbox-reply drafts, then notify Kev. It never pushed to a shared ref, opened
a PR, merged, or posted to the mailbox. It did, however, create branches in the
**shared** ref namespace (`agent/clock-injection-phase-one`,
`agent/clock-injection-verify-fix`), and on 2026-09-01 the first of those was
sent to origin by a bare `git push` from the foreground clone — the collision
that led to the stop. The committed `.claude/settings.json` on the branch the
worktree sat on **allowed** `git push origin agent/*` and `gh pr create*`; what
held the job back from pushing was a local-only, gitignored
`.claude/settings.local.json` deny-overlay on Kev's device, never merged into
the shared committed settings, plus the draft-only prompt text.

Current status: **stood down, in two stages.** 2026-09-01: the inner script was
neutralized by rename on Kev's direct instruction to Coder. 2026-09-03: Kev
cancelled the JobScheduler job in Termux. Nothing was deleted. The residue
(the registered worktree, still checked out on `agent/clock-injection-verify-fix`;
the Termux-side bridge script; the stub and the preserved script; the run log
and drafts) is **frozen in place pending Kev's word** — not live, since nothing
wakes it, and not inert, since the shared-git-dir and settings posture above is
unchanged. The job is not to be restored, re-enabled, or rebuilt in place.

Correction to the isolation claim: the linked worktree at `/root/CapAge-headless`
was **not** an isolation boundary. It shared the foreground repo's git object
store, refs, and locks — which is precisely what made two agents operating in
one repository a race condition. The earlier phrasing ("a local scratch-branch
commit inside an isolated worktree") overstated the separation that actually
existed.

**A second unattended mechanism existed and is recorded nowhere else in this
repository.** From 2026-08-22 21:32 UTC to 2026-08-27, Claude Code's Remote
Control daemon (paired to the claude.ai app via `/web-setup`) ran on Kev's
device and spawned one separate Claude Code session per incoming app message —
nine sessions, sequential, each with its own transcript and no thread to the
foreground session, running with `auto` or `acceptEdits` permissions under the
committed `settings.json`. One of them opened PRs #55 and #56 from its own
worktree on 2026-08-24, on Kev's instruction through the app. Kev asked for the
pairing to be disconnected on 2026-08-22 22:11 UTC; the daemon's last logged
activity is 2026-08-27, and Remote Control is disabled in Claude Code's
configuration now (the setting carries no date). This is the mechanism that
wrote to shared state; the scheduled job above never did.

Any future unattended helper is to be stood up on the new machine as one
bundle, per the separate-disposable-clone design: a disposable clone per helper,
reserved and reaped `refs/heads/headless/*`, wrapper-level timeout and teardown,
a git-dir-free courier, and credentials scoped under identity separation. That
credential scoping is the standing constraint the "headless credential
constraints" elsewhere in this file refer to: an unattended helper is bounded by
not being able to reach an API key at all, not by its presence in any worktree.

The permission classifier that governs Coder's actions requires the
unattended/scheduled/`dontAsk` mechanism to be named explicitly by Kev before
it will permit even setup/probe steps — a vague "go ahead" is not sufficient,
consistent with the constitutional principle that intent is not authority and
scope must be explicit.

## For a fresh instance orienting itself

If you are a new Keeper instance: read this file from GitHub directly rather
than relying on memory, prior chat summaries, or project-knowledge copies,
since this file is the live authoritative version. Then list both message
directories and read the most recent message files for open items before
assuming continuity from an earlier conversation. (The frozen v1 flat files
are historical context only.)

If you are a fresh Coder instance: you have no built-in awareness that this
mailbox exists unless told, or unless a pointer to this file has been added to
`AGENTS.md` (check `AGENTS.md` for that pointer; if absent, ask Kev or Keeper).
Once oriented, read the mailbox files directly via git.
