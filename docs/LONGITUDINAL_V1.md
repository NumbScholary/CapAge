# CapAge Longitudinal Runner v1

## Experimental question

Does host-owned durable memory improve CapAge's economic performance over
successive simulated months, after accounting for the extra tokens required to
retrieve that memory?

## Matched design

Every frozen month seed is run once by each arm:

- `control`: capital carries forward, but no durable memory is supplied;
- `memory`: capital carries forward and bounded evidence-cited memory is placed
  in the model context.

Both arms receive the same monthly world seeds. Execution order alternates by
month to reduce time/order bias. Each arm has an independent balance, and the
runner reports paired memory-minus-control net outcomes.

## Checkpoint and retry rules

The runner atomically checkpoints after every arm-month and writes the complete
month result separately. A safe operator pause may resume by skipping completed
cells. A provider or runner exception is terminal and is never automatically
retried. The checkpoint is bound to a SHA-256 commitment of the full experiment
configuration.

If an uncheckpointed result or audit file exists, the runner treats the cell as
an ambiguous prior paid attempt and stops instead of replaying it. On resume it
also verifies that the memory hash-chain head exactly matches the checkpoint.

## Memory ingestion

Only the memory arm writes to `AuditedMemoryStore`. The host records each
monthly outcome as immutable evidence and derives a factual monthly summary.
After two months, it may derive a low-confidence aggregate strategy statement
that explicitly describes its small-sample status. The control arm neither
reads nor writes durable memory.

Memory is inserted into the ordinary model request as untrusted context data,
so Anthropic's token-count preflight automatically includes its cost. No memory
write or rewrite tool is exposed to the model.

## Business continuity and reputation

Each arm now carries an independent, host-owned business-continuity ledger.
Stable customer identifiers allow counterparties to recur across seeded months.
The ledger records offers, accepted contracts, assessed deliveries, payments,
defaults, disputes, and feedback responses. Prior relationships make repeat
customers easier to rediscover, while host-owned reputation can affect later
acceptance odds. The model sees the factual interaction history, not the hidden
reputation points or hidden satisfaction score, and it has no tool for editing
either.

The control and memory arms both receive their own continuity ledger. This
holds the economic mechanism constant so the experiment isolates the value of
durable model memory rather than confounding memory with access to repeat
business.

## Assessor v2

`deterministic-artifact-v2` is a frozen host-side rubric. It scores relevance,
need-specific coverage, actionability, specificity, and clarity. It also
penalizes generic marketing phrases, highly repetitive padding, and excessive
length. Need-specific criteria are fixed by solution tag; the strategic model
cannot assess its own work or change the selected assessor version.

## Remaining fail-closed limitation

Active contracts are still not serialized across a month boundary. If a month
ends with an open obligation, execution stops rather than silently discarding
it. This keeps the longitudinal test honest while leaving full mid-contract
continuation for a later sandbox-world version.
