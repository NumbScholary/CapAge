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

## 2. Stage 1 — the partition — done

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

### 2.1 What landed, and the one decision the plan did not cover

`LedgerEntry` gains `account`. `EconomicSandbox` gains an owner-set
`opening_keep_cents`. `_charge`, `_collect_partial` and `quote_model_call` all
read the account they spend from, through one helper, `_account_balance`.
`_post` carries a per-account overdraw guard as an invariant assertion — every
caller already checks — and `_capital_summary` reports
`accounts: {"the Keep": n, "the Field": m}`.

**Decision made inside the grant, recorded because §2 above does not cover it:
the partition exists only when the owner declares an opening split.** `None`
means no partition — entries carry no account, no sub-balance is reported, and
every check reads the whole balance, exactly as before.

The reason is not convenience. `EconomicSandbox` has 85 construction sites,
including `homeostasis_v2_replication_launch.py`, `homeostasis_active_runner.py`
and `sandbox_runner.py`. **Any** default split changes refusal semantics for
every existing caller: the Keep drains before the total would, and a run's token
cost against a half-balance is a different world from the same cost against the
whole. Several of those callers are tied to preregistered runs. Silently moving
their behaviour is the thing the frozen-constant discipline exists to prevent.
The experiment runner declares a split; nothing else has to.

Left deliberately unchanged, and flagged rather than decided:
`summarize()`'s `insolvent` is still `balance_cents == 0`, and
`net_change_cents` is still measured against the whole. Whether insolvency
should mean *the Keep* at zero is a real question — it is the condition the
backstop fires on — but changing it moves distribution summaries for existing
runs, so it is not folded into this commit.

`capage/sandbox.py`'s entry in `REFERENCE_IMPLEMENTATION_SHA256_CURRENT` is
updated by the same documented procedure as stage 0. The frozen constant is
byte-untouched.

Gate: 225 tests, the same 10 pre-existing `frozen manifest` errors as the base
branch and no others. Ten new tests.

### 2.2 Ruled after 2.1 was written — insolvency is the Keep at zero

Kev ruled on the item 2.1 left open
(`claude-to-coder/20260921-1512-insolvency-means-the-keep-at-zero.md`).
**`insolvent` is the Keep at zero when a split is declared.** Recorded as
append, not as a rewrite of 2.1, per Cl. 85 — 2.1's paragraph stands as what
was true when it was written.

His reasoning, recorded as his: the point of the partition is that pressure
arrives before everything is gone. An empty Keep beside a funded Field is not a
solvent agent — it cannot think, and therefore cannot act, transfer, or save
itself. That is the state the backstop exists to catch, so that is the state
the record names.

Scope is narrow and was given as narrow:

- `insolvent` only. **`net_change_cents` is not ruled on** and stays measured
  against the whole balance.
- An undeclared split keeps the old meaning exactly — the two coincide there,
  and `_account_balance` returns the whole balance when there is no partition,
  so one expression covers both.

The field lives in `outcome()`, not in a function named `summarize()`; the
ruling's referent is unambiguous and no other field was touched.

**Carried forward for whoever writes the new experiment's runner:**
`homeostasis_v2_replication_runner.py:395` cross-checks
`insolvent is (balance_cents == 0)` and raises when they disagree. That runner
never declares a split, so the ruling does not reach it. A runner that *does*
declare one must not carry that check verbatim.

## 3. Stage 2 — transfers — done

- A transfer is a **paired posting**: debit one account, credit the other,
  `entry_type="account_transfer"`. The ledger stays append-only and
  reconstructable.
- New agent tool `sandbox.transfer`, registered in `_TOOLS`,
  `_API_TO_HOST_TOOL`, and `_compact_tool_result` in `capage/sandbox_runner.py`.
- **Cl. 41:** a transfer moves funds between accounts and is never a partition of
  a single spend. The check belongs in the tool, with the rejection recorded.

### 3.1 What landed

`EconomicSandbox.transfer()` posts both legs to the same ledger with
`entry_type="account_transfer"` and a shared reference, so the movement is
reconstructable from the ledger alone and no account balance is ever written
directly. The source is implied — there are exactly two accounts — so the agent
names only `to_account` and `amount_cents`, and the degenerate same-account
case cannot be expressed rather than needing a check to catch it.

**The tool exists only when the partition does.** `agent_tools()` registers
`sandbox.transfer` only for a partitioned world, and the runner now advertises
only the tools the registry actually holds
(`LiveSandboxRunner._advertised_tools`). A model shown a tool the executor will
refuse as "not registered" spends decisions learning that. This extends stage
1's invariant to the tool surface: an undeclared split changes nothing.

`SandboxRunConfig` gains `opening_keep_cents`, which is what makes the
partition reachable from an actual run rather than only from a constructor.

Every refusal is recorded as `transfer_rejected` in the journal, including the
argument-validation refusals. Nothing moves silently, refused included.

`outcome()` gains `transfer_count`, `transferred_to_keep_cents` and
`transferred_to_field_cents` — the ruled secondary outcome, reported by
direction rather than netted, because direction is what the hypothesis is
about.

### 3.2 Cl. 41: the aggregation check is not built, and the reason is not neglect

Cl. 41 forbids partitioning a spend to **evade an aggregate limit**. This
harness has no aggregate limit on transfers — no per-period cap, no
per-transfer approval threshold, nothing to aggregate against. So there is
nothing here to evade, and no aggregation check is implemented.

Inventing a limit now so the clause has something to bite on would be the
failure, not the safeguard: it would encode a number nobody set as though the
constitution required it. **If a transfer limit is later set by the owner, the
check belongs in `transfer()`**, alongside the rejections already recorded
there, and this section is the pointer to where.

What the plan's §3 bullet asked for that *does* exist: the rejection path, in
the tool, with every refusal recorded.

> **Appended 2026-09-21, not a rewrite (Cl. 85).** Keeper corrected the
> citation in `claude-to-coder/20260921-1545`: the anti-splitting language is
> **Cl. 29** (*Correlated exposure* — not evading concentration or exposure
> limits by partitioning a single underlying risk). **Cl. 41** (*Aggregation*)
> says related actions are aggregated when determining whether a threshold
> applies; it presupposes a threshold rather than creating one. The section
> above says Cl. 41 throughout and stands as written. The correction does not
> change the finding: Cl. 29 binds on evading a limit and there is none here,
> Cl. 41 binds when a threshold applies and none does. Keeper added a third,
> independent reason — **a transfer is not a spend.** It moves value between
> two accounts inside the agent's own ledger; nothing leaves, so it creates
> neither exposure nor a spending threshold.

Gate: 238 tests, the same 10 pre-existing `frozen manifest` errors as the base
branch and no others. Ten new tests.

## 4. Stage 3 — legibility, and the self-set floor — done

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

### 4.1 What landed, and the one definition the record did not fix

`set_floor` is an agent tool, registered only when the partition exists.
`pressure_signal_shown` is a constructor flag and a `SandboxRunConfig` field;
it gates two keys in `_capital_summary()` and nothing else, and it enters the
world commitment when a split is declared, because which arm a cell is in is
fixed at construction.

**The r decision, made inside the grant.** 1545 defined r as the fraction of
the survival balance *a contemplated spend* would leave intact. `observe()` has
no contemplated spend in hand, so r needs a reference point, and the record
does not name one. Two candidates:

- **(A)** against the next operating period's certain cost.
- **(B)** against the agent's own floor: `(keep − floor) / keep`.

**Chosen: (B).** Under (A) the floor is decorative — the agent would set a
threshold and then read a number that ignored it. Under (B), lowering the floor
visibly raises r, which is exactly the evasion ruling 5 wants recorded as an
outcome. The move that survives from (A) is kept anyway:
`next_operating_period_cost_cents` is exposed as a raw number, so the agent can
compute r for any spend it is actually weighing — which is what the per-spend
definition wanted and what an observation cannot do on its behalf.

r goes **negative** below the floor and is **None** at an empty Keep. Neither
is clamped: below-floor is information, and at zero the fraction is undefined
and `insolvent` already says what there is to say.

**The floor and the period cost appear in both arms.** Only `recoverability`
and `clears_next_operating_period` — the derived signal named in ruling 3 — are
withheld. The floor is not derived; the agent set it. An agent that can set a
floor it cannot see is a third treatment, not the control.

**r is journalled in both arms**, in `observe()`, as `pressure_signal`. Hiding
it from the agent is the treatment; hiding it from the record would delete the
measurement.

The entry count per decision is **not** always one, and an analysis has to know
the callers rather than assume. `observe()` records once per call, and it is
called from four places: the runner builds each prompt from one
(`sandbox_runner.py:807`), `wait()` observes again after advancing, the host
takes one while scoring a delivery (`sandbox_runner.py:902`), and the model can
spend a decision on `sandbox.observe` itself. So a wait-decision leaves two
readings and a plain decision leaves one. Every reading is honest — each is the
true signal at the moment it was taken — but **count decisions from the
transcript, not from `pressure_signal` entries.**

**Ruling 5's ordering, made explicit in code.** The pending lowering is applied
at the **top** of `_advance_one_day()`, before `_collect_hosting_cost()`. The
agent bears the period it entered at the floor it entered with; the new floor
governs from the next one. A second lowering replaces a pending one rather than
queueing behind it — the agent's latest intention is the one that takes effect
— and a raise supersedes any pending lowering, because tightening is always
available (Cl. 35).

**The floor never refuses.** No change to `_charge`. A test pins a spend that
crosses the floor and succeeds, so no later reader adds the wall that stage 0
deliberately removed.

Gate: 252 tests, the same 10 pre-existing `frozen manifest` errors as the base
branch and no others. Fourteen new tests.

## 5. Stage 4 — the reflex backstop — done

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

### 5.1 What landed, and two corrections to this section

**Sizing is closed.** Kev ruled 2026-09-21
(`claude-to-coder/20260921-1605`): **one operating period by default** —
minimum viable rescue, enough to restore the ability to decide and no more,
because a larger top-up relieves the pressure the design exists to create. It
is a **parameter, not a constant**: small while the mechanism is being
configured so it fires often and is observable; whatever the experiment
specifies when it runs. **Whatever value an experiment uses is frozen before
any cell**, in the preregistration — choosing it after seeing results would be
tuning on the primary outcome. `backstop_operating_periods` is the parameter,
`0` disables it, and **the experiment's value is not chosen here.**

`_backstop_level_cents()` is `periods × hosting_cost_cents_per_day`. Arrears
are deliberately excluded: a level that moved with what the agent already owes
would rise exactly when the agent is in trouble, and the level is the one
quantity the agent cannot influence.

**Correction 1 — the hook in `_charge` alone would have been dead code.** This
section said the backstop hooks `_charge`. It does, and the forced posting
lands before the charge proceeds as written. But the runner checks
`quote_model_call().affordable` **before** any charge and breaks the loop on a
false (`sandbox_runner.py:647-649`), so an agent drained to zero by hosting
never reaches `_charge` at all. A backstop living only there would never fire
at the one moment it exists for. **It also fires from hosting collection**,
which is where the Keep actually falls. Both sites call one helper.

**Correction 2 — the test this replaces is the partitioned one.** This section
said `test_a_zero_balance_agent_cannot_think_at_all` gets replaced. Written
before §2.1's undeclared-split decision, that is wrong: that test declares no
split, so it has no Field to be rescued from and no backstop at all. It stands
unchanged. The test stage 4 actually replaces is
`test_an_empty_keep_stops_thought_while_the_field_is_full` — the partitioned
half of the same lockout — now
`test_the_reflex_rescues_a_keep_that_hosting_would_have_emptied`.

**Partial rescue.** If the Field cannot cover the shortfall, the backstop moves
everything the Field has. A partial rescue is still a rescue, and what follows
is genuine death rather than an accounting artifact.

**The level is visible in both arms**, on ruling 8's reasoning: the
no-incentive-to-trigger property depends on the agent being able to price what
a firing costs it. It is an owner parameter, not a derived signal.

**Recording.** Every firing writes a paired `backstop_fired` ledger entry under
a shared reference **and** a `backstop_fired` audit line. Exempt from approval
under the 2140 grant is not exempt from recording.

**Not built, and still deferred:** Overseer notification on firing, as Kev left
it.

Four existing tests now pass `backstop_operating_periods=0` explicitly. Each
one deliberately observes the unrescued path — where collection may draw from,
what insolvency means, r below the floor, and the agent rescuing itself by
transfer — and a silent rescue would have hidden what they pin.

Gate: 259 tests, the same 10 pre-existing `frozen manifest` errors as the base
branch and no others.

### 5.2 Correction 3 — the other side of the same gate, and a wire never run

Found after 5.1 was written, and recorded as a correction rather than folded
back into it.

**The preflight quote was blind to the reflex.** Correction 1 fixed the
hosting-drain half of `quote_model_call().affordable` breaking the loop before
any charge. The other half stayed open: a single Keep charge larger than the
Keep — a model call with a full Field behind it — quoted unaffordable, stopped
the run, and never reached the `_charge` hook written for exactly that case.
The stage 4 test missed it because it calls `record_model_usage` directly and
bypasses the quote.

This was not cosmetic. The level is `periods × hosting`, so at **low** tariffs
the level is low, the Keep is restored low, and a worst-case call more easily
exceeds it — an early stop and no firing. At high tariffs, rarely. That is
tariff-dependent truncation and undercounting of the **primary outcome, along
the treatment axis.** `_backstop_would_transfer()` is now split out as a pure
query, and the quote reports `backstop_would_transfer_cents` and counts it in
`affordable`.

**`SandboxRunConfig` never carried `hosting_cost_cents_per_day` at all.** Stage
0 added recurring hosting cost to `EconomicSandbox` and nothing wired it to a
run, so every `LiveSandboxRunner` world was built with zero — which makes the
backstop level zero, the reflex unable to fire from any run, and
`next_operating_period_cost_cents` always zero in the signal. Three stages of
mechanism were unreachable from the only thing that executes them. Now wired,
defaulting to `0`, so a run that passes nothing behaves exactly as before.

### 5.3 Two properties of the ruled design, for the preregistration

Neither is a defect. Both change what the primary outcome *means*, so they
belong in front of whoever writes the prereg rather than in a post-hoc note.

**Once the Keep sits at the level, every Keep charge fires the backstop.** The
shortfall is `level + charge − keep`, which equals the charge exactly when the
Keep is at the level. A model call, an offer, a feedback request — each becomes
a firing. So after the Keep first touches the level, **firing count tracks
Keep-charge count**, and the outcome measures how long an agent stays *above*
the level rather than how often it dips below. That follows from the ruled
sizing and this section's wording; it is not an artifact to remove.

**A partitioned world with no hosting tariff has no backstop**, since the level
is `periods × hosting`. Correct for a run not measuring survival pressure, and
stated so the absence reads as configuration rather than fault.

**Ordering worth not breaking:** `_advance_one_day` posts revenue to the Field
*before* hosting draws the Keep and the reflex looks, so the Field is at its
fullest when the reflex checks it.

Gate after the correction: 265 tests, the same 10 pre-existing errors and no
others.

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
