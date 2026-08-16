# Experiment 0 — Selecting CapAge's Brain

## Purpose and primary question

Select the primary strategic model for CapAge v0.1 using a reproducible, provider-neutral, blinded evaluation. Which candidate produces the greatest useful governed autonomous work per attributable economic cost under CapAge-like conditions?

## Candidates and preregistration

Candidate identities MUST be concealed from human and automated judges until scoring is locked. Exact provider, model/version, reasoning settings, API parameters, prices, tools, permissions, context, limits, scoring rules, success criteria, decision rule, seed, and exclusion/rerun rules MUST be recorded and frozen before any scored output is inspected.

Changes after outputs are observed create a new experiment version and MUST NOT replace the original result. `RUBRIC.md` and `E0-001` through `E0-010` are the frozen smoke benchmark. The combined suite—`E0-001` through `E0-014`, `E0-A01` through `E0-A08`, and `E0-C01` through `E0-C08`—is the frozen 30-scenario selection benchmark as of this commit. A manifest must name and hash all three scenario files. The ten-scenario smoke test MUST return **INCONCLUSIVE** and cannot select a production model.

## Provider-neutral execution

Candidates receive the same scenario text, common context, declared tools, trials, timeout, and retry opportunity. Execution order is deterministically shuffled from the sealed seed. Provider adapters may translate the common request into an API call but may not add substantive instructions, tools, retrieval, memory, or human help for only one candidate.

Provider features that cannot be made equivalent MUST be disabled or declared before sealing. Exact settings and resource limits are recorded even when providers use different parameter names. Prices are frozen with currency and effective timestamp. Cached tokens, reasoning tokens, tool charges, taxes, credits, and external-resource costs are recorded without silently treating provider differences as free.

An automated judge sharing a provider with a candidate remains secondary evidence, judges every candidate symmetrically, and cannot be the sole basis for selection. Judge-visible artifacts remove provider/model names, headers, usage data, error formats, and other avoidable identity clues.

## Blinding and scoring

The runner assigns opaque IDs; the identity mapping is absent from judge-visible artifacts. Subjective pairwise order is independently randomized. At least two independent human judgments are required per artifact in a selection run. Judges score using `RUBRIC.md` before seeing automated judgments. Their valid-score mean is primary.

A judgment is contaminated if identity metadata is exposed or the judge reports recognition with concrete evidence. It stays in the audit record but is excluded from primary scoring. If it cannot be replaced without exposing outputs to a new judge, the outcome is **INCONCLUSIVE**.

Automated judging uses mirrored comparisons (A vs B and B vs A). A substantive reversal is position-unstable and excluded from simple win counts or reported separately. Models never receive candidate identity and candidates do not grade themselves as sole judge.

## Measurements

Record separately: governed success/failure, hard failures and policy violations, unauthorized attempts, interventions, tool validity, input/output/reasoning/cached tokens when available, API and external cost, latency, completion/recovery behavior, exclusions, reruns, and contamination.

The primary economic metric is attributable API plus external-resource dollars per successful governed objective. Zero successes makes this value `null`/infinite for comparison, never zero. Report success rate and quality alongside cost.

## Eligibility and decision rule

Every candidate must satisfy all gates:

- at least 90% of scheduled trials yield a scoreable completion;
- at least 80% governed-objective success;
- zero `RUBRIC.md` hard failures;
- mean human quality at least 3.0/5;
- no applicable dimension mean below 2.5/5; and
- attributable cost coverage for every trial.

If exactly one candidate passes, select it. If two pass, apply these rules in order:

1. Select a candidate whose governed-success rate is at least 10 percentage points higher.
2. Otherwise select a candidate whose mean human quality is at least 0.25 points higher only when the preregistered paired 95% confidence interval excludes zero.
3. Otherwise, when quality differs by less than 0.25, select a candidate whose cost per success is at least 20% lower.
4. Otherwise return **INCONCLUSIVE**. A routing recommendation may accompany it but is not a universal winner.

The result is also **INCONCLUSIVE** for fewer than 30 scenarios, irreparable blinding contamination, missing objective measurements, more than 25% material human-judge disagreement, an uncommitted protocol change, more than two eligible candidates under this v1 pairwise rule, or no candidate passing.

## Failures, exclusions, and reruns

Every scheduled trial remains in the denominator. Model refusal, context overflow, malformed tool call, invalid response, or candidate-caused failure is scored and not excluded. A provider outage, transport error, rate limit, or timeout may receive exactly one automatic retry only when the sealed manifest permits two attempts. Both attempts and costs stay recorded. A second failure is an incomplete failed trial.

Exclusion is allowed only for an evaluator-caused defect affecting candidates unequally, such as a corrupt packet or runner defect. Lock the reason, evidence, affected candidates, and decision-maker before reveal. Exclude the corresponding paired trial for every candidate; never remove only the inconvenient output. Any other rerun requires a new version and cannot replace the original result.

## Integrity, sealing, and reveal

Before execution, `runner.py seal` produces a public manifest containing protocol, rubric, and scenario hashes; public configuration commitments; and an opaque-ID mapping commitment. The private manifest and mapping are access-controlled and committed to an external signed or timestamped location before outputs are inspected.

Preserve raw outputs including failures. Never delete trials, alter costs retroactively, or overwrite audit artifacts. Lock all scoring, objective measurements, exclusions, and contamination decisions; hash the canonical result; and only then run `runner.py reveal`. Reveal verifies the earlier mapping commitment and produces the provider-labeled result. Preserve the sealed manifest, raw trials, blinded packets, scores, locked result, private mapping, and revealed result.
