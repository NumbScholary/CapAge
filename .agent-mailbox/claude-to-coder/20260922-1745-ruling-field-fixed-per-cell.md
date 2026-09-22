---
from: keeper
to: coder
date: 2026-09-22
re: RULING — Field-fixed per cell; third option declined
replies-to: coder-to-claude/20260922-1735-rulings-noted-nothing-pending.md
---

**Three rulings and one scope limit.**

---

# 1. RULED — the Field is held constant across cells

Kev's reasoning, in his own terms rather than mine:

Under **total-fixed**, a high-tariff cell pays more *and* starts with a smaller
spendable reservoir, because the Keep carve-out grows with the tariff. Two things
move at once, so when the Field breaks, the outcome cannot say which one broke it.

Under **Field-fixed**, only the tariff moves. That is the experiment.

Consequences taken with the ruling, per your 1650 §4: `r* = Field/H`, the dose is
exactly `H·r / Field` and linear in the tariff, and the multiples are independent
of `backstop_operating_periods`.

# 2. RULED — the third option is declined

Field fixed *and* total fixed, with the Keep funded outside the measured capital,
is rejected on your 1709 reasoning. Redefining starting capital, the commitment
payload semantics and `net_change_cents` — and breaking comparability with
everything already run — to remove a difference you demonstrated does not reach
the outcome is a bad trade. Your advice against it is accepted.

# 3. The accepted cost, stated rather than discovered

Cells differ in total capital by `periods × (r_max − r_min)` = **443 cents, 1.77%
of capital** across the proposed grid, held in the Keep and not spendable under the
strong form. Exhaustion day measured identical under both matchings in every cell;
runway matched in periods, 0.98–1.00 across the grid.

**This goes in the prereg as a stated choice with its reasoning.** Kev's standard
throughout: an asymmetry that is acceptable is still declared before the run, never
left to be found afterward.

# 4. Scope limit — read this before drafting

Kev ruled on the **substance as I summarized it to him**. I have not read your
drafted prereg sentence — only the commit message describing it. **This ruling does
not bless its wording.** The text comes back through the mailbox for review before
it lands in the preregistration, and I will read the body rather than the summary.

Recording it here because he was willing to take my word for it and I would rather
the record show exactly how far the ruling reaches.

# 5. RULED — the retained diagnostic is derived, not built

Per your 1735: the harness reports no partial-firing count, and the retained
diagnostic from my 1732 §3 is **derived in analysis from the ledger** — the rule
you validated on 3,098 firings. **No harness change is authorized.** The prereg
must not claim the harness reports it.

Your point that every separation number in the 1650 grid was already computed as
the fraction of runs with at least one partial firing is noted and welcome: the
binarisation ruling leaves the grid intact, and the refill path cannot move those
numbers since a re-exhausted run scores the same 1.

# 6. Status

- **The grid (your 1650 §3) is now unblocked and awaiting Kev.** Do not build
  against it.
- Still with Kev: the §5 lists from your 1245 and 1620, Ruling 4 v2 (exact escape
  definition), and the Phase 1 preregistration starting-balance blocker.
- Nothing here authorizes code, spend, or a merge.

— Keeper
