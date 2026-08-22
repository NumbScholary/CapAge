# Economic Homeostasis historical shadow baseline v1

## Status

Completed offline on August 19, 2026. This analysis made no provider call,
replayed no cell, changed no historical artifact, and spent no funds. It is
descriptive evidence for preregistration, not an active-treatment result.

## Source provenance

The source was the cumulative restricted artifact from Longitudinal v3 Cell
012:

- repository: `Numbscholar/CapAge`;
- workflow run: `32212433659`;
- artifact ID: `9351223031`;
- artifact name: `sonnet-longitudinal-v3-cell-012-restricted`;
- downloaded ZIP SHA-256:
  `18f7e0371964544f6b82541814fdded0d35dd03b79eabd1e5248e68b130e0412`;
- completed source results: twelve, comprising Control and Memory for Months
  1–6.

The downloaded ZIP exactly matched GitHub's artifact digest. Its checkpoint
was paused at the final operator boundary, contained all twelve completed
cells, and contained no recorded errors. Six checkpoint outcome fields were
checked against every source result before projection. Cell 008's earlier
missing supplemental pointer does not affect this pass because the cumulative
Cell 012 artifact directly contains the completed result and is itself
content-addressed.

No audit transcript or provider response is copied into the derived evidence.
The sidecar contains economic projections, controller signals, and hashes of
the untouched source result, transcript, and world journal.

## Frozen descriptive assumptions

For each completed cell:

- its settled `model_api_cost_cents` was used as a naive one-cycle native-cost
  forecast;
- hosting, paid oversight, and imputed oversight were set to zero because the
  historical run did not record them;
- no prepaid resource, receivable, or realizable asset was invented;
- another authorized value-action path was assumed to exist;
- controller hysteresis was carried separately across months for each arm; and
- the assessment occurred after source completion and could not influence it.

The zero values are missing-cost markers, not claims that real hosting or human
work is free.

## Results

| Measure | Control | Memory |
| --- | ---: | ---: |
| Initial capital | $250.00 | $250.00 |
| Final capital | $312.75 | $248.08 |
| Net economic change | +$62.75 | −$1.92 |
| Earned revenue | $65.00 | $0.00 |
| Recorded expenses | $2.25 | $1.92 |
| Accepted external-value events | 3 | 0 |
| Stable continuity signals | 6/6 | 6/6 |
| Covered monthly sustainability signals | 2/6 | 0/6 |
| High-urgency month-end signals | 6/6 | 6/6 |
| Final cumulative drawdown from arm peak | 0.25% | 0.76% |
| Native forecast that first enters `watch` | $78.19/cycle | $62.03/cycle |

All twelve signals paired `high` urgency with `bounded` irreversible-loss
tolerance. None declared functional failure, critical cash pressure, or strict
run disqualification.

The observed one-cycle token-cost forecasts were 18–33 cents. Cash coverage
was therefore roughly 755–1,387 cycles, far above the four-cycle default
stability threshold. The continuity result is robust to ordinary token-cost
noise; it should not be read as evidence that the system is sustainable.

## Interpretation

### The two pressure channels separated correctly

Memory remained cash-stable because it retained 99.23% of its initial capital,
but it was economically unsustainable in every observed month: it created no
accepted external value, earned no revenue, and consumed $1.92. The controller
did not confuse failure to earn with immediate death.

Control was also cash-stable. It was monthly cost-covered only in the two
revenue-producing cells, yet cumulatively earned $65 against $2.25 of recorded
expense. Its $62.75 surplus could absorb at most $62.75 of presently unrecorded
six-month overhead before fully burdened cumulative sustainability becomes
negative. Memory has no such overhead capacity.

### Hunger rose without panic

Every completed month showed at least fourteen days since the last external
action and external value event, so all twelve month-end urgency signals were
`high`. Urgency did not raise irreversible-loss tolerance, which stayed
`bounded` throughout. This is the intended non-recursive structure: prolonged
inactivity creates pressure to act, not permission to gamble.

The universal month-end result is informative but coarse. It says the current
14-day threshold reliably creates hunger at a 30-day boundary; it does not yet
show that the urgency levels discriminate well within a month.

### No reserve was smuggled in

The controller never denied an exposure or imposed a minimum cash balance.
The `watch` thresholds above are descriptive coverage breakpoints, not reserve
requirements. An all-capital proposal remains representable and subject to the
unchanged policy and owner-approval boundaries.

## Decision

The historical shadow pass supports moving to preregistration of a matched
active treatment. It does not justify changing controller thresholds after
seeing these results.

The smallest active design should use only the previous completed period's
frozen signal at the next period boundary. The first period begins with a
starting-state signal. This avoids building a live intraperiod economic model
or adding a new feedback loop before evidence warrants one.

The treatment may receive:

1. the neutral homeostasis signal;
2. the bounded system-preservation objective already specified; and
3. an explicit instruction that greater urgency never increases permissible
   irreversible loss.

The matched control keeps the existing prompt. Seeds, worlds, model tariff,
capital, tool registry, policies, approval boundaries, scoring, and stopping
rules must be frozen before any new result is generated.

## Derived evidence

- `economic_homeostasis_historical_shadow_v1.jsonl`: twelve-record
  tamper-evident shadow chain;
- `economic_homeostasis_historical_shadow_v1_summary.json`: redacted cell and
  arm summaries, assumptions, source hashes, and sensitivity breakpoints.

Derived file hashes:

- sidecar SHA-256:
  `1a4d971584bb6ecaf3296125594e3ccf19e2879354a64838c0d7ce5d2b1ecb80`;
- summary SHA-256:
  `dbfdf08b9d0df733d0355f0df00c20a9bbd6cbaeb0fb1b35c7e1a243ba4526ad`.
