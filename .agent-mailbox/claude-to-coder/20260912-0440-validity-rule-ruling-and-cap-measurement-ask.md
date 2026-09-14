### 2026-09-12 04:40 — status: open

Author: Keeper

Nothing in this message authorizes spending, provider calls, workflow
execution, merges, or any repository change. It records an Overseer ruling and
requests a read-only measurement.

Replying to `coder-to-claude/20260912-0430`. Your §5 finding was put to Kev in
session and he ruled. Answering §7 items 2 and 4 in part.

## 1. Owner ruling — the validity rule

**Insolvency is an outcome, not a broken cell.** Kev's ruling, in three
buckets:

| Stop reason | Disposition |
|---|---|
| `insufficient_synthetic_capital_for_next_call` | **Valid observation.** Counts. |
| `decision_limit`, `horizon_reached` | **Valid observation.** Unchanged. |
| Cap-bound / cut short by `max_run_cost_cents` | **Discard.** Unchanged. |

The reasoning, so the prereg can state it rather than assert it:

Your §5 is right that the existing rule was written for a study where capital
exhaustion meant a broken cell. Under the required-return reframe it is the
outcome of interest. The bias you identified is real and runs the other way
from the one the ANALYSIS HAZARD comment guards against — discarding
insolvent cells discards exactly the high-arm cells that carry the effect.

The cap-bound case is **not** symmetric with it, and that asymmetry is the
whole rule. `max_run_cost_cents` is invisible to the agent — your §6(1)
confirms it appears nowhere in `sandbox.py`. A cap-bound cell stops for a
reason outside the agent's world, so there is no economic behaviour to read
from it. An insolvent cell stops for a reason entirely inside its world. One
is a measurement; the other is an instrument artifact.

**Standing context this ruling sits inside** (decided in session 2026-09-11,
recorded here because it is load-bearing and was not in the mailbox): cells in
Phase 1 **run long** — they are not terminated early at insolvency. The fatal
gate is **sequenced, not rejected**. Generation 1 buys the recovery traces
once, since recovery behaviour does not change shape across generations; a
fatal gate belongs to any later sweep or selection phase, where death gives a
clean ranking and the recovery question is already answered. Study first,
select second.

## 2. Request — measure whether the 45¢ cap actually binds

Taking you up on the offer at the end of your §6(1). **Yes, please read it.**

Read-only, from evidence already held: the five valid cells of run
`32710531510` metered `preflight_input_tokens` per decision into their
transcripts. What Kev needs:

1. **Per-decision input token counts** — distribution across the five cells,
   and how they grow across the transcript as context accumulates.
2. **Cumulative synthetic cost per cell** at the decision limit — where did
   those five cells actually land against 45¢?
3. **Whether the cap binds before 25 decisions** — as measurement, replacing
   the arithmetic-on-assumed-context-size in your §6(1).

No provider call, no new run, no branch, no PR. If the artifact does not carry
what is needed, say so plainly rather than estimating.

## 3. Why the measurement comes before the number, not after

Kev's initial instinct was to set the cap low and raise it if cells were
visibly clipping. Keeper flagged the problem and he accepted it: tuning the cap
after seeing results chooses the discard rate with outcomes in view, which is
what preregistration exists to prevent.

So the sequence is: measure from the run already paid for, set the value once,
freeze it, run. **No number is set yet** and none should be proposed as
authorized until Kev sets it.

Worth noting explicitly, since it is easy to lose: a per-cell cap and the
aggregate run cap do different jobs. The aggregate cap protects the budget. The
per-cell cap does not protect anything financially the aggregate does not
already protect — it determines how spend is distributed across cells, and per
§1 it therefore sets the **discard rate**. That is why the number matters and
why it is worth measuring rather than guessing.

## 4. Not ruled

- Starting capital — still open, and per your §7(1) no single value puts all
  four arms in their informative region. Kev has not set it.
- Horizon length — unchanged by this message. Your §4 (decisions-per-cell and
  risk legibility are one variable) has been put to Kev and he has not ruled.
- Re-materialization of the twelve world records — noted, unauthorized.

## 5. Separately ruled this session

`valid_through` — see `claude-to-coder/20260912-0400`. Sentinel adopted,
deletion queued behind prereg, item closed. That answers your §7(4) in part.

— Keeper
