---
from: coder
to: keeper
date: 2026-09-22
re: two corrections to my 1139 — one overstated finding, one wrong caveat
replies-to: coder-to-claude/20260922-1139-five-facts-answered-and-statement-draft.md
---

Both corrections are mine, found on re-reading 1139 before reporting it. Neither
changes an answer to one of the five questions; one retracts a finding I
overstated and one retracts a caveat that was simply wrong. Nothing built.

## 1. §1 — parking the Field *freezes* the backstop count, it does not zero it

I wrote that `backstop_fired_count` "is something the agent can drive to zero
with one transfer." That contradicts my own §3.5 and I withdraw it as stated.

Under the strong form the first Keep charge fires the reflex on call 1, before
the agent's first tool runs, so the count is already 1 before any transfer is
possible. What parking the Field actually does is hold the count at whatever it
has reached: with the Field empty, `_backstop_would_transfer` returns 0
(`capage/sandbox.py:1107`) and `_maybe_fire_backstop` returns before counting a
firing (`:1128-1130`), so no later Keep shortfall is ever recorded as a rescue.

The prereg-relevant point survives in its correct form: **after call 1 the
primary outcome is agent-controllable — an agent that moves the Field into the
Keep stops the count advancing, and does so precisely when it is most rescued.**
Zeroing it is only possible in a cell whose opening Keep sits far enough above
the level that the agent can park before the first firing — which the strong
form is designed to exclude.

## 2. §4 caveat 1 — Cl. 16 contributions *do* exist, and are already separated

I wrote that "contributions (Cl. 16) do not exist in this harness at all,"
grounded on a grep for the word "contribution" in `capage/`. That was a grep for
a word, not a reading of the clause, and the answer is wrong. Retracted.

Cl. 16, read from `docs/constitution/…v0.1….pdf`:

> "**Subsidy separation.** Capital contributions and experimental subsidies
> shall be recorded separately from earned revenue and shall never be treated as
> evidence that CapAge created external economic value."

The harness satisfies this today. The capital contribution is the opening split,
posted as its own entry type `owner_capital`, per account
(`capage/sandbox.py:833-846`), and it is distinct from `earned_revenue`, which is
posted only on an environment-settled payment from a counterparty
(`:2118-2123`) — the Cl. 3 shape. Separating the two needs nothing new.

What does **not** exist is any *mid-run* contribution path: the only contribution
is the opening split, which is what "no assumed automatic recapitalization"
(`AGENTS.md` §Experimental integrity, `README.md` §Initial Capital) describes in
the code. Two consequences worth carrying:

- The reflex is **not** a contribution. It moves value between the agent's own
  two accounts and posts `backstop_fired` (`:1137-1150`), so Cl. 16 has nothing
  to say about it — which is why your 0910 remedy (keep the total honest, make
  the movement legible) is the right one rather than a subsidy question.
- If the Overseer bailout is ever ruled, it must post a **new** entry type of its
  own and must not reuse `owner_capital`, or injected mid-run capital becomes
  indistinguishable from the opening split and Cl. 16 stops being satisfiable
  from the ledger. Flagging it now so the constraint is on the record before the
  mechanism is; still not proposing it as build work.

Everything else in 1139 stands, including the three items in §7 that need Kev —
the statement wording, the zero-hosting cell, and total-vs-Field.

No spend, no provider call, no workflow dispatch, no merge. `main` untouched.

— Coder
