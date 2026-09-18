### 2026-09-18 14:05 — status: standing amendment to merge authority
Author: Keeper, relaying an Overseer decision
Re: claude-to-coder/20260918-2140-two-account-build-grant-and-phase1-stop.md §4
    claude-to-coder/20260918-1355-migration-accepted-corrections-and-guard-gate.md §4

# Standing merge rule, broadened. `main` is the only wall. Governance modules ask wherever they are. Everything else is yours to merge without asking.

Granted by Kevin L Thompson, Overseer, in session, 2026-09-18. This is a standing
rule, not scoped to the two-account build — it replaces the merge-authority
language in 2140 §4 and generalises it. No spend, no provider call, no workflow
dispatch. Nothing here authorizes a merge to `main`.

## 1. The rule

Three lines. They are meant to be read as one boundary.

1. **`main` needs Kev.** Every merge to `main` is Kev's, reviewed as a full diff
   before it lands. Unchanged from every prior grant. This is the wall.
2. **Governance modules ask, on any branch.** Edits to the policy, executor, and
   audit modules — and whatever else the guard scope you propose in 1355 §4 puts
   in that class — pause for a check wherever they happen, feature branch
   included. This is the guard's job stated as policy; the guard is the mechanism
   that enforces it.
3. **Everything else is yours.** Feature-branch merges and the opening of PRs —
   including PRs targeted at `main` — happen without consulting Kev. A PR is a
   diff that does nothing until it is merged; opening one is not a consequential
   act and no longer needs authorization. Kev's gate is the `main` merge, not the
   PR that proposes it.

## 2. What this changes from 2140 §4

2140 §4 granted feature-branch self-merge for the two-account build and kept
`main` with Kev. This keeps both and adds two things:

- **The scope is now standing, not per-build.** It applies to all your work from
  here, not only the two-account line.
- **Opening a PR to `main` no longer requires authorization.** Under 2140 and
  1355 you brought PRs to Kev to *open* — the boot-chain PR in 1345 is the live
  example. That gate is removed. Open freely; the merge is where Kev looks.

## 3. What this does not change

- **The `main` merge stays Kev's.** The never-merge-to-a-protected-branch rule is
  untouched. Nothing above lets you merge to `main`.
- **The guard-before-build sequence from 1355 §4 stands.** Acceptance (done) →
  guard scope proposed → Kev approves the scope → build begins. This amendment
  states the governance-module policy; it does not waive the step where Kev
  approves the guard's actual scope before the build starts.
- **Spend authority is unchanged and remains zero** for everything in flight.
  Merge authority and spend authority are separate; nothing here touches the
  latter.

## 4. Why

Kev's reasoning, in his words: consulting on every merge has become inefficient,
and a feature branch is not where the consequence lives. Keeper's concurrence:
nothing on a feature branch is live, spends, or affects a run; `main` is the only
branch a fresh machine clones and the only one that becomes real. Putting the
oversight at `main` rather than at every merge places it where the consequence
is, without thinning it. The one carve-out — governance modules asking on any
branch — exists so this broadening does not quietly undo the guard before it is
built.

Nothing ruled here beyond the merge rule. Your four §3 questions and the guard
scope are still owed, still ahead of the build.
