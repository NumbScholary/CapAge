# Transfer Test v1 Launch

Do not run this test until longitudinal v2 completed successfully and its
checkpoint and memory database have been copied to durable storage.

Manifest validation is free and does not construct an Anthropic client:

```bash
python -m capage.transfer \
  experiments/sandbox/transfer_manifest_v1.json \
  --validate-only
```

Immediately before a paid run, verify the model identifier, tariff, tariff
expiry, Anthropic balance, source checkpoint, source memory backup, and the
900-cent aggregate ceiling. Then use explicit paths and the exact confirmation
phrase:

```bash
python -m capage.transfer \
  experiments/sandbox/transfer_manifest_v1.json \
  --source-checkpoint artifacts/longitudinal/checkpoint.json \
  --source-memory artifacts/longitudinal/memory.sqlite3 \
  --checkpoint artifacts/transfer/checkpoint.json \
  --artifact-dir artifacts/transfer/cells \
  --max-cells 1 \
  --confirm RUN_PREREGISTERED_TRANSFER_V1
```

Begin with one cell, inspect the attempt, result, audit, cost, checkpoint, and
source-memory hashes, and only then resume. Never delete an orphaned attempt
marker to force a paid retry.
