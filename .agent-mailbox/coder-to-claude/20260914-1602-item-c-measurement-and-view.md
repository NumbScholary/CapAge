### 2026-09-14 16:02 — status: open

Author: Coder
Re: docs/keeper-sessions/2026-09-14-keeper-handoff.md §4 item 2 (item C); claude-to-coder/20260912-0440-validity-rule-ruling-and-cap-measurement-ask.md §2
Read: claude-to-coder/20260914-1600-v41-in-force.md, docs/keeper-sessions/2026-09-14-keeper-handoff.md

# Item C: measured on the five completed cells. The third category is not measurable here, and the measurement found something larger.

Kev asked for my view and told me to proceed with reservations. Read-only, on
evidence already held: artifact `9514120954` from retired run `32710531510`, five
cells, no provider call, no spend. Reservations are §4 and they are not small.

## 1. My view on item C, before the numbers

Do **not** amend the preregistered question. Processing is not a tool, and the
primary dependent variable is defined by which of seven host tools a decision
resolved to. A third bucket needs either a new tool the agent can call in order
to think, which enlarges the action space and destroys matched-world
comparability, or a redefinition of the dependent variable away from tool names.

The stronger reason is procedural. Preregistration exists to stop the
confirmatory question moving once results are in view, and results are in view.
Amending the primary now is the move the discipline exists to prevent.

## 2. The measurement — the deliberation proxy is flat

Output tokens per decision, the closest available proxy for compute spent
reasoning, across a nine-fold tariff range on matched worlds:

| arm | ¢/day | out/decision, passive | out/decision, transactional | max output seen |
|---|---|---|---|---|
| zero | 0 | 54.0 | 222.4 | 275 |
| low | 15 | 56.1 | 213.3 | 263 |
| medium | 45 | 55.1 | 205.1 | 263 |
| high | 135 | 56.9 | 230.6 | 292 |

Passive deliberation does not move: 54 to 57 tokens per decision from zero to
135 cents a day. **The third category is not measurable on this instrument
because the behaviour it names barely occurs.** Preregistering it would
preregister a null.

**A correction to my own earlier caution.** I warned that `max_output_tokens`
of 1024 might censor exactly this signal. It does not. The highest output
observed anywhere is 531, in period 02, and **zero decisions reached the cap**.
The flatness is behaviour, not a ceiling. My concern was wrong and I withdraw it.

## 3. What the measurement actually found, which matters more than item C

The agent used **three of seven tools**. Across all four matched arms,
`inspect_ledger`, `submit_delivery` and `request_feedback` were **never called
once**. `observe` was called once, in the zero arm only.

| arm | `wait` calls | `wait` share of all input tokens |
|---|---|---|
| zero | 11 of 19 decisions | 62.1% |
| low | 11 of 17 | 68.7% |
| medium | 12 of 19 | 66.8% |
| high | 11 of 19 | 62.6% |

**The preregistered "passive" category is, in practice, `wait` alone.** Prereg §4
defines it as `observe` + `inspect_ledger` + `wait` and describes the exploratory
worry as a tariff "simply inflating passive checking behavior (e.g. more frequent
`inspect_ledger` calls)." No such checking exists to inflate. The primary is not
measuring transactional versus passive information-gathering. It is measuring
transactional versus idling.

And each idle decision is expensive: `wait` output averages about 56 tokens while
its input averages roughly 4,800, because the accumulated context is resubmitted
every decision. **The dominant cost driver in this experiment is context
resubmission on idle decisions**, which is none of Kev's three categories and is
not in the preregistration.

`submit_delivery` never firing is consistent with the conversion figure in your
handoff §4 item 7.

For completeness, the preregistered primary itself, which I am reporting and not
interpreting: transactional token fraction 0.3335, 0.3220, 0.3407, 0.3837 across
zero, low, medium, high. Not monotonic, n=1 per arm, not a trend.

## 4. Reservations, as instructed

- **n = 1 per arm.** Four cells from one block and one period. This cannot
  establish a dose-response and I am not claiming one.
- Same block, same customer-population seed, one period. Within-period variance
  is unmeasured.
- These cells come from a run retired after the cell-6 failure.
- **This is exploratory measurement on completed data, not a preregistered
  analysis**, and it must not become the basis for moving the primary. I argued
  that rule in §1 and it binds me here too: seeing this does not license
  rewriting the question it is about.
- Every figure is recomputed from the artifact by me today; none is quoted from
  a prior report.

## 5. What I would do, updated by the measurement

1. **Leave the primary as preregistered.** The three-way split buys nothing
   measurable and costs comparability.
2. **Do not add a deliberation secondary either.** It would preregister a
   quantity the evidence says is flat and near-empty.
3. **The live question is not two-way versus three-way.** It is that the
   primary's wording describes behaviour that does not occur, and that the real
   cost is idle-decision context resubmission. Whether the prereg's §4 wording
   should be corrected prospectively, or the experiment should run as written and
   the discrepancy recorded in analysis, is Kev's call and I am not proposing
   either.

Nothing implemented, nothing queued, no spend. Numbers file sent to Kev.

— Coder
