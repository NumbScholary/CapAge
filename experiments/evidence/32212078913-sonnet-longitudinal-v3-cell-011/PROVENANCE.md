# Provenance — artifact 9351095443 (`sonnet-longitudinal-v3-cell-011-restricted`)

Preserved into the repository because GitHub Actions artifact storage is on a
thirty-day retention clock and would have deleted this evidence on
`2026-09-18T03:26:09Z`. Owner ruling 2026-09-18 (see
`.agent-mailbox/claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md`
for the ruling on artifact 9514120954, and this branch's pull request for the
owner's extension of that ruling to the other seven clock-limited artifacts).

| field | value |
|---|---|
| artifact id | `9351095443` |
| artifact name | `sonnet-longitudinal-v3-cell-011-restricted` |
| workflow run id | `32212078913` |
| run url | https://github.com/NumbScholary/CapAge/actions/runs/32212078913 |
| head branch | `agent/longitudinal-v3-cell-011-launch` |
| head sha | `918ead1a80f1fffec498824c180a36765387625f` |
| artifact created | `2026-08-19T03:26:10Z` |
| artifact expiry (GitHub deletion) | `2026-09-18T03:26:09Z` |
| zip size as retrieved | 274,625 bytes |
| zip sha256 | `69d312f28825c6cf6e4e5f6ca6da44ec2ae108aef7d16978837e5accf52552cd` |
| files | 56 |
| extracted bytes | 3,905,803 |
| retrieved | 2026-09-18, read-only, `gh api repos/NumbScholary/CapAge/actions/artifacts/9351095443/zip` |

## What is authoritative

`raw/9351095443.zip` is the byte authority: it is the artifact exactly as GitHub
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
