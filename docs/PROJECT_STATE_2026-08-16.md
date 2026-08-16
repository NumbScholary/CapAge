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

### 2. Stateful sandbox economy

Build a seeded, multi-round simulation that complements static scenarios. The simulator—not the candidate—controls hidden state, settlement, counterparty behavior, scoring, and transitions.

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
