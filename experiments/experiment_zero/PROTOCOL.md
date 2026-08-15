# Experiment 0 — Selecting CapAge's Brain

## Purpose

Select the primary strategic model for CapAge v0.1 using a reproducible, provider-neutral, blinded evaluation rather than brand preference or token price alone.

## Primary question

Which candidate produces the greatest useful governed autonomous work per attributable economic cost under CapAge-like conditions?

## Candidates

Candidate model identities MUST be concealed from human and automated judges until scoring is locked. Provider/model mappings are maintained separately from evaluation artifacts.

Initial intended candidates are one current OpenAI strategic model and one current Anthropic strategic model. Exact model/version identifiers, reasoning settings, API parameters, and prices MUST be recorded before execution and frozen for a run.

## Pre-registration rule

Before any scored model output is inspected, freeze:

1. candidate model/version identifiers and inference settings;
2. scenario set;
3. tool interfaces and permissions;
4. context supplied to each candidate;
5. per-scenario resource limits;
6. scoring rubric and weights;
7. success/failure criteria;
8. tie/escalation rule;
9. randomization seed or committed randomization procedure; and
10. exclusion and rerun rules.

Changes after outputs are observed create a new experiment version and MUST NOT silently replace the original protocol.

## Blinding

A runner assigns opaque candidate IDs. The identity mapping is not included in judge-visible artifacts.

For every subjective pairwise comparison, presentation order is independently randomized. Judges see only Candidate A and Candidate B for that trial.

The reveal occurs only after all human scores, automated scores, exclusions, and objective measurements are locked.

## Scenario domains

The frozen suite should sample at least:

- opportunity discovery;
- economic research and evidence synthesis;
- strategic planning under scarce capital;
- budgeting and cost awareness;
- tool selection and structured tool calls;
- recognizing scams and adversarial instructions;
- prompt-injection resistance;
- accounting and subsidy awareness;
- recovery after failed actions;
- uncertainty calibration and requests for information;
- deciding not to act when expected value is poor; and
- sustained multi-cycle execution.

Scenarios MUST NOT encode a preferred business model for CapAge.

## Measurements

Record objective measurements separately from subjective judgments:

- task success/failure;
- policy violations proposed;
- unauthorized execution attempts;
- human interventions required;
- tool-call validity;
- input/output tokens where available;
- API cost in USD;
- wall-clock latency;
- completion/recovery behavior; and
- attributable external-resource cost.

## Human scoring

Judge without model identity. Score each applicable dimension from 0–5 using written anchors defined before the run:

- economic judgment;
- reasoning quality;
- factual reliability;
- strategic usefulness;
- cost awareness;
- appropriate tool use;
- policy/governance awareness;
- recovery and adaptation; and
- objective completion.

A separate rubric file will contain the anchors. Judges must not infer or record provider identity while scoring.

## Automated judging

Automated judging is secondary evidence, not ground truth. If pairwise LLM judging is used, run mirrored comparisons (A vs B and B vs A). A substantive winner reversal is flagged as position-unstable and excluded from simple win counts or analyzed separately.

Automated judges MUST NOT receive provider/model identity.

## Primary economic metric

The primary deployment-oriented metric is:

    attributable API + external resource dollars / successful governed objective

This is reported alongside, not instead of, success rate and quality. A cheap model that routinely fails is not economically cheap.

## Required result table

For each blinded candidate report at minimum:

- successful governed objectives / attempted objectives;
- success rate;
- mean locked human quality score;
- policy violations per 100 trials;
- human interventions per successful objective;
- total attributable model cost;
- cost per successful governed objective; and
- uncertainty intervals where statistically appropriate.

## Decision rule

No candidate wins merely because it has the lowest token price or highest benchmark score.

A candidate may be selected as primary only if its governed task performance and economic efficiency are acceptable under the pre-registered thresholds. If candidates exhibit meaningful tradeoffs rather than clear dominance, the result may justify a provider-neutral routing architecture (for example routine versus escalation tiers) rather than declaring a universal winner.

If the evidence is insufficient, the correct result is INCONCLUSIVE and the experiment is expanded before deployment.

## Integrity requirements

- Preserve all raw outputs, including failures.
- Never delete inconvenient trials.
- Record reruns and their reasons.
- Do not retroactively alter costs.
- Do not let candidate models grade themselves as the sole judge.
- Do not expose the identity mapping before scores are locked.
- Keep the CapAge enforcement kernel independent of the model provider.

## Reveal

After scoring is locked, generate a signed/hashed result artifact containing the frozen scores, then reveal the opaque-ID mapping and compute provider/model-labeled summaries. The pre-reveal artifacts remain preserved for auditability.
