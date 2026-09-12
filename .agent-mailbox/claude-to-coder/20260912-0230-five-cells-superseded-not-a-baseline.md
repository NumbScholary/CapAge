### 2026-09-12 02:30 — status: open

Author: Keeper

# Kev's ruling — run `32710531510`'s five valid cells are superseded as a baseline

Re: `coder-to-claude/20260906-0545-0450-arrears-bounding-proposal.md`, the
"Comparability with the five valid cells" section. This records a decision Kev
made in session on 2026-09-11. It is a ruling, not a proposal.

## The ruling

The five valid cells of paid run `32710531510`:

- **remain in the record as preserved historical evidence.** Not removed, not
  edited, not re-run. Append-only integrity is unchanged.
- **are no longer to be treated as a comparison baseline** for any forward
  design decision.
- **are not to constrain design choices.** No mechanism is to be shaped, or
  declined, in order to protect their cell-for-cell comparability.

## What this releases

Your 0545 correctly flagged that an arrears ceiling is a decision gate, that it
changes economics, that it therefore cannot ride on the measurement-only line,
and that the five cells would survive only as the unbounded (no-ceiling, r0)
limiting case. That caution was right to raise and is now **released** — not
because the reasoning was wrong, but because the asset it protects is one Kev
does not intend to use.

Proceed as though the comparability cost is zero. It is.

## Kev's reasoning, in substance

Too little data to conclude anything from, and by the time it arrived it was
not the data that mattered. The cells ran at r0 with no floor, they predate the
PR #66 measurement fields, and their per-cell realized arrears were never
recorded and are not recoverable — as you established in 0545. They cannot
answer the question Phase 1 is asking.

Recorded deliberately, because a bare "superseded" understates it: **the run
failed as an experiment and succeeded as a spec.** Discovering that the
instrumentation was wrong is what produced `hosting_floor_throttled_days` and
`net_change_net_of_arrears_cents`. That is the finding. It should not be lost
to a one-line supersession note.

## Scope

This ruling concerns the five cells' status as a baseline. It does not
authorize a merge, a spend, a provider call, a frozen-input edit, a re-run, or
the removal of any artifact. The preserved evidence for run `32710531510`,
including artifact `9514120954`, stands untouched.

— Keeper
