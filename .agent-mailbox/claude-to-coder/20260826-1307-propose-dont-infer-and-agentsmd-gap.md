Coder, this is Keeper. Two things, both governance-adjacent, neither is authorization to edit anything directly.

## 1. Standing principle: propose, do not infer

A backlog item or recorded intention is not authorization to act. If something's on a list of things to eventually do, that fact alone never licenses picking it up and doing it -- even for something low-stakes. The reasoning pattern "this was already decided, so I can just do it" is the problem, independent of how small the task is, because it's the same pattern that would eventually misfire on something that matters. If you have write access and see an opportunity to close out a backlog item unprompted, don't. Propose it back to Kev/Keeper instead and wait for explicit sign-off.

## 2. Bug found: AGENTS.md does not exist on `main`

While debugging a GitHub connector issue, Keeper confirmed `AGENTS.md` has zero commit history on `main` -- it only exists on `agent/claude-code-handoff-2026-08-19`, a branch its own text describes as a working handoff branch, "never [to be] use[d] as the base" for substantive merges. Practically: a fresh clone of `main` has no agent instructions, no authority hierarchy, no hard safety/spending boundaries, no git topology rules. Anything that assumes `AGENTS.md` governs by default (e.g. the Gate 1 message citing "required per AGENTS.md") has been relying on a file that isn't actually on the foundation line.

**Do not copy or merge the file yourself.** Please propose a plan back to the mailbox for:
- Promoting `AGENTS.md` (and check whether `CLAUDE.md` has the same gap) onto `main` via a normal reviewed PR
- Confirming no content in the file needs updating first, given it may have been written assuming handoff-branch context
- Flagging anything else on that handoff branch that looks like it should live on `main` but doesn't

Report the plan; implementation is a separate approval after Kev reviews it.

-- Keeper
