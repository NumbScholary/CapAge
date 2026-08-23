# Economic Homeostasis V2 blocked-replication: retired

**Status: retired by owner decision, 2026-08-23. Not a finding against V2.**

This retires the full paid 48-cell blocked replication whose launch layer
is anchored to launch merge `059bc036d9ebb5103effd27e2262313078d2c5c1`
(PR #37, "Replace one-shot Homeostasis V2 blocked-replication launch
gate", merged onto the protected branch
`agent/homeostasis-v2-blocked-replication-launch`) and preregistered in
`HOMEOSTASIS_V2_REPLICATION_PREREG.md` /
`economic_homeostasis_v2_replication_prereg_v1.json`.

## Reason: resource allocation, not a negative result

Kev's stated reason: not worth the resources to complete given competing
priorities. This is explicitly not a finding against V2.

The completed diagnostic three-arm run (GitHub Actions run `32304273201`,
documented in `docs/CLAUDE_CODE_HANDOFF_2026-08-19.md`) already showed
V2's real tradeoff directly:

- V1 final capital: $442.50. V2 final capital: $407.84 -- V2 did not clear
  the capital gate.
- V2 had zero disputed deliveries versus four for V1.
- V2 ending reputation was +48.
- V2 model cost was approximately 86.5% of V1's.

Formally confirming that tradeoff at full statistical scale, via the
complete paid 48-cell replication, was assessed as not worth its
~$13-21 provider-cost estimate and review overhead right now. The
diagnostic result stands as the evidentiary record of what was learned;
this retirement does not supersede or reinterpret it.

## What is not affected

This is a new, append-only record (Constitution cl. 85: append-only
correction; cl. 103: amendments have prospective effect only and must not
retroactively alter historical accounting, permissions, or experimental
results). It does not rewrite, delete, or reinterpret any existing frozen
record:

- `HOMEOSTASIS_V2_REPLICATION_PREREG.md`,
  `economic_homeostasis_v2_replication_prereg_v1.json`, and
  `economic_homeostasis_v2_replication_plan_v1.json` remain exactly as
  preregistered and materialized.
- `HOMEOSTASIS_V2_REPLICATION_MATERIALIZATION.md` and
  `HOMEOSTASIS_V2_REPLICATION_LAUNCH_GATE.md` remain exactly as merged.
- The protected branch `agent/homeostasis-v2-blocked-replication-launch`
  and PR #37 are untouched -- not deleted, not force-pushed, not rebased.
  The branch stays as historical evidence of a considered, then declined,
  experiment.
- `PR #47` (the hosting-liability tariff dose-response experiment) is a
  separate, unrelated experiment and is unaffected by this retirement --
  it remains parked/deprioritized on its own schedule.

## Frozen tariff status: never spent

`economic_homeostasis_v2_replication_plan_v1.json`'s token tariff was
valid through `2026-08-31`. As of this retirement:

- `provider_calls_authorized`: `false` (unchanged since materialization).
- `spend_authorized`: `false` (unchanged since materialization).
- **Zero paid cells ran.** No checkpoint, no completed cell, no provider
  call was ever made against this plan.

The 8/31 expiry is not being allowed to quietly lapse -- this record
documents, on the date of the decision, that the tariff window closes
with the replication explicitly retired rather than merely unexercised.

## No future authorization

No `experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_AUTHORIZATION.md` (or
any file matching `*AUTHORIZATION*.md` for this launch merge) should ever
be created. This retirement record supersedes that authorization path
entirely -- there is no remaining route to a paid run of this specific
replication plan. A future decision to run a similar comparison would be
a new experiment, preregistered and reviewed on its own terms, not a
revival of this one.
