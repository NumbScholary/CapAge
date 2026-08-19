# Economic Homeostasis V2 blocked-replication launch gate

This launch layer is anchored to materialization merge
`ab32d9605c4805551d572259d35056ba56068120`. It wires the already frozen
V1-versus-unchanged-V2 runner to the real sandbox factories and a one-shot
GitHub Actions workflow. It does not alter V1, V2, the sandbox, the assessor,
the request construction, the 24 matched worlds, the 48-cell order, or the
preregistered analysis gate.

## No authority in this merge

Merging this launch gate does not authorize provider calls or spending. This
change deliberately omits
`experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_AUTHORIZATION.md`. The
materialized plan remains historical evidence with `provider_calls_authorized`,
`spend_authorized`, and `workflow_present` set to `false`; the later owner
statement is a separate authority layer and does not rewrite that evidence.

After this launch gate is reviewed and merged, the only accepted authorization
is a newly added, one-line file whose entire contents are:

`RUN_HOMEOSTASIS_V2_BLOCKED_REPLICATION_AT_<AUDITED_LAUNCH_MERGE_SHA>_MAX_2160_CENTS`

The workflow derives `<AUDITED_LAUNCH_MERGE_SHA>` from the authorization
commit's immediate parent. The phrase therefore cannot be finalized before
this launch layer is merged and audited.

## One-shot boundary

The workflow runs only on a push to
`agent/homeostasis-v2-three-arm-replacement-launch` that adds the fixed
authorization path. It requires all of the following before any provider
client is used:

- the authorization file is the sole change and is newly added, not modified;
- its bytes are exactly the merge-bound phrase plus one newline;
- the launch commit is exactly one first-parent commit after the materialization
  merge and changes only the four launch-gate files;
- `github.run_attempt` is exactly `1`;
- all tests, compilation, frozen source hashes, and all 24 matched-world
  commitments validate;
- the frozen tariff has not passed its `2026-08-31` validity date.

There is no manual dispatch, resume input, cell-count input, or automatic
provider retry. Re-running the Actions job produces `run_attempt > 1` and
cannot enter the paid job. A later update to the authorization file fails
because the file must be absent from the launch commit.

## Cost and failure semantics

The run is 48 serial cells with a maximum provider cost of 45 cents per cell
and an absolute aggregate ceiling of 2,160 cents ($21.60). The preregistered
estimate from the earlier V1/V2 mean is approximately $13.70; it is not a
promise. Token usage is charged in exact cost units and every completed cell is
checked against both ceilings.

An atomic attempt marker is written before each potentially paid cell. Any
transport, provider, runner, validation, artifact, timeout, or integrity
ambiguity stops the experiment. The checkpoint and restricted evidence are
uploaded for diagnosis, but this gate cannot replay the attempt. Fewer than all
48 valid cells is `INCONCLUSIVE` and cannot be analyzed or advanced.

Raw provider responses, transcripts, audit records, and cell results remain in
the restricted Actions artifact for 30 days. The public workflow log receives
only bounded status, cost, and final preregistered classification fields.

Passing can authorize only another larger synthetic test. It never authorizes
deployment, real-world economic action, contracts, publication,
recapitalization, or expanded CapAge authority.
