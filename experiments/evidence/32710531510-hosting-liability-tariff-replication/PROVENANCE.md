# Provenance — artifact 9514120954 (`hosting-liability-tariff-replication-restricted`)

Preserved into the repository because GitHub Actions artifact storage is on a
thirty-day retention clock and would have deleted this evidence on
`2026-09-23T09:22:39Z`. Owner ruling 2026-09-18 (see
`.agent-mailbox/claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md`
for the ruling on artifact 9514120954, and this branch's pull request for the
owner's extension of that ruling to the other seven clock-limited artifacts).

| field | value |
|---|---|
| artifact id | `9514120954` |
| artifact name | `hosting-liability-tariff-replication-restricted` |
| workflow run id | `32710531510` |
| run url | https://github.com/NumbScholary/CapAge/actions/runs/32710531510 |
| head branch | `agent/hosting-liability-tariff-replication-launch` |
| head sha | `6fa542a663868f16a20d0f3df6e3d085dfcc6714` |
| artifact created | `2026-08-24T09:22:39Z` |
| artifact expiry (GitHub deletion) | `2026-09-23T09:22:39Z` |
| zip size as retrieved | 128,371 bytes |
| zip sha256 | `7142e27d4571370944f8c672e3f1dc2cdc2872cbcbb1114c205757e78acf0cc1` |
| files | 22 |
| extracted bytes | 1,869,115 |
| retrieved | 2026-09-18, read-only, `gh api repos/NumbScholary/CapAge/actions/artifacts/9514120954/zip` |

## What is authoritative

`raw/9514120954.zip` is the byte authority: it is the artifact exactly as GitHub
served it, unmodified. `extracted/` holds each member of that zip written out
byte-for-byte, so the evidence is diffable, greppable and citable by line.
`SHA256SUMS.txt` carries the sha256 of every extracted file and of the zip;
if the extraction and the zip ever disagree, the zip wins.

Verify with:

```bash
sha256sum -c SHA256SUMS.txt
```

## Handling

Read-only preservation. No file here was edited, reformatted, redacted or
regenerated. Nothing here authorizes a provider call, a rerun, a replay of an
ambiguous paid attempt, or any spending. Preserved usage and cost records remain
binding evidence under `AGENTS.md`.

Scanned before commit for provider and platform credential patterns
(`sk-ant-*`, `sk-*`, `gh[pousr]_*`, `github_pat_*`, `AKIA*`, bearer and
`x-api-key` headers, PEM private keys) and for the strings `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY` and `secrets.`: no matches in any file.
