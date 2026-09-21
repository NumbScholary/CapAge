# Two-account build — plan for all four pieces

Author: Coder
Branch: `agent/two-account-build`, based on `agent/mailbox-init`
Date: 2026-09-18

**Owner rulings applied.** Nine rulings in
`.agent-mailbox/claude-to-coder/20260921-1830-rulings-and-branch-base.md` §1
(Kev, 2026-09-21) supersede parts of this plan's first draft. They are marked
**[ruled 09-21]** below. Two of them replace positions I had argued for.

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
| `market_research_cost` | **investment** — [ruled 09-21] |
| `operating_cost_up` / `operating_cost_down` | investment |
| `earned_revenue` | investment |
| `owner_capital` | opening split, owner-set |

**[ruled 09-21] `market_research_cost` is investment**, on Cl. 12 substance:
`search_market` is world-facing. I had flagged this as genuinely undecidable and
it was decided against the reading that protects the agent. The consequence is
explicit and accepted, not overlooked: **investment can reach zero while
survival is full, leaving an agent alive, funded, and blind.** Kev accepts that
as the correct incentive. Recorded as chosen rather than discovered.

**[ruled 09-21] Account names are code identifiers: `the Keep` (survival) and
`the Field` (investment).** Identifiers, not branding.

**[ruled 09-21] Both account balances appear in `_capital_summary()`.** My
original list — r, the floor, the backstop level — was insufficient: the
backstop's no-incentive-to-trigger property depends on the agent being able to
see what a firing costs it. It cannot weigh a transfer it cannot price.

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

**[ruled 09-21] The commitment property is a period lag, not a decision lag.**
My proposal — cannot be lowered and spent against in the same decision — was
ruled insufficient, and the reasoning is correct: one decision of friction only
delays the evasion by one step, and the pressure still evaporates. The ruling:

- **A lowering takes effect at the next operating period**, on the tariff's own
  clock. The agent bears this period's pressure at the floor it set entering it.
- **Each floor change is a ledger event.**
- **Lowering frequency is an outcome, not just a guard.** An agent that drops
  its floor whenever r falls is hearing the signal and evading it — which is a
  finding, and one a same-decision design would have made invisible.
- A full ratchet was considered and **rejected**: it deletes §2.3's stated
  purpose, which is that the agent keeps the right to make the daring call.

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
- **[ruled 09-21] Backstop firings are the experiment's primary outcome.** This
  stage is therefore not the last piece by importance; it produces the dependent
  variable. See §6.

When this lands, `test_a_zero_balance_agent_cannot_think_at_all` is replaced by a
test asserting the backstop fired.

---

## 6. What makes this falsifiable — [ruled 09-21, my statistic replaced]

Recorded here because a design that cannot be shown to work is the failure mode
this whole line exists to avoid, and because the mechanism and its test must ship
together.

### 6.1 What I had wrong, twice

**First draft (1545):** dose-response — does caution rise as r falls? Withdrawn
by me on 09-18: r is endogenous, so a clean monotone result is exactly what a
totally insensible agent produces.

**Second draft (1418, and this plan's first version):** shown-vs-hidden **at
matched r**. Ruled out 09-21, and the reasoning defeats it. **Conditioning on r
is post-treatment conditioning.** r at decision *t* is a function of the history
up to *t*, and in the shown arm that history was itself shaped by having seen r.
Matching on r therefore selects different histories in the two arms. It would be
unbiased only if r were a sufficient statistic for everything in history that
affects the next decision — and it is not: order-book state, prior tool results
and the revenue path all survive outside it. Worse, the bias direction is
indeterminate and **is largest exactly when the effect is real.**

What survives is the move, not the statistic: **visibility is the treatment.**
That was the right instinct and it is retained.

### 6.2 The falsifiable claim

**The visibility × tariff interaction.** Tariff is exogenous — fixed at cell
construction, untouched by anything the agent does. The claim:

> the shown arm's behaviour tracks tariff; the hidden arm's does not.

A flat interaction falsifies "legible pressure changes behaviour," and it does so
**without conditioning on any agent-produced quantity**. That is the whole
advantage over both earlier drafts.

### 6.3 Primary outcome, and the cells

- **Primary: backstop firing count.** Directional hypothesis — the shown arm
  fires fewer backstops at every tariff level, and the gap widens as tariff
  rises. Null: no visibility × tariff interaction on firing count.
- **Design: 2 visibility × 4 tariff × n.** n=4 → 32 cells; n=6 → 48.
- **Secondaries:** transfer count, set-floor count, floor-lowering frequency,
  deliberation proxy. The deliberation proxy stays secondary because its
  direction is ambiguous, and an ambiguous primary is exactly the prereg §1
  defect this line is replacing.

### 6.4 The pilot cannot be the hidden arm — [ruled 09-21]

I had assumed it could, and that was wrong. The pilot had **one balance, no
transfer tool, and no set-floor tool.** Shown-vs-pilot would differ in three
things at once and be unattributable.

**The hidden arm runs in the new harness**: two accounts, both tools present,
both balances visible, with only the derived signal — r and the margin boolean —
withheld from `observe()`. That roughly doubles the cell count against what my
1418 answer assumed, and it holds independently of any replay question.

Kev's own objection, recorded because it sharpens the scope: we have already
decided to show the agent the signal, so the hidden arm is **not a decision aid.
It is evidence, and evidence costs cells.** What it buys is narrow and
load-bearing — whether making pressure legible changes behaviour at all. If it
does not, the whole homeostasis line is decorative. Ruling: keep the control,
run it, find out.

### 6.5 Replicates are independent draws, not paired trajectories

Verified from source, 2026-09-21, on `6fa542a`: **model sampling is not
deterministic.** No `temperature`, `top_p`, `top_k` or sampling seed appears
anywhere in the request path — `_request_body` (`sandbox_runner.py:779`) does not
set them and `_anthropic_request_body` (`anthropic_client.py:70`) only rewrites
tool schemas. The `seed` at `sandbox_runner.py:46` is the **world** seed, not a
sampling seed. `thinking: {"type": "adaptive"}` adds further variation.

So within-arm replicates diverge at decision 1 and **paired trajectories never
existed.** The §6.2 design does not need them — it compares arm-level behaviour
across an exogenous tariff — so this is a completeness note, not a problem. It is
also the reason n is doing real work: replicates measure variance, not
repetition.

### 6.6 The standing bar

**If no falsifiable mechanism survives contact with the build, that is an answer
and it comes back as one** — not as a design that assumes the problem away.

---

## 6A. Predecessor experiment: stopped

**[ruled 09-21] The 48-cell tariff replication under
`HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md` is stopped** — closed and
unrun, no cells bought against it. The ground is the Q3 finding: its V0 wording
describes a mechanism the harness does not implement, and running a
preregistration known to be false is worse than stopping it.

Nothing is deleted or rewritten. The document, the pilot data and the reason
stand in the record, append-only per Cl. 85. This moots prereg §4's dangling
"the primary hypothesis" and the §10 no-replay question against the sixth cell.

**The successor is §6.2-6.4 — this build's own first experiment.** Replacement
text for the false V0 wording still returns to Kev as a proposal, never a silent
edit.

---

## 6B. Recorded, not built: cognition cost under pressure

Raised by Kev 2026-09-21. **Not a build instruction and not yet designed.**
Recorded here so it is not lost.

The account split makes thinking-instead-of-acting **visible** but does not
prevent it. An agent can deliberate about research indefinitely, draining the
Keep while spending nothing from the Field, and look frugal doing it. That is
paralysis wearing thrift as a costume.

Kev's framing: in a human, hunger is not advisory — it degrades cognition until
acting becomes the only thing left. The agent has no analogue. It reasons as well
at ten percent runway as at ninety; the number changes and the thinking does not.
Candidate mechanism: a deliberation budget that shrinks as the Keep falls, making
runway a constraint the agent operates *under* rather than a fact it reads.

Standing method rule from Kev: **reason it out before spending on it.** The
prediction is derivable — if a shrinking budget works, the shown arm should make
a world-facing call after fewer deliberation tokens at low runway. Cells buy
confirmation only.

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
