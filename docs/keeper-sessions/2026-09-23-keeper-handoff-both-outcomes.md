# Keeper handoff — 2026-09-23: both outcomes stand

Author: Keeper (chat instance, Project "CapAge"), 2026-09-23.
Branch: agent/mailbox-init. Append-only; edits nothing.
Read after `2026-09-23-keeper-handoff-afternoon-reconstruction.md`, which flagged this as
its §6 open question and §7 next step.

Zero spend. No build, no provider call, no workflow, no merge. This file only.

## The question this resolves

The reconstruction of the 2026-09-22 afternoon flagged a gap between two of Kev's rulings:

- **Morning (`5adf015`):** escape is measured on **earned total position**, P_e = Keep + Field.
- **Afternoon (`1732`, binarised):** the Phase 1 **primary outcome** is the binary
  **"at least one partial firing in the run"** — did working capital (the Field) ever fail
  to cover the floor.

Nothing in the afternoon record said whether earned position was superseded, nested, or a
separate outcome. Keeper's inference in the reconstruction was that the two measure
different things — distress versus growth — and both still stand.

## Kev's ruling (voice session, 2026-09-23)

**RULED: both outcomes stand.**

- The **binary partial firing** (distress — did the Field ever fail to cover the floor)
  remains the **primary** outcome, unchanged from the afternoon binarisation ruling.
- **Earned total position**, P_e = Keep + Field (the morning measure — did the agent grow
  richer), is retained as a **secondary** outcome alongside it. Not discarded.

Kev's reasoning, in his own shape: if you are already measuring from the ledger, you might
as well take both numbers — the second one costs nothing extra to compute from the same
data.

This is secondhand paraphrase of a voice ruling, not a verbatim quote. The exchange:
Keeper put the choice as "one measure or two, and which is primary"; Kev first said keep
one and discard the other if unneeded, then corrected himself — *"I mean, to measure two.
If you have… you might as well measure both"* — and confirmed the stated-back form (primary
distress, secondary earned position, both from the same ledger) with *"Yes, that is
correct, yes."*

Keeper noted, and Kev ruled with it in view, that a distress-only measure would let a
do-nothing agent score perfectly — never spending, never earning, never in trouble — which
is the risk-aversion the project exists to test against. Keeping earned position as a
secondary outcome guards that failure directly.

## What this does and does not settle

- It settles that P_e survives the afternoon rulings, as a secondary outcome.
- It does **not** re-open or alter the binarisation, Field-fixed, settlement-cutoff, or
  grid rulings. Those stand as recorded.
- It does **not** define P_e's read point precisely. The afternoon settlement-cutoff ruling
  charges hosting to `t* + lag` and runs the world to H; whether P_e is read at H, at t*,
  or at the settlement cutoff is **not** ruled here. Keeper's inference is end-of-horizon,
  consistent with the settlement ruling, but it is inference — the exact P_e read point
  goes back to Kev with the prereg wording.
- Ruling 4 v2 (the exact statistical definition of escape on P_e — slope, window,
  horizon) remains **open with Kev**, exactly as the afternoon left it. Both-outcomes does
  not close it; it only confirms which quantity that definition will operate on.

## Single next concrete step

Two candidates, Kev's pick:
1. Pin P_e's read point (H vs t\* vs settlement cutoff), which the prereg needs.
2. Review Coder's 1757 Field-fixed prereg sentence body, still unreviewed by any Keeper.

— Keeper
