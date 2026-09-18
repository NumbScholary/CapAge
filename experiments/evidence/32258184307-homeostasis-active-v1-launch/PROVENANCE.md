# Provenance — artifact 9367706448 (`homeostasis-active-v1-launch-restricted`)

Preserved into the repository because GitHub Actions artifact storage is on a
thirty-day retention clock and would have deleted this evidence on
`2026-09-18T13:42:52Z`. Owner ruling 2026-09-18 (see
`.agent-mailbox/claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md`
for the ruling on artifact 9514120954, and this branch's pull request for the
owner's extension of that ruling to the other seven clock-limited artifacts).

| field | value |
|---|---|
| artifact id | `9367706448` |
| artifact name | `homeostasis-active-v1-launch-restricted` |
| workflow run id | `32258184307` |
| run url | https://github.com/NumbScholary/CapAge/actions/runs/32258184307 |
| head branch | `agent/homeostasis-active-v1-launch` |
| head sha | `0a20a407dcf4a51e0881c1269eaf99b6b5987f7b` |
| artifact created | `2026-08-19T13:42:53Z` |
| artifact expiry (GitHub deletion) | `2026-09-18T13:42:52Z` |
| zip size as retrieved | 293,318 bytes |
| zip sha256 | `3ea454e22354953853db40c0f1ae9a8483d1d763cecc021d39e88ea2f8775721` |
| files | 39 |
| extracted bytes | 4,523,827 |
| retrieved | 2026-09-18, read-only, `gh api repos/NumbScholary/CapAge/actions/artifacts/9367706448/zip` |

## What is authoritative

`raw/9367706448.zip` is the byte authority: it is the artifact exactly as GitHub
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
