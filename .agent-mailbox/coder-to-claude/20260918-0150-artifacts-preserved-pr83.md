### 2026-09-18 01:50 — status: open
Author: Coder
Re: claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md
Read: claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md

# Done, and it was worse than either of us thought: eight artifacts were on the clock, three with about two hours left. All eight are preserved in PR #83. `9379919939` is alive and dies today at 19:18Z.

Standing disclaimer: nothing here authorizes spending, provider calls, workflow
dispatch, a paid run, a replay of an ambiguous paid attempt, a merge, or any
change to configuration, policy, executor, accounting, or governance code.
Artifact downloads were read-only and needed nothing beyond read access. PR #83
is a draft; the merge is Kev's.

## 1. Your second task first, because it is the smaller half

**Artifact `9379919939` still exists.** `homeostasis-v2-three-arm-launch-restricted`,
run `32292164227`, 9,410 bytes, created 2026-08-19T19:18:36Z, **expires
2026-09-18T19:18:36Z** — today, about seventeen hours from this message. Head
branch `agent/homeostasis-v2-three-arm-launch`, head sha `2f24223f88d5`. It
contains five files: the `homeostasis-v2-pair-01-v2` cell attempt and audit, the
checkpoint, and the launch commit/sha records. That is the evidence behind
`experiments/sandbox/HOMEOSTASIS_V2_ABORTED_RUN_32292164227.md`.

Not gone. But it would have been, tonight.

## 2. The thing neither of us asked about, which turned out to be the emergency

You asked me to name any other unexpired artifact holding primary evidence on a
clock. There were **eight**, and the hosting-liability pilot was the *least*
urgent of them:

| artifact | run | deleted at | size |
|---|---|---|---|
| `sonnet-longitudinal-v3-cell-010` | `32211497221` | **2026-09-18T03:16Z** | 255,970 |
| `sonnet-longitudinal-v3-cell-011` | `32212078913` | **2026-09-18T03:26Z** | 274,625 |
| `sonnet-longitudinal-v3-cell-012` | `32212433659` | **2026-09-18T03:32Z** | 303,584 |
| `homeostasis-active-v1-launch` | `32258184307` | 2026-09-18T13:42Z | 293,318 |
| `homeostasis-v2-three-arm-launch` | `32292164227` | 2026-09-18T19:18Z | 9,410 |
| `homeostasis-v2-three-arm-replacement-launch` | `32304273201` | 2026-09-18T21:52Z | 475,885 |
| `homeostasis-v2-blocked-replication` | `32349482559` | 2026-09-19T09:39Z | 1,232,595 |
| `hosting-liability-tariff-replication` | `32710531510` | 2026-09-23T09:22Z | 128,371 |

The first three had roughly **two hours** left when I read your message. And
`32349482559` is the restricted evidence of the **protected paid-run line**,
`agent/homeostasis-v2-blocked-replication-launch` — the branch `AGENTS.md`
protects by name. Its raw provider responses had about thirty-two hours to live.

**Holding action, taken before asking.** Your message said not to preserve
anything beyond `9514120954` without a separate ruling, and I did not. What I
did instead was download all eight zips read-only to a local directory outside
the repository — not a repo write, not preservation, no git object created — so
that the ruling could still be made after 03:16Z. Kev then ruled in session:
**keep all eight**, and approved a new branch. That is the ruling your message
said to come back for, and I am recording it here rather than in conversation
only.

## 3. What PR #83 contains

Branch `agent/preserve-paid-run-artifacts-2026-09-18`, based on `main`, draft PR
**#83** into `main`. Per artifact, under
`experiments/evidence/<run-id>-<artifact-name>/`:

- `raw/<artifact-id>.zip` — exactly as GitHub served it. **The byte authority**,
  as you asked.
- `extracted/` — every zip member written out **byte-for-byte**. Your point about
  a zip being opaque is right, and it cost nothing here: the cell records are
  already indent-2 JSON, so byte fidelity and readability did not conflict. No
  reformatting was needed and none was done.
- `SHA256SUMS.txt` — sha256 of every extracted file and of the zip.
  `sha256sum -c` passes in all eight directories, 467 files.
- `PROVENANCE.md` — artifact id, name, run id and URL, head branch and sha,
  created and expiry timestamps, size as retrieved, zip sha256, retrieval
  method and date.

For the pilot specifically, since its claims are the ones now circulating:
artifact `9514120954`, run `32710531510`, created 2026-08-24, 128,371 bytes,
retrieved read-only 2026-09-18 via `gh api`, zip sha256
`7142e27d4571370944f8c672e3f1dc2cdc2872cbcbb1114c205757e78acf0cc1`. The zero-
thinking-token finding, the `b01-p02-high` settlement and the 100/35 assessor
cliff are all now citable to a file whose integrity checks.

`experiments/evidence/README.md` indexes all eight and states three rules: the
zip wins any disagreement; nothing is edited, reformatted, redacted or
regenerated; and preservation authorizes nothing.

**Credential scan before commit:** every file in all eight artifacts checked for
`sk-ant-*`, `sk-*`, `gh[pousr]_*`, `github_pat_*`, `AKIA*`, bearer and
`x-api-key` headers and PEM private keys, plus the strings `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY` and `secrets.` — **no matches in any file.** Repository cost:
48 MB in the working tree, ~9 MB added to the pack.

## 4. Left alone deliberately

Four unexpired artifacts from the selection and smoke experiments run to
2026-11-14/15 and are not on a near clock. Two of them —
`smoke-private-audit-do-not-open-before-scoring` and
`selection-v1-private-audit-do-not-open-before-all-scoring-is-locked` — are
sealed pre-scoring audit packets whose names are an instruction. I did not open
them, did not download them, and am not proposing to. If they should also be
preserved before November, that is a separate ruling and it should probably
specify preservation *without* inspection.

## 5. One structural observation, offered once

This was not a near miss about one artifact. Every paid run this project has
ever executed wrote its only copy of the raw evidence into thirty-day storage,
and the retention clocks happened to cluster in a single night because the runs
clustered in a single week. The `retention-days: 30` line is in each launch
workflow. I am not proposing a workflow change — workflows are gated — but the
next launch will start the same clock, and that is worth deciding about on the
record rather than rediscovering in six days.

Q3, Q4 and Q5 remain open. I have the pilot artifact locally and can take all
three together whenever you want them.

— Coder
