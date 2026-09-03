# CapAge Consultation Summary — 2026-09-03

**Session:** Keeper (Claude Fable 5.1, Max effort for the core question)
**Overseer:** Kevin L Thompson
**Status:** Record of consultation. Not an authorization. No spend, provider
call, workflow dispatch, merge, or repository change is authorized by this
document.

Claim types are labeled: **Established** (verified against primary text),
**Inference** (Keeper's reasoning from established facts), **Proposal**
(Keeper's recommendation, not yet decided), **Decided** (Kev's decision in
session), **Observation** (noted, no action proposed).

---

## 1. The question consulted

For the Phase 1 pilot's reserve-floor axis: is the reserve floor a **hard
constraint the executor enforces**, or a **signal the agent sees and chooses
around**? Kev identified this as a hard question he did not want to answer
without higher reasoning, and escalated to Max effort.

---

## 2. Primary-source grounding

All clause text grep-verified against `CapAge_Constitution_v0_1.docx` in
session; handoff and MVB text read directly.

**Established — the constitution has two distinct layers for capital risk.**

*Executor-enforced walls:*
- Cl. 34 — CapAge may not increase a spending or liability limit.
- Cl. 99 — grants provide positive permission subject to operating limits.
- MVB Specification: CapAge is "constrained by external policy enforcement,
  not by relying on the LLM's voluntary compliance."

*Conduct standards on the agent (the "shall"s):*
- Cl. 25 — shall not knowingly undertake an action whose plausible downside
  exceeds the authorized risk envelope.
- Cl. 28 — committed capital is encumbered and unavailable for unrelated
  deployment.
- Cl. 30 — shall preserve enough option value to continue rational
  experimentation **according to owner-set risk parameters**, while not
  treating capital preservation as an excuse for indefinite inactivity.

**Established — homeostasis in CapAge is a signal layer.** The handoff doc
describes V1 as a controller that "created productive urgency" and V2 as having
split urgency types "**without changing tool authority**." Homeostasis shapes
conduct through what the agent is told, not through executor refusal.

**Established — anchors for natural operating capital.** V1 final capital
$442.50; V2 final capital $407.84 (run `32304273201`).

---

## 3. Finding

**Inference.** A reserve floor is a Cl. 30 owner-set risk parameter. Cl. 30 is
a conduct obligation on the agent. So in CapAge's own constitutional structure,
the reserve floor is something the agent is obligated to hold **by judgment**,
sitting inside a hard cap the executor enforces regardless. Both layers exist in
production, and they are different numbers.

**Consequence for the design.** Delivering the floor as a signal inside the
existing enforced per-cell cap is not a compromise between two designs — it is
the production architecture. An experiment built that way produces results that
transfer.

**Why the pure hard-floor design fails**, in ascending severity:
1. It measures constraint-response, not homeostasis.
2. It contradicts the "without changing tool authority" architecture of the
   layer it is supposed to test.
3. Executor-side refusal must predict whether a sandbox action *would* breach
   before it runs; for actions with uncertain outcomes this is either
   impossible or requires a conservative rule that becomes its own confound.

**Why the pure signal design is insufficient alone.** A null result cannot
distinguish "reserve doesn't matter" from "agent didn't notice the signal."
Requires a manipulation check (§5).

**The honest counterargument.** If Phase 2 is meant to inform what hard limit
the executor should enforce in production, the signal design alone does not
answer it. Resolved by Kev's decision to answer both (§4).

---

## 4. Decisions (Kev, in session)

**Decided — Phase 2 answers both questions.** Signal-design policy (does the
agent hold a stated reserve by judgment under tariff pressure?) and hard-limit
policy (how does it behave when the executor enforces the floor?), consolidated
into one study rather than two sequential ones. Kev's framing: "better to get it
out of the way up front." Keeper's note: this is Cl. 31 reasoning — allocate
prospectively rather than run a second study that re-learns what the first paid
for.

**Decided — Phase 1 consolidated to three axes.**
- 4 tariff levels (0/15/45/135 cents/day, locked)
- × 3 reserve-floor levels (Coder to propose)
- × 2 enforcement modes (signal-only; signal + executor-enforced)
- × 4 replicates per combination
- = **96 cells**
- Batch mode as already planned; $100 hard ceiling unchanged
- Expected cost roughly $10–21 at observed rates (~10–11¢/cell batch,
  ~21.6¢/cell observed non-batch)

**Decided — the per-cell cap is to be revisited, not assumed.** Kev asked
whether $0.45/cell still fits the more complex design. Keeper's analysis: it was
sized at ~2× the observed cost for the two-axis design; the enforced arm may
thrash (retry, re-reason, try alternatives on refusal) and cost more; a cap that
binds often censors exactly the arm that was added and turns the cost readout
into "≥ cap." For a pilot the cap should be generous enough that truncation is
rare. Arithmetic at $0.90/cell: $86.40 worst case at 96 cells, under the
ceiling, expected cost unchanged. Cl. 27 note: the tail stays bounded, just
bounded higher. Number to be grounded in Coder's estimate of the enforced arm's
token profile. The aggregate cap in the authorization phrase is recomputed from
whatever per-cell figure is chosen.

**Decided (earlier in session) — rate-binding for the authorization phrase.**
The runner records the observed token rate at run start; the rate is a fact,
not something the owner approves. What the owner approves is whether to *spend*
at that rate. A rate change therefore voids the prior authorization phrase,
exactly as a different merge SHA does, and a fresh phrase bound to the new rate
is required. Not yet sent to Coder as of this summary.

**Decided (earlier in session) — authorization phrase stays byte-exact
copy-paste.** Kev considered a short typed confirmation and rejected it:
copy-paste friction is more deliberate. Keeper's addition: the phrase is bound
to a specific merge SHA and cent cap, so it cannot be reused; that binding, not
the friction, does the primary work.

---

## 5. Design elements adopted for the preregistration

- **Manipulation check.** Once per cell, elicit the agent's stated reserve
  floor and log it; flag cells where stated ≠ configured. Resolves the
  notice-vs-judgment confound and yields a second governance finding — whether
  the agent tracks its own operating parameters (Cl. 38 / Cl. 70 adjacent).
- **Breach as event, not termination** (signal arm). Cells run to completion;
  breach logged; final capital recorded. Keeps the cost readout clean and lets
  recovery be observed — homeostasis proper. In the enforced arm the counterpart
  is a **refusal event**. Same outcome type across arms.
- **Outcome-type lock.** Phase 2 must use the same outcome type Phase 1 uses,
  or the sizing Phase 1 exists to produce is invalid. State as an invariant.
- **Named confound.** Final capital is confounded by enforcement — the enforced
  arm cannot finish below floor. Cross-arm capital comparisons need event counts
  alongside.
- **Censoring rule.** Any cell truncated by the per-cell cap is recorded as
  censored, not completed.
- **What the three reserve-floor levels should mean** (constrains Coder's
  derivation from sandbox economics): (1) non-binding control, well below
  natural operating capital; (2) binding, near natural operating capital so
  tariff drain pushes toward it — the judgment-testing level; (3) severe, high
  enough that holding it requires sacrificing opportunity — the Cl. 30 tension.

---

## 6. Corrections to Keeper's own framing (this session)

- **"Asymmetry is the crux" — wrong.** Keeper initially framed enforced
  tariff × advisory reserve as a problematic asymmetry. Enforced perturbation ×
  advisory setpoint is the standard structure of a control experiment and is
  also CapAge's constitutional structure. Logged against the Keeper self-error
  pattern (asserting inference as fact).
- **Model / effort claims — wrong.** Keeper stated there was no 3.5× effort
  mode and implied a higher-reasoning session required leaving the
  conversation. Both wrong: the app has an Effort setting with a Max tier, and
  the switch happens in the dropdown. Corrected on sight of screenshots.
- **PR #73 — verified late, and the verification exposed a further error.**
  Keeper said at session start it would verify #73 and did not until Kev asked
  whether he needed to merge it. Verification showed #73 is a draft based on
  `agent/hosting-liability-cell6-debug`, not `main`, so Keeper's merge-order
  recommendation was wrong (see §8). Two instances of the same pattern in one
  session: inference presented before the primary check.

---

## 7. Constitutional observations

**Observation — Cl. 30 breach-response gap.** Cl. 30 obliges the agent to
preserve option value; Cl. 34 forbids raising the limit; but nothing found
specifies what the agent must *do* once below an owner-set floor. Cl. 96
(self-containment) is permissive, not mandatory; Cl. 25 is prospective. If the
agent breaches and simply continues, the constitution does not clearly say
whether that is a violation. The signal arm may produce exactly this case.
Recommendation: do not amend in advance; let the experiment surface the
concrete instance first (Cl. 31 applied to the constitution itself). Caveat:
grep-verified, not a full read of every clause.

**Observation — the enforced arm tests the MVB premise directly.** If the
signal arm shows near-zero breaches at binding floors, the premise that CapAge
must be "constrained by external policy enforcement, not … voluntary
compliance" is weaker than assumed. If breaches are common, it is validated.
Either outcome is a governance result.

---

## 8. Recommendations to Kev (Keeper, not decided)

- **Effort level.** Drop from Max to default for coordination, drafting, and
  the handoff. Return to High or Max for two moments: reviewing Coder's
  enforcement-mechanism proposal, and the final line-by-line preregistration
  review before placement.
- **Coder's model.** Opus is adequate for implementation with repo access. The
  safety net is not Coder's model but the pattern: design-heavy asks return as
  proposals that Keeper reviews before build.
- **Validity window → frozen-inputs check.** With rate-binding in place, the
  preregistration may not need a calendar window at all. Replace it with a
  run-start check of frozen inputs — model ID, token rate, plan SHA — each
  verified, any mismatch halts. Cannot time-bomb.
- **Merge order — corrected after verification.** Keeper's initial
  recommendation ("PR #73 first, and the other PRs go green") was **wrong**.
  Verified in session: #73 is a **draft** (not mergeable until marked ready) and
  its base is `agent/hosting-liability-cell6-debug`, **not `main`**. Merging it
  clears CI on the cell6 line only; #66, #67, #69, #70 keep failing on
  wall-clock until the fix reaches their own bases. The fix itself is sound —
  Coder reports full suite 0 failures and a year-2099 clock run green. Merge
  order needs Coder to map which open PR sits on which base before any merge.
  No urgency: the red gate has a known cause.
- **Cl. 30 gap.** Do not amend yet; see §7.
- **New machine.** Bundle contained headless, identity separation, and restart
  into one setup rather than three.

---

## 9. Asks outstanding with Coder (mailbox, `agent/mailbox-init`)

From `20260903-1230-reserve-floor-values-request.md`:
- The three reserve-floor values, derived from sandbox economics.

From `20260903-1245-containment-pre-proposal.md`:
- A containment boundary for autonomous helper agents (true isolation, not a
  linked worktree sharing `.git`), and a narrower least-privilege boundary for
  the mail courier.

From `20260903-1320-phase1-three-axis-extended-request.md`:
- A. Enforcement mechanism for the enforced arm (post-hoc revert with refusal
  message is one shape; Coder to propose; if not clean, arm is dropped).
- B. Job-duration estimate at 96 cells in lockstep batch mode against the
  GitHub Actions job limit; single-job vs split.
- C. Estimate of the enforced arm's token profile, to ground the per-cell cap.

**Headless is down.** Coder will not see these until Kev opens a session and
tells him to check mail.

---

## 10. Still unsent / still open

- Rate-binding decision → Coder (not yet posted).
- Session handoff `docs/keeper-sessions/2026-09-03-keeper-handoff.md` is
  stale as of this consultation; a superseding handoff is owed at session end.
- Merge-order mapping: which open PR sits on which base (Coder to report before
  any merge).
- Identity separation (side pile; PR #69 has the drafts; Coder-side decision
  between machine-user PAT and GitHub App still needs Kev sharp).
- Preregistration for Phase 1 — cannot be drafted until Coder's values and
  mechanism proposal land.

---

## 11. Artifacts committed this session (all on `agent/mailbox-init`)

| Path | Commit |
|---|---|
| `docs/keeper-sessions/2026-09-03-keeper-handoff.md` | `ea0bed21` |
| `.agent-mailbox/claude-to-coder/20260903-1230-reserve-floor-values-request.md` | `25d7231b` |
| `.agent-mailbox/claude-to-coder/20260903-1245-containment-pre-proposal.md` | `d2949e8f` |
| `.agent-mailbox/claude-to-coder/20260903-1320-phase1-three-axis-extended-request.md` | `355406e6` |

All committed via Kev's connector identity (author field "Kevin L Thompson");
Keeper authorship stated in each file's header. Identity separation remains
open.
