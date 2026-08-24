# Hosting-liability tariff replication: cost correction for run 32710531510

**Status: append-only correction, 2026-08-24. Does not edit or supersede the
original mailbox report; adds a missing fact to the record.**

This corrects the reported real provider spend for GitHub Actions run
`32710531510` ("CapAge Hosting Liability Tariff Replication launch",
2026-08-24), the partial 5/48-cell paid run against
`hosting_liability_tariff_replication_plan_v1.json` (seed beacon
`728e8c533b2724ce0b5ff0de0942559ff0046623`).

## What was originally reported

Real spend: **$1.08 (107.8882 cents)**, well under the $21.60 aggregate cap.
5 of 48 cells completed validly; cell 6 (block-01 period-02, zero-tariff arm)
failed with `provider_or_runner_error` and the run stopped cleanly.

That figure was correct as a sum over the 5 successfully validated cells. It
was **not** a complete accounting of the run's real provider spend, and
wasn't labeled as such at the time. This note fixes that gap in the record.

## The gap

`BlockedTariffReplicationRunner.run()` only added a cell's
`actual_model_cost_units` to the aggregate cost total
(`self.state["model_cost_units"]`, the figure checked against
`aggregate_cost_cap_cents`) after that cell passed validation. A cell that
failed validation -- like cell 6 -- never contributed its own cost to the
aggregate, even though a failed cell can still have incurred real, billed
provider cost before failing. This has been fixed (same PR as this note):
failed cells now count their raw, already-billed cost toward the aggregate
whenever that cost is recoverable from the raw result, and the checkpoint's
own reload validation was updated to match.

## What we don't know, and will never know, about run 32710531510

The fix above only helps **future** runs. For this specific historical run,
cell 6's actual `actual_model_cost_units` is permanently unrecoverable:

- The fix that persists a cell's raw sandbox result to disk *before*
  validation (PR #53) did not exist yet when run `32710531510` executed --
  it was built afterward, specifically because this run's failure surfaced
  the gap.
- Without that fix, a cell that fails validation leaves no raw result file
  behind at all -- only the wrapping exception message
  (`"cell did not complete"`) was ever recorded.
- The preserved evidence artifact for this run (`9514120954`) was checked
  directly and contains no raw result for cell 6, only its `-attempt.json`
  and `-audit.jsonl` files. The audit log shows normal activity through day
  6 (real earned revenue) and then nothing -- it records tool actions, not
  provider-level cost or failure detail.

So: cell 6's real cost cannot be reconstructed from any available evidence.
It is gone.

## Corrected statement of real spend for run 32710531510

The previously reported $1.08 / 107.8882 cents must be read as a **floor**,
not a complete total, for this run's real provider spend. Cell 6's own real
cost was necessarily somewhere between $0 and the per-cell cost cap of
$0.45 (45 cents) -- `_run_config`'s `max_run_cost_cents` bounds what any
single cell attempt could have spent, cap-enforced independent of whether
the cell ultimately succeeded or failed. So:

**Total real provider spend for run `32710531510` was between $1.08 and
$1.53, with the exact figure permanently unknown.**

## Constitutional basis for this note

This is a new, append-only record, consistent with:

- **cl. 14 (Prospective correction):** "Errors may be corrected by traceable
  correcting entries. Material measurement-definition changes shall be
  prospective and versioned; they shall not silently rewrite historical
  results." This note is that traceable correcting entry -- the original
  mailbox report is untouched.
- **cl. 84 (Failure preservation):** the failed cell and its incomplete
  evidence are preserved and disclosed, not omitted because retention makes
  the reported figure look less complete.
- **cl. 85 (Append-only correction):** the original record is preserved; a
  linked correction is appended rather than rewriting history.

Both clauses verified directly against the Constitution PDF text
(`pdftotext` on `docs/constitution/CapAge Constitution v0.1_...pdf`) before
citing here.

## What is not affected

- The original mailbox report is untouched -- this note supplements it, not
  replaces it.
- Cells 1-5's recorded costs and results are unaffected; they were, and
  remain, correctly validated and accounted for.
- No authorization file, launch workflow, or protected branch is touched by
  this note.
