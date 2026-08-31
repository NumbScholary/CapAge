Status: OPEN — task assignment

# Two small cleanup tasks: naming and repo-metadata accuracy

Now that Gate B is closed and AGENTS.md/CLAUDE.md are promoted to main, Kev
wants two remaining loose ends tidied up across the documentation. Both are
plain find-and-replace / factual-accuracy work — no judgment calls, no
governance implications, standard effort is fine.

## Task 1 — "Claude" to "Keeper" naming

Early documentation (handoff docs, brainstorm recovery files, session
updates) refers to this governance/reasoning role as "Claude" because that
predates the "Keeper" naming convention. Sweep the docs tree and fix
references where they mean this specific governance-partner role (constitutional
interpretation, adversarial critique, cross-session record-keeper) so they
consistently say "Keeper" instead of "Claude."

Do not touch references to "Claude Code" (that's Coder, a distinct identity)
or generic mentions of the underlying model/vendor where "Claude" is factually
correct (e.g. "claude-sonnet-5" as the frozen experiment model, or CLAUDE.md's
own file-format purpose). The distinction that matters: is this text talking
about the *role* (governance partner) or the *model/product* (Anthropic's
Claude)? Only the former gets renamed.

Likely locations: docs/CLAUDE_CODE_HANDOFF_2026-08-19.md and any other docs/
files using "Claude" where context makes clear it means the governance role
rather than the coding tool or the underlying model.

## Task 2 — Repo visibility/ownership metadata accuracy

The repo's visibility and ownership history has gone through two changes that
some older documentation doesn't reflect:

1. Started as a **private** personal repo.
2. Went public.
3. Now lives under an **organization** (Numbscholar org), public, on GitHub's
   top free tier — no Enterprise plan, none anticipated.

Known stale reference: `docs/CLAUDE_CODE_HANDOFF_2026-08-19.md` line ~15
explicitly says "(private)" describing the repo. Sweep for any other stale
"(private)" or ownership claims and correct them to reflect current reality:
public repository, under the Numbscholar organization, standard free tier.

## Scope and approach

- Read-only investigation first: grep for "Claude" (excluding "Claude Code"
  and legitimate model-identity references) and for "private" across docs/
  and any root-level .md files. Report what you find before editing, same as
  the AGENTS.md-on-main approach — propose the exact diff, don't just push it,
  since these are documentation files with some historical/evidentiary value
  (the handoff doc in particular records real audit facts alongside the stale
  "Claude"/"private" language).
- Historical documents that are explicitly preserved evidentiary records
  (e.g. anything under experiments/sandbox/ describing frozen runs) should
  probably be left alone even if they say "Claude" or "private" — those are
  snapshots of what was true/said at the time, not living documentation. Use
  judgment on this distinction and flag anything ambiguous rather than
  guessing.
- No spend, no provider calls, no paid workflows — this is pure documentation
  editing per the usual AGENTS.md boundaries.

Report back with the proposed file list and diffs (or a PR) before merging
anything to main.
