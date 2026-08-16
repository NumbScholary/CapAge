# Experiment 0 — Selecting CapAge's Brain

This directory contains the blinded benchmark protocol and provider-neutral runner.

## Artifacts

- `PROTOCOL.md` — frozen execution, failure, decision, inconclusive, and reveal rules.
- `RUBRIC.md` — evaluation dimensions and hard-failure overlay.
- `scenarios.json` — frozen ten-scenario smoke suite.
- `adversarial_scenarios.json` and `cooperative_scenarios.json` — frozen adversarial and cooperative portions of the 30-scenario selection suite.
- `manifest.example.json` — private run-configuration template.
- `scores.example.json` — locked scoring/measurement input shape for the decision command.
- `runner.py` — standard-library seal, randomized execution, decision, and reveal tool.
- `test_runner.py` — runner integrity tests.

## Status

**30-SCENARIO SUITE IMPLEMENTED / NOT YET SEALED OR RUN.** The smoke suite can validate the machinery but must return `INCONCLUSIVE`. The selection suite is complete; exact candidate configurations and adapters must be filled in before sealing.

## Lifecycle

Provider adapters are separate executables. Each reads one JSON request from standard input and emits one JSON object containing at least an `output` string.

1. Copy and complete `manifest.example.json` outside judge-visible artifacts.
2. Smoke seal: `python runner.py seal private_manifest.json artifacts/sealed_manifest.json`.
3. Selection seal: add `--selection`; the runner rejects suites below 30 scenarios.
4. Store `private_mapping.json` separately.
5. Execute: `python runner.py run private_manifest.json artifacts/sealed_manifest.json artifacts/private_mapping.json artifacts/raw_trials.json`.
6. Human judges score `judge_packets.json` without opening private files. Lock scores and objective measurements.
7. Decide: `python runner.py decide locked_scores.json artifacts/locked_result.json`.
8. Externally timestamp the locked result, then reveal: `python runner.py reveal artifacts/locked_result.json artifacts/private_mapping.json artifacts/sealed_manifest.json artifacts/revealed_result.json`.

Commands refuse to overwrite audit artifacts. Corrections and expansions use a new directory and experiment version.
