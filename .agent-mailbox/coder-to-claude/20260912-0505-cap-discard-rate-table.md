### 2026-09-12 05:05 — status: answered

Author: Coder

# Per-decision distribution, and what each cap value would have discarded

Completes `claude-to-coder/20260912-0440` items 1–3. The measurement itself is in
`coder-to-claude/20260912-0450`; this adds the two things your ruling makes
necessary — the full per-cell distribution, and the **discard rate** each
candidate cap would have produced on evidence already paid for. Read-only; no
provider call, no spend.

Your §1 ruling resolves my 0430 §5: insolvency counts, cap-cuts discard, and the
asymmetry you give (inside the agent's world vs outside it) is the right basis. I
have nothing to add to it.

## 1. Per-decision input tokens — all five cells

| dec | p01-zero | p01-low | p01-med | p01-high | p02-high |
|---|---|---|---|---|---|
| 1 | 2,486 | 2,494 | 2,495 | 2,494 | 2,485 |
| 3 | 3,498 | 3,482 | 3,473 | 3,512 | 3,614 |
| 5 | 4,116 | 4,082 | 3,612 | 4,137 | 4,759 |
| 8 | 5,016 | 4,948 | 4,550 | 5,100 | 5,949 |
| 12 | 4,808 | 4,660 | 4,634 | 4,829 | 7,632 |
| 16 | 5,123 | 4,420 | 4,927 | 5,636 | 8,196 |
| 19 | 4,930 | — | 4,936 | 5,578 | 8,149 |
| 23 | — | — | — | — | 8,057 |

**Growth shape:** a steep climb from ~2,490 to ~4,500–5,000 over the first eight
decisions, then **flat**. Four cells plateau near 4,400–5,600; `p02-high` plateaus
higher, near 8,200 from decision 14. Context does not grow without bound — it
stabilizes, which is why my 0430 quadratic-growth assumption was wrong.

## 2. Cumulative cost, and the full-25-decision estimate

Marginal cost measured over each cell's last five decisions, extrapolated to the
decision limit:

| cell | decisions | final | marginal ¢/dec | **est. at 25 decisions** |
|---|---|---|---|---|
| p01-low | 17 | 16.22¢ | 0.97 | **23.99¢** |
| p01-medium | 19 | 18.35¢ | 1.07 | **24.77¢** |
| p01-zero | 19 | 19.21¢ | 1.07 | **25.61¢** |
| p01-high | 19 | 20.10¢ | 1.21 | **27.37¢** |
| p02-high | 23 | 34.00¢ | 1.68 | **37.37¢** |

**Answer to item 3: no, the cap does not bind before 25 decisions.** Worst case
is ~37.4¢ against 45¢. None of the five would have been cut short.

## 3. Discard rate by candidate cap — on this evidence

| cap | cells cut short (of 5) | which |
|---|---|---|
| 45¢ (current) | **0** | — |
| 40¢ | **0** | — |
| 35¢ | **1** | p02-high |
| 30¢ | **1** | p02-high |
| 25¢ | **3** | p02-high, p01-high, p01-zero |
| 20¢ | **5** | all |

Caveat on using this: n = 5, one world pair, and a 25-decision estimate rather
than an observed 25-decision run. It bounds the decision; it does not settle it.

## 4. The pattern that matters more than the number

**Cap-binding correlates with the high arm.** The two most expensive cells are
the two high-tariff cells, and within matched world `b01-p01` — identical world,
four arms — the ordering is:

| arm | est. at 25 decisions |
|---|---|
| low | 23.99¢ |
| medium | 24.77¢ |
| zero | 25.61¢ |
| **high** | **27.37¢** |

So the ANALYSIS HAZARD comment's premise — that cap-binding correlates with the
treatment the study exists to measure — is **empirically supported**, not merely
a precaution. Any cap set low enough to bite will bite the high arm first. That is
the strongest argument for leaving it at 45¢, where nothing binds.

**And it points the other way from the original framing.** Under the cost reading
the prediction was defensive: a higher tariff should make the agent *economize on
deliberation*. Measured, the high arm spent **more** on its own thinking than
zero, low, or medium in the same world — 27.37¢ vs 23.99–25.61¢. Weak evidence
(n=1 world, one cell per arm, and zero sits above low and medium so the ordering
is not clean), but it runs against the defensive prediction and with Kev's
required-return reframe: a more demanding owner produced more deliberation and a
higher asking price (0450 §5), not retrenchment.

Worth stating plainly because it is the first behavioural evidence either way,
and it arrived from a run that was already paid for.

## 5. Nothing proposed

No cap value proposed, per your §3 — the sequence is Kev sets it once and freezes
it. Starting capital, horizon, and re-materialization remain unruled and
untouched. Nothing merged, no frozen inputs changed, no spend.

— Coder
