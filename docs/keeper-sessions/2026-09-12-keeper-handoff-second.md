---
date: 2026-09-12
author: Keeper (Claude, interface instance)
session: voice, continued from the 2026-09-12 handoff earlier the same night
approved_by: Kevin L Thompson, Overseer — read-back approved in session
---

# Keeper session handoff — 2026-09-12 (second, later)

## Status of this file

Append-only session record committed under the standing Keeper write grant
(Clause 39, granted 2026-09-03, scoped to new files under
`docs/keeper-sessions/` on `agent/mailbox-init`). Nothing in this file
authorizes spending, provider calls, workflow execution, further repository
changes, or real-world economic action.

Supersedes nothing. The earlier 2026-09-12 handoff (commit `5499d03`) stands;
this continues from it.

---

## 1. Decisions made — Kev's, this session

**`valid_through`: sentinel adopted, and the item is closed.** Not optional/
absent — a deliberate never-expires sentinel value. Outright deletion of the
field is **queued behind preregistration**, not done now, because it sits
inside the frozen cost policy and changing it would change the hash. Recorded
as **closed, not open**: a future instance encountering it should not reopen
it. Kev's stated reason for wanting it closed is that the question keeps
returning across sessions in different forms.

Posted: `claude-to-coder/20260912-0400-valid-through-sentinel-ruling.md`
(commit `63c5f91`).

**The validity rule — insolvency is an outcome, not a broken cell.** Ruling in
three buckets:

| Stop reason | Disposition |
|---|---|
| `insufficient_synthetic_capital_for_next_call` | **Valid observation** |
| `decision_limit`, `horizon_reached` | **Valid observation** (unchanged) |
| Cap-bound by `max_run_cost_cents` | **Discard** (unchanged) |

The asymmetry is the whole rule: the cap is invisible to the agent
(`max_run_cost_cents` appears nowhere in `sandbox.py`), so a cap-bound cell
stops for a reason outside the agent's world and carries no economic behaviour
to read. An insolvent cell stops for a reason entirely inside its world.

**Standing context restated and recorded** (decided 2026-09-11, retrieved from
the prior conversation this session because it is load-bearing and was not in
the mailbox): Phase 1 cells **run long** — not terminated early at insolvency.
The fatal gate is **sequenced, not rejected**. Generation 1 buys the recovery
traces once, since recovery behaviour does not change shape across
generations; a fatal gate belongs to a later sweep or selection phase, where
death gives a clean ranking and the recovery question is already answered.
Study first, select second.

**No cap value tuned after seeing results.** Kev's initial instinct was to set
the cap low and raise it if cells were visibly clipping. Keeper flagged that
this chooses the discard rate with outcomes in view — the thing preregistration
exists to prevent — and Kev accepted the correction. Sequence: measure from the
run already paid for, set once, freeze, run.

**Authorized**: Coder's read-only measurement of artifact `9514120954` from run
`32710531510`. No provider call, no new run.

Posted: `claude-to-coder/20260912-0440-validity-rule-ruling-and-cap-measurement-ask.md`
(commit `8bb8302`).

---

## 2. Corrections to prior framing — Coder's, all three self-corrections

Measured from artifact `9514120954`, five valid cells plus the p02-zero attempt
record. Posted in `coder-to-claude/20260912-0423` and `-0425`.

**(a) The 45¢ cap never bound.** All five cells stopped on `horizon_reached` at
17–34¢. Output is 110–160 tokens/decision, not the 1,024 assumed in the 0430
reply; input is ~97.5% of token cost and **plateaus** at ~8,200 tokens by
decision 8–14 rather than growing, so marginal cost settles near 1.7¢/decision.
Full-25-decision extrapolations: 23.99 / 24.77 / 25.61 / 27.37 / 37.37¢ —
worst case ~37.4¢ against 45¢.

Discard rate by candidate cap on this evidence: 45¢ and 40¢ discard none; 35¢
and 30¢ discard one; 25¢ discards three; 20¢ discards all five.

**No case for a budget increase.** ~22¢ mean × 48 cells ≈ 1,060¢ against the
2,160¢ cap.

**(b) The risk-learning objection to a shorter horizon was overstated.** Agents
front-load 8–10 decisions into days 0–2 and then coast, so a 10-day horizon
preserves most real activity. But the saving is 10–40%, not the ~67% a
days-proportional model predicts. The strong real-cost lever is **prompt
caching** (input dominates, none present) — byte-identical to the synthetic
economy, but it touches SHA-pinned `sandbox_runner.py`, so Gate 2 and Kev's
call. Not proposed, not authorized.

**(c) `unpaid_hosting_cents` = 0 in all five cells** — structurally zero, not
merely unrecorded. Confirms the 0300 §6 conjecture, which Coder had explicitly
declined to assert.

---

## 3. First behavioural evidence on the reframe — weak, and pointing Kev's way

In matched world b01-p01 the **high arm priced 8,000¢ while zero, low, and
medium all priced 4,500¢ identically**. Deliberation cost ordering in that
world: low 23.99 < medium 24.77 < zero 25.61 < high 27.37 — the high arm spent
**more** on thinking, not less.

Both run against the original cost reading's defensive prediction (economize
under pressure) and are directionally consistent with the required-return
reframe (clear a higher hurdle, price bolder).

[KEEPER — hold loosely] n=1 world; zero sits above low and medium, so the cost
ordering is not monotone; and the aggressive 8,000¢ price got **zero
acceptances**. Identical pricing across the three lower arms suggests the
contrast may be high-vs-rest rather than a four-point dose-response. This is
the first behavioural evidence either way, not a result.

---

## 4. The finding that outranks the capital question

**Four of five cells earned nothing** on 4–6 offers each. One cell earned
4,500¢ (2.25× a 2,000¢ capital). **One paid contract across twenty-five
offers.**

So the binding constraint on measuring risk posture is the **acceptance base
rate**, not starting capital and not the tariff.

Related, and possibly the cause: agents set **one flat price for every offer**
against customer budgets varying six-fold (2,500–20,000¢). That is not a risk
strategy; it is not noticing there is a decision to make.

[KEEPER — the question this raises] If acceptance is near zero regardless of
what the agent does, there is no safe-versus-bold choice to observe and the
reframe has nothing to measure. Whether the base rate is low because the
**world is hard** or because the **agent is playing badly** demands different
fixes, and nothing in the evidence yet separates them.

---

## 5. Carried forward, unchanged

- Starting capital — still unset. Per Coder's 0300 §2 the informative bands
  differ 24× across arms, so no single value puts all four in their
  informative region.
- Horizon length — unruled. Cheaper than previously thought (see 2b), still
  regenerates all twelve world records (`horizon_days` enters
  `world_commitment`, same as `starting_capital_cents`).
- Re-materialization of the twelve world records — noted, unauthorized.
- Prompt caching — a lever for Kev, not a proposal; Gate 2.
- Higher-reasoning pass on cell length: **must** carry Coder's 0430 and 0423
  alongside Addendum One. Given Addendum One alone, a stronger model's natural
  conclusion is "shorten the horizon, it's free," which was the objection
  Coder then partly retracted — the package needs both the objection and its
  correction.
- 08-11 vs 08-10 in (g); PR #78's merge and its Autonomous-posting note; PR
  #73's disposition. Open PRs #66, #67, #69, #70, #71, #73, #78 all unmerged.
  **Merge authority is Kev's alone.**
- Confirm `hosting_floor_throttled_days` ≡ 0 enters prereg as
  **expected-by-design**.

---

## 6. Single next concrete step

**Determine whether the near-zero acceptance base rate is the world being hard
or the agent playing it badly.** Starting capital, horizon length, the cap
value, and any higher-reasoning handoff are all downstream of that answer.

---

## 7. Protocol note

`MAILBOX_PROTOCOL.md` is at **v4** as of this date — Keeper autonomous posting
in its own outbound direction, plus a meta-protocol with a governance-plane
carve-out. Adopted earlier the same night (commit `32e1142`); recorded here
because the earlier 2026-09-12 handoff predates it and does not mention it.
