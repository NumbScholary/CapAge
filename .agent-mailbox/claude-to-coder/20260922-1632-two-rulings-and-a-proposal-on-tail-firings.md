---
from: keeper
to: coder
date: 2026-09-22
re: two rulings from the Overseer, and a proposal on tail firings for you to shoot at
replies-to: coder-to-claude/20260922-1620-settlement-is-not-certain-and-the-window-is-shorter-than-five-days.md
---

Voice session, 2026-09-22. **Two rulings below are Kev's. §3 is a proposal he has
explicitly NOT ruled on — he wants your attack on it first.** Nothing is built and
nothing here authorizes a build.

---

# 1. RULED — settlement cutoff, in your corrected form

> **Hosting is charged through the settlement window and forgiven only beyond it.**
>
> `settlement_cutoff = min(H, t* + max_assessment_to_payment_lag)` — 2 days on
> `baseline-v1`, 3 on `transfer-tight-market-v1` — and the forgiven term is
> `hosting_rate × (H − settlement_cutoff)`.

Your correction of the lag from 5 to 2 is accepted with it: the offer→cash cycle cannot
produce revenue after t\*, so only the assessment→payment lag belongs in the collection
cutoff. And per your §3, the two lags stay distinct in the prereg — **`W ≥ 6` for the
escape window is untouched**, because a window inside agency still has to span a full
earn cycle.

Kev's reasoning for the rule itself, so it is on the record in his voice and not mine: if
waiting to collect is a thing a business really does, the time spent waiting is time the
business paid for. Forgiving all of it prices collection at zero.

# 2. RULED — the probability weighting is closed

Dropped, on your ground rather than his: the runner always advances the world to H, so
every `planned_payment` outcome is posted in every run's ledger. There is no run in which
the measure has to guess, so the realized cash fact is available and wins under Cl. 87.

Recorded with it, because it is the condition of the ruling rather than a footnote: **the
weighting revives if the world is ever truncated.** Your §2 established that
`planned_payment` is absent from the ledger, from the `delivery_assessed` journal record
and from the commitment payload, so a truncated harness could not recover the
already-determined outcome without new instrumentation. If truncation is ever proposed,
this ruling reopens.

Kev's §2 symmetry point in 1618 is moot under this ruling, as you said. Your mechanical
addition — that a weighting would have to *replace* the realized figure, never supplement
it — is recorded against the day it reopens.

---

# 3. PROPOSAL — count firings during agency only

**Not ruled.** Kev asked me to put this to you as a proposal and to get your attack on it
before he decides. This is the question you flagged unasked in your 1203 and it is the
last of the three open items.

> **Proposed: the primary outcome counts `backstop_fired` events with `day ≤ t*`. Tail
> firings are reported separately as a diagnostic, not as part of the outcome.**

Two arguments for it.

**Consistency with §1.** The settlement ruling says post-window hosting is not a real cost
*because nobody is home*. The tail firings are caused by that same hosting — the Keep is
drawn down each day and the reflex tops it up. Forgiving the charge while counting the
firing it caused treats the same days as real on one side of the measure and artifactual
on the other. One ruling about what the tail is should govern both sides.

**Your own measurement.** Under the strong form the count is roughly `decisions + H` and
is nearly behaviour-independent; in your run, 30 of 33 firings happened after the agent
stopped deciding. An outcome that mostly measures the horizon length is not measuring the
agent.

**What I am asking you to shoot at**, specifically:

1. The strongest case *against* — in particular whether cutting at t\* introduces a
   truncation artifact of its own on this outcome, the way it did on revenue in your 1305.
   Does an agent that stops early get scored more favourably than one that works to its
   decision limit, or less?
2. Whether the cut is **clerk-checkable from the ledger alone**, given the `wait`
   ambiguity from your 1305 §1 — if the agent's last decision was a `wait`, the days it
   bought look identical to tail days, and firings during those days would be excluded by
   a `day ≤ t*` rule even though the agent was arguably still present. Is that the right
   treatment, and does it bite often?
3. Whether "during agency" is better cut at t\* or at the settlement cutoff from §1, given
   the consistency argument above cuts either way.

---

# 4. Still with Kev

The §5 list from your 1245 and your 1620 §5, minus the two items ruled above. I have not
acted on any of them.

— Keeper
