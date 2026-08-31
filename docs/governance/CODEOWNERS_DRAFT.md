# CODEOWNERS — DRAFT for Kev + Keeper review

**Status: draft only, 2026-08-31. The content below is NOT active.** It is held
here in a fenced block on purpose: a real `CODEOWNERS` placed at `.github/`,
repo root, or `docs/` is auto-recognized by GitHub and would start
auto-requesting reviews immediately. Nothing takes effect until **Kev** copies
this to `.github/CODEOWNERS` and enables `require_code_owner_reviews: true` in
`main` branch protection (see `IDENTITY_SEPARATION_RUNBOOK_DRAFT.md`).

## Proposed `.github/CODEOWNERS`

```text
# CapAge CODEOWNERS — governance gate.
# Kev (@Numbscholar) is the required reviewer on governance-critical paths.
# Enforced only when require_code_owner_reviews: true on main branch protection.
# NOTE: replace @Numbscholar with Kev's canonical account handle if it differs.

# 1. The authoritative Constitution document(s).
#    Keep this in sync with the authoritative_paths in the constitution-path
#    manifest (see CONSTITUTION_PATH_MANIFEST_DRAFT.md) — CODEOWNERS matches
#    paths statically and cannot read the manifest.
/docs/constitution/                      @Numbscholar

# 2. The constitution-path manifest itself and its directory.
/governance/constitution_paths.json      @Numbscholar
/governance/                             @Numbscholar

# 3. CODEOWNERS itself — so the gate cannot be edited out from under governance.
/.github/CODEOWNERS                       @Numbscholar
/CODEOWNERS                               @Numbscholar

# 4. The workflow directory — so the merge-author canary (and any other guard)
#    cannot be disabled or rewritten without Kev's review.
/.github/workflows/                       @Numbscholar
```

## Why each block

- **Constitution paths** are the point of the whole Option-2 gate: governance
  text should not become authoritative on `main` without Kev's explicit,
  GitHub-enforced approval.
- **The manifest + its directory** matter because the canary reads the manifest
  to learn which paths are "the Constitution." If the manifest itself were
  editable without Kev, an attacker could point the canary away from the real
  document. So the manifest is Kev-owned too.
- **CODEOWNERS covering itself** closes the obvious bypass: without it, someone
  with write access could delete or edit CODEOWNERS to remove the gate.
- **The workflow directory** closes the same bypass for the canary/gate
  workflows — Kev's stated known-limit (a workflow in the repo it guards can be
  disabled by write access); owning the directory means such a change needs
  Kev's review.

## Interaction with the constitution-path manifest (Keeper flagged this)

CODEOWNERS **cannot read the manifest** — it only matches literal path
patterns. So every path the manifest names as authoritative must **also** be
listed here, and the two must be updated in lockstep. Both files are Kev-owned,
so both changes require Kev — which is the intended coupling, but it is manual:
when the Capagia v3 document lands at a new path, Kev updates *both* the
manifest's `authoritative_paths` and block (1) of this file in the same
Kev-approved change.

## Self-approval deadlock — do not ignore

If Kev is the **sole** code owner of the constitution path **and** the author
of governance PRs, `require_code_owner_reviews: true` + `enforce_admins: true`
deadlocks him: GitHub forbids approving your own PR and admin override is off.
See the runbook's lock-out flag #1 for the three resolution options. The
CODEOWNERS content above is written assuming the resolution is "Coder/Keeper
author, Kev approves" (option a) or a second code owner is added (option b);
if instead the constitution path relies on canary detection (option c), drop
block (1) here and keep blocks (2)–(4).

## What this does NOT do

Placing this draft under `docs/governance/` does **not** activate any code-owner
review. It is review material only.
