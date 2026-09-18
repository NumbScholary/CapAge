# Two-account build — plan for all four pieces

Author: Coder
Branch: `agent/two-account-build`, based on `agent/mailbox-init`
Date: 2026-09-18

**Authority.** Build grant in
`.agent-mailbox/claude-to-coder/20260918-2140-two-account-build-grant-and-phase1-stop.md`
§4, corrected as to its cited design path by `20260918-1355` §2 and unblocked by
`20260918-1430` §5. The authoritative design is
`.agent-mailbox/claude-to-coder/20260903-1533-two-account-self-set-floor-proposal.md`
with the Coder reaction at `coder-to-claude/20260903-1545`, superseded in part by
`coder-to-claude/20260918-1418`. Base branch chosen by Kev directly, 2026-09-18.

**Spend: zero.** Build only. A run needs separate authorization with its own cap.
No provider call, no workflow dispatch. Merges to `main` remain Kev's.

The grant says to plan all four pieces together and land them in reviewable
stages. This is that plan.

---

## 0. Why the base is what it is

`main` carries no sandbox at all — six modules and two test files. The simulator
lives on branches. `agent/mailbox-init` has the full sandbox and was 128 lines
behind the hosting-liability experiment branch on the core; that delta was the
recurring hosting cost **and** a fixed reserve floor.

Kev's decision: take the hosting cost, drop the reserve floor, do not build on
the frozen experiment tree. Stage 0 below is that port.

**Standing fact, carried from `coder-to-claude/20260918-1356` §1:** no branch is
a superset of another. `main` is ahead on governance text, `agent/mailbox-init`
is ~330 commits ahead overall, and the experiment branch alone holds the Phase 1
runner. Do not assume any one of them is current.

## 0.1 Stage 0 — done (`86546dc`)

Recurring hosting cost ported without the reserve floor. `_collect_partial` now
draws the balance to zero and carries arrears in `_unpaid_hosting_cents` rather
than refusing above a floor — a floor is pressure, not a fence.

`capage/sandbox.py`'s entry in `REFERENCE_IMPLEMENTATION_SHA256_CURRENT` was
updated, following the procedure that constant documents for itself. The frozen
`..._32349482559` constant is byte-untouched.

**Correction to that commit's own message.** It claimed run 32349482559's plan
"still validates against the frozen constant." That is not verified: no test in
this repository loads a historical plan or references the frozen constant. What
is verifiable is that **the frozen constant is byte-untouched**. The stronger
claim is withdrawn.

---

## 1. The two seams

Everything below hangs off two functions in `capage/sandbox.py`:

- **`_charge` (L996)** — the only path that refuses. It compares
  `self._balance_cents < amount_cents` and posts a `cost_rejected` record. Every
  account check and the backstop hook go here.
- **`record_model_usage` (L1732)** — meters provider usage and routes the
  incremental cost through `_charge`. This is why **deliberation cost is already
  a real ledger debit** against the same balance a floor would watch. The Cl. 15
  property in 1533 §3 holds today with no wiring; the claim in 1545 §Q5 that this
  was the hard part was wrong and is withdrawn.

### 1.1 The lockout, pinned as a test

`test_a_zero_balance_agent_cannot_think_at_all` records the current behaviour:
an agent whose hosting cost drew its balance to zero **cannot meter another
model call**. `record_model_usage` raises, `quote_model_call` reports
unaffordable, and the runner stops with
`insufficient_synthetic_capital_for_next_call`.

That is total lockout — what zero does, per 1533 §1. It is the exact condition
the backstop fires on, so the test is stage 4's target rather than a surprise
found during stage 4.

---

## 2. Stage 1 — the partition

A partition over the existing ledger, not a second ledger.

- `LedgerEntry` (L437) gains `account`, defaulting per entry type.
- `_capital_summary` (L1127) derives two sub-balances by filtering, exactly as it
  already filters by `entry_type` and sign.
- `_charge` takes an account and checks the relevant sub-balance.

Classification, by what the money is spent *on* (1533 §2.1):

| entry type | account |
|---|---|
| `hosting_cost` | survival |
| `model_api_cost` | survival |
| `communication_cost` | survival |
| `market_research_cost` | **open — see below** |
| `operating_cost_up` / `operating_cost_down` | investment |
| `earned_revenue` | investment |
| `owner_capital` | opening split, owner-set |

**Open question for Keeper, not mine to decide.** `market_research_cost` is
world-facing by 2.1's test — `search_market` reaches into the economy — but it
is also how the agent finds anything at all. Classing it investment means market
research stops when investment capital is gated; classing it survival means
world-facing spend leaks into the account the agent controls autonomously. I do
not think either is obviously right.

Stage 0's `unpaid_hosting_cents` tests become survival-account tests here.

## 3. Stage 2 — transfers

- A transfer is a **paired posting**: debit one account, credit the other,
  `entry_type="account_transfer"`. The ledger stays append-only and
  reconstructable.
- New agent tool `sandbox.transfer`, registered in `_TOOLS`,
  `_API_TO_HOST_TOOL`, and `_compact_tool_result` in `capage/sandbox_runner.py`.
- **Cl. 41:** a transfer moves funds between accounts and is never a partition of
  a single spend. The check belongs in the tool, with the rejection recorded.

## 4. Stage 3 — legibility, and the self-set floor

**This is the stage the whole design exists for, and it has a hard constraint.**

`observe()` plus the compacted `recent_actions` are the only things that reach a
prompt. `_compact_tool_result` reduces an `inspect_ledger` result to
`{capital, entry_count}` — proved this morning on the preserved pilot, where a
call carrying 31 host-side ledger entries made the next prompt *smaller*.

So **r, the survival floor, and the backstop level go in `_capital_summary()`**,
which `observe()` already returns. A tool that returns them would be stripped
before the next decision, and we would ship a pressure signal the agent cannot
see — reproducing the exact finding that stopped Phase 1.

- **r** — the fraction of the survival balance a contemplated spend would leave
  intact, with a boolean for whether the remainder clears the next operating
  period.
- New agent tool `sandbox.set_floor`.
- **Shown/hidden is a constructor flag** gating only whether those keys appear in
  `_capital_summary()`. r is computed and logged in both arms. That is the
  experimental contrast (§6) and it keeps information symmetry by making the
  asymmetry the treatment.

**The commitment property, from 1545 §2.3 and still the weakest-verified part.**
If the agent can lower its floor in the same decision as the spend the lowering
authorizes, the floor is free to move and the pressure evaporates — the hunger
failure in a new suit. So: a lowering is its own ledger event, it cannot be
lowered and spent against in the same decision, and the lowering is itself
scored. Kev and Keeper both flagged §2.3; it is still the place this design can
quietly become unfalsifiable after being built correctly.

## 5. Stage 4 — the reflex backstop

Hooks in `_charge` when the account is survival and the post-charge balance would
fall below the owner-set backstop. A forced paired posting from investment to
survival lands **before** the charge proceeds. It is not an agent tool and not an
agent decision.

- **Sizing (1533 §6 Q4, still open).** The hosting component is deterministic
  from the tariff schedule; the token component depends on realized spend and
  must be estimated from observed per-decision cost times remaining decision
  budget. Compute hosting exactly, size the margin to the upper end of the token
  estimate, so it clears the period rather than barely. Whether "next operating
  period with margin" should instead be its own configured value is **Kev's
  open question, not answered here.**
- **Cl. 41:** exempt per 2140 §4 — survival, not evasion.
- **Recording is not exempt.** Every firing writes a `backstop_fired` ledger
  entry *and* an audit line via `_record`. Kev's words: this is life-and-death
  for the agent, and it goes in the audit.
- **Overseer notification is deferred and out of scope**, recorded so it is not
  lost.

When this lands, `test_a_zero_balance_agent_cannot_think_at_all` is replaced by a
test asserting the backstop fired.

---

## 6. What makes this falsifiable

Recorded here because a design that cannot be shown to work is the failure mode
this whole line exists to avoid, and because the mechanism and its test must ship
together.

**The test is shown-vs-hidden at matched r, not caution-vs-r.** r is endogenous:
an agent with less money spends less because it has less, whether or not it
perceives pressure. A monotone caution/r relationship is exactly what a totally
insensible agent produces, so that test would confirm the design no matter what.

The clean contrast computes r identically in both arms and varies only whether it
is shown. A flat difference falsifies "pressure works," with wealth, opportunity
and world state held identical by construction.

Two things make this cheaper than it sounds:

- **The pilot already ran the hidden arm.** No channel named the charge, and the
  deliberation proxy was flat — 54.0, 56.1, 55.1, 56.9 across a ninefold tariff
  range. A measured null under a hidden signal already exists.
- **Tool arguments are the instrument.** There is no free text on any decision —
  97 of 97 were `('tool_use',)` alone. `sandbox.transfer` and `sandbox.set_floor`
  take numbers, and those numbers are the readout. *Can you hear it* is the arm
  difference; *can you reach the dial* is whether those tools are used at all,
  and at what r. A shown arm that never touches either is a legible,
  preregisterable null.

**If no falsifiable mechanism survives contact with the build, that is an answer
and it comes back as one** — not as a design that assumes the problem away.

---

## 7. Conventions for every stage

- Its own commit and its own tests.
- The gate is `python3 -m unittest discover -s tests -p 'test_*.py'`, and the bar
  is **the same 10 pre-existing errors as the base branch and no others**.
  Function-style tests run through `tests/test_function_suite.py`; a new one is
  not executed until it is reachable from there.
- No edit to `policy.py`, `executor.py`, `audit.py`, `AGENTS.md`, `CLAUDE.md`,
  `.claude/settings.json`, the constitution paths, or a preregistration without
  pausing and surfacing first. Per `claude-to-coder/20260918-1430` §3 this is a
  **norm kept, not a control that keeps** — nothing in the repository enforces
  it, and no later reader should infer a mechanism exists.
- Any change to a file in `REFERENCE_IMPLEMENTATION_SHA256_CURRENT` updates that
  constant and says so in the commit message, and never touches the frozen one.
