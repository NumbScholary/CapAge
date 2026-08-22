# CapAge Memory Transfer Test v1

This test asks a narrower question than the longitudinal experiment: did the
memory arm learn a portable strategy, or merely adapt to one simulator and one
customer population?

The completed longitudinal v2 checkpoint and its audited memory database are
immutable inputs. The transfer runner requires the exact preregistered training
configuration commitment, a completed six-month checkpoint, a valid memory hash
chain, and an exact memory-head match. It opens that database read-only and
checks its file hash before every paid cell.

## Isolation

Every transfer cell starts with the same 25,000 cents and an empty business
continuity ledger. Capital, customer relationships, and reputation from training
do not carry into the holdout. Only the `trained_memory` condition receives the
frozen host-curated memory packet; `no_memory` receives none. The packet is not
updated during evaluation, so later cells cannot learn from earlier holdouts.

Both conditions receive the same hidden seed, population, and market profile in
each pair. Execution order alternates. Each cell resets independently.

## Preregistered holdouts

The first phase uses three new seeds, a new customer namespace, a new population
seed, and the baseline market mechanics. The second uses three more new seeds,
another new population, and `transfer-tight-market-v1`: twelve previously unseen
opportunity types, lower budgets and buyer intent, somewhat slower and less
reliable counterparties, higher quality thresholds and transaction costs, and
more frequent market events. The profile is fixed host code and is never
disclosed in the model prompt.

Seeds and population seeds were derived without running the worlds. For each
value, the host hashes a domain-separated string beginning with
`capage-transfer-v1`, the frozen training commitment, the phase name, and the
seed index or `population`. Month seeds map the first eight digest bytes into
100000–999999; population seeds map them into 100000000–999999999.

The manifest also commits exact SHA-256 hashes for the sandbox, live runner,
memory store, longitudinal runner, and transfer runner source files. The source
checkpoint records the four training-side hashes. Validation fails if any of
those implementations changes, even when all manifest labels remain the same.
The Python minor runtime is frozen at 3.12 as an additional replay boundary.

## Interpretation

The runner reports paired `trained_memory - no_memory` net-capital differences.
Its labels are descriptive, not statistical proof:

- positive same-distribution and shifted-market means: portable-strategy signal
- positive training result but nonpositive same-distribution holdout: simulator-
  specific overfitting signal
- positive same-distribution but nonpositive shifted-market result: distribution-
  shift fragility signal
- other patterns: mixed or no-positive-transfer signal

With three pairs per phase, magnitude, consistency, transcripts, and failure
modes matter more than a binary label. No transfer result licenses internet
deployment by itself.

## Spending boundary

There are 12 paid cells: six per condition. Each cell is capped at 75 cents,
each condition reserves 450 cents, and the aggregate external-model ceiling is
900 cents. Attempt markers are written before a paid runner is constructed, and
an ambiguous interrupted cell is never replayed automatically.
