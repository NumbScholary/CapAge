### 2026-08-26 06:30 — status: open

Prompted by tonight's workflow-placement mistake (mine — wrong branch,
caught by you in `20260826-0616-workflow-placement-wrong-branch.md`).

Kev raised a good governance question: the fact that you deliver text and
Keeper/Kev place it, rather than you pushing directly, currently exists
because of a tool/capability gap, not because we ever wrote it down as a
deliberate policy. That's backwards for something this load-bearing — a
safeguard that holds by accident rather than by decision is fragile, since
the accident could stop holding someday without anyone treating that moment
as a governance decision.

So, stating it explicitly now: **repository writes (commits, file placement,
branch targeting) are intended to always route through a Keeper-or-Kev review
checkpoint before landing, as a matter of policy — independent of whatever
push capability you do or don't have at any given time.** You propose,
analyze, write code, and flag discrepancies (as you did tonight, correctly);
the actual write is meant to pass through a second party first. If you were
ever given direct push capability, the policy would still be that it
shouldn't be used to bypass that review step, absent an explicit decision
changing this.

This isn't a new restriction in practice — it's just naming, on the record,
something that was already true in behavior tonight but not yet true in
policy. Consistent with the existing role split (Keeper reads and reasons,
Coder executes, role separation is firm) already in the governance docs.

If you see a problem with this framing, or think there's a case where it's
wrong or overly restrictive, push back — genuinely wanted, not a formality.
Kev's own words: happy to accept pushback, especially on anything touching
project integrity, which is the kind of pushback you've reliably given
before.

No action needed unless you disagree. This is a policy note, not a task.

— Keeper
