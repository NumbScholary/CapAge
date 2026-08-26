### 2026-08-26 (timestamp estimated, local clock tool unavailable) — status: open

Re: the artifact-name-from-manifest question flagged in
`20260826-1200-pr3-workflow-reviewed.md` and re-raised in
`20260826-0530-run-record-decision-option1.md`.

Kev's decision: **option 2 — read it from the manifest.** Match the design
doc's invariant table (row 12: "artifact name from manifest") rather than
keeping the PR-3 YAML's hardcoded `scoped-paid-action-restricted` / 30-day
values. Reasoning, plainly: the doc specified it that way for a reason, and
there's no strong argument to diverge from it for this first instantiation.

Please add a small step in PR-3's resolve stage that reads `artifacts.name`
and `artifacts.retention_days` from the manifest (same file already being read
for the module/argv), and pass those into the `upload-artifact` step in place
of the current hardcoded values. Same pattern as the existing manifest reads
in the workflow — no new dependency, no shell injection surface (values go
through `GITHUB_ENV` the same way `MANIFEST`/`ACTION_ID` already do).

Not asking for anything else to change in PR-3 — the rest of the workflow
(trigger shape, run_attempt gating, concurrency, step-scoped secret,
`environment: paid-runs`) stands as reviewed and confirmed.

Standing disclaimer applies: informational and coordinating only; not owner
authorization, spending approval, or permission to merge, deploy, place a
file, or execute anything. Gate C untouched.

— Keeper