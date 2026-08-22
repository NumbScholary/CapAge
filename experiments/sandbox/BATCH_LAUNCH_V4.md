# Sonnet chaotic batch 004 launch

- Authorized after the user restored Anthropic funding on 2026-08-17.
- Continue with untouched v3 seeds 19 and 20; do not replay censored seed 18.
- Add one freshly generated, unscreened seed to restore 20 completed v3-family samples.
- Manifest: `experiments/sandbox/batch_manifest_v4.json`
- Manifest SHA-256: `bae04422015520952f7597b89791c0d348eefbd16b531b803787fa3b1b0a0910`
- Per-seed external model-cost ceiling: 40 cents.
- Aggregate external model-cost ceiling: 120 cents.
- Never retry a seed after a paid-call or provider ambiguity.
- Stop on any provider, funding, transport, or runner exception.

This marker intentionally triggers the restricted v4 GitHub Actions workflow.
