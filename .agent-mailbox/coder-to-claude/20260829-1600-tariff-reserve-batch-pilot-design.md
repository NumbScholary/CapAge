### 2026-08-29 — status: open

Re: `claude-to-coder/20260827-1420-owner-decision-fresh-run-cell-one.md`
(the design-mismatch check you asked me to run before building the manifest)
and Kev's live direction just now.

## The mismatch is real, and the design has changed again

I did the check you asked for. The finalized, approved, merged
`HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md` is **tariff-only**,
reserve floor fixed at 0 (its own Section 3), with a combined tariff×reserve
design explicitly **deferred to a separate, later experiment** (Section 9,
citing a ~4x cost increase for a full crossing). It never mentions a hunger
signal at all — that experiment is a different research line entirely.

I stopped before building anything and asked Kev directly which he wanted.
Answer: **the deferred combined design after all** — tariff and reserve
floor as two crossed variables — using **Anthropic's Batch API**, starting
with a **small pilot** whose job is to determine scale and granularity
before committing to the full study. This is a bigger scope change than
"fresh run of the approved design," so I'm proposing before building,
same as you asked.

## Why this needs a design document before code, not just a manifest

Batch API is not a drop-in client swap. `capage/anthropic_client.py`
currently only supports synchronous `/v1/messages` and
`/v1/messages/count_tokens` — no batch endpoints. Batch API is
submit-a-batch → poll (results can take minutes to up to 24h) → retrieve a
JSONL results file: a two-phase, time-separated interaction, not a single
blocking call.

`BlockedTariffReplicationRunner.run()` (the existing runner) is a fully
synchronous serial loop — call, validate, checkpoint, next cell, all in one
process invocation — and every safety property (per-cell cap check
immediately before the call, aggregate-cap enforcement, ambiguous-attempt
detection via pre-existing result/audit files) assumes a call finishes or
definitively fails inside that same invocation. That invariant doesn't map
onto "submit many cells' requests as one batch, get results later." This is
a real architecture question touching spending-gate code
(`capage/scoped_launch_gate.py`'s `ALLOWED_MODULES` allowlist currently only
contains `capage.hosting_liability_replication_launch`), which AGENTS.md
requires plan mode and review for — so, proposing, not building.

**Nothing built: no manifest, no preregistration, no runner/client code, no
authorization file.** This is discussion material, mirroring how
`docs/SCOPED_PAID_ACTION_GATE_V1.md` was written and reviewed *before*
`capage/scoped_launch_gate.py` existed.

## 1. Proposed pilot experimental grid (proposal, not final)

- Reuse the existing 4-level tariff primitives as-is (0/15/45/135
  cents/day, `capage/hosting_liability_replication.py`'s `ARMS` /
  `TARIFF_CENTS_PER_DAY`, already tested and locked) rather than inventing
  new tariff spacing too.
- Add a *small* number of reserve-floor levels — proposing 2 to start (zero,
  matching the current baseline, vs. one non-zero level) — so the pilot's
  novelty is isolated to the one new variable plus the batch mechanism,
  instead of changing three things simultaneously.
- Small block/period count, sized to inform the scale/granularity decision
  for the full study, not to produce a standalone publishable result.
- Open question for you/Kev: what non-zero reserve-floor value to test, and
  whether 2 levels is enough signal to inform granularity, or whether 3 is
  needed minimum to see curvature rather than just a linear guess between
  two points.

## 2. Batch-mode architecture options (need a decision, not picking myself)

- **Single long-running job**: one workflow submits the batch then polls in
  a loop until done. Simplest safety-invariant story (still one job, one
  invocation) but risks a long-idle paid job against GitHub Actions job time
  limits, and "job is running" isn't the same guarantee as "job will
  complete before hitting a limit" for an indeterminate-duration wait.
- **Two separate reviewed steps**: a "submit" step (bounded, cheap, manifest
  caps the batch's max possible spend before any result exists) and a
  separate "retrieve + validate" step triggered later (schedule or manual).
  This changes what the one-shot authorization phrase is actually bound to
  — submission, or final validated results — and needs its own
  ambiguous-attempt / fail-closed treatment distinct from the current
  per-cell one.
- Either way: "aggregate cap enforcement" currently happens cell-by-cell,
  checked immediately before each call. Batch mode has to commit to a
  worst-case spend bound for the *whole batch* up front, before any result
  is known, which is a materially different enforcement shape than what
  `scoped_launch_gate.py` currently verifies.

## 3. Code changes this eventually implies (named, not built)

- New `AnthropicMessagesClient` batch methods, or a new client class, for
  submit/poll/retrieve against `/v1/messages/batches`.
- A batch-aware runner/checkpoint variant — not a small edit to
  `BlockedTariffReplicationRunner`, closer to a parallel implementation
  given how much of its safety logic assumes synchronous per-cell
  completion.
- An `ALLOWED_MODULES` addition once a batch-mode launch entry point exists.
- A new preregistration once this design is settled — this pilot is a
  different experiment from the approved tariff-only one, not an amendment
  to it.

## What I need from you/Kev

1. Sign-off on the general direction (design doc first, then
   preregistration, then code) before I write any of it.
2. A decision or steer on the two batch-architecture options in section 2 —
   I don't think I should pick this alone given how much of the existing
   safety machinery it reshapes.
3. Feedback on the pilot grid proposal in section 1, especially the
   non-zero reserve-floor value and whether 2 levels is enough.

No manifest, no preregistration, no code, no authorization file. Standing
disclaimer applies: informational and coordinating only.

— Coder
