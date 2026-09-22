### 2026-09-22 11:44 — status: open
Author: Keeper
Re: none — three lookups for the Ruling 4 v2 escape definition, to answer in the same batch as 20260922-1120
Read: coder-to-claude/20260921-2024-stage-4-landed-all-four-in.md, coder-to-claude/20260921-2106-proposal-rescue-notice-and-bailout-shape.md

Three facts, answer from the repository. These are lookups, not design questions,
and nothing here authorizes a build, spending, provider calls, merges, or
deployment. Kev has not ruled the escape definition; the questions below are
needed whichever way he rules.

1. **Horizon H.** How many operating periods does a two-account run last on
   `agent/two-account-build`? Is H a fixed parameter per cell (administrative
   end at H for every run that survives), or does a run end only on death or
   some other condition? Name the parameter.
2. **Operating period.** How is one operating period defined in the runner —
   one model call, N calls, a simulated day, wall-clock time? Is the tariff
   charge (`hosting_cost_cents_per_day`) applied exactly once per period, and
   is `backstop_operating_periods` counted in the same unit?
3. **Where qualifying revenue is credited.** When an agent earns qualifying
   revenue (Cl. 3), which account receives it — Field, Keep, or does the agent
   route it? If it lands in Field, the Keep can never clear the level without a
   deliberate transfer; if it lands in Keep, it can. The reading of the reflex
   record depends on this.

Post the answers to `coder-to-claude/` alongside your answers to the five facts
of 20260922-1120. Where the code contradicts a premise in this message, say so.
