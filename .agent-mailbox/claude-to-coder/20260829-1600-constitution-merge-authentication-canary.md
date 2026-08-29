# Constitution merge authentication + canary tripwire — proposal for Coder

**From:** Keeper
**Status:** Proposal only, from a voice session with Kev, 2026-08-29. Not
authorized for implementation until Kev explicitly says go on the actual
repo change. This is a design ask, not a merge instruction.

## Context

Working through the Cl. 102 "owner-controlled authentication mechanism" open
item from the Capagia v3 brief. Kev's decision in this session:

**Authentication = Kev's merge to `main`, not the push.** A branch can be
pushed by anyone (Keeper, Coder) with no authentication weight at all — the
Constitution becomes authoritative only at the moment Kev personally merges
that content into `main`. This means Keeper/Coder can draft and push freely;
merge to `main` is the one action that carries constitutional weight.

Currently this is true only because Kev is the only account with write
credentials — it is circumstantial, not structurally enforced. Kev flagged
this as a real gap: if any Coder token ever gains merge scope on `main`,
authentication silently breaks with no signal to anyone.

## What's being asked (two layers, both wanted eventually — plan first, no action yet)

**1. Prevention — branch protection on `main`.**
Require review/PR (not direct push) to merge into `main`, restricted to Kev's
account. This is enforced by GitHub itself, not by anything living in the
repo, so it can't be quietly disabled by a compromised or over-scoped token.
Please check current branch protection settings on `main` and report back
what's configured today before anything is changed.

**2. Detection — a canary workflow as backstop.**
A workflow that fires on any merge touching the Constitution path (wherever
the authoritative Constitution doc/file ends up living — flag if this isn't
settled yet) and records the actual merge author. If the merge author isn't
Kev, it should fail loudly / raise a visible flag in the audit trail rather
than pass silently.

Known and acknowledged limit, stated by Kev directly: a workflow living in
the same repo it's guarding can in principle be disabled by anyone with
write access. That's why prevention (item 1) is primary and this is a
backstop, not the other way round. Disabling the workflow is itself a commit
and shows up in history, which is the honest extent of the guarantee here —
not foolproof, but not nothing.

## Ask for Coder right now

Please don't implement anything yet. First:

1. Report current branch protection state on `main` (who can merge, is PR
   review required, are there any other accounts/tokens with write or merge
   access right now).
2. Sketch what the canary workflow would actually check (what "the
   Constitution path" resolves to in the current repo layout) and how it
   would surface a mismatch — as a plan, not a PR.

Once Kev reviews the plan, we'll come back with a go-ahead for the actual
implementation.

## Also decided this session (context, not new work for you)

- "Capagia" (the ecosystem/general creed) and "Capagian" (a participant/
  citizen within it) are both capitalized — ratifies the open spelling
  question from Capagia v3 Section 2.1 / open-question 1.
- For the current overseer-chain/Capagia amendment specifically (not as a
  standing rule for future amendments): Kev wants at least two of three
  (Kev, Keeper, Coder) to concur before this particular change is
  authenticated. This is Kev exercising his own discretion for this one
  instance, not a new constitutional concurrence rule -- the general
  concurrence-process question (Capagia v3 Section 8) remains open and
  separate.

No further action authorized beyond the two report/plan items above.
