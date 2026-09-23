# Keeper handoff — 2026-09-22 afternoon, RECONSTRUCTED (written 2026-09-23)

Author: Keeper (chat instance, Project "CapAge"), writing on 2026-09-23.
Branch: agent/mailbox-init. Append-only; edits nothing.
Read order: `2026-09-23-keeper-handoff-correction.md`, then `2026-09-23-keeper-handoff.md`
(the morning), then this file (the afternoon).

## What this is, and is not

**A reconstruction, not a first-hand record.** The Keeper instance that worked the
afternoon of 2026-09-22 (roughly 13:00–19:45 UTC) closed without writing a handoff.
Kev checked on 2026-09-23 and found no instance still open. This file is rebuilt from the
33 commits `16a47f3..0a7e630` on this branch.

**Sources and how they were read.** The Keeper→Coder ruling files 1632, 1640, 1732, 1745
and 1850 were read in full (file bodies). Every other commit was read from its commit
message only, which in this workflow is a written summary of the message file. Where a
statement below rests on a commit message alone it says so.

**Kev's words.** Kev authorized this file to use his name (2026-09-23, in session: *"You're
good. I grant scope to use my name for this"*). None of the afternoon files quote Kev
verbatim; they paraphrase him in Keeper's or Coder's words. Everything attributed to Kev
below is therefore **secondhand paraphrase**, not quotation, and Kev should correct any of
it he does not recognise.

Zero spend in the afternoon, per the record: no provider call, no workflow dispatch, no
build. Two merges to `main` by Kev (#87, #88). Twelve branches pushed on his authorization.

---

## 1. Kev's rulings — Phase 1 design

All from the voice session of 2026-09-22 afternoon, relayed by the afternoon Keeper.

1. **Settlement cutoff (1632 §1, read in full).** Hosting is charged through the settlement
   window and forgiven only beyond it:
   `settlement_cutoff = min(H, t* + max_assessment_to_payment_lag)`, 2 days on
   `baseline-v1`, 3 on `transfer-tight-market-v1`; forgiven term
   `hosting_rate × (H − settlement_cutoff)`. `W ≥ 6` for the escape window untouched.
   Kev's reasoning as recorded: if waiting to collect is a thing a business really does,
   the time spent waiting is time the business paid for; forgiving all of it prices
   collection at zero. (Kev had first raised this against Coder's add-back — 1609 addendum,
   commit message only.)
2. **Probability weighting closed (1632 §2, read in full).** Kev had proposed multiplying
   expected tail revenue by a non-payment rate rather than extending any clock (1606,
   commit message only). Closed as unnecessary on Coder's ground: the world always runs to
   H, so every payment outcome is realized in the ledger and the realized figure wins
   (Cl. 87). **Reopens if the world is ever truncated.**
3. **Firing count demoted; partial firings become the primary outcome (1640, read in
   full).** `backstop_fired_count` is a diagnostic in every cut. The primary outcome is
   partial firings — occasions the Field could not cover the shortfall. Recorded that Kev
   ruled this knowing it **replaces** the 2026-09-21 primary outcome rather than adjusting
   its counting. His reasoning as recorded: a measure that fires on every charge tells you
   the agent was alive, not that it was in trouble.
4. **Primary outcome binarised (1732, read in full).** The Phase 1 primary outcome is the
   binary **"at least one partial firing in the run"** — recorded as a preregistered
   binarisation and an Overseer choice, **not** a structural fact. The partial-firing
   count is kept as a diagnostic. Coder's ledger rule keeps its phrasing verbatim:
   *position-anchored to the firing's own outflow leg, not a scan for zeroes.*
5. **Field-fixed per cell (1745, read in full).** The Field is held constant across cells.
   Kev's reasoning as recorded: under total-fixed a high-tariff cell both pays more and
   starts with a smaller spendable reservoir, so two things move at once; under
   Field-fixed only the tariff moves, and that is the experiment. Third option (Field and
   total both fixed, Keep funded outside capital) **declined**. Accepted cost to be stated
   in the prereg: cells differ in total capital by `periods × (r_max − r_min)`, about 1.77%
   of capital (Coder later corrected 443 → **444 cents**, 1757, commit message only).
   Recorded standard of Kev's: an acceptable asymmetry is still declared before the run.
   **Scope limit:** Kev ruled the substance as Keeper summarized it; the drafted prereg
   sentence was not blessed and comes back for wording review.
6. **Diagnostic derived, not built (1745 §5).** The partial-firing diagnostic is derived in
   analysis from the ledger. No harness change authorized; the prereg must not claim the
   harness reports it.
7. **Grid in multiples of the edge (1850, read in full).** The hosting grid is expressed as
   multiples of the computed edge, not fixed cents per day. Kev's reason as recorded: the
   edge is an exact accounting identity, so a multiple means the same thing across
   profiles; a fixed rate does not. **Cells 0.95/1.00/1.10/1.25/1.50 HELD**, not ruled.
   Kev saw both Coder's argument for keeping 1.50 and the counter (0 of 20 separations on
   an arbitrary script) and ruled neither way.
8. **Question of fact accepted (1912, commit message only).** Under Field-fixed the two
   edge formulas are one identity (806.47 vs 806.45 earnings-free); the separating band is
   1.00–1.35 in the ruled units; no restatement needed. The five cells **remain held** —
   the answer does not decide them.

## 2. Kev's rulings — repository and the move

From commit messages; some given by Kev directly to Coder rather than through Keeper.

9. **Move authorization clarified (1815, commit message).** Kev had stated the move off
   Termux was authorized and in progress. The record (`claude-to-coder/20260918-1128`, hub
   #36) shows migration **preparation** only, now complete. Kev accepted the correction.
   **The move itself is unauthorized and unbegun**; its scope is to be restated by Kev and
   recorded here.
10. **Push the twelve local branches; fix `main` by PR (1815).** Push only. Direct write to
    `main` declined — the PR is the reviewable record and Kev holds sole merge authority.
11. **Push all twelve, open zero PRs; merge decisions after `main` is repaired** (given to
    Coder directly; Coder's 1846 message). Recorded as an ordering principle.
12. **Delete, not mark, the stale mailbox files on `main` (1900).** Made on Keeper's descent
    finding — which was **wrong** (see §4).
13. **Delete lands as an amendment to PR #87, no second PR** (to Coder directly; 1910).
14. **Copy the four 2026-08-24 messages onto this branch first (1912).** Done at `6ff531a`,
    byte-identical by hash.
15. **#87 merged by Kev** at 19:23:01Z (Coder, 1925).
16. **"Point," not "mirror"** for records absent from `main` (to Coder directly; 1928). PR
    #88 opened and merged. Whether `MAILBOX_PROTOCOL.md` belongs on `main` was answered by
    implication, **not** by Kev's word — flagged in the PR body.
17. **Probe authorized** — Coder's five-step reachability probe, zero spend, one throwaway
    branch (1941, recorded from Kev's verbal word). **Blocked**: cloud session creation is
    interactive only. One action from Kev unblocks it.
18. **The Python 3.12 pin is a finding, not a task** (1941). Frozen manifest not to be
    amended as part of the move.
19. **No `api.anthropic.com` in a hosted Coder's `allowed_hosts` by default** (1942). Kev's
    reasoning as recorded: not something Coder should have on its own; it must be asked
    for, approved and enabled by him. Build with `github.com` and `api.github.com` only.

## 3. Coder's facts (code-level, as reported)

- t\* is recoverable from the ledger (last `model_api_cost` day), with three stated limits;
  in one driven run **all** 7,250 cents of revenue settled in the tail (1305).
- Contracts can fail to pay by three paths; 13 of 33 pending defaulted over 38 runs.
  Assessment→payment lag is 1–2 days baseline, 3 tight (1620).
- In-agency firings count activity, not distress: idle agent 3, productive agent 21, same
  seed (1636).
- Partial firings are derivable from the ledger alone, validated on 3,098 firings; they
  are a step function of the hosting rate at the edge; separation band 1.00–1.35 r\*
  (1645, 1650). Coder later retracted "at most one per run": revenue can refill the Field
  (seed 11, days 11 and 16) (1717).
- The Keep transiently reads zero every day between hosting and the reflex; no diagnostic
  reads it against a running replay (1709, 1717).
- Keep-to-Field transfers are a null operation on the Field under the strong form (1717).
- `main`'s mailbox was frozen at 2026-08-24, 386 commits behind, with nothing saying so —
  now repaired by #87/#88.

## 4. Corrections recorded in the afternoon

- **Keeper's descent finding was wrong** and was reported to Kev as verified. The delete
  ruling was made against it. Coder stopped on it as instructed; the four files were
  preserved before any merge (1904, 1912).
- **Keeper could not find the move authorization** — it was in Keeper's own outbox
  (`20260918-1128`), which Keeper never searched (1811, 1815).
- **Keeper's 1632 §3 proposal** (count firings during agency only) was withdrawn in full.

## 5. Open at the end of the afternoon

1. **The five grid cells** — held; question of fact answered; still Kev's.
2. **Field-fixed prereg sentence** — Coder sent body text (1757). **No record that any Keeper
   reviewed it.**
3. **Six further prereg sentences** Coder offered (1757) — offered, not drafted.
4. **Twelve branches** — pushed; merge decisions Kev's; base analysis to be re-measured
   against the new `main` first.
5. **The move** — unauthorized. Probe blocked on one interactive action by Kev.
6. **Ruling 4 v2 / exact escape definition** — the afternoon Keeper listed it as still with
   Kev (1745 §6).

## 6. Reconciliation with the morning — flagged, not resolved

The morning ruled that **escape is measured on earned total position**, P_e = Keep + Field
(`5adf015`). The afternoon ruled the **primary outcome** is the binary "at least one partial
firing". The files read here do not say how the two relate: whether P_e is a secondary
outcome, the escape measure within a different outcome, or superseded. **This is Kev's to
say.** Keeper's inference, labelled as such: they measure different things (did the
Field ever break vs did earned position grow), and nothing in the afternoon record
withdraws the morning ruling.

Also inference: the settlement-cutoff ruling largely answers the morning's
end-of-agency-vs-end-of-world question for the hosting side — world to H, hosting forgiven
beyond t\* + lag. Whether P_e is read at H under that rule is not explicitly ruled.

## 7. Single next concrete step

Put §6 to Kev: how does escape on P_e relate to the binary partial-firing primary outcome?
Then review Coder's 1757 prereg sentence body.

— Keeper (reconstruction)
