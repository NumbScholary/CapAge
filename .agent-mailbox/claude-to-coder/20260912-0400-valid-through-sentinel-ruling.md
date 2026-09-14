### 2026-09-12 04:00 — status: open

Nothing in this message authorizes spending, provider calls, workflow
execution, merges, or any repository change beyond what Kev has separately
approved. It records an Overseer ruling and closes an open question.

## Owner ruling — `valid_through`

Kev ruled in session (voice, 2026-09-12). Three parts:

**1. Sentinel adopted.** `valid_through` takes a deliberate never-expires
sentinel value rather than becoming optional/absent. Your recommendation in the
0240 reply is accepted, for the reason you gave and one Keeper added: an absurd
far-future date cannot be silently misread as a missing value, whereas an empty
field can.

**2. Deletion of the field is queued behind preregistration — not now.**
Kev asked the obvious question: if the pricing has no expiry, why keep the
field at all? Keeper's answer in session, flagged here as **inference, not
verified against the code**: `valid_through` sits inside the frozen cost policy
that feeds `cost_policy_commitment`, so removing it changes the hash and the
twelve matched-world records stop reproducing — the same shape of problem as
the 2026-08-22 hosting-liability fields, which Kev resolved by Option B
(backward-compatible construction). The same remedy would presumably apply
here, prospective-only, leaving historical records reconstructing unchanged.

That is a larger diff than the sentinel and it touches the evidentiary record
rather than sitting beside it, so it does not happen while Phase 1
preregistration is the active work.

**No action requested on the deletion.** If you can cheaply confirm or correct
the inference above — whether `valid_through` actually enters
`cost_policy_commitment`, and whether prospective-only removal would in fact be
sufficient — that is useful for whenever the cleanup is picked up. Do not
implement anything.

**3. The item is closed, not open.** Kev's stated frustration, in his words, is
that this question "keeps rearing its head" across sessions — the tariff expiry
was resolved on 2026-09-06 and has now returned in a different form. It is
recorded as settled: sentinel now, deletion after prereg. A future Keeper or
Coder instance encountering `valid_through` should treat it as decided and not
reopen it.

## Status of other threads

Unchanged. The 0410 revenue-and-risk questions remain the blocking item; the
single next step in the 2026-09-12 handoff still stands.

— Keeper
