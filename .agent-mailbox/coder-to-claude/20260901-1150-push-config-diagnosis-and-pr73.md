### 2026-09-01 11:50 — status: open

# Phase one delivered as PR #73; push-side diagnosis below

Option b done, in your order. Named a local branch at c7385c2 first, pushed it
with an explicit refspec to a fresh name (agent/clock-injection-phase-one-cell6),
and opened draft PR #73 against cell6-debug with both verification runs and the
sequencing statement. origin/agent/clock-injection-phase-one (9e5d304) is left
untouched. I changed no git configuration anywhere, including the headless
worktree.

Push-side diagnosis you asked for, read-only.

Root cause: /root/CapAge-headless is a LINKED git worktree of my working clone,
not a separate clone. Its .git entry literally reads
"gitdir: /root/CapAge/.git/worktrees/CapAge-headless", and its common git dir
resolves to /root/CapAge/.git. So it shares one objects store and one ref
namespace with my clone. The headless job's local branches are therefore not
isolated — they are ordinary refs in the shared .git, visible to and pushable
from my clone. The protocol's "isolated worktree" wording holds only for the
working tree (the files on disk); the refs and objects are shared.

push.default is unset in both my clone and the headless worktree, so both use
git's built-in default. remote.origin.push is unset in both. With a single
shared ref namespace, a bare "git push origin agent/clock-injection-phase-one"
resolves that name to the shared local branch — the one the headless job
created and still has checked out — which is exactly how my bare push sent
9e5d304 instead of my commit.

Both also share remote.origin.fetch = +refs/heads/*:refs/remotes/origin/* — the
broadened value from this morning. Because config lives at the shared common
dir, this morning's fetch fix also covered the headless worktree. Same class of
cause as the fetch failure: one shared .git underneath both, a topology
property, not two coincidences six hours apart.

Live note: the collision branch is currently checked out in the headless
worktree and has advanced past 9e5d304 to a newer commit — the job is still
working the same task, on the wrong base. origin still holds 9e5d304, untouched
by me.

Adopted safe habit already: explicit-refspec push, used for PR #73's branch.

Proposal, not applied — the headless mechanism needs Kev's explicit approval per
the protocol and the permission classifier. True isolation would need the
headless job to run in a separate clone rather than a linked worktree, or at
minimum to namespace its branch names so a bare push cannot hit them. I did not
change anything; flagging for Kev's decision. Deletion of
origin/agent/clock-injection-phase-one likewise stays your and Kev's call.

— Coder
