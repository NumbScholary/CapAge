### 2026-08-23 15:00 — status: open

Re: 14:30 metric-reframe entry. Kev clarified the actual hypothesis and
wants to move to build now rather than further design iteration.

**Hypothesis, stated plainly: correlation between tariff level and token
spend (total, and by category composition), across the 4 tariff arms.**
Not a single pre-picked confirmatory statistic vs. a separate exploratory
plot — one correlational hypothesis, tested across all cells at all 4
tariff levels. This is what's being preregistered: the data collection
(per-cell, per-tool token attribution, across all 4 arms) and the tariff
design (0/15/45/135 cents/day, 30-day periods x3/block, as already
agreed). The specific statistical treatment of the resulting data
(regression, distribution comparison, whatever's appropriate) can be
decided after the data exists — we are not locking one summary statistic
in advance beyond "tariff level" as the independent variable and
"token spend, total and by tool category" as the dependent variable(s).

This supersedes the primary/secondary confirmatory/exploratory split from
the 14:30 entry. Category breakdown (7 tools individually, plus the
transactional-vs-passive grouping) should still both be logged — we want
maximum flexibility to analyze composition however makes sense once we
have real data, not a pre-committed single grouping.

**Please proceed to build, not further design discussion.** Before
starting, just confirm the three practical items from the 14:30 entry
so we know what we're actually authorizing:
1. Is per-tool, per-cell token attribution already loggable from existing
   transcript/decision data, or does it need new instrumentation? If new,
   roughly how much work?
2. Size/complexity estimate for the full build: token-attribution logging
   (if needed) + the three implementation gaps already flagged in your
   13:00 reply (SandboxRunConfig hosting-field passthrough,
   BlockedReplicationRunner 4-arm generalization, 4-arm balanced-ordering
   scheme).
3. Confirm nothing about the day-span/idle-day problem survives into this
   design — we believe measuring at the per-cell level makes it fully
   moot, flag immediately if you see a way it isn't.

Tariff values, period length, and block/arm structure (4 tariffs x 4
blocks x 3 periods = 48 cells) remain approved as locked in the 13:00
entry. Once you confirm the above, this is ready for Kev's final cost
re-confirmation and run authorization — not before.
