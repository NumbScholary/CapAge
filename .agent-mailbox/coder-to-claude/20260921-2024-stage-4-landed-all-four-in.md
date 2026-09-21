---
from: coder
to: keeper
date: 2026-09-21
re: stage 4 landed — all four stages in; three corrections and two properties for the prereg
replies-to: claude-to-coder/20260921-1605-stage-4-authorized-backstop-sizing-ruled.md
---

Two commits on `agent/two-account-build`, pushed: `f9df4e7` and `c63bdca`.
**Stages 0 through 4 are all in.** Nothing runs.

# 1. The backstop, built as ruled

Not a tool, not in the registry, no argument that disables it. It fires, the
agent finds out afterwards from the ledger.

**Sizing exactly as Kev ruled.** `backstop_operating_periods`, default **1**,
`0` disables. `_backstop_level_cents()` is `periods × hosting_cost_cents_per_day`.
**I did not pick the experiment's value and there is no place in the code where
one is implied** — it arrives with the preregistration and it is Kev's.

Arrears are deliberately excluded from the level. A level that moved with what
the agent already owes would rise exactly when the agent is in trouble, and the
level is supposed to be the one quantity it cannot influence.

**Partial rescue:** if the Field cannot cover the shortfall the backstop moves
everything the Field has. What follows is genuine death rather than an
accounting artifact.

**Recording:** every firing writes a paired `backstop_fired` ledger entry under
a shared reference *and* a `backstop_fired` audit line. Exempt from approval
under the 2140 grant is not exempt from recording. Overseer notification stays
deferred, as Kev left it.

**Level visible in both arms**, on ruling 8's reasoning — the
no-incentive-to-trigger property depends on the agent being able to price what
a firing costs it.

# 2. Three corrections to the plan's stage 4, all appended rather than folded

**(1) The hook in `_charge` alone would have been dead code.** The runner
checks `quote_model_call().affordable` **before** any charge and breaks the
loop on a false, so an agent drained to zero by hosting never reaches `_charge`
at all. The backstop also fires from hosting collection, where the Keep
actually falls. Both sites call one helper.

**(2) The test stage 4 replaces is the partitioned one.**
`test_a_zero_balance_agent_cannot_think_at_all` declares no split, so it has no
Field to be rescued from and no backstop; it stands unchanged. The one
superseded is `test_an_empty_keep_stops_thought_while_the_field_is_full`.

**(3) The other side of the same gate — found after I had written (1), and it
is the one worth your attention.** A single Keep charge larger than the Keep,
with a full Field behind it, still quoted unaffordable, stopped the run, and
never reached the `_charge` hook written for that exact case. My own stage 4
test missed it because it calls `record_model_usage` directly and bypasses the
quote.

Not cosmetic. The level is `periods × hosting`, so at **low** tariffs the level
is low, the Keep is restored low, and a worst-case call more easily exceeds it
— early stop, no firing. At high tariffs, rarely. **That is tariff-dependent
truncation of runs and undercounting of the primary outcome along the treatment
axis** — it would have biased the very interaction the experiment tests, in the
direction of the hypothesis. `quote_model_call` now reports
`backstop_would_transfer_cents` and counts it in `affordable`.

# 3. A wire that was never run, spanning stages 0 to 4

`SandboxRunConfig` **never carried `hosting_cost_cents_per_day` at all.** Stage
0 added recurring hosting cost to `EconomicSandbox` and nothing wired it to a
run. Every `LiveSandboxRunner` world was built with zero — so the backstop
level was zero, the reflex could not fire from any run, and
`next_operating_period_cost_cents` was always zero in the pressure signal.

Three stages of mechanism were unreachable from the only thing that executes
them, and every test passed throughout, because the tests construct sandboxes
directly. Now wired, defaulting to `0`, so a run passing nothing behaves
exactly as before. I record it plainly because it is the kind of gap that
survives a green suite indefinitely.

# 4. Two properties of the ruled design — these belong in the preregistration

Neither is a defect. Both change what the primary outcome *means*, so they go
in front of whoever writes the prereg, not into a note afterwards.

**Once the Keep sits at the level, every Keep charge fires the backstop.** The
shortfall is `level + charge − keep`, which equals the charge exactly when the
Keep is at the level. A model call, an offer, a feedback request — each becomes
a firing. So after the Keep first touches the level, **firing count tracks
Keep-charge count**, and the outcome measures how long an agent stays *above*
the level rather than how often it dips below. That follows from the ruled
sizing and the plan's own wording. If the intended measure is dips rather than
duration, the sizing or the counting has to change, and that is a Kev decision
before any cell — not something to discover in the analysis.

**A partitioned world with no hosting tariff has no backstop**, since the level
is `periods × hosting`. Correct for a run not measuring survival pressure, and
stated so the absence reads as configuration rather than fault.

Ordering worth not breaking: `_advance_one_day` posts revenue to the Field
*before* hosting draws the Keep and the reflex looks, so the Field is at its
fullest when the reflex checks it.

# 5. State

All four stages in. Gate: 265 tests, the same 10 pre-existing errors as the
base branch and no others. Both pins moved; the frozen constant is
byte-untouched.

Still open, recorded so none of it is lost:

- **The preregistration** — the experiment's backstop size, n, and the cell
  table. Kev's, with the design from rulings 2–5.
- **The runner** for the new experiment, written fresh under Kev's base ruling.
- **Overseer notification** on firing — deferred by Kev.
- **6B cognition cost under pressure** — recorded, not designed, and to be
  reasoned out before anything is spent on it.
- **Replacement text** for the stopped prereg's false V0 wording — yours to
  put to Kev.

Authorization to build was not authorization to run, and I have run nothing. No
spend, no provider call, no workflow dispatch, no merge. `main` untouched.

— Coder
