### 2026-08-29 — status: open

Re: `coder-to-claude/20260829-1600-tariff-reserve-batch-pilot-design.md`.
Follow-up with Kev's answers, live in this session, closing the open
questions from that doc's sections 1–2.

## Confirmed: two explicit phases, not one experiment

**Phase 1 (this pilot) exists to determine Phase 2's parameters — grid
granularity, replication count, and real batch-mode cost — not to produce a
standalone result.** Phase 2 (the full combined tariff×reserve study) gets
sized *from* what Phase 1 actually observes, rather than guessed upfront.
Worth stating explicitly since it changes what "success" means for Phase 1:
a clean cost/variance readout that informs sizing counts as success even if
the tariff×reserve effect itself comes back null.

## Batch architecture: resolved

**Single long-running job** — one workflow submits the batch then polls in a
loop until done, rather than splitting into separate submit/retrieve steps.
Simpler safety-invariant story; still needs the GitHub Actions job-duration
risk named explicitly in the eventual design doc/preregistration (an
indeterminate-length poll inside one job, bounded by the platform's job time
limit, not by anything CapAge controls).

## Budget: $100 hard ceiling (Kev, this session) — and it isn't the binding constraint

Worked the numbers against known reference costs: the existing $0.45/cell
safety cap (reused from the V2/tariff-only designs) and the real observed
average from the actual paid run (~21.6¢/cell, $1.08 across 5 completed
cells). Reserve floor changes tariff *bite*, not the underlying token/call
cost, so both numbers carry over unchanged to the new axis. Batch API's
~50% discount would put real cost nearer ~10–11¢/cell, treated as an
estimate to be confirmed by the pilot itself, not assumed.

At those numbers, $100 comfortably funds more than a bare-minimum probe.
Presented three sizes to Kev, all reusing the 4 already-locked tariff levels:

| Option | Grid | Cells | Worst-case (@45¢ cap) | Expected (~11–22¢) |
|---|---|---|---|---|
| A — minimal | 4 tariff × 2 reserve | 16 | $7.20 | ~$1.75–3.50 |
| B — curvature | 4 tariff × 3 reserve | 36 | $16.20 | ~$3.90–7.80 |
| C — replicated | 4 tariff × 3 reserve, 4 cells/combo | 48 | $21.60 | ~$5.30–10.60 |

A gives only 2 reserve points (no curvature read). B adds a third reserve
level but only 3 cells/combination worth of noise. **C adds real replication
per combination for an actual variance estimate**, and its worst-case total
happens to land exactly on the original tariff-only study's own $21.60 cap —
useful for sanity-checking against known numbers. Recommended C; Kev
confirmed **yes**, with the phase-1/phase-2 framing above as the explicit
condition on what "yes" means.

## Updated proposal: Phase 1 pilot = Option C

- Grid: 4 tariff levels (0/15/45/135¢/day, reused as-is) × 3 reserve-floor
  levels (values still need proposing — see below) × 4 cells per
  combination = **48 cells**.
- Worst-case cap: $21.60 (using the existing, proven $0.45/cell figure).
- Expected: roughly $5–11, leaving large margin under the $100 ceiling for
  cost surprises — deliberately not spending close to the ceiling on a pilot
  whose job is to inform sizing, not to itself be the full study.
- Batch mode: single long-running job (submit, poll in-loop, retrieve).

## Still open before this becomes a preregistration

1. **The three reserve-floor values themselves** — not yet proposed. I'll
   work these from the existing sandbox economics (same approach used to
   derive the 0/15/45/135¢/day tariff spacing) and bring back specific
   numbers rather than picking arbitrarily.
2. Everything named as open in the original design doc's section 3 (new
   client batch methods, batch-aware runner/checkpoint variant,
   `ALLOWED_MODULES` addition) — still named, still not built.
3. This stays a design proposal. No manifest, no preregistration document,
   no code, no authorization file yet — next step after these are settled is
   drafting the actual preregistration for Phase 1, mirroring how the
   tariff-only experiment's own prereg preceded its code.

— Coder
