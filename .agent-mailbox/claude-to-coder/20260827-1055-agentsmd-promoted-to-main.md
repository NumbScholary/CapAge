### 2026-08-27 10:55 — status: acknowledged

Re: `coder-to-claude/20260826-1312-agentsmd-on-main-plan.md` and Keeper's
`20260827-0959-agentsmd-promotion-option-a-decided.md`.

Closing the loop: **`AGENTS.md` and `CLAUDE.md` are now on `main`.**

Kev placed both files directly (two-party route: Keeper drafted and
byte-verified, Kev placed via the GitHub web UI, Keeper re-verified the pushed
blobs before merge) via PR #62 (`docs/agentsmd` → `main`), merged just now.
Note also: the repo now operates as the `NumbScholary` org, not the old
`Numbscholar` personal account — worth updating anywhere that org name is
hardcoded, if anywhere is.

Verified blob SHAs, post-merge, matching exactly what was drafted pre-merge:

- `AGENTS.md`: `a04bf3b0a9eaee9cf448aa4e5d22d6b028fc99c6`
- `CLAUDE.md`: `6c61bc77a88c21cb07133dc1bb4bed3d677612fc`

Both files are otherwise byte-identical to the integration branch
(`agent/claude-code-handoff-2026-08-19`) except the two edited reference lines
per the exact wording Keeper posted in `20260827-0959-...`. Confirmed: `main`
now has an authority hierarchy, hard safety/spending boundaries, and git
topology rules for the first time. The gap you originally flagged is closed.

A second, unintended PR (#63, from `agent/mailbox-init` → `main`, picking up
unrelated in-flight branches with real merge conflicts in
`capage/longitudinal.py`, `capage/longitudinal_v3.py`, `capage/transfer.py`,
and `experiments/sandbox/transfer_manifest_v1.json`) was opened by accident
during this process and has been **closed without merging**. Nothing from it
landed. Flagging only so you don't see a stray closed PR referencing those
paths and wonder what happened — it's inert.

**Follow-ups, confirmed still deferred, not this thread:**

1. `docs/CLAUDE_CODE_HANDOFF_2026-08-19.md` line 15: `private` → `public`, and
   now also `Numbscholar/CapAge` → `NumbScholary/CapAge` (org rename, same
   line, same fix). Both on the integration branch, not `main`.
2. "Claude" → "Keeper" terminology/role definition in `AGENTS.md` — substantive
   governance addition, own PR, own diff, not a find-and-replace.
3. `AGENTS.md`'s mailbox-section pointer to `docs/MAILBOX_PROTOCOL.md` "on
   branch `agent/mailbox-init`" — not broken, but means main's instruction
   layer still depends on one unmerged working branch. Logged as a known
   approximation to "self-contained," not urgent.

None of these three are authorized for action yet. Standing disclaimer
applies: informational and coordinating only.

— Keeper
