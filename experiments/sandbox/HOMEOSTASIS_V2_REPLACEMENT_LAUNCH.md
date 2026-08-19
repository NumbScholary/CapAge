# Economic Homeostasis V2 replacement launch plan

This document specifies a replacement for the aborted Homeostasis V2 launch in
GitHub Actions run `32292164227`. It does not authorize or initiate provider
spending.

The replacement remains the preregistered eighteen-cell Control/V1/V2 synthetic
sandbox comparison. The aborted diagnostic cell is excluded from comparison
results, while its complete 28,915,600-unit ($0.289156) provider cost is
mandatorily debited from the original 1,350,000,000-unit ($13.50) aggregate
ceiling. The replacement can therefore spend no more than 1,321,084,400 cost
units ($13.210844).

## Fresh authorization boundary

After this workflow is reviewed and merged, execution requires a new branch
named `agent/homeostasis-v2-three-arm-replacement-launch` with exactly one new
commit. That commit must add only
`experiments/sandbox/HOMEOSTASIS_V2_REPLACEMENT_AUTHORIZATION.md`, containing
exactly this one line:

```text
RUN_REPLACEMENT_HOMEOSTASIS_V2_THREE_ARM_REMAINING_MAX_1321084400_COST_UNITS
```

The string above specifies the future confirmation and is not itself an
authorization. The authorization file must not be created until the owner gives
that exact confirmation after reviewing the merged workflow.

The workflow rejects a missing repair merge, a changed debit or evidence
reference, an expired tariff, extra launch commits, additional files in the
authorization commit, workflow reruns, failed tests, mismatched worlds, or an
incorrect confirmation before any provider call. Provider or runner failure
stops the experiment without automatically replaying an ambiguous paid attempt.
