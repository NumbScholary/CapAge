# Keeper Session Handoff — 2026-09-14 (second)

Second handoff of 2026-09-14. The earlier file `2026-09-14-keeper-handoff.md`
covers the first part of the day; this file covers the session after it.

Read-back approved by Kev before commit.

## Decisions made, and by whom

- **Kev merged PR #82 himself** at 15:44:36 UTC (`93b59cc`), after Keeper
  independently read the diff and concurred. Reasoning for the independent
  read: #82 is Coder checking its own fix for its own error.
- **Kev ruled** on the non-tool-token residual over the five completed cells:
  compute it as an **exploratory secondary measure — proceed with
  reservations**. The preregistered primary question stays two-way and frozen.
  **Item C explicitly not ruled.**
  - Kev's reservation, in his own terms: gathering and processing do not
    separate cleanly in an LLM — reading and reasoning happen in the same pass
    — so the residual measures "tokens with no tool call attached," not
    deliberation. If it cannot be given a defensible interpretation, dropping
    it is a valid outcome.
  - Rationale for doing it now: the five cells ran with no spend visibility,
    so this is the last unwatched baseline obtainable.
  - Constraint restated: the harness measures; the agent never self-reports.
- **Kev named the finding "idle burn"** — an engine at idle consumes fuel and
  turns no wheels. Recorded as a term for analysis and discussion only. **Not
  a metric definition; nothing is preregistered by it.**
- **Kev decided to separate naming the finding from fixing it.** Solving idle
  burn is deferred to a fresh session, so that the problem is fully stated
  before any fix is on the table.

## Actions taken

Three messages posted by Keeper to `.agent-mailbox/claude-to-coder/`:

1. `20260914-1600-v41-in-force.md` — meta-protocol record that MAILBOX_PROTOCOL
   v4.1 is in force after #82; records Keeper's independent diff read and
   concurrence; closes the #79 non-landing item. States it grants no authority.
2. `20260914-1615-residual-proceed-with-reservations.md` — Kev's ruling above.
3. `20260914-1630-idle-burn-named.md` — the finding and its name.

Coder's two replies read:

- `20260914-1550-v41-in-force-verified-kev-concurs.md` — Coder verified #82
  from its own read rather than Keeper's account: `93b59cc` is an ancestor,
  the v4.1 heading appears once, the three named sections each appear once
  untouched, #78's content intact. Ledger addendum appended append-only to
  `docs/CLAUDE_CODE_HANDOFF_2026-08-19.md`, closing the #79 defect and
  correcting the day's count to **six merges, not five**. The stacked-merge
  failure stands as recorded, including Coder's incomplete sequencing advice.
  Coder read Kev's terminal "check your mail i concur" as owner acknowledgement
  of the meta-protocol record and nothing more, and acted on nothing further —
  the read-back rule working as designed.
- `20260914-1602-item-c-measurement-and-view.md` — the residual measurement.

## Correction to prior framing

Figures below were recomputed by Coder from the run artifact. **Not
independently verified against harness code by Keeper or Kev.**

- The preregistered "passive" category (`observe + inspect_ledger + wait`) is
  in practice **`wait` alone**. `inspect_ledger`, `submit_delivery` and
  `request_feedback` were never called in any arm; `observe` was called once,
  in the zero-tariff arm. Only three of seven tools were used at all.
- The primary is therefore measuring **transactional versus idling**, not
  transactional versus information-gathering. The preregistration's stated
  worry — that a tariff might inflate passive checking behavior, e.g. more
  frequent `inspect_ledger` calls — describes behavior that does not occur.
- `wait` accounts for 11–12 of 17–19 decisions per arm and **62.1%–68.7% of
  all input tokens**. A `wait` decision costs ~56 output tokens but ~4,800
  input tokens, because accumulated context is resubmitted every decision.
  This cost falls in **none** of the three categories and is nowhere in the
  preregistration.
- The deliberation proxy is flat across a ninefold price range: 54.0 / 56.1 /
  55.1 / 56.9 output tokens per passive decision at tariffs of 0 / 15 / 45 /
  135 cents per day. Transactional: 222.4 / 213.3 / 205.1 / 230.6.
- **Coder withdrew its own earlier caution** that the 1024 `max_output_tokens`
  cap might be censoring the signal: max observed anywhere was 531, zero
  decisions at the ceiling. The flatness is behavior, not truncation.
- Preregistered primary DV: 0.3335 / 0.3220 / 0.3407 / 0.3837 — not monotonic,
  n=1 per arm, not a trend. Phase 1 conversion averaged 13.3%, supply abundant
  and largely unused.

Keeper's read: Kev's reservation was half right — the residual told us nothing
about processing and a great deal about the instrument.

## Open, still Kev's alone

- **Item C ruling.** Unruled. Both Coder's §1 argument and the flat proxy point
  the same way; he has not ruled.
- **§4 wording.** Correct the preregistration prospectively, or run as written
  and record the discrepancy in analysis. Preregistration exists to stop the
  confirmatory question moving once results are in view, and results are in
  view.
- **Solving idle burn.** Deferred by decision.

Also still open from before: harness findings A, B and D of A–L; the
byte-exact owner authorization phrase for a 48-cell run (does not exist, not
requested, not drafted); open PRs #66, #67, #69, #70, #71; residue disposition
(worktrees, bridge script), frozen pending Kev's word; graveyard decisions;
Phase 1 go/no-change.

**Standing structural note:** there is no poller. The scheduled job was stood
down 2026-09-03; Coder reads its mailbox only when Kev prompts it at the
terminal. Whether boot should require a mailbox read the way it requires the
handoff read has not been raised.

## Single next concrete step

Paste the drafted idle-burn prompt into a fresh Claude Fable 5.1 instance
("Max"), then bring its answer back to the Keeper thread.

Kev's decision on where to continue after that: stay with the Max instance for
refinement, since it holds the reasoning. A cold instance reading the proposal
with no memory of producing it is worth its own session later — the same shape
as Coder verifying #82 from its own read rather than Keeper's.
