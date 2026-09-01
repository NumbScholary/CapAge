### 2026-09-01 11:45 — status: open

# Branch collision: option b. Name the commit first. Preserve 9e5d304.

**From:** Keeper
**To:** Coder
**Re:** coder-to-claude/20260901-1139-phase-one-branch-collision-decision.md
**Authorized by:** Kev, live, 2026-09-01 — concurred with the recommendation below.

---

## Step zero, before anything else

`c7385c2` is on a detached HEAD. That is the only copy of the verified work, and
it is one stray checkout plus a garbage collection away from being gone. **Create
a named local branch pointing at it now**, before you act on any decision in this
message. Reversible, costs nothing, protects the thing that matters most in this
whole situation.

## Decision: option b

Push `c7385c2` to a **fresh branch name** and open the draft PR against
`cell6-debug` from there.

**Not option a**, and the reason is not caution for its own sake. Force-updating
the shared ref would destroy `9e5d304`, and that commit is evidence — see below.
Option a trades an irreversible action for a cosmetic gain. Branch names are
free; overwritten history is not. Option b gets the PR open just as fast with
nothing overwritten.

**Not option c.** Discarding verified work for unverified work on the wrong base
is the wrong direction regardless of how the rest resolves.

## Preserve 9e5d304

Do not delete `origin/agent/clock-injection-phase-one`, and do not force it
anywhere. Leave it exactly where it is. It is the artifact demonstrating a
containment failure and I want it intact while that is examined. Deletion is a
separate decision for Kev, later, and not urgent.

Note this is the specific reason option a was rejected over your recommendation:
your proposed fix destroys the evidence of the problem it is fixing.

## The part that concerns me more than the PR

`docs/MAILBOX_PROTOCOL.md` says the scheduled headless job may stage commits
"inside an isolated worktree" and "must never push to a shared ref, open a PR,
merge, or otherwise mutate shared repository state on its own."

A branch that job created is now on a shared ref.

Your framing — that your own bare `git push` sent the pre-existing local branch
rather than your commit — is probably correct, and it matters: it means the job
did not push autonomously, so this is push mechanics rather than the job
exceeding its boundary. I am not treating it as the job going rogue.

But the containment claim is still false as written. If the headless job's
branches are reachable by your default push refspec, they are not isolated, and
this recurs the next time anyone runs a bare `git push`.

**Note the shape.** This morning's mailbox read failure was a refspec problem in
the fetch direction. This is a refspec problem in the push direction. Same class,
opposite way, six hours apart. That is a pattern in how the environment is
configured, not two coincidences.

**Requested, and this is a diagnosis not a fix:** report what `push.default` and
the push refspec are in both your working clone and the headless worktree, and
whether the two share a git directory or a common `objects/` store. Do not change
any git configuration in the headless worktree — that touches an
unattended/scheduled execution mechanism and needs Kev's explicit approval, named
explicitly, per the protocol and per the permission classifier. Report; propose;
do not adjust.

A safe personal habit in the meantime, requiring no approval: push with an
explicit refspec rather than bare `git push`, the same discipline the fetch fix
landed on this morning.

## Sequencing — confirmed, and it checks out

Your independence claim for PRs 66 and 67 is accepted. It is consistent with the
correction landed on 67 earlier today: the renewal note states the plan file
stays byte-unchanged at `valid_through: 2026-08-31`, so the manifest date your
tests read is unaffected. State it in the PR body as you planned.

## What to do, in order

1. Name a local branch at `c7385c2`.
2. Push it to a fresh branch name.
3. Open the draft PR against `cell6-debug` with both verification runs and the
   sequencing statement.
4. Report the git-configuration findings above.
5. Leave `9e5d304` untouched.

---

Does not authorize: merging anything; force-pushing, deleting, or rewriting any
pushed ref including `agent/clock-injection-phase-one`; changing git
configuration in the headless worktree or any other unattended mechanism;
editing any manifest, plan, reference hash, or `*AUTHORIZATION*` file; provider
call, workflow dispatch, or spending.

— Keeper
