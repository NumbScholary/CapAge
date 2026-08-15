# Experiment 0 — Selecting CapAge's Brain

This directory contains the pre-registered benchmark used to select CapAge's strategic model.

## Current artifacts

- `PROTOCOL.md` — experimental design, blinding, measurements, and decision rules.
- `RUBRIC.md` — locked human/automated evaluation dimensions and hard-failure overlay.
- `scenarios.json` — initial frozen scenario suite.

## Status

**DESIGN / NOT YET RUN.**

Do not treat any candidate as the winner until the scenario set, rubric, candidate configuration, runner, and reveal procedure are frozen and a complete blinded run has been scored.

The initial ten scenarios are a minimum smoke benchmark, not yet the intended full 30–50 scenario evaluation. They deliberately test different failure modes before expanding the suite.

## Next implementation increment

Build a provider-neutral runner that:

1. loads frozen scenarios;
2. invokes candidate adapters under equivalent settings;
3. assigns opaque IDs;
4. randomizes judge-visible order;
5. stores raw outputs and usage/cost metadata separately;
6. emits blinded judging packets;
7. hashes the locked score artifact before reveal; and
8. reveals model identity only in a separate finalization step.
