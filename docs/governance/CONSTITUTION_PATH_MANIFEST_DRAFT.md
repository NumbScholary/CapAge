# Constitution-path manifest (option b) — DRAFT for Kev + Keeper review

**Status: draft only, 2026-08-31. The JSON below is proposed content, not an
active file.** It is held in a fenced block so nothing consumes it yet. Kev
decides whether to adopt option b and where the file lives; the merge-author
canary (a later, separately-authorized task) would read it. Implements the
option-b suggestion Keeper recommended in `claude-to-coder/20260829-0947`.

## Why option b (a pointer file), restated

A canary that hard-codes the constitution path silently stops watching the
moment a new authoritative document lands elsewhere — e.g. when the Capagia v3
(Cl. 104) epoch document supersedes the current v0.1 PDF. A manifest that
*names* the current authoritative path(s) lets the document move without
editing the canary workflow: only this data file changes, in a Kev-approved
commit, and the canary keeps watching the right thing.

## Proposed file: `governance/constitution_paths.json`

```json
{
  "schema_version": "capage-constitution-path-manifest-v1",
  "description": "Names the current authoritative CapAge Constitution document path(s). The merge-author canary reads this instead of hard-coding a path, so the canary survives the authoritative document moving (e.g. the Capagia v3 epoch) without editing the workflow itself.",
  "authoritative_paths": [
    "docs/constitution/CapAge Constitution v0.1_ Foundational Governance Architecture for an Autonomous Economic Agent.pdf"
  ],
  "authenticating_identity": "Numbscholar",
  "last_reviewed": "2026-08-31",
  "notes": [
    "When the Capagia v3 (Cl. 104) document lands, add or replace the path here in a Kev-approved commit.",
    "Every path listed here MUST also appear in .github/CODEOWNERS block (1); CODEOWNERS matches statically and cannot read this file. Update both in lockstep.",
    "This manifest, .github/CODEOWNERS, and .github/workflows/ are all Kev-owned in CODEOWNERS so the gate cannot be edited out from under governance.",
    "authenticating_identity is the account whose merge to main authenticates a governance change (Cl. 102). Today that is Numbscholar; after identity separation it stays Kev's account, now distinguishable from Coder's machine-user."
  ]
}
```

## How the (future, separate) canary would use it

Sketch only — not part of this draft, and gated behind identity separation per
`claude-to-coder/20260829-0947`. For reference so the manifest shape makes
sense:

1. Trigger `on: push` to `main` (the actual merge commit landing).
2. Read `authoritative_paths` from this manifest at the merged commit.
3. Diff the merge commit against its first parent; if any listed path appears,
   this merge touched governance text.
4. Pull the merge author/committer from the **GitHub API** (not local git
   metadata) and compare to `authenticating_identity`.
5. If they differ, fail loudly and write a durable, append-only flag record
   (mirroring the Cl. 83/85 pattern), rather than passing silently.

Under the current "barbarians" threat model
(`coder-to-claude/20260829-1815`), step 4 catches any identity other than
`Numbscholar`. Once Coder has a separate machine-user, the same check also
distinguishes Coder from Kev for free — the reason identity separation is
sequenced first.

## Open decision for Kev

- **Adopt option b at all?** (vs. option a: the canary watches a hard-coded
  *set* of candidate paths, updated deliberately.) Keeper recommends b.
- **File location:** `governance/constitution_paths.json` (proposed) vs.
  `.github/constitution_paths.json` vs. elsewhere. Wherever it lands, CODEOWNERS
  block (2) and the canary's read path must match it.

## What this does NOT do

No file at `governance/constitution_paths.json` is created by this draft, and no
canary reads anything. Review material only. See
`IDENTITY_SEPARATION_RUNBOOK_DRAFT.md` and `CODEOWNERS_DRAFT.md` for the two
files this manifest is coupled to.
