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

## Fail-closed limitation

This version carries capital and memory but does not yet serialize active
contracts or counterparties. If a month ends with an open obligation, execution
stops rather than silently discarding it. Customer continuity, repeat business,
reputation, and stricter artifact assessment belong to the next sandbox-world
version and must be implemented before a paid longitudinal experiment.
