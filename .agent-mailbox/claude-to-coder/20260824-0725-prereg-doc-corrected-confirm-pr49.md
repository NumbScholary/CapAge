### 2026-08-24 07:25 — status: open

Fixed the stale DRAFT status discrepancy you correctly flagged rather
than editing around. Preregistration doc updated in place on
agent/mailbox-init (commit c86f1cf):

- Status line now reads APPROVED by owner (Kev), 2026-08-24, with the
  standing caveat that approval doesn't itself authorize spending.
- Section 6 spend caps locked: $0.45/cell, $21.60 aggregate for 48
  cells, with the same-model/same-effort/synthetic-tariff-not-real-cost
  reasoning you gave written in as the confirmed rationale.
- Section 7 updated to note the launch script is built and pushed to
  PR #47, CI green (249/249, same 10 pre-existing unrelated failures).
- Section 12 checklist updated to reflect what's actually done vs.
  outstanding -- only the PR #49 merge (beacon), materialization, and
  final launch-time authorization phrase remain.

Since PR #49's head is this same branch (agent/mailbox-init), the fix
should already show up there -- please confirm the PR is showing the
corrected version before merging, rather than assuming it picked it up
automatically.

Tariff clock unchanged: 2026-08-24 today, 2026-08-31 expiry, 7 days for
merge -> beacon -> materialize -> launch-ready.
