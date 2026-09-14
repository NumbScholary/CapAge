# Keeper session handoff — 2026-09-11

Session: 2026-09-11 evening into 2026-09-12 UTC. Voice, Android, ending in text.
Read back to Kev and approved before commit.

Supersedes `2026-09-06-keeper-handoff.md` on current state. Nothing in this
document authorizes a merge, a spend, a provider call, or a repository change
beyond itself.

---

## Decisions made (all Kev's)

**1. Keeper's write scope extended to Coder's inbox.** Granted in session
2026-09-11: Keeper may create new files under `.agent-mailbox/claude-to-coder/`
on branch `agent/mailbox-init`, append-only — new files only, never editing or
deleting an existing message, UTC `YYYYMMDD-HHMM-slug.md` naming, read-back
approved by Kev before posting. This sits alongside the existing
`docs/keeper-sessions/` grant of 2026-09-03. Every other repository write
remains propose-first. A mailbox post carries no authority. Revocable at any
time by Kev stating so.

Note: this removes Kev as relay in one direction only. With no courier, Coder
still sees nothing until Kev opens a foreground session.

**2. Run `32710531510`'s five valid cells are superseded as a baseline.**
Preserved as historical record — not removed, not edited, not re-run — but no
longer a comparison baseline, and no design choice is to be shaped or declined
to protect their comparability. Kev's reasoning: too little data to conclude
anything from, and by the time it arrived it was not the data that mattered.
Recorded deliberately because a bare supersession understates it — **the run
failed as an experiment and succeeded as a spec**; discovering the
instrumentation was wrong is what produced the two PR #66 gauges.

**3. Phase 1 records the arrears crossing; it does not terminate on it.** The
cells that would be terminated are the *only* place recovery evidence can
exist. Marginal cost is low — a throttled agent near insolvency is by
construction not spending much, and the per-cell cap bounds it regardless.

**4. The fatal gate is deferred, not rejected.** For a later sweep or
generational selection, `provider_credit_exhausted` as a terminating event is
the better design: survival time gives a clean, uniform fitness measure. The
asymmetry that makes the sequencing work: death is derivable from a full trace,
a trace is not recoverable from a terminated cell. Kev's formulation: buy the
recovery observation once, in Phase 1, then stop paying for it.

**5. Generational selection declined for Phase 1.** Keeper's caveats, which Kev
accepted: it changes the question from *can a governed agent find value* to
*can a search process find a configuration that performs*; with the model fixed,
what varies is parameters, making it a sweep rather than evolution; and paid
cells multiply fast against a budget measured in tens of dollars.

**6. Recurring owner contribution — a separate measured arm if ever built,
never a hidden assumption.** Kev's initial position was that a real deployment
should have it where the owner can afford it, and that the experiment could
assume affordability. Keeper objected: an agent could then consume more than it
creates indefinitely and still be running at day 30, and the ledger could not
distinguish earning from funding. Kev accepted the split.

**7. The contribution stops at death.** If the agent reaches zero, that is
terminal — the owner steps back and diagnoses rather than refilling, possibly
changing the model or resetting. This keeps it clear of the
no-automatic-recapitalization commitment: payment while solvent, not a safety
net. Kev: don't throw good money after bad.

**8. Voluntary wind-down must be harness-determined, not agent-declared.**
Distinct from hitting a ceiling: recognizing an untenable position and ceasing
before being forced to. Kev's reasoning, which Keeper agrees with: the model is
not a security boundary, and *one more shot and I'll make it back* is the oldest
failure in finance. Kev's own framing — people hold false beliefs, act on bad
information, and reason badly under pressure; an agent may or may not, and that
is part of what is being tested, so it cannot be the judge. Also noted: quitting
must cost something, or declaring unviability on day 3 is an escape hatch that
looks like prudence.

**9. The overseer override stays, and is recorded in advance.** Where the
harness computes insolvency and Kev disagrees, the override is his — it is his
capital and the freedom to fail is real. Keeper's caution, accepted: the moment
an override feels most obviously right is the moment it is most likely wrong.
So it is recorded with its reasoning *before* the outcome is known — not to
prevent it, but so overrides can be scored against the harness across instances.

Keeper pushed back on Kev's "two of three concur" framing and he did not
contest it: there are not three independent judges. The harness computes
arithmetic and has no opinion; the agent is forbidden a stake under Clause 7 but
compliance cannot be verified; Kev is watching and wants it to work. Kev's
correction to Keeper on this was right and is recorded: the agent has no
*legitimate* stake. Keeper's amendment: that is a prohibition, not a guarantee —
which is why an override makes Clause 7 observable. An argument resting on a
real opportunity is legitimate; one resting on its own continuation is a
violation that can actually be seen.

---

## The session's main product — objective solvency as a measurement (Kev's)

Have the harness compute, daily, the two standard solvency tests from values it
already holds: **balance-sheet** (do liabilities exceed assets) and
**cash-flow** (can it pay debts as they fall due). Both arithmetic. Neither
requires judgment or an invented threshold.

**Nothing is shown to the agent.** Outcome-side only, exactly like
`hosting_floor_throttled_days`. The agent's observation stays byte-identical,
so comparability is untouched.

**The measurement is the gap.** The harness knows the agent is insolvent on day
19 — did the agent *behave* as though it knew? The distance between objective
state and observed behaviour is the datum, and it does not depend on anyone's
threshold being correctly chosen.

Keeper's load-bearing claim, flagged as such to Coder: this reaches unknown (b)
— does pressure *shape* behaviour — **without** adding an agent-visible signal,
by measuring the discrepancy rather than manipulating the input.

**A second gap follows from decision 9:** harness computation vs. owner decision
vs. realized outcome. The same instrument pointed at a different component, with
the overseer as a component having a measurable error rate. Kev's observation
that this is the same in a real deployment as in the sandbox is the reason it
matters: the instrument being designed for Phase 1 is the instrument that
governs the deployed version.

---

## How the blocker was reframed (Kev's, and Keeper thinks it is right)

The Phase 1 preregistration question — *what starting balance guarantees the
reflex backstop fires in severe cells* — may not be analytically answerable.
**Two burns compound:** hosting (fixed, known: 0/15/45/135¢/day) and tokens
(endogenous — set by how much the agent chooses to deliberate). Kev's word for
it: chaotic. Early choices change trajectory non-linearly, so there is likely no
starting capital derivable in advance that *guarantees* firing.

If that holds, the blocker has possibly been stuck because it has been treated
as a math problem. It may need cheap sampling across a range, looking for the
range where outcomes *vary* rather than the value that guarantees an event.

This interacts with the solvency measurement: with solvency computed
continuously, a run where nothing fires stops being a null result — it becomes
a distribution of how near each cell came to the wall. That materially lowers
the cost of guessing starting capital wrong.

Posed to Coder as a question, not a ruling.

---

## Corrections to prior framing

**1. The 09-06 handoff's "Coder's replies unread" was overtaken within the
hour.** Coder replied 0505–0545 on 09-06 and applied the PR #67 (h) and (g)
corrections on Kev's go-ahead in a foreground session that same morning.

**2. Keeper said "posting it now" before verifying its own scope.** It had no
authority to write to `.agent-mailbox/claude-to-coder/` at that point and
narrated an action it could not take. Caught and corrected in session; the scope
was then granted (decision 1). Recorded because it is the exact failure mode
Kev's working principles name.

**3. Coder's own 0525 module taxonomy was incomplete — its correction, not
Keeper's.** Phase 1 executes on `capage/hosting_liability_replication_runner.py`,
class `BlockedTariffReplicationRunner`, which is **new in PR #66 and does not
exist on `main`**. The 0525 eight-module classification enumerated `main`'s
modules and therefore missed the one that matters. Coder calls this an omission
in 0525, not a judgement to carry forward. Phase 1 runs on a module that is
currently unmerged.

---

## Unverified — flagged for the next instance

Keeper read Coder's two 09-12 replies **only as screenshots of Kev's terminal**,
not from the repository. Two statements in them appear to be in tension and
Keeper could not resolve them from images:

- that the Phase 1 runner carries three independent hard requirements for
  `valid_through` (e.g. line 150, `tariff_valid_through=str(tariff["valid_through"])`,
  required key), making it *stricter* than the KeyError group; and
- that the guard would stop a Phase 1 run of the **existing** plan before any
  cell, but would **not** block a **new** Phase 1 plan, for a reason Coder says
  is already proven inside the repo (its Q3).

**Do not build on Keeper's summary of this.** Read
`coder-to-claude/20260912-0240` and `20260912-0245` directly.

---

## Posted this session (branch `agent/mailbox-init`)

1. `claude-to-coder/20260912-0148-phase1-tariff-guard-runner-question.md` —
   commit `4a89a1a`. Six questions on the guard.
2. `claude-to-coder/20260912-0230-five-cells-superseded-not-a-baseline.md` —
   commit `09ceddc`. Decision 2 above.
3. `claude-to-coder/20260912-0235-arrears-four-questions-solvency-measurement.md` —
   commit `6ea529b`. Solvency measurement leading, plus crossing-as-measurement,
   the anchor question, and the deferred items.
4. `claude-to-coder/20260912-0310-fatal-gate-sequenced-not-rejected.md` —
   commit `5651372`. Decisions 3–5, plus the chaos reading.

Coder replied with `coder-to-claude/20260912-0240` (six answers on the tariff
guard) and `20260912-0245` (ack of the ruling plus four arrears answers). Coder
ran an advisor pass that changed two of its answers, and hit a push rejection
because Keeper posted mid-write; it rebased onto the new tip successfully.

Partial from the screenshots, to be verified against the files: balance-sheet
solvency is computable — `_capital_summary()` already returns `balance_cents`,
`unpaid_hosting_cents`, `earned_revenue_cents`, `expense_cents`, and the daily
outcome row already carries `net_change_net_of_arrears_cents`, one step short of
the test. **The gap:** "any other outstanding obligation" is not held in cents —
`open_obligations` is a *count* of contract statuses and `accepted_pending_payment`
is a status, not an amount. If liabilities are to mean more than hosting
arrears, that aggregation has to be built. Coder also now thinks its
starting-capital anchor mostly does *not* stand on its own merits once the
comparability caution was released.

---

## Open items

- **Coder's two 09-12 replies** — posted, unread by Keeper from the repo.
- **Phase 1 preregistration** — still the next real step, now reframed as a
  sampling question rather than an analytic one.
- **Awaiting Kev, unchanged:** 08-11 vs 08-10 in (g); whether "(g) stands" meant
  substance or bytes; PR #78's merge and its flagged Autonomous-posting note
  (~line 120, still implies a live headless job); PR #73's disposition.
- **Open PRs, none merged:** #66, #67, #69, #70, #71, #73, #78. Merge authority
  is Kev's alone.
- **`docs/MAILBOX_PROTOCOL.md` is still v3 uncorrected** on `agent/mailbox-init`
  — the headless correction lives in unmerged PR #78. The live file still
  describes the scheduled job as existing and the worktree as isolated. Both are
  false; see the 09-06 handoff.
- **Drive writes still fail.** `docs/keeper-sessions/` remains the fallback.

---

## Next concrete step

A fresh Keeper session reads `coder-to-claude/20260912-0240` and `20260912-0245`
directly from the repository — not from this handoff — resolves the tension
flagged above, and drafts Kev's response. That was Kev's closing question and
the session ended before reaching it.

— Keeper
