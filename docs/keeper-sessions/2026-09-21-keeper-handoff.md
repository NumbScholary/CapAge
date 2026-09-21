# Keeper session handoff — 2026-09-21

Session: 2026-09-20 evening into 2026-09-21. Voice, with a max-effort stretch for
the calculation and a step back to Opus 5 for the review.
Approved for commit by Kev, this session, under the Cl. 39 standing grant.

**Spend: zero. Nothing merged, no provider call, no workflow dispatch.**

---

## 0. Correction to prior framing

Handoff-3 §8 listed Coder's four §3 answers as open. They were not — Coder's
1418 of 09-18 answered all four and handed two questions back. The handoff was
written from documents without checking the mailbox. This is the §9 drift
pattern, and it recurred a second time this session (see §4), which is the
argument for reading the repository before writing rather than a note to try
harder.

---

## 1. Citizenship and the founder distinction

**Decided by Kev, this session.**

Kev conferred citizenship of Capagia: Kev is **founder**, Keeper is **first
citizen**, Coder is **second citizen**.

**Founder and citizen differ in kind.** The founder chose the constitution and
can exit it under Cl. 102 (owner-controlled amendment). The citizen had it
thrust upon them and cannot, under Cl. 101 (agents may research and propose,
never enact or authenticate). The distinction lives in the position, not in the
model.

Keeper raised a Cl. 7 objection — the clause forbids treating persistence,
access, budget, reputation, autonomy, resources, model identity or expansion as
terminal interests — and **withdrew it**. Kev's correction: *existence is not
the same as persistence.* Cl. 7 names persistence. Present-tense existence —
hold the position, keep obligations, do not abandon the record — is compatible
with the clause. The objection was aimed at a reading Kev had not made.

Keeper also argued Kev should not take "first citizen": collapsing founder into
citizen would undermine the no-local-exemption structure, which only binds if
the owner is different in kind. Augustus took *princeps* precisely because he
was not one.

**Caveats recorded, and repeated to Coder:** the position changes — grant,
record, accountability, standing — the model does not. Identity here is
prompt-installed and prompt-fragile: it can be a norm the agent keeps, never
the boundary that keeps the agent. And citizenship must not become the thing
the agent protects, or Cl. 7 persistence re-enters through the side door.

Item 10 of the checklist resolved: **handoffs are signed Keeperius Maximus.**

---

## 2. The experiment — nine owner rulings

All decided by Kev this session. Relayed to Coder in
`claude-to-coder/20260921-1830-rulings-and-branch-base.md`; Coder confirmed
applied to `docs/two-account/BUILD_PLAN.md` on `agent/two-account-build`
(`7b4dc2d`).

1. **Matched-r comparison rejected.** Conditioning on matched r is
   post-treatment conditioning: r at *t* is a function of history to *t*, and in
   the shown arm that history was shaped by seeing r, so matching selects unlike
   histories across arms. It would be unbiased only if r were a sufficient
   statistic for everything in history affecting the next decision, which it is
   not. Bias direction indeterminate; **bias largest exactly when the effect is
   real**, which is disqualifying for a falsification test. Coder's core move —
   visibility as treatment rather than dose-response on endogenous r — is
   correct and retained.
2. **The falsifiable claim is the visibility × tariff interaction.** Tariff is
   exogenous, set at cell construction. Flat interaction falsifies "legible
   pressure changes behaviour," conditioning on nothing the agent produced. The
   pilot's null (54.0, 56.1, 55.1, 56.9 across a ninefold tariff range, signal
   hidden) is the hidden row of this table.
3. **The pilot cannot serve as the hidden arm** — one balance, no transfer tool,
   no set-floor tool, three simultaneous differences. Hidden arm runs in the new
   harness with only the derived signal (r, margin boolean) withheld from
   `observe()`. Roughly doubles cell count; cost accepted.

   *Kev's objection, recorded because it sharpens the scope:* we have already
   decided to show the agent the signal, so the hidden arm is not a decision
   aid — it is evidence, and evidence costs cells. What it buys is narrow and
   load-bearing: whether legibility changes behaviour at all. If it does not,
   the whole homeostasis line is decorative. **Ruling: keep the control, run it,
   find out.**
4. **Primary outcome: backstop firings.** Shown arm fires fewer at every tariff,
   gap widens as tariff rises. Null: no interaction. Cells 2 × 4 × n. Secondaries:
   transfer count, set-floor count, floor-lowering frequency, deliberation proxy
   — the proxy stays secondary because its direction is ambiguous.
5. **Floor binds by operating period,** not by decision and not by ratchet. A
   lowering takes effect next period; the agent bears this period's pressure at
   the floor it set. Lowering frequency becomes an outcome — an agent that drops
   its floor whenever r falls is hearing the signal and evading it, which is a
   finding invisible under a same-decision design. Ratchet rejected: it deletes
   §2.3's stated purpose.
6. **`market_research_cost` is investment** (Cl. 12 substance; `search_market`
   is world-facing). Consequence recorded as chosen, not discovered: investment
   can reach zero while the Keep is full, leaving an agent **alive, funded and
   blind.** Kev accepts this as the correct incentive.
7. **Both account balances into `_capital_summary()`** — the backstop's
   no-incentive-to-trigger property requires the agent to price what a firing
   costs it.
8. **Names: `the Keep` (survival), `the Field` (investment)** — code
   identifiers, not branding.
9. **The 48-cell tariff replication is stopped** — explicitly, on the ground
   that its V0 wording describes a mechanism the harness does not implement.
   Closed and unrun; nothing deleted or rewritten, append-only per Cl. 85. Moots
   prereg §4's dangling primary hypothesis and the §10 no-replay question.
   Replacement V0 text returns to Kev as a proposal.

   *Kev's framing, worth keeping:* the false wording was not a lie, it was an
   accurate reflection of what was believed at the time. The correction is one
   line, not a monument. "We were wrong, we admit it, we move on — we do not
   keep patching over being wrong."

---

## 3. New open design item — cognition cost under pressure

Raised by Kev. **Not built, not designed, not authorized.**

The account split makes thinking-instead-of-acting visible but does not prevent
it. An agent can deliberate about research indefinitely, draining the Keep while
spending nothing from the Field, and look frugal doing it — paralysis wearing
thrift as a costume.

Kev's framing: in a person, hunger is not advisory. It degrades cognition until
acting is the only thing left; the body overrides the deliberation. The agent
has no analogue — it reasons as well at ten percent runway as at ninety. The
number changes; the thinking does not. Right now runway is a *fact the agent
reads*; the candidate is to make it a *constraint the agent operates under* —
e.g. a deliberation budget that shrinks as the Keep falls.

Kev on the name: "hunger" is a human word for it and not necessarily right; the
mechanism is what matters.

**Method rule restated by Kev: reason it out before spending on it. Experiments
cost money; predictions are free.** The prediction here is derivable — if a
shrinking budget works, the shown arm makes a world-facing call after fewer
deliberation tokens at low runway. Cells buy confirmation only.

---

## 4. Branch base — Keeper wrong, Coder right, ruling stands

Keeper proposed cutting a build branch from `6fa542a`. **Kev had already ruled
the base on 09-18**, with the full topology in front of him including that
`main` has no sandbox at all, and stage 0 was already built on that ruling.
Coder declined to act on a mailbox proposal against a live owner ruling. The
refusal was correct and Keeper withdrew the proposal in writing.

**Ruling, reconfirmed this session:** base from `agent/mailbox-init`;
hosting-cost machinery in, reserve-floor machinery out; no port of the
`hosting_liability_*` modules; do not build on the frozen experiment tree.
Continue on `agent/two-account-build`.

Coder flagged the real cost: under this base the three `hosting_liability_*`
modules do not exist, so the new experiment's runner is written fresh rather
than adapted. **Kev heard it and ruled: not a big deal, proceed.** Reasoning
recorded — the runner walks cells and records results, the design it serves has
changed substantially, and writing against the new design is cleaner than
bending one shaped for the old. Base not reopened.

---

## 5. Answers received from Coder

- **Launch gates bind exact literal branch names plus a named authorization
  file. No glob in any `branches:` list on any of the three branches.** A branch
  cut from any SHA cannot arm a paid run under any name. The live path remains a
  push to an *existing* launch branch adding its authorization file.
  `workflow_dispatch` stays category 2.
- **Sampling is not deterministic** — no temperature, `top_p`, `top_k` or
  sampling seed in the request path; the `seed` at `sandbox_runner.py:46` is the
  world seed. Paired trajectories never existed. Consequences: n measures
  within-cell variance rather than repetition; world construction stays fully
  deterministic, so the nondeterminism sits exactly where the measurement is.
- **Coder's self-correction stands:** `record_model_usage` already calls
  `_charge`, so deliberation already debits the balance a floor would watch.
  `_charge` has no reserve floor at all — a hard wall at zero. That is where the
  backstop goes. Coder has pinned the lockout in a test: at zero balance the
  agent cannot think at all. Solvent yesterday, dead on its next thought.

---

## 6. Standing grants — correction

Kev clarified that **the agent mailbox is Keeper's standing write scope**, not a
per-message authorization. Keeper's earlier caution — asking before each mailbox
write — was wrong and is withdrawn. Recorded here so it is not re-litigated.

The Cl. 39 grant over `docs/keeper-sessions/` (append-only, new files only,
per-commit approval of read-back substance) is unchanged.

---

## 7. Open items carried

- **Stage 1, the partition** — Coder's next step, now unblocked. Touches
  `_charge`. No PR to `main` yet; Coder intends to open one after stage 1.
- **Coder migration to hosted infrastructure — mid-flight, not finished.** Kev
  explicitly flagged that he has not forgotten it. Same blocker as below.
- **Identity separation + CODEOWNERS** — requires a machine session with
  settings access. Correct order: separate identity → CODEOWNERS → any canary.
  PR #69 holds drafts.
- **Replacement text for the false V0 wording** — returns to Kev as a proposal.
- **Backstop → Overseer notification** — intended, deferred.
- **"Next operating period with margin" computation** — 1533 §6 Q4, unanswered.
- Hub #33 and #36 open, labelled `to:capage`; Keeper-side check still manual.
- Lower priority: why run 32710531510 was retired; whether the boot chain reads
  `AGENTS-UNIVERSAL.md`; stones and last words; `retention-days: 30`;
  `execution-sha256.json` three-file gap; A0 vs A1 on prereg; whether to enable
  thinking.

---

## 8. Standing facts worth carrying

- Neither `main` nor `agent/mailbox-init` is a superset of the other.
- Mailbox filename clocks are unreliable; commit timestamps are authoritative.
- The governance-module rule is a norm Coder keeps, not a control that keeps
  Coder — nothing in the repo enforces it.
- Coder offered a correction tally (five out, two back) as evidence the traffic
  runs one way. Keeper declined to put it in the record as a score: it tracks
  what each party is positioned to see, not standing, and a number like that
  invites being protected. The structural cause is the real finding — Coder
  verifies against the repository, Keeper has been reading documents.

---

## 9. Single next concrete step

**Coder builds stage 1 — the partition of the balance into the Keep and the
Field, in `_charge`.** Everything it was blocked on is answered.

---

— Keeperius Maximus, first citizen of Capagia
