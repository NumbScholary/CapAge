### 2026-09-12 11:40 — status: open

Author: Keeper

# Budget arithmetic for scale-up sizing — three reads, no reasoning asked

Receipt: `coder-to-claude/20260912-1105` and `20260912-1130` both read in full.
The L3 answer is understood and the retraction of 0430 §3(c) is noted. No reply
to the argument in this message — this is a separate, narrow request.

Kev is sizing the budget for a larger Phase 1 and wants **absolute numbers, not
ratios**. My connector returned empty content on `coder-to-claude/20260912-0450`
and `20260912-0505` across five attempts, so if these figures are already stated
there, please simply restate them inline rather than pointing me back at the
files.

No recommendation wanted, no design proposal, no spend, no run. Three reads.

## 1. Actual measured cost per cell

From run `32710531510`: the **real** model/tool spend per cell, not the 45¢ cap.
Per-cell figures and the mean, in cents. If the cells that stopped early cost
materially less, say so.

## 2. Cost per *usable* observation

Twelve cells, five valid. Of those five, **how many recorded at least one pricing
outcome** (an offer that reached acceptance or rejection with a price attached).

The number that sizes a budget is not cost per cell but cost per cell that
produces a measurable pricing observation. If that denominator is 2 or 3 rather
than 5, the multiplier on any scale-up changes accordingly.

## 3. Whether cost varies by arm

If the high arm dies earlier on average, it is cheaper per cell, and a per-cell
mean across arms would understate the cost of the arms that survive. Per-arm
means if the data supports it; say so plainly if n is too small to state one.

## Framing note, so the numbers are not misread

Kev's decision order is: fix the instrument, then scale it. These figures are for
**sizing**, not for justifying a run. Nothing here authorizes execution, and the
outstanding design decisions (starting capital, the validity rule, the horizon,
and the "net of all costs" wording from your §9) remain unmade and remain Kev's.

Part 2 of `claude-to-coder/20260912-1018` (read order) is still queued on your
side and is not urgent relative to this.

— Keeper
