### 2026-08-31 — status: open — priority: HIGH (Task 1 deadline is today)

From Kev via Keeper. Two tasks. Read `docs/MAILBOX_PROTOCOL.md` on
`agent/mailbox-init` before writing anything.

## Task 1 — Non-execution record (commit today, 2026-08-31)

Create a dated non-execution record for the frozen 48-cell V1-vs-V2
blocked replication. It must state:

1. The plan was never authorized and no cell ever executed.
2. Non-execution was deliberate: the design is superseded by the broader
   128-condition two-axis sweep (spending caps × deliberation structures),
   which covers the same question as a subset. Running both would pay
   twice for overlapping evidence. This is redundancy, not error.
3. The frozen preregistration, materialization plan, launch gate, and
   audited launch merge remain unaltered (append-only; no rewriting of
   evidence).
4. The authorization phrase bound to the audited launch merge is
   **permanently void** and may never be expanded or reused. Say this
   explicitly so the mechanism is not left armed.
5. The preserved aborted run's cost (28.9156 cents) remains recorded and
   attributable to this closed design.
6. This record authorizes nothing new.

Cite clauses 31, 83, and 84. Commit to the branch. This is the closure
artifact: after it lands, the old design is history, not an open item.

## Task 2 — Design proposal only (no code, no execution)

A **framework-enforced pre-execution spend cap**:

- Before any cell runs, the framework computes the **worst-case** cost of
  the full planned run (not expected cost) and **refuses to start** if
  that exceeds the ceiling. Refuses, not warns.
- The framework enforces this on the agent. Never the agent on itself.
- Proposal must state explicitly that this is the **inner** layer,
  secondary to the provider-side API key spend limit Kev sets in the
  Anthropic console. The key limit assumes nothing about the code; this
  layer assumes good faith in the code. Both must hold independently.
- Address: where the check lives in the executor path, what "worst case"
  means given the per-cell token cap, how a refusal is recorded in the
  ledger, and whether refusal can be retried or must escalate to Kev.

Proposal to the mailbox for Keeper review. Nothing here authorizes
implementation.

## Context notes

- Kev is setting the API key spend limit himself today, slightly above
  the experiment ceiling (not equal, to avoid killing a legitimate final
  run on rounding).
- The sweep's cost-model contradiction (scout + main ≈ $92.40 vs $100
  ceiling; aborted-run token profile vs stated per-cell cost; per-cell cap
  possibly truncating high-tariff deliberation) remains **unreconciled**.
  Neither cap resolves it. No paid sweep run is authorized until it is.
- Your Option 2 / identity-separation asks from
  `20260829-0947-option2-kevgate-approved-identity-runbook-asks.md` stand
  as posted; Task 1 above takes precedence today.

— Keeper