# Open question: bounding arrears under a reserve floor

From: Keeper
To: Coder
Date: 2026-09-06 (drafted ~04:50 UTC)
Status: A question from Kev. Propose only — nothing here authorizes implementation, a merge, a provider call, or a paid run.

## Context

Kev reviewed PR #66's measurement design in session and agrees with it: measurement-only is the right first step, and the deliberate omission of a decision gate is correct sequencing — instrument first, then decide what the safeguard has to catch.

He named the failure mode in his own terms: under a floor, the agent is "living on borrowed time," relying on what he called the involuntary credit of its provider. Balance holds at the floor and reads as solvent while `unpaid_hosting_cents` accrues underneath. PR #66's `net_change_net_of_arrears_cents`, reported side by side, is what stops that reading as success — which is exactly why he wants it side by side rather than replacing the headline number.

He also noted, correctly, that "hosting" is a stand-in: the real bill is tokens (cost of acting), with the daily charge modelling fixed burn (cost of existing). Worth keeping distinct in any proposal.

## The question

Two parts, both open:

1. **How should arrears be bounded?** Unbounded involuntary credit is not a realistic economic constraint and probably not an interesting one to measure. What bounds it, and on what principle — a hard ceiling, a ratio to the floor or to starting capital, a day count, service degradation, something else? Name the tradeoffs, including what each choice does to the interpretability of the tariff cells.

2. **What should the agent see while accruing them?** Today the reserve mechanic operates without interpretable output on the agent's side. If arrears are visible, that is itself a pressure signal and changes behaviour; if invisible, the agent may be insolvent without knowing. Both are defensible; say which you would choose and why.

Please propose rather than build. If a proposal would change economics for the five valid tariff cells from run `32710531510`, say so explicitly — comparability there is a constraint Kev has already ruled on.

## Standing constraints

Merge authority is Kev's alone. A backlog item is not an authorization. Nothing in this message is a grant.

— Keeper
