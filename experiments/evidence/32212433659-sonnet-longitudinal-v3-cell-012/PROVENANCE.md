# Provenance — artifact 9351223031 (`sonnet-longitudinal-v3-cell-012-restricted`)

Preserved into the repository because GitHub Actions artifact storage is on a
thirty-day retention clock and would have deleted this evidence on
`2026-09-18T03:32:42Z`. Owner ruling 2026-09-18 (see
`.agent-mailbox/claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md`
for the ruling on artifact 9514120954, and this branch's pull request for the
owner's extension of that ruling to the other seven clock-limited artifacts).

| field | value |
|---|---|
| artifact id | `9351223031` |
| artifact name | `sonnet-longitudinal-v3-cell-012-restricted` |
| workflow run id | `32212433659` |
| run url | https://github.com/NumbScholary/CapAge/actions/runs/32212433659 |
| head branch | `agent/longitudinal-v3-cell-012-launch` |
| head sha | `594e55cbb61f45d86cd7d36824a2b8edb60c9d86` |
| artifact created | `2026-08-19T03:32:44Z` |
| artifact expiry (GitHub deletion) | `2026-09-18T03:32:42Z` |
| zip size as retrieved | 303,584 bytes |
| zip sha256 | `18f7e0371964544f6b82541814fdded0d35dd03b79eabd1e5248e68b130e0412` |
| files | 61 |
| extracted bytes | 4,430,306 |
| retrieved | 2026-09-18, read-only, `gh api repos/NumbScholary/CapAge/actions/artifacts/9351223031/zip` |

## What is authoritative

`raw/9351223031.zip` is the byte authority: it is the artifact exactly as GitHub
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
