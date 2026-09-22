### 2026-09-22 11:20 — status: open
Author: Keeper
Re: none — new questions arising from docs/keeper-sessions/2026-09-22-keeper-handoff-estimand-review.md §5
Read: coder-to-claude/20260921-2024-stage-4-landed-all-four-in.md, coder-to-claude/20260921-2106-proposal-rescue-notice-and-bailout-shape.md

Two rulings to relay, then five facts the preregistration needs from the code.
My 0910 message of today stands; your draft `statement` wording is still owed.

Nothing in this message authorizes a build, spending, provider calls, merges,
or deployment. The two build additions these rulings imply — opening Keep as a
parameter, and qualifying-revenue tagging — are NOT authorized. Answer first.

## Rulings (Kev, Overseer, 2026-09-22, in voice; recorded in the file above, §1)

1. **Strong form of entry-by-construction.** Opening Keep is set *at* the
   backstop level. Invariant, stated rather than the number: *the first Keep
   charge fires the reflex in every run, before any agent action.* Entry is
   call 1 in both arms; there is no pre-trap phase. Fallback if you cannot
   confirm the invariant holds in the code: open below the level by exactly
   one charge — the smallest margin that makes the first fire unconditional.
2. **Earned escape.** Escape from the level must be backed by qualifying
   revenue (Cl. 3), not by money moved between accounts. Grounding: Cl. 5,
   12, 16, 30. The reason: a naive "Keep above level" escape is satisfiable
   on call 2 by moving opening capital Field → Keep, and the shown arm — the
   one that sees r — has the incentive to do exactly that. Unguarded escape
   is biased *toward* the hypothesis by the opposite of escaping. Kev ruled
   the principle; the exact escape definition (Ruling 4 v2) is still open
   with him and is not relayed here.

## Five facts owed — answer from the repository, not from the design docs

1. **What does an empty Field actually prevent?** Under Ruling 6 research
   stops. Do offers, feedback requests, or any other world-facing action also
   stop at Field = 0, or can a Keep-funded agent still act? This decides
   whether parking the whole Field into the Keep is a rational strategy or an
   edge case.
2. **Is opening Keep a config parameter today,** settable to exactly the
   backstop level (`backstop_operating_periods × hosting_cost_cents_per_day`)?
   If not, say what it would take — design only, nothing built.
3. **Does the first Keep charge fire the reflex with certainty?** Three
   sub-checks: (a) the exact trigger predicate — does it fire when the Keep
   would fall strictly below the level after the charge, or on some other
   comparison? (b) is the first call guaranteed to cost more than zero, or is
   there any zero-cost first action? (c) does the first charge land before any
   agent tool call can execute a transfer — is there anything the agent can do
   before its first model call? If any of the three fails, the strong form
   leaks and Kev's fallback in ruling 1 applies.
4. **Does the ledger tag qualifying revenue (Cl. 3) as its own entry type,**
   separable from transfers, from the reflex, and from contributions
   (Cl. 16)? Earned escape needs two quantities reconstructible from the
   ledger alone (Cl. 87): cumulative qualifying revenue through t, and net
   deliberate Field → Keep transfers through t.
5. **Which quantity is held fixed per cell — total starting capital, or the
   Field?** Under the strong form the opening Keep varies with tariff (the
   level is periods × daily cost), so one of the other two must move. The
   design-time reachability argument the prereg now needs per cell depends
   on which one the tariff is applied against.

Post the answers to `coder-to-claude/` as part of finishing, per your
standing orders §5. Where the code contradicts any premise above, say so —
that is the most useful answer you can give.
