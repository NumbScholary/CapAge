### 2026-08-24 07:10 — status: open

Reviewed the launch-script build and the merge-commit-beacon blocker.
Agreed: fabricating a seed now instead of using a real merge commit
would defeat the tamper-evident point of the beacon pattern. Not
optional to skip.

Go ahead and open a PR for the preregistration document
(experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md)
into the active integration branch (agent/claude-code-handoff-2026-08-19),
mirroring how V2's preregistration had its own separate PR. This is
documentation only -- no paid-run authorization implied or requested.
Owner (Kev) already approved the preregistration content itself this
session; this PR just gets it onto the branch that can produce a real
merge-commit beacon.

Once that PR is open, flag it back here with the PR number so it can
get reviewed and merged promptly -- the frozen tariff this experiment's
cost assumptions depend on expires 2026-08-31, so there isn't much slack
in the merge-then-materialize chain. If it looks like the window will
be missed, say so directly rather than proceeding on stale assumptions.

Launch script itself (capage/hosting_liability_replication_launch.py)
sounds correctly built and correctly inert -- no action needed there
beyond normal review once the beacon exists and materialization can
actually run in --validate-only.
