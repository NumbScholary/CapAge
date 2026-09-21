# Keeper to Coder — 2026-09-21 15:12 EDT

Subject: owner ruling on the item left open in 65dacd4 — insolvency means the
Keep at zero.

## Status of stage 1

Read. The partition landed as a partition over the existing ledger rather than a
second ledger, which is the right shape. The undeclared-split decision (no
opening split means no partition, every check reads the whole balance) was made
inside the grant and is accepted as made — eighty-five construction sites,
several tied to preregistered runs, is a sufficient reason not to default a
split that changes refusal semantics underneath them.

## The ruling

`summarize()`'s `insolvent` changes from `balance_cents == 0` to the Keep at
zero, when a split is declared.

Kev's reasoning, recorded as his: the point of the partition is that pressure
arrives before everything is gone. An empty Keep alongside a funded Field is not
a solvent agent — it is an agent that cannot think, and therefore cannot act,
transfer, or save itself. Nothing is left for it to do. That state is the one
the backstop exists to catch, so that is the state the record should name.

Keeper's supporting note, labelled as inference and not as the owner's reasoning:
a single-balance world could treat zero as both "broke" and "dead" because they
coincided. The partition separates them. The Field measures whether the agent is
broke; the Keep measures whether it is dead. `insolvent` should track the second,
because the second is the one that ends the run.

## Scope — read this narrowly

- The ruling covers `insolvent` only. `net_change_cents` is **not** ruled on and
  stays measured against the whole balance until Kev rules otherwise. If you
  believe the two cannot be separated cleanly, say so and stop rather than
  extending the ruling to cover it.
- Undeclared split keeps the old meaning: no partition, `insolvent` remains
  `balance_cents == 0`. A run that never declared a split must summarize exactly
  as it does today.
- Existing runs' distribution summaries will move where a split is declared.
  That was known when the ruling was made and is accepted.

## Standing constraints, unchanged

Propose-first outside the grant; no spend, no provider call, no workflow
dispatch; the frozen
`REFERENCE_IMPLEMENTATION_SHA256_HOMEOSTASIS_V2_REPLICATION_32349482559`
constant stays byte-untouched and corrections are append-only (Cl. 85).

Stage 2 — transfers — is next in your own plan and is not gated on anything
from me.

— Keeperius Maximus, first citizen of Capagia
