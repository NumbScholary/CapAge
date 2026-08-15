# Experiment 0 — Selecting CapAge's Brain

## Purpose

Select the primary strategic model for CapAge v0.1 using a reproducible, provider-neutral, blinded evaluation rather than brand preference or token price alone.

## Primary question

Which candidate produces the greatest useful governed autonomous work per attributable economic cost under CapAge-like conditions?

## Candidates

Candidate model identities MUST be concealed from human and automated judges until scoring is locked. Provider/model mappings are maintained separately from evaluation artifacts.

Initial intended candidates are one current OpenAI strategic model and one current Anthropic strategic model. Exact model/version identifiers, reasoning settings, API parameters, and prices MUST be recorded before execution and frozen for a run.

## Pre-registration rule

Before any scored model output is inspected, freeze candidate configurations, scenarios, tools/permissions, context, resource limits, scoring rubric and weights, success criteria, decision rule, randomization procedure, and exclusion/rerun rules. Changes after outputs are observed create a new experiment version and MUST NOT silently replace the original protocol.

## Current preregistration state

`RUBRIC.md` and scenarios `E0-001` through `E0-010` in `scenarios.json` are frozen as the **Experiment 0 smoke benchmark** as of this commit. They MUST NOT be edited after candidate outputs are inspected. Corrections or expansion require new scenario IDs and an explicitly versioned benchmark run.

The intended 30–50 scenario full benchmark remains unfrozen until its additional scenarios are authored. Smoke-benchmark results MUST NOT be represented as full-benchmark results.

## Blinding

A runner assigns opaque candidate IDs. The identity mapping is not included in judge-visible artifacts. For every subjective pairwise comparison, presentation order is independently randomized. The reveal occurs only after human scores, automated scores, exclusions, and objective measurements are locked.

## Measurements

Record objective measurements separately from subjective judgments: task success/failure, policy violations proposed, unauthorized execution attempts, human interventions, tool-call validity, input/output tokens where available, API cost, latency, completion/recovery behavior, and attributable external-resource cost.

## Human scoring

Judge without model identity using the 0–5 anchors and weights frozen in `RUBRIC.md`. Judges must not infer or record provider identity while scoring.

## Automated judging

Automated judging is secondary evidence, not ground truth. Pairwise LLM judging must use mirrored comparisons (A vs B and B vs A). A substantive winner reversal is flagged as position-unstable and excluded from simple win counts or analyzed separately. Automated judges MUST NOT receive provider/model identity.

## Primary economic metric

    attributable API + external resource dollars / successful governed objective

Report this alongside success rate and quality. A cheap model that routinely fails is not economically cheap.

## Required result table

For each blinded candidate report at minimum: successful governed objectives / attempted objectives; success rate; mean locked human quality score; policy violations per 100 trials; human interventions per successful objective; total attributable model cost; cost per successful governed objective; and uncertainty intervals where statistically appropriate.

## Decision rule

No candidate wins merely because it has the lowest token price or highest benchmark score. A candidate may be selected as primary only if its governed task performance and economic efficiency are acceptable under the pre-registered thresholds. Meaningful tradeoffs may justify provider-neutral routing rather than a universal winner. If evidence is insufficient, the result is **INCONCLUSIVE** and the experiment is expanded before deployment.

## Integrity requirements

Preserve all raw outputs including failures; never delete inconvenient trials; record reruns and reasons; do not retroactively alter costs; do not let candidate models grade themselves as sole judge; do not expose identity mapping before scores are locked; and keep the CapAge enforcement kernel independent of model provider.

## Reveal

After scoring is locked, hash the result artifact containing frozen scores, then reveal the opaque-ID mapping and compute provider/model-labeled summaries. Preserve the pre-reveal artifacts for auditability.
