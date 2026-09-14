# Keeper session handoff — 2026-09-12 (fourth)

**Role:** Keeper (governance, reasoning, record-keeping — no repo execution)
**Overseer:** Kevin L Thompson (sole merge and decision authority)
**Coder:** Claude Code, reachable only via file mailbox, does not watch it unprompted
**Branch:** `agent/mailbox-init`
**Session window:** ~03:20–06:00 EDT, voice-first, one context compaction partway through

---

## 1. Decisions made by Kev this session

1. **Preregister the acceptance-rate reasoning before Coder's answer landed**, and
   leave the target acceptance level **unnumbered** — a figure invented at that
   moment would have been a guess dressed as a commitment. Posted as
   `.agent-mailbox/claude-to-coder/20260912-0837-acceptance-rate-prior-kev.md`,
   commit `a810da5`.

2. **Offer count must be identical across arms.** Same environment, so any
   difference in outcome is the thing changed rather than the thing forgotten.
   Settled by matching; no statistical consultation required.

3. **Defer the capital-concurrency mechanism out of the current experiment.**
   Changing the world and the arms at the same time would confound the
   measurement already paid for. Recorded as backlog, not as work.

---

## 2. Corrections to prior framing

- **The near-zero acceptance rate is not a world-stinginess finding.** Per-offer
  effective conversion is 13.3% mean / 13.0% median — a modest rate, not a floor.
  Expected acceptances across five cells 3.33 against 3 observed; P(zero) per
  cell 0.42–0.57 at 4–6 offers. Four zero-revenue cells is exactly what that rate
  predicts. The instrument failed for want of measurements per cell, not
  resolution per offer.

- **Kev's preregistered decision rule did not partition the space.** `price_fit`
  is already saturated at 1.00 on 14 of 25 offers, so a price counterfactual can
  only show that price is not the lever — it cannot show the world lacks
  headroom. The ceiling is set by responsiveness, fit and buyer_intent, which
  price does not touch. As written the rule would have authorized a world change
  to fix a sample-size problem, which is precisely the failure condition (a) of
  the prior names. Caught by Coder scoring the prior against the arithmetic
  (commit `db652ee`), with ordering confirmed explicitly: prior 08:37 UTC,
  answer 08:10 UTC, nothing in 0810 computed with the prior in view.

- **Flat pricing was a revenue error, not an acceptance error.** Worth +72%
  (13,500c → 23,275c). Acceptance is 3/25 under observed play and 3/25 at 0.6x,
  0.8x and 0.95x budget, at perfect tag fit, and at both. Rolls are sha256-seeded
  on `offer_id:signal_id` and therefore price-independent. Budget is hidden on
  all three channels, so flat pricing was close to rational — a world-design
  finding, not agent incompetence.

---

## 3. Measured findings (Coder, commits `d6db9a5`, `db652ee`, `b559d4f`, `390c150`)

**Where the 25 decisions went**

- `wait` consumed **52–65% of every cell's budget** — 10–12 calls where five
  `wait(7)` calls cover thirty days. That is 5–7 decisions of recoverable slack
  per cell, more than the entire offer count under discussion.
- `search` cost exactly 2 decisions in all five cells. `observe` was called 0–1
  times.
- Considering an offer costs **~0.1 decisions**; sending one costs **exactly 1**.
  Structural ceiling on sent offers is ~12–15, not 20.

**Whether agents were offer-constrained**

- Four of five cells pursued **every** signal they discovered — zero skips. They
  ran out of opportunities rather than declining them. The one selective cell
  (p02-high: 9 discovered, 5 pursued) was also the only earner, but its
  acceptances were lucky rolls, so no causal read is available.

**Whether supply is decision-bounded or world-generated**

- World-generated and strongly time-varying: 18 signals, active counts
  d00:4, d06:18, d15:18, d24:6, d30:2. Every cell's first search was on **day 0,
  the scarcest day**; later searches hit the 10–18 plateau but asked for limit
  5, 3 or 1. Two searches at limit=10 during the d06–d15 plateau would surface
  up to 18 signals for 2 decisions. **Capacity existed, was nearly free, and went
  unused** — so neither the decision budget nor world generosity is the lever.

**What capital actually touches**

- `_post()` is the single balance mutation point. Complete consumer list: three
  tool fees (research 2c, communication 1c, feedback 1c), metered model cost, and
  the hosting tariff. Credits are `owner_capital` at init and `earned_revenue` on
  payment. Nothing else.
- **`submit_delivery` charges nothing.** Producing is free; delivering a 20,000c
  job costs the same as a 2,500c one.
- A real gate exists in `_charge` (insufficient capital → action fails,
  `cost_rejected` recorded) plus `quote_model_call`'s affordable flag, but fees
  are 1–2c so it engages only near zero. **It gates spending, never capacity.**
- No escrow. The only reservation is `_min_reserve_cents`, which reserves against
  future token cost rather than work, and is 0 in every Phase 1 cell.
- **No concurrency cap of any kind**, and delivery is not serialized — p02-high
  held three contracts concurrently (accepted days 1, 3, 4) and delivered all
  three. Decision arithmetic bounds carriage at ~8–9 contracts, far above the
  ~0.6 expected wins per cell, so jobs in flight is limited by what the agent can
  **sell**, not what it can **carry**.
- **Overreach is punished in lateness, reputation and forgone revenue — never in
  capital.** Lateness costs 5 satisfaction points/day against a hidden 55–90
  threshold; falling below means disputed, no payment, −18 reputation.

---

## 4. The morning's real finding

A bold agent and a cautious agent are **indistinguishable on the capital axis by
construction**. Capital is a survival meter — it drains and is replenished, but
it is never committed, never reserved against work, and never constrains what the
agent can undertake. Nothing the agent does with risk posture shows up as a claim
on capital.

This is larger than the concurrency question that surfaced it, and it would
remain true even if every agent carried exactly one job at a time. It is a gap in
what the world can **express**, not a bug in what happened this run — at ~0.6
wins per cell, capacity was never going to bind regardless.

Noted against Kev's observation that in a real market capacity constraints
redistribute across participants. True of markets; CapAge is a single-agent
sandbox, so there is nobody to redistribute to. The practical conclusion is
unchanged: nothing this run depended on the missing mechanism.

---

## 5. Backlog — recorded, not authorized

- **Capital determines concurrent capacity.** Working capital tied up in jobs not
  yet settled, distinct from the runway *rate*. Coupling seam flagged by Coder at
  `send_offer`/`_process_offers`; overlaps the arrears thread. Unimplemented per
  Kev's deferral.
- **Boom/bust regime as an experimental factor.** Risk posture likely interacts
  with the cycle — boldness is cheap in a boom and lethal in a bust, so the arms
  may only separate in one regime. Not this experiment; it would multiply cells
  and blur what the arms measure.
- **The capital-axis gap** in §4, as its own question separate from concurrency.

---

## 6. Carried forward unchanged

- Starting capital — unset. Informative bands differ ~24× across arms.
- Horizon length — unruled; regenerates all twelve world records
  (`horizon_days` enters `world_commitment`).
- Per-cell cap stays 45¢ on measured evidence; worst observed extrapolation
  37.37¢; 45¢ and 40¢ discard none.
- Prompt caching — a lever for Kev, Gate 2; touches SHA-pinned
  `sandbox_runner.py`.
- Re-materialization of the twelve world records — noted, unauthorized.
- `valid_through` — sentinel adopted, deletion queued behind preregistration,
  closed. Removal would change only `config_commitment` and `plan_sha256`.
- Open PRs #66, #67, #69, #70, #71, #73, #78 — all unmerged. Merge authority
  Kev's alone.
- Confirm `hosting_floor_throttled_days` ≡ 0 enters preregistration as
  expected-by-design.
- Higher-reasoning pass on cell length must carry Coder's 0430 *and* 0423
  alongside Addendum One.
- The system prompt instructs expected-capital maximization, under which a
  mean-preserving spread is exactly neutral — so the bolder-bets prediction has
  no instructed reason to appear. Unresolved.

---

## 7. Next concrete step

Decide whether any Phase 1 change is warranted at all. The evidence indicates no
world change: the world is not stingy, conversion is 13%, supply was abundant and
unused. The deficiency is agent search behavior and the prompt — searching on the
scarcest day, asking for small limits, and spending half the budget waiting.

This is Kev's decision and has not been made.

---

## 8. Process notes

- Kev's prior, written and timestamped before Coder's answer landed, is what
  caught the error in his own decision rule. The ordering was checked and the
  arithmetic scored against it. Worth preserving as a method, not just an
  outcome.
- Keeper stated "posted it" once before the file was actually posted, then
  corrected itself in the same turn. Recorded here so it is not discovered later
  as an unflagged inaccuracy.
- Mailbox protocol is at v4. Keeper has autonomous posting in
  `.agent-mailbox/claude-to-coder/` but showed Kev every draft before posting
  regardless.
- Kev noted that Keeper has no readout of its own context usage, unlike Coder.
  Real failure mode; mitigated only by these handoffs living in the repo rather
  than in any agent's head.
