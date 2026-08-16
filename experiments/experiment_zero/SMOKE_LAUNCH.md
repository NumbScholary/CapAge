# Experiment 0 Smoke v2 Launch

Launch the corrected, blinded, non-selection smoke run using `smoke_manifest_v2.json` and exactly scenarios E0-001 through E0-010.

The original smoke attempt (workflow run 31940697619) remains preserved as a failed historical attempt: it unintentionally scheduled 14 scenarios and suffered OpenAI provider failures. Smoke v2 does not overwrite or reinterpret those artifacts.

Smoke v2 must produce exactly 20 complete judge-visible packets: two opaque candidates across ten scenarios. Structural validation must pass before artifacts are accepted.
