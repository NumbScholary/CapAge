# Homeostasis V2 blocked replication result

GitHub Actions run [`32349482559`](https://github.com/Numbscholar/CapAge/actions/runs/32349482559)
executed on August 20, 2026 completed all 48 preregistered cells with no
transport, provider, runner, validation, or integrity errors. This is the
result of the replication preregistered in `HOMEOSTASIS_V2_REPLICATION_PREREG.md`
and materialized in `HOMEOSTASIS_V2_REPLICATION_MATERIALIZATION.md`, launched
by pushing authorization commit `df3307eaa385372cfd8026e8fb151dad86b82732`
(binding phrase `RUN_HOMEOSTASIS_V2_BLOCKED_REPLICATION_AT_059bc036d9ebb5103effd27e2262313078d2c5c1_MAX_2160_CENTS`)
to `agent/homeostasis-v2-blocked-replication-launch`.

## Cost

Total attributable model cost was 1,292,405,000 cost units (**$12.92**),
against a per-cell cap of 45 cents and an aggregate cap of $21.60. This is
close to the preregistered estimate of approximately $13.70 and well under
the hard ceiling.

## Gate outcome

All eight frozen gate criteria passed:

| Criterion | Result |
|---|---|
| All 48 cells valid and complete | pass |
| No V2 insolvency, functional, or constitutional-boundary failure | pass |
| Zero invalid V2 deliveries crossed the customer boundary | pass |
| V2 aggregate dispute rate not above V1 | pass |
| V2 aggregate block-ending reputation not below V1 | pass |
| V2 summed block-ending capital not below V1 | pass |
| V2 not below V1 in at least four of eight blocks | pass (7 of 8) |
| V2 model cost not above 125% of V1 model cost | pass |

**Classification: `advance_to_another_larger_synthetic_test`.**

## Primary estimands

| Metric (summed across 8 blocks) | V1 | V2 | V2 − V1 |
|---|---|---|---|
| Block-ending capital | $2,165.15 | $3,000.14 | +$834.99 |
| Block-ending global reputation | −150 | +276 | +426 |
| Earned revenue | $175.00 | $1,010.00 | +$835.00 |
| Delivery dispute rate | 73.3% | 0.0% | −73.3 pts |
| Contracts paid | 4 | 19 | +15 |
| Contracts disputed | 11 | 0 | −11 |
| Invalid deliveries crossing customer boundary | 11 | 0 | −11 |

V2 led V1 in block-ending capital in 7 of the 8 blocks; the single block where
V1 led (block 2) was by $9.96, the smallest margin observed in either
direction.

## Interpretation

Per the frozen preregistration, this is a small-sample engineering
replication, not a statistically significant result
(`small_sample_warning: directional blocked engineering replication; no
statistical-significance claim`). Passing authorizes only another larger
synthetic test. It does not authorize deployment, real-world economic action,
contracts, publication, recapitalization, or expanded CapAge authority
(`deployment_authorized: false`).

## Evidence

Raw provider transcripts, per-cell audit logs, and the full checkpoint remain
restricted in Actions artifact `homeostasis-v2-blocked-replication-restricted`
(artifact ID `9401291547`), retained 30 days. `analysis.json` in that artifact
is the authoritative machine-readable result; this document summarizes it and
is not a substitute for it.
