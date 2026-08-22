# Matched longitudinal launch v3

## Frozen question

Does outcome-complete, host-owned durable memory improve Sonnet 5's economic
performance across six matched simulated months without increasing real-world
authority?

The primary outcome is the paired memory-minus-control difference in monthly
net economic change. Memory-record presence is a framework-integrity check, not
economic success. Secondary descriptive outcomes are delivery disputes,
accepted deliveries, customer payment defaults, recorded satisfaction,
reputation change, and attributable model cost.

## Preregistration

The six month seeds and customer-population seed were derived mechanically on
August 18, 2026, without generating or inspecting their worlds. For each
purpose, compute:

```text
100000 + (int(sha256("capage-longitudinal-v3|unseen-seed-v1|" + purpose)[:12], 16) mod 900000)
```

The purposes are `month-001` through `month-006` and
`customer-population`. The resulting values are frozen in
`longitudinal_manifest_v3.json`; none appears in the prior longitudinal v2
manifest.

The memory and control arms receive each same month seed and the same stable
customer population. Each arm carries separate capital, customer history, and
reputation. Only the memory arm receives host-owned durable memory. Execution
order alternates by month under the runner.

Do not change the framework, seeds, primary outcome, scoring, or interpretation
in response to results observed during the six matched months. Stop only for a
provider, infrastructure, accounting, safety, tariff, funding, or integrity
failure. Any framework change requires a separately versioned experiment with
new seeds.

## Cost and pricing boundary

The manifest freezes Anthropic's introductory Sonnet 5 API tariff of 200 cents
per million input tokens and 1,000 cents per million output tokens, published
as valid through August 31, 2026. The model has a 1,024-token output ceiling and
medium effort. Each arm-month is capped at 75 cents, each arm reserves 450
cents, and the experiment-wide ceiling is 900 cents. These are maximums, not a
spending instruction.

Pricing, model availability, the repository secret, and the Anthropic account
balance must be checked immediately before Cell 001. The runner stops before a
paid attempt if the frozen tariff has expired.

## Cell cadence and interpretation

One GitHub launch branch may authorize exactly one paid cell. Two successful
cells complete one matched month. A started cell is never automatically
replayed after ambiguity or process death. Continue only from the exact
restricted checkpoint artifact and verify its hashes before the next cell.

The six-month result is descriptive evidence, not proof. A positive memory
effect may justify a separately preregistered transfer evaluation. A
nonpositive effect does not justify altering seeds or rerunning individual
cells.

## Disabled launch boundary

This preregistration does not include the Cell 001 authorization marker. The
included workflow listens only on the future branch
`agent/longitudinal-v3-cell-001-launch` and requires the exact marker text
`CAPAGE_LONGITUDINAL_V3_CELL_001_MAX_75_CENTS`. Merging the preparation PR
cannot call Anthropic or spend funds.

Validate locally without constructing a provider client:

```bash
python -m capage.longitudinal_v3 \
  experiments/sandbox/longitudinal_manifest_v3.json \
  --checkpoint /tmp/capage-v3-validation-checkpoint.json \
  --artifact-dir /tmp/capage-v3-validation-months \
  --memory /tmp/capage-v3-validation-memory.sqlite3 \
  --validate-only
```

Paid execution additionally requires the literal CLI confirmation
`--confirm RUN_MATCHED_LONGITUDINAL_V3`.
