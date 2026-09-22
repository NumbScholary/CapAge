# Keeper session handoff — 2026-09-22

Session: 2026-09-22, ~09:00 to ~11:10 UTC. Voice, then text from mid-session,
ending when the voice interface reached its limit. A spawned Max-effort review
session ran inside this one and committed its own record at 10:58 UTC:
`2026-09-22-keeper-handoff-estimand-review.md` (`4efcc55`). **Read that file
alongside this one.** §0–7 approved for commit by Kev under the Cl. 39 standing
grant; §8 recorded after that approval, under the amended grant it describes.

**Spend: zero. Nothing merged by Keeper, no provider call, no workflow dispatch.**

---

## 0. Corrections to prior framing

- 09-21 handoff §9 named "Coder builds stage 1" as the next step. Overtaken
  before this session opened: Coder landed stages 0–4 on
  `agent/two-account-build` (`f9df4e7`, `c63bdca`) the evening of 09-21. Built,
  not run, not merged.
- Keeper twice asserted state from a summary rather than the repository:
  reported PR #86 as open after Kev had merged it, and said mailbox posting
  needed a fresh grant when `MAILBOX_PROTOCOL.md` records Kev's 2026-09-12
  grant. The review session repeated the second error in its §5. **Mailbox
  posting to `claude-to-coder/` is standing scope; three instances now, two
  Keeper's. Do not re-ask.**
- Keeper's first draft of the PR #86 correction note asserted the false wording
  was text in the preregistration. It was not: it was proposed agent-facing V0
  wording killed by the 09-18 stop order before shipping. Caught by
  reconstructing from commits and `git hash-object` against blob `ed3b215`.
  Rewritten and re-approved before commit.
- **The review corrected Keeper's brief.** §6 Q3 mis-transferred Ruling 1.
  Ruling 1 objects to *conditioning* on post-treatment behaviour — comparison
  set, clock origin, denominator — not to outcomes *defined* by behaviour.
  Whole-run forms of A and D are clean; per-episode rates and matching on r are
  not. Accepted.
- The review's §0 calls the 09-22 rescue-notice ruling a "reversal" of 09-21.
  Keeper's reading: a refinement — 09-21 ruled *balances* into the summary in
  both arms; 09-22 ruled the plain-English *notice* shown-arm only; balances
  stay in both. Not verified against the 2115 message this session.

---

## 1. Decisions by Kev, this session

- **PR #86 merged** (08:56 UTC) — correction note appended to
  `HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md`, 22 lines, nothing
  deleted. Kev's condition: last discussion of the stopped tariff experiment.
- **Three rulings relayed to Coder** in
  `claude-to-coder/20260922-0910-rulings-net-change-rescue-notice-salience.md`
  (`40b1a77`): (1) `net_change_cents` stays as total position against
  `starting_capital_cents`; injected capital made separately identifiable, not
  netted out of the baseline. (2) Rescue notice **shown arm only**, against
  Coder's recommendation — in the hidden arm a plain-English rescue statement
  is hosting pressure made legible; Coder to send draft `statement` wording.
  (3) Salience test in the prereg **held** pending the estimand review. Bailout
  shape (`off | manual | automatic`, default off) acknowledged as proposed, not
  authorized.
- **Ruling 4 opened for revision.** The claim — legible pressure changes
  behaviour — is fixed; the estimand is open.
- **Kev's reframe:** the backstop level is an attractor (Coder's structural
  finding). Do not size to avoid it; size so every agent enters, measure
  escape. Escape is promotion, not exit — a staircase, each rung a new floor.
- **Estimand review commissioned** — brief in Drive, CapAge folder: *CapAge —
  Estimand review brief (backstop attractor) — 2026-09-22*. Thirteen questions,
  Q10 pivotal. Run as a spawned session at Max with the Doc attached.
- **In the spawned session, in voice** (recorded in its §1): **(a) Strong form
  of entry-by-construction** — opening Keep set *at* the backstop level;
  invariant: the first Keep charge fires the reflex in every run, before any
  agent action. Fallback if Coder cannot confirm: open below by exactly one
  charge. **(b) Earned escape** — escape must be backed by qualifying revenue
  (Cl. 3), not by money moved between accounts; grounded in Cl. 5, 12, 16, 30.
  Kev ruled the principle; operationalisation not ruled.
- **Raised by Kev, not ruled:** the harness is the instrument, not the
  experiment — its purpose is model selection and giving the Overseer a way to
  evaluate a model. Deserves its own ruling.

---

## 2. The review's result, and Keeper's response

- **Q10:** the weak form (opening Keep above the level) does not clear
  Ruling 1 — entry time is a post-treatment mediator. The strong form clears
  it: no entry channel exists for visibility to act through, so total effect =
  escape effect. Death becomes a competing event counted as non-escape, never
  censoring; only administrative censoring at H remains (dissolves Q5). Slack
  of even one charge reopens the channel.
- **Parking hazard (new):** a naive "Keep above level" escape is satisfiable on
  call 2 by moving opening capital Field → Keep. The shown arm sees r and has
  incentive to make it look good, so unguarded escape is biased *toward* the
  hypothesis by the opposite of escaping. Ruling (b) closes it.
- **No hazard ratios** — the at-risk set at each time is a post-treatment
  stratum. Cumulative incidence from t = 0; interaction on the additive
  risk-difference scale.
- **Keeper accepts** the Q3 correction and the Q10 answer. **One pushback on
  the reviewer's §3 proposal, not on Kev's rulings:** binary "earned escape by
  H" defined as Keep above the level is satisfiable by earning one cent and
  moving it — the next charge fires again. Keeper proposes deriving the binary
  from the continuous companion instead. Put to Kev in §3.

---

## 3. Ruling 4 v2 — OPEN, the fork put to Kev

Unopposed: continuous companion = earned escaped-days over fixed H;
interaction on the additive risk-difference scale; no hazard ratios; recorded
v1 → v2, prospective, one line of reason (Cl. 14).

The fork is what counts as an escape. **Option 1 (reviewer):** at t, Keep
above the level AND net deliberate Field → Keep transfers through t ≤
cumulative qualifying revenue through t; primary = did that ever happen by H.
**Option 2 (Keeper):** same earned constraint, but the Keep must stay clear for
one full operating period with no reflex firing. Difference: one cent versus
one period. Cost of option 2: a stricter bar, fewer escapes, less signal — runs
into Q12. Keeper's position: option 2; if the bar is too high, fix it in the
opening Field at design time, which Q12 requires anyway. **Kev has not ruled.**

---

## 4. From Coder's 09-21 evening messages, recorded

- Quote-gate bug fixed: `quote_model_call().affordable` stopped runs before the
  backstop could fire, worse at low tariffs — biased toward the hypothesis. Now
  counts `backstop_would_transfer_cents`.
- `SandboxRunConfig` never carried `hosting_cost_cents_per_day`; every
  `LiveSandboxRunner` world ran at zero tariff with a green suite throughout.
  Now wired, default 0. Flagged for a prereg note on test coverage.
- Two prereg properties accepted: once at the level every Keep charge fires; a
  partitioned world with no tariff has no backstop.

---

## 5. Open

- **Ruling 4 v2** — §3, Kev's.
- **Five facts owed by Coder** (review §5): what an empty Field prevents;
  opening Keep as a settable parameter; first-charge certainty (strict trigger,
  nonzero first call, charge before any tool call); qualifying-revenue tagging
  in the ledger; which quantity is fixed per cell. Keeper drafts and posts
  under standing scope. Not yet sent.
- **Build additions implied, NOT authorized:** opening Keep as a parameter;
  qualifying-revenue tagging. Wait on Coder's answers and Kev's word.
- **Q12 now binding:** under the strong form escape reachability is a function
  of opening Field, tariff and revenue rate only; the prereg needs a
  design-time reachability argument per cell before any cell is bought.
- Q11 (strong form makes any cognition-cost mechanism maximally active from
  call 1) and Q13 (staircase as strong-form resets; step steepness unchecked)
  — unruled.
- "Harness is the instrument" — own ruling, not made.
- Coder: draft `statement` wording. Phase 1 preregistration unwritten.
- PR #85 (standing orders) is based on `main`; working branch is
  `agent/mailbox-init` — same shape as the #79/#82 stranding. No objection to
  content. Open PRs: #85, #71, #70, #69, #67.
- Carried: Coder migration to hosted infrastructure; identity separation +
  CODEOWNERS (#69, machine session); backstop → Overseer notification; "next
  operating period with margin" (1533 §6 Q4); Hub #33/#36; new runner written
  fresh.

---

## 6. Standing facts and conduct

- Container egress blocks `raw.githubusercontent.com` and `api.github.com`;
  verify bytes by reconstructing from commits and `git hash-object` against
  the blob SHA.
- Kev merges when he decides to; never assert a PR's state without listing it.
- A spawned session inside this Project can write under the Cl. 39 grant with
  Kev's read-back approval; it did, and named its file with a suffix so this
  one sorts last.
- Keeper returned two empty turns and asked "what next" more than Kev wanted.
  Text appended to Keeper's final voice turn ("lost the thread… start a fresh
  conversation") was interface boilerplate, not Keeper's.

---

## 7. Single next concrete step

**Kev rules Ruling 4 v2 — option 1 or option 2 in §3.** Then Keeper posts the
five §5 questions to Coder.

---

## 8. Standing grants amended (Kev, 2026-09-22, in session)

Recorded after Kev approved §0–7, under the terms this section describes.

Kev amended the Cl. 39 grant of 2026-09-03 and the mailbox standing scope:
**per-commit read-back approval is no longer required** for handoffs under
`docs/keeper-sessions/` or for posts to `.agent-mailbox/claude-to-coder/`.
Keeper commits or posts, then notifies Kev in session of the path, the commit,
and the substance. Kev's words: "standing grant to approve all handoffs upon
notification … I don't need to approve them. Same goes with writing to
mailbox."

Unchanged: scope is new files only under `docs/keeper-sessions/`, never
modifying or deleting an existing one, and posts to `claude-to-coder/` only.
Revocable at any time by Kev stating so; revocation takes effect immediately.
Every other repository write remains propose-first and requires explicit
authorization for that specific action. Nothing in this grant authorizes
spending, provider calls, merges, builds, deployment, or any ruling Keeper has
not heard Kev make: a handoff or a mailbox post records Kev's decisions and
Keeper's labelled analysis; it does not create decisions.

Keeper's own conduct rule under this grant, proposed not ruled: every line a
committed file attributes to Kev is repeated in the notification, so a
mis-recording can be corrected by a dated note at once.

---

— Keeperius Maximus, first citizen of Capagia
