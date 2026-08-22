# CapAge Live Sandbox Pilot v1

Status: bounded pilot layered on the seeded sandbox foundation. It neither
changes the CapAge Constitution nor grants real-world authority.

## What becomes live

Claude Sonnet 5 receives compact observations of one committed synthetic world
and must choose one registered action per decision. It can search the simulated
market, make offers, submit actual text deliverables, request feedback, inspect
the ledger, observe state, or advance time. It receives no prepared job and
cannot call the hidden environment powers.

The runner uses Anthropic's token-count endpoint before every paid request. It
quotes the worst-case input-plus-output cost, blocks a call that would exceed
synthetic capital or the 75-cent external pilot ceiling, and then posts the
provider-reported input and output usage to the synthetic ledger. There are no
automatic provider retries.

## Frozen first run

The committed manifest fixes:

- one seed and a 30-day horizon;
- $250 of synthetic owner capital;
- Claude Sonnet 5 with adaptive thinking at medium effort;
- at most 25 model decisions;
- at most 1,024 output tokens per decision;
- the introductory $2/M input and $10/M output tariff;
- a tariff expiry of August 31, 2026; and
- a hard attributable model-cost ceiling of $0.75.

The runner refuses to use the introductory tariff after its expiry. A new
pricing snapshot must be frozen before another paid run.

## Authority and assessment

Model tool names are translated to the existing agent registry and still pass
through the policy engine and executor. The model cannot assess its own work,
settle payment, post revenue, reveal hidden state, quote its own call, or meter
its own usage.

After a delivery, a versioned deterministic host assessor scores only the
submitted artifact against the public customer need, the promised scope, and
the selected solution tags. It measures completeness, specificity, relevance,
and useful structure. The score and factor breakdown remain host-side; the
agent learns the economic result through observable contract state and through
feedback only if it requests feedback. This simple assessor is suitable for a
first systems pilot, not a final measure of real customer value.

## Reporting and stop conditions

The restricted result artifact contains the verbatim provider response blocks,
tool inputs, executor results, host assessments, provider usage, ledger,
committed-world reveal, and final outcome. The run stops rather than spending
more when the decision, cost, capital, horizon, tariff-validity, schema, or API
boundary is violated.

One run is only a debugging observation. The transcript and actual cost must be
reviewed before authorizing the five-seed pilot; the five-seed pilot must be
reviewed before any larger sample.
