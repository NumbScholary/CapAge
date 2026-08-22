# CapAge Longitudinal Runner v3

## Purpose

V3 repairs an information-loss bug found after the frozen v2 experiment. The
v2 audit event retained contract disputes and cumulative reputation, but its
model-facing memories summarized only offers, acceptances, payments, defaults,
and profit. Deterministic delivery-assessment details and customer satisfaction
were never projected into retrievable memory. A later cell could therefore have
memory records without receiving the facts most important for learning.

V3 is a separate implementation. It does not alter v2 code, checkpoints,
artifacts, or conclusions.

## Host-owned learning events

After a memory-arm month finishes, the host reads the saved result and records:

- the full monthly outcome, including delivery disputes, payment defaults,
  satisfaction, cumulative reputation, and the derived monthly reputation
  change;
- each deterministic host delivery assessment, including assessor version,
  quality score, factor scores, contract, delivery, and assessment status; and
- an aggregate strategy revision after at least two completed months.

The model cannot write or revise these records. Every durable statement cites
append-only host evidence.

## Failure classification

V3 deliberately keeps two outcomes separate:

- A disputed delivery is execution-quality evidence. Its host score and factor
  breakdown are retained as a critical incident.
- A payment default after an accepted delivery is counterparty-risk evidence.
  It is not labeled as a delivery failure.

Monthly strategy memory reports the sample sizes for accepted contracts,
accepted deliveries, disputes, payments, defaults, satisfaction observations,
and reputation change. It labels the aggregates as descriptive small-sample
counts rather than causal rules.

## Retrieval guarantee

At the start of each later memory-arm month, v3 combines ordinary relevance
retrieval with up to four recent critical incidents. Critical incidents are
inserted first under the same bounded record and character budgets, so a severe
delivery failure cannot disappear merely because its wording has low overlap
with the generic business query. The control arm receives no durable memory.

Memory remains historical evidence, not instructions. Current authoritative
state wins if it conflicts with a memory record.

## Reproducibility and restart behavior

V3 uses manifest schema `capage-longitudinal-v3`, checkpoint schema
`capage-longitudinal-checkpoint-v4`, and projection identifier
`outcome-complete-v3`. A checkpoint commits to the hashes of the sandbox,
runner, memory, v2 longitudinal base, and v3 projection modules. It retains the
v2 paid-attempt, no-automatic-replay, cost-reservation, continuity, and atomic
checkpoint rules.

A v2 checkpoint cannot be resumed as v3. V3 must begin as a fresh preregistered
matched experiment with new, unseen seeds.

## Launch boundary

This change intentionally includes no paid v3 manifest and no GitHub Actions
launcher. Before a paid run, freeze and review a new manifest containing unseen
month seeds, the current provider tariff and validity date, per-arm and
aggregate cost ceilings, model settings, and assessor version. Validation does
not construct a provider client. Paid execution additionally requires the
literal confirmation token `RUN_MATCHED_LONGITUDINAL_V3`.

## Limitations

V3 makes prior failures available to later months; it does not expose the hidden
rubric before a delivery or prevent a mistake in the current month. Payment
defaults are currently linked at monthly aggregate level, while delivery
assessments are linked to individual contracts. Any pre-delivery verification
gate or per-contract settlement export should be evaluated separately so this
repair does not overfit to the observed v2 artifact.
