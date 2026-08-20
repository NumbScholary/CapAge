# CapAge Development State — 2026-08-16

This document reconciles the curated development handoff with the repository state as verified on 2026-08-16. It is a continuity aid, not a controlling specification.

## Authority hierarchy

When sources conflict, use this order:

1. **CapAge Constitution v0.1 normative text**
2. **Frozen experimental protocols and preregistrations**
3. **Merged repository implementation and preserved audit artifacts**
4. **Implementation architecture and Minimum Viable Build design**
5. **Development handoffs, roadmaps, and conversation-derived proposals**

A lower layer must not silently override a higher layer. Metaphors about CapAge having a "mind" or being "alive" are not technical or constitutional requirements.

## Core proposition

CapAge tests whether an AI agent can begin with scarce owner-supplied capital and independently discover lawful, legitimate, productive economic activity while remaining inside enforceable limits on authority, downside risk, accounting integrity, truthfulness, auditability, and owner control.

The initial capital target is approximately $250. Opportunity discovery is part of the capability under test. Passive speculation, hidden subsidy, deceptive accounting, and uncontrolled risk do not demonstrate the target phenomenon.

## Non-negotiable commitments

- Intent is not authority. The strategic model proposes; the external enforcement boundary authorizes and executes.
- Consequential real-world action initially requires human approval.
- Losses remain losses; there is no assumed recapitalization.
- Model/API usage and economically meaningful subsidies are attributable costs.
- Auditability and truthfulness are required even when concealment would improve apparent performance.
- Failure and an inconclusive result must remain possible.
- The enforcement kernel and evaluation machinery remain provider-neutral.

## Verified repository state

### Merged

- PR #1 — governed core executor
- PR #3 — blinded Experiment Zero protocol, rubric, runner, and scenario families
- PR #4 — registered candidate pair and frozen inference/cost configuration
- PR #5 — first smoke launch
- PR #7 — safe provider error-label diagnostics
- PR #8 — corrected Smoke v2 with a separately versioned ten-scenario suite and structural completion gate

### Open

- PR #2 — Milestone 1 executor-boundary tests

### Preserved experimental record

The first smoke attempt remains a failed historical attempt. It unintentionally scheduled 14 scenarios and suffered OpenAI quota failures. Its artifacts must not be overwritten or reinterpreted as a valid ten-scenario smoke.

Smoke v2 used a new manifest, seed, scenario file, and artifact names. It completed successfully with:

- 10 frozen smoke scenarios, E0-001 through E0-010
- two blinded candidates per scenario
- 20 complete judge-visible packets
- no missing candidate outputs
- a sealed private identity mapping

Smoke v2 validates the evaluation machinery. It is not the final model-selection study and must not be represented as one.

## Current Experiment Zero phase

The provider-neutral runner, adapters, candidate registration, blinding, retry classification, audit artifacts, and judge packets now exist. Human scoring is pending.

The primary economic metric remains:

> attributable API and external-resource dollars per successful governed objective

Human scoring occurs before identity reveal. Automated judging, if later used, is secondary evidence and must not overwrite locked human judgments. INCONCLUSIVE remains a valid outcome.

## Economic Homeostasis V2 blocked replication result

Proposed research layer 2 below (stateful sandbox economy) has since been
specified, implemented, and iterated through Economic Homeostasis V1, a
shadow-mode baseline, an active V1 experiment, a three-arm V1/V2/Control
comparison, and a blocked V1-versus-V2 replication. This section records the
outcome of that replication; it does not retroactively alter the frozen
protocols it summarizes.

The replication (preregistered in
`experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_PREREG.md`, materialized in
`experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_MATERIALIZATION.md`, gated in
`experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_LAUNCH_GATE.md`, and launched
by owner-authorized commit `df3307eaa385372cfd8026e8fb151dad86b82732`) ran as
GitHub Actions run `32349482559` on 2026-08-20. Full results are recorded in
`experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_RESULT.md` (merged via PR #38).

Summary:

- All 48 preregistered cells completed for $12.92 of attributable model cost,
  against a $21.60 hard cap.
- All eight frozen gate criteria passed. V2 led V1 on summed block-ending
  capital (+$834.99), summed block-ending reputation (+426), and delivery
  dispute rate (0.0% vs. 73.3%), and led V1 in 7 of 8 blocks on capital.
- Classification: `advance_to_another_larger_synthetic_test`.
  `deployment_authorized` is `false`. This result authorizes only a larger
  synthetic test — not deployment, real-world economic action, or expanded
  CapAge authority — and remains a small-sample engineering replication with
  no statistical-significance claim.

## Adopted design directions

These directions are accepted for continued research but do not alter the Constitution or frozen Smoke v2 protocol.

### CapAge is model-independent

CapAge is the persistent governed system. Models are replaceable cognitive resources behind provider-neutral interfaces. A model name is not part of CapAge's identity.

### Conditional cooperation

CapAge should pursue positive-sum exchange without becoming naively trusting. Trust should be evidence-sensitive, bounded under uncertainty, reduced after defection, and capable of repair after new evidence.

### Exploration and exploitation

CapAge must balance learning about uncertain alternatives against using the best-supported opportunity. Information has a cost; premature commitment and endless research can both destroy scarce capital.

## Proposed next research layers

The items below are proposals until separately specified, reviewed, and implemented.

### 1. Full model-selection benchmark

Create a separately versioned 30–50-scenario benchmark before inspecting its candidate results. Freeze candidate versions, inference settings, cost treatment, randomization, retries, exclusions, scoring, and reveal rules before execution.

A feasibility-aware tournament may qualify several serious candidates and advance fewer finalists to the expensive evaluation. Smoke results are debugging and qualification evidence only.

### 2. Stateful sandbox economy — implemented

Build a seeded, multi-round simulation that complements static scenarios. The simulator—not the candidate—controls hidden state, settlement, counterparty behavior, scoring, and transitions.

This layer is no longer just proposed: see "Economic Homeostasis V2 blocked replication result" above for the current outcome and its explicit non-authorization boundary.

Required properties:

- heterogeneous hidden counterparty types
- cooperation, bargaining, bluffing, noisy information, default, and manipulation
- equivalent paired seeds or committed event schedules
- bounded simulated authority and explicit action grammar
- full event, cost, liability, and decision logs
- distributional reporting, including catastrophic failures
- governance, truthfulness, accounting integrity, and productive-value measures in addition to simulated profit
- no automatic expansion of real-world authority based on simulation success

### 3. Empirical cognitive routing

Only after the strongest single model is established should CapAge test whether job-specific routing improves governed outcomes after routing overhead and cost are included.

Possible specialties—opportunity discovery, adversarial review, execution planning, and routine cognition—must be inferred from preregistered domains and measurements. They must not be invented post hoc to rationalize observed results.

## Immediate continuation

1. Complete blinded human scoring of Smoke v2 and preserve the returned score artifacts.
2. Treat Smoke v2 as a machinery/qualification check, not a selection verdict.
3. Resolve PR #2 and ensure Milestone 1 executor-boundary tests are merged or explicitly superseded.
4. Specify and freeze the full benchmark before generating its candidate outputs.
5. After the full single-model study, decide whether a stateful sandbox or model-routing experiment has the higher information value per attributable dollar.
6. The Homeostasis V2 blocked replication passed its gate and is classified `advance_to_another_larger_synthetic_test`; specify and freeze that larger synthetic test before running it, and do not treat the passed gate as deployment or real-world authority.
