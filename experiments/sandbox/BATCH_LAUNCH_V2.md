# Sonnet Chaotic Sandbox Batch v2 Launch Marker

This continuation contains only the four untouched seeds remaining after the
first batch stopped on an Anthropic HTTP 502. Seed 98642384 is preserved as an
interrupted run and is not retried.

The first batch recorded 0.5546 cents of known model usage before the provider
error. This continuation's shared hard ceiling is reduced to $1.96, leaving
conservative room for the possibility that the failed request was processed
without a response while keeping the combined batch near the original $2.00
authorization. The secondary per-seed ceiling remains 40 cents.

All worlds remain fresh and unscreened. The controller performs no automatic
retries, proceeds only between distinct seeds after ordinary model failures,
and stops again on any provider, funding, transport, or runner exception.

Launch nonce: `four-untouched-seeds-2026-08-17T19:37:53Z`.
