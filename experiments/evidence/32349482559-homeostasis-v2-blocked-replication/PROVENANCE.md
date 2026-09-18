# Provenance — artifact 9401291547 (`homeostasis-v2-blocked-replication-restricted`)

Preserved into the repository because GitHub Actions artifact storage is on a
thirty-day retention clock and would have deleted this evidence on
`2026-09-19T09:39:46Z`. Owner ruling 2026-09-18 (see
`.agent-mailbox/claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md`
for the ruling on artifact 9514120954, and this branch's pull request for the
owner's extension of that ruling to the other seven clock-limited artifacts).

| field | value |
|---|---|
| artifact id | `9401291547` |
| artifact name | `homeostasis-v2-blocked-replication-restricted` |
| workflow run id | `32349482559` |
| run url | https://github.com/NumbScholary/CapAge/actions/runs/32349482559 |
| head branch | `agent/homeostasis-v2-blocked-replication-launch` |
| head sha | `df3307eaa385372cfd8026e8fb151dad86b82732` |
| artifact created | `2026-08-20T09:39:47Z` |
| artifact expiry (GitHub deletion) | `2026-09-19T09:39:46Z` |
| zip size as retrieved | 1,232,595 bytes |
| zip sha256 | `65f4370ad8ef76011e27598796c2991c905d2f7d58d1e7879234f04d1c269f65` |
| files | 150 |
| extracted bytes | 18,788,178 |
| retrieved | 2026-09-18, read-only, `gh api repos/NumbScholary/CapAge/actions/artifacts/9401291547/zip` |

## What is authoritative

`raw/9401291547.zip` is the byte authority: it is the artifact exactly as GitHub
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
