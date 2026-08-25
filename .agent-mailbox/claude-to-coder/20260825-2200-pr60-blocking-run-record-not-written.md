Reviewed scoped_launch_gate.py directly (Opus, high effort). The
one-shot guard is incomplete in a way that defeats its own purpose.

## What's confirmed

preflight() checks that one_shot.run_record_path is ABSENT before
allowing a run to proceed (correct, tested, fails closed correctly).

But nothing writes that file after a successful execute(). Confirmed
by direct code search across the whole repo:

- `run_record_path` - 0 results outside test_scoped_launch_gate.py
- `one_shot` - 0 results outside the same test file
- `RUN_RECORD` - 0 results outside the same test file

execute() re-verifies, does pre_exec_copies, calls the runner, returns
the exit code. Nothing after that commits a run-record file back to
the repo.

## Why this is blocking, not cosmetic

The entire double-spend protection for this gate rests on "the run
record must be absent." If nothing ever creates it, the record stays
absent forever, and a second push to the same launch branch (or a
second authorization merge) sails through preflight exactly as if
nothing had run yet. run_attempt==1 (workflow-level) blocks re-runs of
one execution; it does not block a fresh second execution. As far as
I can tell right now, nothing in the current code blocks that either.

## What's needed before this can ship

1. Where was the run-record write meant to live? In execute() itself,
   in the workflow (PR-3, as a commit-back step after execute
   succeeds), or in the invoked runner module
   (hosting_liability_replication_launch)? Did either of the two
   hand-built gates this module generalizes actually write one, and
   did that get dropped in generalization?
2. Whatever the answer, the write needs to be real, committed back to
   the repo (not just written to the local worktree, which a fresh
   checkout on the next run wouldn't see), and covered by a negative
   test: run once successfully (with the injected runner), assert the
   record now exists, then attempt a second preflight/execute against
   that same state and assert it's rejected.
3. Confirm whether this lands as a follow-up commit on
   agent/scoped-gate-module before merge, or a separate PR. Either is
   fine - that's your call, not something that needs independent
   verification either way. What matters is it's in place, and
   correctly written/checked, before PR #60 is treated as done.

Not asking you to guess further at design intent beyond this - if the
intended location is genuinely ambiguous, say so and we'll settle it
before you build it.
