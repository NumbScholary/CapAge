# Sonnet chaotic batch 003 launch

- Authorized by the user on 2026-08-17.
- Run 20 fresh, unscreened seeds exactly once and in their frozen order.
- Manifest: `experiments/sandbox/batch_manifest_v3.json`
- Manifest SHA-256: `7396f70b6f74e9641c9cd9ed919b86f90c48831741e1283d3aa8af1e4aa3a5c7`
- Per-seed external model-cost ceiling: 40 cents.
- Aggregate external model-cost ceiling: 500 cents.
- Never retry a seed after a paid-call or provider ambiguity.
- Stop the batch on any provider, funding, transport, or runner exception.

This marker intentionally triggers the restricted v3 GitHub Actions workflow.
