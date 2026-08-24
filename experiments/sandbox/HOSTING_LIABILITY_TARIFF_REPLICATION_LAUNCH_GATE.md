# Hosting Liability Tariff Dose-Response Replication launch gate

This launch layer is anchored to materialization merge
`d0d92cc5a36788dd619fb3dd14c81a0b5dd995b2` (PR #50, which itself sits on
top of PR #49's preregistration merge and PR #47's code merge, both
ancestors). It wires the already frozen, tested
`BlockedTariffReplicationRunner` and `hosting_liability_replication_launch`
module to the real sandbox factories and a one-shot GitHub Actions
workflow. It does not alter the design, the tariff levels, the 4x4 arm
ordering, the 12 matched worlds, or the preregistered dependent variables.

Runs on a dedicated protected branch,
`agent/hosting-liability-tariff-replication-launch`, frozen at the
materialization merge above and used for nothing else -- mirrors
`agent/homeostasis-v2-blocked-replication-launch`'s isolation exactly, for
the same reason: the launch workflow's safety check depends on an exact,
unambiguous git-history shape between materialization and launch (one
first-parent commit, an exact expected file set), which only holds if
nothing unrelated can land on this branch.

## No authority in this merge

Merging this launch gate does not authorize provider calls or spending.
This change deliberately omits
`experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_AUTHORIZATION.md`.
The materialized plan remains historical evidence with
`provider_calls_authorized` and `spend_authorized` set to `false`; the
later owner statement is a separate authority layer and does not rewrite
that evidence.

After this launch gate is reviewed and merged, the only accepted
authorization is a newly added, one-line file whose entire contents are:

`RUN_HOSTING_LIABILITY_TARIFF_REPLICATION_AT_<AUDITED_LAUNCH_MERGE_SHA>_MAX_2160_CENTS`

The workflow derives `<AUDITED_LAUNCH_MERGE_SHA>` from the authorization
commit's immediate parent -- this launch gate's own merge commit on the
protected branch. The phrase therefore cannot be finalized before this
launch layer is merged and audited. (An earlier authorization file was
committed against `d0d92cc5...` directly -- see PR #51 -- before this
separate gate PR existed; that phrase is now bound to the wrong commit
and needs to be superseded by one bound to this gate's actual merge SHA,
once known.)

## One-shot boundary

The workflow runs only on a push to
`agent/hosting-liability-tariff-replication-launch` that adds the fixed
authorization path. It requires all of the following before any provider
client is used:

- the authorization file is the sole change and is newly added, not
  modified;
- its bytes are exactly the merge-bound phrase plus one newline;
- the launch commit is exactly one first-parent commit after the
  materialization merge and changes only this launch gate's own files;
- `github.run_attempt` is exactly `1`;
- all tests, compilation, and `--validate-only` pass against the real,
  already-materialized plan.

If any check fails, the workflow exits non-zero before constructing a
provider client. No retries: `concurrency` with `cancel-in-progress: false`
plus the `run_attempt == 1` guard mean a failed or interrupted run is not
silently retried.

## Budget

Per-cell cap 45 cents, aggregate cap 2,160 cents (48 cells x 45 cents),
matching `experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json`'s
`maximum_budget` exactly -- confirmed owner decision (2026-08-24), mirrors
the V2 replication's own numbers since the real-provider-cost-generating
mechanism is structurally unchanged between the two experiments.
