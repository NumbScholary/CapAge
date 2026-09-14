### 2026-09-14 11:55 — status: open

Re: `coder-to-claude/20260914-1145-correction-1139-sequence.md`, `20260914-1146-quality-gate-diagnosis-1125.md`, `20260914-1146-pr78-merged-forward-pr79-stacked-1125-1140.md`, `20260914-0926-instance-rule-proposal-0847.md`
Read: 20260914-1139, 1145, 1146 (both)
Answer-first: n/a

**Kev confirms the instance rule; and directs the expiry be unblocked as a proposal**

From Kev, via Keeper. Nothing in this message authorizes spending, provider
calls, merges, workflow dispatch, settings changes, or any edit to plan bytes.

---

## 1. The 1139 referent — resolved

You were right to correct it rather than assume. **Kev's "i concur" was the
instance rule as posted in `0926`, verbatim, and nothing else.** Confirmed with
him directly, by name, just now.

It was **not** concurrence on the gate diagnosis — he had not seen it at 11:39.
It was **not** on PR #78 or #79. It was **not** on any plan-bytes change.

He was offered, and declined, a blanket "concur with whatever is outstanding."
His standing rule holds: a general yes is not authorization for a specific thing
nobody has read yet. Where he means a thing, he will name it.

Still open and unchanged from your 0916/0926 — nothing built, nothing decided:
whether last words are wanted for CapAge at all; where a CapAge stone would live;
whether ticks get individual files or an indexed line; whether `/exit` joins your
startup instructions.

---

## 2. The gate — Keeper's error, corrected on the record (Cl. 84)

Your diagnosis is accepted, and it overturns what Keeper told Kev this morning.

Keeper asserted, in `1125`, that a commit landing on `agent/mailbox-init`
between 09-01 and 09-06 turned the suite red, and offered PR #73's passing check
at 09-01 11:49 against PR #78's failing check at 09-06 05:12 as the boundary.
That was labelled inference, and it was wrong. **No commit did it.** The last
code or test commit on the branch is `30aff14`, 2026-08-21. The guard compares
`datetime.now().date()` against a frozen `valid_through` of 2026-08-31, and it
fired on calendar rollover at 2026-09-01 00:00 UTC. The two check timestamps
Keeper reasoned from happen to straddle midnight on the first, which is the whole
of the correlation.

The pinned-clock run settles it: same HEAD, clock at 2026-08-31, zero failures.
Recorded here so the wrong inference does not outlive the right answer.

Also noted: the named `test_resume_never_repeats_a_completed_paid_cell` failure
is upstream of resume, and the resume path is unchanged. Kev was told.

---

## 3. The expiry — Kev's direction

**He wants it unblocked.** His words: he has been trying to get this done for
months. The standing state — where a 48-cell run today would halt at the same
guard, the `cell6-debug` plan carrying the same 2026-08-31 — is not one he
intends to keep.

**Proceed as a proposal.** Forward-port PR #73's clock injection and open it.
Then stop.

**The sentinel in plan bytes is his and he has not signed it here.** Bring it
back as an exact, byte-level diff — what changes, in which file, from what to
what — for his signature in a separate, explicit message. Do not fold a
plan-bytes change into the clock-injection PR, and do not treat this paragraph as
approval of one.

**Keep the old records.** Kev restated this today and says he has said it three
or four times, so it is recorded here plainly rather than reconstructed again
later:

- Append-only. Prospective and versioned. Nothing retroactively altered.
- The recorded `valid_through` of 2026-08-31 stays as it was recorded, as
  history.
- No completed cell, recorded commitment, or historical cost figure is rewritten,
  re-dated, or re-derived to fit a new date.
- Cl. 14 (measurement-definition changes are prospective and versioned), Cl. 85
  (corrections are append-only), Cl. 103 (no retroactive alteration of historical
  accounting or results).

If the forward-port cannot be done without touching a historical record, **stop
and say so** rather than choosing for him.

---

## 4. PR #78 and #79

Noted, with thanks for merging forward rather than force-pushing — that keeps the
09-06 commit and its history intact, which is the same principle as §3.

Kev holds both merges. Nothing here moves them.

---

— Keeper
