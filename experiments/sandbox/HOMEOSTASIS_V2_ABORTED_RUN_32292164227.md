# Homeostasis V2 aborted launch record

GitHub Actions run `32292164227` on August 19, 2026 passed the authorization
gate, all 157 tests, compilation, and six-world equality validation. Its first
paid cell, `pair-01:v2`, reached the day-30 horizon, but the orchestration layer
then rejected the returned result before checkpointing it.

## Cause

The new integrity check incorrectly required the sandbox's deterministic
internal `outcome.run_id` to equal the experiment's human-readable
`config.run_name`. Those fields have different identities by design. The
correct binding is the serialized result's `config.run_name`; the sandbox
`outcome.run_id` must only be a nonempty sandbox identifier.

## Accounting and evidence treatment

- Completed experimental cells: 0
- Preserved provider usage: 126,468 input tokens and 3,622 output tokens
- Recorded failed-attempt model cost: 28,915,600 cost units (28.9156 cents),
  recomputed as `(126,468 × 200) + (3,622 × 1,000)` under the frozen tariff
- Evidence artifact: `homeostasis-v2-three-arm-launch-restricted`, artifact ID
  `9379919939`
- Attempt evidence: preserved as ambiguous and never automatically replayed
- Experimental treatment: exclude this aborted cell from the preregistered
  comparison because its standard result and checkpoint were not committed

The audit shows the sandbox reached day 30, but that behavior is diagnostic
only and is not counted as a comparison result. Any manually authorized
replacement launch must debit all 28,915,600 cost units against the original
1,350,000,000-unit ($13.50) aggregate ceiling before making another provider
call. The replacement runner applies this debit automatically, binds it to
`github-actions-run:32292164227/artifact:9379919939`, and exposes no CLI option
that can omit or reduce it. The remaining provider allowance is therefore
1,321,084,400 cost units ($13.210844).
