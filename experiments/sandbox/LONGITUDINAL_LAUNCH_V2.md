# Matched longitudinal launch v2

This launch remains unpaid and disabled by default. The six month seeds and
customer-population seed in `longitudinal_manifest_v2.json` were frozen before
any model outputs were observed for them. Do not inspect their hidden worlds or
change them in response to results.

Validate without contacting Anthropic:

```bash
python -m capage.longitudinal \
  experiments/sandbox/longitudinal_manifest_v2.json \
  --checkpoint artifacts/longitudinal-v2/checkpoint.json \
  --artifact-dir artifacts/longitudinal-v2/months \
  --memory artifacts/longitudinal-v2/memory.sqlite3 \
  --validate-only
```

Paid execution additionally requires the exact command-line confirmation
`--confirm RUN_MATCHED_LONGITUDINAL_V2`. The manifest permits at most 450 cents
per arm and 900 cents total. A started attempt is never automatically replayed,
even if the process stops before an audit or result file can be written.

Do not authorize the paid command until PR review, the dependency-free quality
gate, current-price verification, and account-balance review are complete.
