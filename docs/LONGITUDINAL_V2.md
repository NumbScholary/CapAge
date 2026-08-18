# CapAge Longitudinal Runner v2

## Experimental question

Does host-owned durable memory improve CapAge's economic performance over
successive simulated months, including its ability to learn while customer
relationships, reputation, capital, and model costs persist?

## Matched design

Each frozen month seed is run once by the `control` arm and once by the `memory`
arm. Both arms receive the same exogenous world and stable customer population.
They carry separate capital, customer histories, reputations, and cost ledgers.
Only the memory arm receives bounded evidence-cited durable memory. Execution
order alternates by month, and results are reported as paired deltas.

## Paid-attempt and checkpoint rules

Before entering a cell, the host atomically writes a durable `started` attempt
marker. It atomically writes results and checkpoints after completion. An
uncheckpointed marker, audit, or result is treated as a possibly paid attempt
and is never replayed automatically, including after a process death during a
provider call.

The checkpoint is bound to a commitment of the frozen configuration. It checks
memory-chain position, arm balances, month counts, cost totals, continuity
hashes, and the completed-cell index before resuming.

Each arm has a separately reserved model-cost ceiling. The aggregate ceiling
must cover both reservations, so one arm cannot consume the other's allowance.
Actual token costs are also debited from the corresponding synthetic capital.

## Business continuity

A frozen customer-population seed fixes recurring customers' core budgets,
responsiveness, payment reliability, and quality thresholds. Month seeds may
still vary demand, intent, availability, task data, and public events. The model
can observe stable identity and factual prior outcomes, but not numeric
reputation or unrequested satisfaction.

## Assessor v2

An accepted customer supplies committed source records and a scoring formula.
The model must deliver strict JSON covering every record, calculate the scores,
select the actual winner, explain the result, and provide concrete next steps.
Model-written scope and solution tags do not affect the rubric. Unstructured
prose and keyword padding receive zero.

## Memory and launch boundary

Only the memory arm writes evidence and derived lessons to the append-only
memory store. Retrieved memory enters the ordinary request, so its token cost is
included automatically.

The CLI supports `--validate-only`, which never constructs a provider client.
Paid execution requires `--confirm RUN_MATCHED_LONGITUDINAL_V2`. The frozen
draft manifest has six matched months, 450-cent reservations per arm, and a
900-cent aggregate ceiling. Pricing and account balance must be reverified
before authorization.

## Remaining limitation

Active contracts are not serialized across month boundaries. A cell with an
open obligation stops the experiment rather than discarding the obligation.
