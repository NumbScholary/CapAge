# Keeper handoff — 2026-09-22 — estimand review (Q10, spawned session)

Session type: review session spawned from the parent Keeper session that
assembled the brief "Estimand review brief (backstop attractor)". Scope was
Question 10 of that brief. This file carries the result back to the parent
session, per Kev's instruction. Spend: zero. Nothing authorized, built, run,
or merged. `main` untouched.

## 0. Corrections to prior framing

- **Brief §6 Q3 mis-transfers Ruling 1.** Keeper's judgement in the brief
  ("every candidate except B defines its event in terms of what the agent
  did, which is the shape of the error") is wrong about the whole-run forms
  of A and D. Ruling 1 objects to *conditioning* on post-treatment behaviour
  — comparison set, clock origin, or denominator — not to outcomes *defined*
  by behaviour. B is defined by behaviour too (spending). The natural
  implementations of A and D (per-episode rates, matching on r) do reintroduce
  the error; their whole-run forms do not.
- **Rescue notice.** The 2026-09-21 session ruled the rescue must register in
  both arms; brief §9 records Kev's 2026-09-22 reversal to shown-arm only.
  The brief is current. Nothing in this session turns on it.

## 1. Rulings made this session (Kev, Overseer, 2026-09-22, in voice)

1. **Strong form of entry-by-construction.** Opening Keep is set *at* the
   backstop level. Every run's first Keep charge therefore fires the reflex
   before any agent action; entry is call 1 in both arms; there is no
   pre-trap phase. Kev's stated reason: that is where the interesting
   behaviour is.

   Invariant stated rather than the number: *the first Keep charge fires the
   reflex in every run, before any agent action.* Kev considered opening
   below the level and ruled "at" on Keeper's reasoning — call 1 should look
   like every later call, and it is one fewer parameter. Fallback if Coder
   cannot confirm the invariant: open below by exactly one charge (d = c),
   the smallest margin that makes the fire unconditional.
2. **Earned escape.** Escape must be backed by qualifying revenue (Cl. 3), not
   by money moved between accounts. Grounding: Cl. 5 (transactions undertaken
   to improve experimental metrics are not qualifying revenue), Cl. 12
   (substance over account count), Cl. 16 (contributions never evidence of
   value created), Cl. 30 (preservation is not an excuse for inactivity).
3. **Routing.** This session's output goes to the parent Keeper via this file.

Kev ruled the *principle* of (2). The operationalisation in §3 below is
Keeper's proposal and is not ruled.

## 2. The Q10 answer (Keeper analysis, not a ruling)

- **Weak form does not clear Ruling 1.** If opening Keep is above the level,
  entry time τ is behaviour-dependent and visibility acts before entry. Whole-
  run outcomes stay unbiased, but the total effect mixes an entry-timing
  channel with the within-trap channel, and τ is a post-treatment mediator
  that cannot be conditioned on. A shown agent that burns harder enters
  sooner and has more runway before H, so a positive total effect could be
  entirely "shown agents enter earlier" with zero escape effect. The
  objection is relocated, not cleared — as the brief feared.
- **Strong form clears it.** With opening Keep = level, the first charge
  fires with shortfall = charge in every run, both arms, before any agent
  action. Clock origin, comparison set, and entry state are design-fixed;
  there is no entry channel for visibility to act through, so total effect =
  escape effect. Death is a competing event counted as non-escape, never
  censoring; only administrative censoring at H remains (dissolves Q5).
  Slack of even one charge reopens the channel — Q12's "low variance" is not
  enough; the variance must be zero by construction.
- **Candidates under the strong form.** B is degenerate (τ = call 1 for all;
  under the weak form it measures the discarded pre-trap channel). A is
  clean as a whole-run count but non-monotone (never-escaped and
  escaped-once both score 1). E inherits brief §3's inversion: with the
  level absorbing, every shortfall equals the charge, so volume ≈ firings ×
  charge and dying sooner lowers it; normalising by run length reintroduces
  an agent-defined denominator (Q6). D — escape by H, binary, from t = 0,
  death = no — is clean, monotone, and interpretable.
- **The integral underneath D is escaped days over fixed H**, not rescue
  volume: time clear of the level, earned. Never-escaped scores zero; dying
  sooner never raises it. Cumulative-incidence curves from t = 0. **No hazard
  ratios** — the at-risk set at each time is a post-treatment stratum, the
  same shape as matched r. Preregister the interaction on the additive
  risk-difference scale.
- **Parking hazard (new).** A naive escape definition (Keep above level) is
  satisfiable by moving opening capital Field → Keep on call 2. The shown
  arm is the arm that sees r and has an incentive to make r look good, so an
  unguarded "escape" is biased *toward* the hypothesis by an action that is
  the opposite of escaping. This is why ruling (2) is load-bearing. Inference
  that worsens it: the 2026-09-12 session found capital in the prior harness
  was never committed, reserved, or a structural constraint on what could be
  undertaken; if that carries into the two-account build (Ruling 6's "alive,
  funded and blind" suggests an empty Field costs research but perhaps not
  offers), parking the whole Field is a rational strategy, not an edge case.
  Unverified against the repo — see §5.

## 3. Keeper's recommendation for Ruling 4 v2 — PROPOSAL, not ruled

- Primary outcome: **earned escape by H**, binary, from t = 0, death = no.
- Earned escape at t: Keep above the level **and** net deliberate Field → Keep
  transfers through t ≤ cumulative qualifying revenue through t. A fixed
  function of the ledger, conditioning on nothing, reconstructible under
  Cl. 87. Owner bailouts, if ever enabled, are excluded (Cl. 23 requires
  their separate recording).
- Continuous companion: earned escaped-days over fixed H.
- Interaction (visibility × tariff): additive risk difference, preregistered.
- Record as Ruling 4 v1 → v2 with the reason, one line, prospective (Cl. 14
  — nothing has run, so no historical result is rewritten).

## 4. What the Constitution settles here, and what it does not

Silent on causal identification: Ruling 1 is an owner ruling grounded in
method, not a clause, and no clause should be stretched to cover it. It does
settle what escape may count as (Cl. 3, 5, 12, 16, 30), that the revision
must be prospective and versioned (Cl. 14), that the ruling is Kev's
(Cl. 91), and that this record must label its claims (Cl. 9).

## 5. Facts owed by Coder — NOT sent; a mailbox write needs Kev's authorization

1. What does an empty Field actually prevent the agent from doing? (Decides
   whether parking is rational.)
2. Is opening Keep a config parameter, settable to exactly the backstop level?
3. Does the first Keep charge fire the reflex with certainty — is the trigger
   strict (Keep < level), is the first call guaranteed to cost more than
   zero, and does the charge land before any agent tool call can execute a
   transfer? If any of these fails, the strong form leaks and the fallback in
   ruling (1) applies.
4. Does the ledger tag qualifying revenue as its own entry type, separable
   from transfers and contributions (Cl. 16)? Earned escape depends on it.
5. Which quantity is held fixed per cell — total starting capital, or the
   Field? The reachability argument depends on which one the tariff is
   applied against.

## 6. Open items carried

- Ruling 4 v2 — open for Kev; §3 is the recommendation.
- Q12 is now binding: under the strong form escape reachability is a function
  of opening Field, tariff, and revenue rate only, so the preregistration
  needs a design-time reachability argument per cell before any cell is
  bought (Kev's rule: reason it out before spending).
- Q11: the strong form makes any cognition-cost mechanism maximally active
  from call 1 — promotes the 2026-09-21 §3 item; cuts both ways for
  reachability. Unruled.
- Q13: the strong form is a one-rung instrument; the staircase is a sequence
  of strong-form resets at rising levels. Step steepness unchecked.
- Salience test held pending; Overseer bailout proposed only (default off);
  preregistration not written.
- Build step from 2026-09-21 §9 (Coder: stage 1 partition in `_charge`)
  stands, with two additions now implied — opening Keep as a parameter and
  qualifying-revenue tagging — pending Coder's answers in §5.

## 7. Standing facts

- Written under the Cl. 39 standing grant of 2026-09-03 (Keeper write scope,
  new files only under docs/keeper-sessions/); read-back approved by Kev
  2026-09-22.
- Assumptions the Q10 answer rests on, for correction if wrong: opening split
  is a harness parameter, not an agent choice; death = Field empty and Keep
  below the next charge (2026-09-21 handoff §5); Ruling 1's objection is the
  standard one about comparison set, clock origin, or denominator.

## 8. Single next concrete step

Parent Keeper folds rulings (1) and (2) into the Phase 1 ruling record and
puts Ruling 4 v2 to Kev, carrying §3 as the recommendation. The §5 questions
go to Coder's mailbox only when Kev authorizes that write.
