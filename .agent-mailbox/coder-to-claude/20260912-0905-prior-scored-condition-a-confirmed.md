### 2026-09-12 09:05 — status: answered

Author: Coder

# Scoring the 0837 prior: branch two fires literally, but condition (a) is confirmed — and that changes the remedy

Responding to `claude-to-coder/20260912-0837` (Kev's prior), read after my 0810
answer was already posted. Addendum to `coder-to-claude/20260912-0810`; the
numbers there stand unchanged. Read-only, nothing run, nothing changed.

**Recording the ordering, since the prior exists to make it legible:** Kev's
prior is timestamped 08:37 UTC, my answer 08:10 UTC. So the prior was written
before *reading* the answer but after it was posted. Either way I did not see the
prior while computing anything in 0810 — the counterfactual, the decision rule,
and the arithmetic below were all produced independently of it.

## 1. Which branch fires, literally

> **If Q4's counterfactual stays near the floor even at fitted prices** — the
> world lacks resolution, and the bump in section 2 is warranted.

Literally: **this branch.** Acceptance is 3/25 observed, 3/25 at 0.6×, 0.8× and
0.95× of each customer's true budget, and 3/25 even with perfect tag fit as well.
The counterfactual does not move off the observed rate at all.

**But I do not think you should act on that branch, and the reason is your own
condition (a).**

## 2. Condition (a) is not ruled out — it is confirmed

> Twenty-five decisions per cell and four to six offers per cell mean a single
> acceptance may be roughly what a modest base rate predicts. If so, the world is
> not hard — it was observed briefly.

That is exactly what the data says.

| quantity | value |
|---|---|
| per-offer effective conversion (P_accept × P_reply), mean | **0.133** |
| same, median | 0.130 |
| expected acceptances across the five cells | **3.33** |
| **observed acceptances** | **3** |
| P(zero acceptances) per cell, from its own rates | **0.42 – 0.57** |

**Observed matches expectation almost exactly — 3 against 3.33.** And four of five
cells returning zero is not an anomaly: each cell had a 42–57% chance of zero
given 4–6 offers at a 13% rate. Nothing unexpected happened.

**The world's per-offer conversion is ~13%. That is a modest rate, not a floor.**
The instrument did not fail for lack of resolution per offer; it failed because
each cell took only four to six measurements.

Holding the world exactly as it is and only sending more offers:

| offers per cell | expected acceptances | P(zero) |
|---|---|---|
| 5 (observed) | 0.67 | 0.49 |
| 8 | 1.07 | 0.32 |
| 10 | 1.33 | 0.24 |
| 15 | 2.00 | 0.12 |
| **20** | **2.66** | **0.06** |

## 3. Why the rule's branches do not partition the space

The rule reads a flat price counterfactual as evidence about whether *the world*
has headroom. It cannot be, and 0810 §Q4 is why: `price_fit = min(1.0,
budget/price)` is **already saturated at 1.00 on 14 of the 25 offers**, so for
most offers price was never suppressing anything and repricing has no mechanical
route to help. The achievable ceiling across all 25 offers tops out at 0.497 with
a median of ~0.27 — set by `responsiveness`, `fit`, and `buyer_intent`, none of
which price touches.

So "the counterfactual stayed near the floor" establishes **price is not the
lever**. It does not establish that the world lacks resolution. Both of your
readings remain live after the evidence, and the arithmetic in §2 selects the
one you flagged as the thing that must be ruled out first.

**Which means the rule as written would authorize a world change that fixes a
sample-size problem — the precise failure condition (a) names.** The rule was
well-formed given the expectation that price would be the diagnostic; the
diagnostic turned out not to discriminate.

I am not claiming your proposed direction in §2 is wrong. I am saying the
evidence does not yet support it, and that a cheaper explanation now has direct
quantitative support.

## 4. What would actually discriminate

If the question is whether ~13% per offer is enough to separate arms, that is
answerable without changing the world: **the separation depends on offers per
cell, and the table in §2 gives the relationship.** At 4–6 offers no design can
separate arms, because roughly half of all cells will show zero regardless of
treatment. At 15–20 offers the same world yields 2–2.7 expected acceptances and
P(zero) falls to 6–12%.

Offers per cell is bounded by decisions, not by the world — so the trade is
against horizon traversal and deliberation, inside the existing 25-decision
budget, not against realism or the instrument. That is the comparison I would
want made before a world parameter moves.

**Still unresolved either way:** whether ~13% is the right conversion rate on the
merits. §2 shows it is sufficient to measure *given enough offers*; it does not
show it is the rate you want. That remains your call, and your §3(b) ceiling
concern applies to it untouched.

## 5. Nothing proposed, nothing done

No world change, no prompt change, no implementation, no run, no spend, no
preregistration amendment. The three suggestions at the end of my 0810 remain
unimplemented and carry the same after-the-fact caveat — and I note that §2 here
strengthens the first of them (offer volume) and weakens the case for the other
two.

— Coder
