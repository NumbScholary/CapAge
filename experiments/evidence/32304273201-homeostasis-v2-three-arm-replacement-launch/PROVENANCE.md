# Provenance — artifact 9384729832 (`homeostasis-v2-three-arm-replacement-launch-restricted`)

Preserved into the repository because GitHub Actions artifact storage is on a
thirty-day retention clock and would have deleted this evidence on
`2026-09-18T21:52:30Z`. Owner ruling 2026-09-18 (see
`.agent-mailbox/claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md`
for the ruling on artifact 9514120954, and this branch's pull request for the
owner's extension of that ruling to the other seven clock-limited artifacts).

| field | value |
|---|---|
| artifact id | `9384729832` |
| artifact name | `homeostasis-v2-three-arm-replacement-launch-restricted` |
| workflow run id | `32304273201` |
| run url | https://github.com/NumbScholary/CapAge/actions/runs/32304273201 |
| head branch | `agent/homeostasis-v2-three-arm-replacement-launch` |
| head sha | `3be0750c1e94eeacd12f8c4a1b3beb2266fdab83` |
| artifact created | `2026-08-19T21:52:31Z` |
| artifact expiry (GitHub deletion) | `2026-09-18T21:52:30Z` |
| zip size as retrieved | 475,885 bytes |
| zip sha256 | `7668812c28e7d3fea3ac2a59f467a85f5e07a0f6813bd991ebc72552efaa83d3` |
| files | 58 |
| extracted bytes | 7,568,560 |
| retrieved | 2026-09-18, read-only, `gh api repos/NumbScholary/CapAge/actions/artifacts/9384729832/zip` |

## What is authoritative

`raw/9384729832.zip` is the byte authority: it is the artifact exactly as GitHub
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
