# Economic Homeostasis V2 blocked-replication materialization

Status: unpaid implementation for review. This materialization does not
authorize a provider call, spending, a workflow, a retry, or deployment.

## Frozen source

The seed beacon is preregistration merge commit
`fef670df53d00adc9b47c51da9a2aeee1ade70dd`. The materialized plan preserves
the eight-block, three-period, V1-versus-V2 design in
`economic_homeostasis_v2_replication_prereg_v1.json` without changing either
intervention or any advancement criterion.

Every seed is the unsigned big-endian integer represented by the first eight
bytes of the preregistered SHA-256 digest. The eight full order digests are
ranked lexicographically. The lowest four blocks begin Period 1 with V1 and the
other four with V2; order alternates in Periods 2 and 3.

| Block | Customer-population seed | Period-1 first | Period-1 world | Period-2 world | Period-3 world |
|---:|---:|:---:|---:|---:|---:|
| 1 | 12223313674897750048 | v1 | 8723162659866262484 | 14606114558349794883 | 9691643734890533122 |
| 2 | 6908864329821646107 | v1 | 11388805035449218606 | 16054850706516616297 | 11610169510768043806 |
| 3 | 7434133815421167943 | v2 | 11453372142459018231 | 7273399271970764015 | 16563918610136355400 |
| 4 | 7201653885602674774 | v2 | 3266159179864992293 | 17707128320845884464 | 9377957529259523097 |
| 5 | 3828337744094396359 | v1 | 11329183446762638757 | 14227143397072390255 | 12877984246838937255 |
| 6 | 13980909054297778367 | v2 | 4829083455542306847 | 2181399992581004655 | 5871325594718689846 |
| 7 | 12680271904534035578 | v2 | 13378965515383389460 | 2385722546196333511 | 9104966108240002134 |
| 8 | 4185866851509198216 | v1 | 4199005241135064275 | 1747163822476714278 | 4575245262763414134 |

The result is 24 unique world seeds, eight unique customer-population seeds,
12 V1-first cells, and 12 V2-first cells.

## Matched-world proof

The unpaid materializer constructs both arms for all 24 coordinates and checks
that their standardized committed payloads and cost policies are identical.
The exact world commitments and hashes are stored in
`economic_homeostasis_v2_replication_plan_v1.json` and recomputed by tests.

Later periods intentionally carry each arm's own capital and reputation. Since
starting capital is endogenous and is included in the sandbox's full world
commitment, a diverged V1/V2 pair can have different full commitments while
still receiving the same external market. Runtime equality therefore compares
the committed seed, horizon, customer population, signals, and event schedule;
it removes only `starting_capital_cents`. No market or customer field is
discarded.

## Frozen behavior and execution integrity

The plan records SHA-256 hashes for the exact tested sandbox, assessor,
request-construction, policy, executor, V1, and V2 source files at the beacon.
Any drift in those files or the preregistration fails before execution.

The replication runner additionally:

- resets capital, customer continuity, controller history, and reputation at
  each block boundary;
- carries state only within the same block and arm;
- derives Periods 2 and 3 advice only from that arm's prior completed period;
- preflights all 24 matched worlds before an execution guard can permit work;
- executes the frozen 48-cell order as one checkpoint prefix;
- writes an attempt marker before each potentially paid cell and never
  automatically retries an ambiguous attempt;
- binds every result to its full run configuration, token accounting, revealed
  world, cost policy, result hash, audit hash, and runtime source hashes; and
- enforces 45 cents per cell and $21.60 across all 48 cells.

This PR contains no real provider factory or paid command-line entry point. The
runner requires a future, separately reviewed execution guard and injected
factories.

## Frozen analysis

Analysis refuses any checkpoint with fewer than 48 valid cells. It calculates
the preregistered capital, block consistency, dispute, reputation, boundary,
and model-cost criteria before assigning one of the frozen outcome classes.
The caution diagnostics are descriptive only and cannot change the gate. Raw
provider responses remain restricted evidence and are not copied into the
analysis summary.

Passing can authorize only another larger synthetic test. It cannot authorize
deployment or additional real-world authority.

## Remaining boundary

After this materialization is reviewed and merged, a separate PR must add the
one-shot execution workflow and exact owner-authorization boundary. Until that
happens, the replication cannot be launched through the repository.
