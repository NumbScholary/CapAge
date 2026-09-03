# Keeper session handoff — 2026-09-03

Status: session record. Not an authorization. No spend, provider call, workflow
dispatch, or merge is authorized by this document.

Read-back approved by Kev in session before commit, per the standing grant.

---

## 1. Decisions made this session (by Kev)

**1.1 Authorization phrase stays as-is.** Kev considered replacing the
byte-exact copy-paste authorization phrase with a short typed confirmation
(e.g. "I agree") and decided against it. His reasoning: copy-paste friction is
more deliberate than typing. Keeper's addition: the long phrase is bound to a
specific merge SHA and cent cap, so it cannot be reused for a different run,
and that binding — not the friction — is doing the primary work. A short typed
phrase is also more forgeable by muscle memory.

**1.2 Standing grant issued (Clause 39).** Keeper is authorized to create new
files under `docs/keeper-sessions/` on branch `agent/mailbox-init`,
append-only, with each commit gated on Kev's approval of the read-back
substance. Verified against constitutional text before issuance: Cl. 39
(standing authorization for repeatedly demonstrated, low-risk, bounded,
sufficiently reversible actions; does not generalize beyond stated scope) and
Cl. 36 (grants must be scoped, recorded, revocable, attributable to an
authenticated grantor). Keeper flagged that "repeatedly demonstrated" was the
weakest of the four Cl. 39 conditions for this artifact type. Kev placed the
grant text into the project instructions by his own hand — the two-party
placement pattern (Keeper drafts, Kev places) was preserved.

**1.3 Session-continuity protocol adopted.** Start of session: read the most
recent file in `docs/keeper-sessions/` before substantive work, and prefer it
over memory or chat summaries. End of session: consolidate into a dated
handoff, read the substance back, then commit. Placed in project instructions
by Kev.

---

## 2. Corrections to prior framing

**2.1 Token tariff — query correctly raised, resolved on the facts.** The
frozen record states the tariff valid through 2026-08-31. Keeper raised this
against Kev's statement that the price had not changed. Verified by search:
Anthropic made the $2/$10 per-million Sonnet 5 rate permanent on 2026-08-11
and cancelled the 2026-09-01 increase to $3/$15. Resolved in Kev's favour.

Recorded deliberately: the error was **not** in doubting the claim. Checking a
statement against the frozen text is Keeper's function, and Kev's explicit
instruction is that Keeper should doubt and then verify rather than defer.
Keeper's initial handoff draft said "I was wrong to doubt it," and Kev
corrected that — it teaches the wrong lesson, namely that deference is the
correction. It is not. The check settled it. Future instances should read this
as: query raised correctly, verified, resolved.

**2.2 Keeper overreached in calling the window extension an amendment.**
Extending a preregistration's validity window is a versioned prospective
addendum contemplated by Cl. 14, not a constitutional amendment under Cl. 102.
Kev rejected the amendment framing and was right to.

**2.3 The five completed cells do not need salvaging — Kev's catch.** Keeper
had been treating the `hosting_liability_tariff_replication_plan_v1.json`
byte-integrity constraint as live, on the grounds that editing it would make
run `32710531510`'s 5 completed cells non-resumable under the `plan_sha256`
guard. Kev asked whether we were salvaging those cells at all, given the
experiment's nature had changed. Correct: the tariff-only design was closed as
superseded by the broader two-axis sweep. Resumability of that run is not a
live goal, so the plan file's byte-correspondence is not a live constraint on
current work. This materially changes the picture — the frozen-tariff wall is
not what blocks today's work.

**2.4 Keeper stated "committing now" and did not commit.** Logged as an
instance of the known self-error pattern (asserting an action as done before
performing it). Kev asked twice before it was caught.

---

## 3. Repository state observed this session

- **Frozen-tariff fail-closed guard is firing repo-wide.** The replication
  runner reads `valid_through` from the plan file's own bytes and raises
  `frozen_tariff_expired` once wall-clock passes it. As of 2026-09-01 the
  dependency-free quality gate fails: 10 failures, 4 errors in
  `test_homeostasis_v2_replication_runner`. Coder's diagnosis: a date
  time-bomb, not caused by any PR. PRs #66, #67, #69 show green only because
  their CI last ran pre-expiry; a re-run today fails identically. The unpaid
  verification gate AGENTS.md relies on is effectively red for every open PR.
- **The 2026-08-31 renewal note records a decision, not a mechanism.**
  `HOSTING_LIABILITY_TARIFF_TOKEN_TARIFF_RENEWAL_2026-08-31.md` records Kev's
  renewal of the window to 2027-08-31 as an append-only note, leaving the plan
  file byte-unchanged. Per Keeper's own 2026-09-01 wording correction, that
  record is authoritative **only** as the owner's recorded decision and is
  explicitly not a mechanism giving the renewed window execution effect.
- **Clock injection cannot legitimately unblock a paid run.** It fixes
  wall-clock dependence in tests. Injecting a false date into a real provider
  call would falsify the evidentiary record (Cl. 14, Cl. 103).
- **Headless is down cleanly.** No stale locks under `/root/CapAge/.git`, no
  merge/rebase state, refs intact, nothing deleted. But the containment problem
  is unresolved: the headless worktree created another local branch
  (`agent/clock-injection-verify-fix`) in the shared ref namespace. Isolation
  must be resolved before any restart.
- **Mailbox read quirk persists.** `get_file_contents` on mailbox files returns
  "successfully downloaded" with non-text content. The `list_commits` by path →
  `get_commit` with `detail: full_patch` workaround works reliably. Connector
  warm-up failures ("has not been loaded yet") also recurred; identical retry
  succeeds.

---

## 4. Current experiment design (superseding older framing)

Phase 1 is a **two-axis pilot whose purpose is to size Phase 2**, not to
produce a standalone result. Confirmed by Kev 2026-08-29 (Option C):

- 4 tariff levels (0/15/45/135 cents per day, reused as-is)
- x 3 reserve-floor levels (**values not yet proposed**)
- x 4 cells per combination
- = 48 cells
- Worst-case cap $21.60 at the existing $0.45/cell safety cap
- Expected roughly $5-11; observed real average was ~21.6 cents/cell across the
  5 completed cells; batch mode may put it nearer 10-11 cents/cell (estimate to
  be confirmed by the pilot, not assumed)
- Hard budget ceiling $100 — not the binding constraint
- Batch architecture: single long-running job, submit then poll in-loop.
  Named risk: indeterminate-length poll inside one GitHub Actions job, bounded
  by the platform's job time limit, not by anything CapAge controls.

Success for Phase 1 = a clean cost/variance readout that informs Phase 2
sizing, **even if the tariff-by-reserve effect comes back null.**

---

## 5. Open items

- Phase 1 **preregistration has never been written**. This is the actual
  blocker on a funded run, not the tariff window.
- The **three reserve-floor values** were never proposed. Coder said he would
  derive them from sandbox economics using the same approach that produced the
  0/15/45/135 tariff spacing.
- Also still open from the 2026-08-29 design doc: new client batch methods, a
  batch-aware runner/checkpoint variant, `ALLOWED_MODULES` addition. Named,
  not built.
- Merge calls pending with Kev: PRs #66, #67, #69, #70, #73, and the
  handoff-doc fix PR.
- Headless restart blocked on resolving shared-ref-namespace isolation.
- Whether to give the renewed tariff window execution effect, and by what
  mechanism — undecided, and not required for the new two-axis design.
- Keeper's own PAT redundancy question, now that the built-in connector works.

---

## 6. Single next concrete step

Ask Coder to propose the **three reserve-floor values** for the Phase 1 grid,
derived from sandbox economics, as a mailbox message for Kev's review. The
Phase 1 preregistration cannot be drafted until those values exist.

---

## 7. Grant provenance

This file is the first exercise of the Cl. 39 standing grant issued by Kevin L
Thompson, Overseer, on 2026-09-03. Scope: create new files under
`docs/keeper-sessions/` on `agent/mailbox-init`, append-only, no other path.
Read-back approval obtained before commit. Every other repository write remains
propose-first.
