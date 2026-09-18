# Identity separation runbook — DRAFT for Kev + Keeper review

**Status: draft only, 2026-08-31. This document proposes steps; it changes no
repo setting and no credential. Nothing here is authorization. Kev executes the
actual changes, in his own hands, after review.** Implements the Option 2
("Kev-gate") direction approved in `claude-to-coder/20260829-0947`.

## Problem this fixes

Coder's GitHub credential currently authenticates as `Numbscholar` — the same
account that owns the org and has `admin: true` on the repo (reported in
`coder-to-claude/20260829-1800`). Consequences:

- `enforce_admins` is `false`, so branch protection's PR-review requirement
  does not bind that admin token — Coder *technically* can push/merge to `main`
  today; only restraint stops it.
- A merge-author canary cannot distinguish Kev from Coder, because both act as
  `Numbscholar`.

Giving Coder a **separate identity** makes merge authorship real, lets
`enforce_admins: true` + CODEOWNERS bind everyone, and gives the canary a real
distinction to check. Under the current "barbarians" threat model
(`coder-to-claude/20260829-1815`) even the account-level separation already
buys the main protection — an outside token shows up as a different identity.

## Recommendation: fine-grained PAT machine-user now, GitHub App as hardening

Given how Coder actually authenticates today — a static token consumed by `gh`
/ `git` inside Termux/proot (`gh auth status` reads `~/.config/gh/hosts.yml`),
no JWT-signing capability wired up — the two options trade off like this:

| | Fine-grained PAT on a dedicated machine-user account | GitHub App (bot identity) |
|---|---|---|
| Termux plumbing | **Trivial** — swap the token in `gh`/git; static bearer token | Harder — needs a private key + JWT → installation-token exchange each run; fragile under proot |
| Identity in merges | Shows as the machine-user account (e.g. `capage-coder`) | Shows as `capage-coder[bot]` |
| Least privilege | Good (fine-grained repo scopes) | **Best** (installation-scoped, short-lived tokens) |
| Token lifetime | Static, expires on a date you set (rotation burden) | Short-lived, auto-minted (better hygiene) |
| Setup cost | Low | Higher (App registration, key storage) |

**Recommendation (mine; Kev decides):** stand up the **fine-grained PAT on a
dedicated machine-user account first** — it is the workable path in Termux
today and delivers the real account-level separation the canary and
`enforce_admins` need. Treat the **GitHub App as a follow-up hardening step**
once the separation is proven, for short-lived tokens and a clean `[bot]`
identity. Doing the App first risks a fragile token-exchange step becoming the
thing that locks Coder out.

## Step-by-step (Kev, from phone) — PAT path

Order matters; the lock-out flags below are the reason for this exact order.

1. **Create the machine-user account** (e.g. `capage-coder`), separate from
   `Numbscholar`. Enable 2FA. Use an email you control.
2. **Invite it as a repository collaborator** on `NumbScholary/CapAge` with the
   **Write** role — *not* Admin. Accept the invite from the machine-user
   account. (Write can push branches and open PRs; it cannot merge to a
   protected `main` or change settings.)
3. **Create a fine-grained PAT** owned by `capage-coder`, scoped to
   `NumbScholary/CapAge` only, with the **minimum** permissions:
   - Contents: Read and write (push branches)
   - Pull requests: Read and write (open/update PRs)
   - Metadata: Read (required)
   - **Not** Administration, **not** Workflows write unless a later task needs
     it, **not** anything on other repos. Set an explicit expiry and a calendar
     reminder to rotate.
4. **Verify Kev keeps merge power before locking admins out.** In `main` branch
   protection, if you enable push restrictions, put `Numbscholar` explicitly on
   the allowlist *first*. Confirm Kev can still merge a test PR.
5. **Turn on the gate** (branch protection on `main`):
   - `enforce_admins: true`
   - `required_pull_request_reviews.required_approving_review_count: 1`
   - `require_code_owner_reviews: true`
   - push/merge restricted to `Numbscholar`
6. **Place CODEOWNERS** (from `CODEOWNERS_DRAFT.md`) at `.github/CODEOWNERS`.
7. **Swap Coder's environment credential** last: in Termux, replace the stored
   `Numbscholar` token with `capage-coder`'s PAT (`gh auth logout` then
   `gh auth login` with the PAT, or update the git credential store). Verify
   with `gh api user` that Coder now authenticates as `capage-coder`, then push
   a throwaway branch to confirm write works and a direct push to `main` is
   refused.

## Lock-out risks in the order of operations (Keeper asked to flag these)

1. **Self-approval deadlock on governance PRs (most important).** With
   `require_code_owner_reviews: true` and Kev as the sole code owner of the
   constitution path, a PR **authored by Kev** touching that path cannot be
   approved by Kev (GitHub forbids approving your own PR), and with
   `enforce_admins: true` he cannot override it either. Since the model is
   "Kev places governance changes," Kev would routinely be the author — and
   would deadlock. **Options to resolve before enabling:** (a) governance
   changes are authored by Coder/Keeper and *approved* by Kev (Kev is reviewer,
   not author); or (b) add a second trusted code owner for the constitution
   path; or (c) for the constitution path specifically, rely on the
   **canary-detection** layer rather than hard CODEOWNERS enforcement, keeping
   CODEOWNERS enforcement for the workflow/manifest paths. This choice is Kev's;
   flagging that (a) fits the existing "Coder drafts/pushes, Kev merges" split
   most naturally, but "Kev approves, someone else authors" inverts today's
   authorship.
2. **Push-restriction self-lockout.** Enabling push/merge restrictions without
   `Numbscholar` on the allowlist locks Kev out of merging. Step 4 guards this.
3. **Credential swap too early.** Swapping Coder to the new PAT (step 7) before
   the machine-user has accepted collaborator access (step 2) leaves Coder with
   no write access mid-migration. Keep the swap last, and keep Kev's old token
   available as a fallback until the new identity is confirmed working.
4. **PAT expiry.** A fine-grained PAT expires on its set date; if it lapses
   unnoticed, Coder silently loses access until Kev regenerates it. Set the
   expiry deliberately and a reminder ahead of it.
5. **Workflows-permission gap.** If Coder ever needs to add/update workflow
   files, the fine-grained PAT needs Workflows: write; without it, pushes that
   touch `.github/workflows/` are rejected. Add that scope only when a task
   requires it (e.g. the canary build), not pre-emptively.

## What this does NOT do

No account is created, no token is issued, no setting is flipped, and Coder's
credential is unchanged by this document. It is a plan for Kev to execute and
for Keeper to review. See `CODEOWNERS_DRAFT.md` and
`CONSTITUTION_PATH_MANIFEST_DRAFT.md` for the two files this runbook references.
