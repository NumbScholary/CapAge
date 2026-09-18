# Preserved paid-run evidence

GitHub Actions artifacts expire. Every paid CapAge run's restricted evidence was
uploaded as an Actions artifact with thirty-day retention, which means the raw
provider responses, usage records, audit trails and world reveals behind the
project's cost and outcome claims were sitting on a deletion clock and were not
durable. Eight of them were within thirty-two hours of deletion when this was
noticed on 2026-09-18. This directory is the durable copy.

Each subdirectory holds one artifact: `raw/<id>.zip` exactly as GitHub served it,
`extracted/` with every member written out byte-for-byte, `SHA256SUMS.txt` over
both, and `PROVENANCE.md` recording artifact id, run id, head branch and sha,
creation and expiry timestamps, size, retrieval method and the zip's sha256.

| directory | artifact | run | created | would have expired | zip bytes | files |
|---|---|---|---|---|---|---|
| [`32211497221-sonnet-longitudinal-v3-cell-010`](32211497221-sonnet-longitudinal-v3-cell-010/) | `9350907989` | `32211497221` | 2026-08-19 | **2026-09-18T03:16:22Z** | 255,970 | 51 |
| [`32212078913-sonnet-longitudinal-v3-cell-011`](32212078913-sonnet-longitudinal-v3-cell-011/) | `9351095443` | `32212078913` | 2026-08-19 | **2026-09-18T03:26:09Z** | 274,625 | 56 |
| [`32212433659-sonnet-longitudinal-v3-cell-012`](32212433659-sonnet-longitudinal-v3-cell-012/) | `9351223031` | `32212433659` | 2026-08-19 | **2026-09-18T03:32:42Z** | 303,584 | 61 |
| [`32258184307-homeostasis-active-v1-launch`](32258184307-homeostasis-active-v1-launch/) | `9367706448` | `32258184307` | 2026-08-19 | **2026-09-18T13:42:52Z** | 293,318 | 39 |
| [`32292164227-homeostasis-v2-three-arm-launch`](32292164227-homeostasis-v2-three-arm-launch/) | `9379919939` | `32292164227` | 2026-08-19 | **2026-09-18T19:18:36Z** | 9,410 | 5 |
| [`32304273201-homeostasis-v2-three-arm-replacement-launch`](32304273201-homeostasis-v2-three-arm-replacement-launch/) | `9384729832` | `32304273201` | 2026-08-19 | **2026-09-18T21:52:30Z** | 475,885 | 58 |
| [`32349482559-homeostasis-v2-blocked-replication`](32349482559-homeostasis-v2-blocked-replication/) | `9401291547` | `32349482559` | 2026-08-20 | **2026-09-19T09:39:46Z** | 1,232,595 | 150 |
| [`32710531510-hosting-liability-tariff-replication`](32710531510-hosting-liability-tariff-replication/) | `9514120954` | `32710531510` | 2026-08-24 | **2026-09-23T09:22:39Z** | 128,371 | 22 |

## Rules

- **The zip is the authority.** `extracted/` exists so the evidence can be read,
  diffed, grepped and cited by line; if the two ever disagree, the zip wins.
- **Read-only.** Nothing here is edited, reformatted, redacted or regenerated.
  Preserved usage, cost, artifact and failure records remain binding evidence
  under `AGENTS.md`, including for any attempt that failed or was retired.
- **No authority.** Preserving evidence authorizes nothing: no provider call, no
  rerun, no replay of an ambiguous paid attempt, no spending.
- Every file was scanned for credential patterns before commit; no secret values
  are present. The GitHub secret *names* used by these workflows are public;
  their values are not in the repository and are not in these artifacts.

## Not preserved here

Four unexpired artifacts from the selection and smoke experiments
(`smoke-judge-packets`, `smoke-private-audit-do-not-open-before-scoring`,
`smoke-v2-*`, `selection-v1-*`) run to November 2026 and are not on a near clock.
Two of them are sealed pre-scoring audit packets whose names say they must not be
opened before scoring is locked, so they are left alone pending a separate owner
ruling.
