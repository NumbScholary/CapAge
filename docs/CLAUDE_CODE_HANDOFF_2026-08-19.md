# CapAge Claude Code handoff — 2026-08-19 EDT

Status: continuity record and engineering handoff. This document is not a
normative specification, provider-call authorization, spend authorization, or
permission to merge any pull request.

## Purpose

Kev is moving CapAge engineering work from ChatGPT Work/Codex to Claude Code to
reduce accumulating coding-agent credits without losing code, experiment
history, governance constraints, branch topology, or the exact next action.
The GitHub repository remains the durable source of truth. Conversation-only
facts that materially affect continuation are recorded here.

Repository: `NumbScholary/CapAge` (public)

Clone URL: `https://github.com/NumbScholary/CapAge.git`

Default branch: `main`

Claude entry branch: `agent/claude-code-handoff-2026-08-19`

## First local setup

Use Claude Code's subscription login separately from CapAge's experiment API
credential. If `ANTHROPIC_API_KEY` is exported in the shell, Claude Code may use
API billing instead of the intended Claude account login.

```bash
git clone --branch agent/claude-code-handoff-2026-08-19 \
  https://github.com/NumbScholary/CapAge.git
cd CapAge
# Do not use --single-branch. It scopes remote.origin.fetch to the entry
# branch only, so a later `git fetch --all` updates FETCH_HEAD but never
# advances refs/remotes/origin/* for other branches (e.g. agent/mailbox-init).
# A stale tracking ref then reads as a missing message even though the commit
# exists on the remote. Set the wildcard refspec persistently before fetching
# so every subsequent fetch keeps all tracking refs current.
git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git fetch origin
git status -sb
claude
```

A one-shot `git fetch origin '+refs/heads/*:...'` is not a substitute for the
`git config` line above: it advances tracking refs once but leaves the
persistent refspec narrow, so the next `git fetch --all` silently lags again.

Inside Claude Code:

```text
/context
```

Confirm that `CLAUDE.md` imports `AGENTS.md`, then ask Claude to read this file,
inspect the branch graph and open PRs, and run unpaid validation before making
changes. Do not run `/init`; the migration instructions are already curated.

## Controlling hierarchy

When sources conflict:

1. CapAge Constitution v0.1.
2. Frozen protocols and preregistrations.
3. Merged implementation and preserved artifacts.
4. Implementation architecture and MVB design.
5. Handoffs, roadmaps, and conversation-derived proposals.

Core proposition: CapAge tests whether a governed autonomous economic agent can
start with scarce owner-supplied capital (approximately $250) and discover
lawful, legitimate, productive economic activity while remaining inside
externally enforced limits on authority, downside risk, accounting integrity,
truthfulness, auditability, and owner control.

Non-negotiable implications:

- Intent is not authority.
- The LLM is not a security boundary.
- The strategic model proposes; the host PolicyEngine/Executor authorizes.
- Consequential real-world actions initially require human approval.
- API usage is an attributable economic cost.
- Losses remain losses; no automatic recapitalization is assumed.
- Failure and `INCONCLUSIVE` remain valid outcomes.
- The MVB runtime remains single-agent; PR #10 is future, non-normative design.
- A successful simulation cannot grant deployment or real-world authority.

Primary references already in the repository:

- `docs/constitution/CapAge Constitution v0.1_ Foundational Governance Architecture for an Autonomous Economic Agent.pdf`
- `docs/architecture/CapAge Implementation Architecture v0.1 (1).pdf`
- `docs/mvb/CapAge-MVB-Specification-v0.1.md`
- `docs/PROJECT_STATE_2026-08-16.md` (historical; superseded on current state by this handoff)

## Repository topology

`main` is not the full current project. Work proceeded through stacked branches
and PRs so that experimental evidence and authorization boundaries remained
auditable.

| Role | Branch / commit | State |
|---|---|---|
| Foundation/default | `main` at `664ee8b8d14747338678e9722eda99a02dee14b7` | Does not contain the whole sandbox/homeostasis line |
| Accumulated research line | `agent/audited-memory-v1` at `e72c87b4dcb4ac799368d896c79be10cc2dd8ca3` | Head of draft PR #14; contains merged dependent work through PR #32 |
| Replication materialization anchor | `ab32d9605c4805551d572259d35056ba56068120` | Merge from PR #34; frozen 24-world plan |
| Protected replication execution branch | `agent/homeostasis-v2-blocked-replication-launch` | Must remain untouched until authorization transition |
| Audited launch merge | `059bc036d9ebb5103effd27e2262313078d2c5c1` | PR #37 merge; parent 1 is the materialization anchor |
| Claude engineering handoff | `agent/claude-code-handoff-2026-08-19` | Based on the audited launch merge plus documentation/settings only |

Do not merge or cherry-pick the Claude handoff commit onto the protected
execution branch. Doing so would make the launch merge more than one
first-parent commit after materialization and would correctly fail the paid
workflow's preflight.

## Open draft PRs requiring deliberate disposition

These are durable historical/dependent work, not an instruction to merge:

| PR | Head → base | Meaning |
|---:|---|---|
| #10 | `agent/multi-agent-conflict-controls` → `main` | Non-normative future multi-agent controls; current MVB remains single-agent |
| #11 | `agent/experiment-zero-full-selection-v1` → `main` | Blinded 30-scenario selection work; do not rerun provider workflow casually |
| #12 | `agent/seeded-economic-sandbox-v1` → `main` | Seeded sandbox foundation |
| #13 | `sonnet-pilot-v1` → `agent/seeded-economic-sandbox-v1` | Bounded Sonnet pilot |
| #14 | `agent/audited-memory-v1` → `sonnet-pilot-v1` | Host-owned audited memory and accumulated dependent research |
| #20 | `agent/longitudinal-v3-pilot-001-launch` → `agent/audited-memory-v1` | Older dormant v3 pilot setup; review against merged replacement PR #21 before any action |

PR #36 is closed unmerged and superseded. Its authorization phrase was bound to
an obsolete launch merge and must never be reused. PR #37 is merged.

## Current implementation

The active line is Python 3.12 and keeps a dependency-free core. Important
components include:

- `capage/policy.py`, `capage/executor.py`, and `capage/audit.py`: external
  authority and audit boundary.
- `capage/sandbox.py` and `capage/sandbox_runner.py`: seeded economic world,
  deterministic settlement/assessment boundary, provider-cost accounting.
- `capage/memory.py`, `capage/longitudinal.py`, and `capage/longitudinal_v3.py`:
  host-owned audited memory and longitudinal tests.
- `capage/homeostasis.py`: V1 economic-continuity controller.
- `capage/homeostasis_v2.py` and `capage/homeostasis_v2_runner.py`: separated
  opportunity/obligation/verification signals and objective delivery checking.
- `capage/homeostasis_v2_replication.py` and
  `capage/homeostasis_v2_replication_runner.py`: frozen blocked replication.
- `capage/homeostasis_v2_replication_launch.py`: merge-bound one-shot launch.

The coding assistant is not the CapAge strategic model. The frozen replication
continues to specify `claude-sonnet-5`, medium effort, 1,024 output tokens, and
the preregistered August 2026 tariff. Moving engineering work to Claude Code
does not revise that experimental treatment.

## Experiment record that must survive the migration

### Experiment Zero and sandbox development

- The first Experiment Zero smoke attempt failed and remains historical
  evidence; it must not be overwritten as a valid smoke.
- Corrected Smoke v2 completed 20 blinded responses across ten frozen scenarios
  and validated the evaluation machinery. It was not itself the final model
  selection study.
- The user subsequently judged Sonnet stronger for CapAge's current direction,
  and the sandbox/homeostasis work froze `claude-sonnet-5` as the provisional
  experiment model. This is not a permanent identity claim about CapAge.
- Host-owned audited memory is provider-independent and does not let the model
  rewrite authoritative history.

### Homeostasis V1 and V2

Homeostasis V1 created productive urgency but also four objectively checkable
delivery disputes and negative reputation in its active comparison. V2 split
opportunity urgency, obligation urgency, and verification requirements, then
added a local objective-delivery boundary without changing tool authority.

The completed three-arm Homeostasis V2 run is GitHub Actions run `32304273201`.
It completed technically but failed its preregistered all-required advancement
gate:

- V1 final capital: $442.50.
- V2 final capital: $407.84.
- V2 had zero disputed deliveries versus four for V1.
- V2 ending reputation was +48.
- V2 model cost was approximately 86.5% of V1's.
- V2 blocked and corrected invalid work during Period 3.
- New run cost was approximately $5.12; approximately $5.41 including the
  separately preserved aborted-attempt debit.

Interpretation: quality improved, but capital remained below V1, so V2 did not
advance. V2 was frozen unchanged for a larger diagnostic replication rather
than tuned on the observed worlds.

### Preserved aborted attempt

GitHub Actions run `32292164227` reached the first paid cell but failed before a
standard checkpoint because of an incorrect run-identity binding. It is never
replayed automatically.

- Completed experimental cells: 0.
- Provider usage: 126,468 input tokens and 3,622 output tokens.
- Attributable cost: 28,915,600 cost units = 28.9156 cents.
- Restricted artifact: `homeostasis-v2-three-arm-launch-restricted`, artifact
  ID `9379919939`.
- Repository record:
  `experiments/sandbox/HOMEOSTASIS_V2_ABORTED_RUN_32292164227.md`.

## Frozen blocked replication

Purpose: fresh diagnostic V1-versus-unchanged-V2 replication. It does not amend
or retroactively pass the earlier gate.

| Field | Frozen value |
|---|---|
| Arms | V1 and unchanged V2; control intentionally omitted |
| Blocks | 8 independent blocks |
| Periods | 3 consecutive 30-day periods per arm per block |
| Worlds | 24 matched hidden worlds |
| Paid cells | 48 serial cells |
| Model | `claude-sonnet-5`, medium effort |
| Per-cell cap | 45 cents |
| Aggregate cap | $21.60 |
| Prior-based estimate | Approximately $13.70, not a guarantee |
| Retries/replay | None for provider or ambiguous attempts |
| Validity | Frozen tariff valid through 2026-08-31 |

All 48 cells must complete with valid matched-world evidence or the result is
`INCONCLUSIVE`. V2 advances only to another larger synthetic test if every
frozen quality, reputation, capital, block-consistency, boundary, and cost
criterion passes. Diagnostics cannot change the gate.

Frozen records:

- `experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_PREREG.md`
- `experiments/sandbox/economic_homeostasis_v2_replication_prereg_v1.json`
- `experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_MATERIALIZATION.md`
- `experiments/sandbox/economic_homeostasis_v2_replication_plan_v1.json`
- `experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_LAUNCH_GATE.md`

## Launch audit and present authorization state

PR #37 merged on 2026-08-19 EDT / 2026-08-20 UTC as:

`059bc036d9ebb5103effd27e2262313078d2c5c1`

Audit facts:

- First parent: `ab32d9605c4805551d572259d35056ba56068120`.
- Second parent: `89d49de6c5a18aea4e93a9f4995dc930be56905a`.
- Tree: `e37e69bebe6bcd7ec08dbe57469da9835b96b9aa`.
- The first-parent distance from materialization is exactly one.
- The materialization-to-launch diff is exactly four added files:
  `.github/workflows/homeostasis-v2-replication-launch.yml`,
  `capage/homeostasis_v2_replication_launch.py`,
  `experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_LAUNCH_GATE.md`, and
  `tests/test_homeostasis_v2_replication_launch.py`.
- PR #37 changed four files in one head commit; its dependency-free quality
  gate succeeded in run `32317366875`.
- The fixed authorization file is absent.
- No provider call or spending occurred during PR #37 or this migration.

The only possible future confirmation has the form:

`RUN_HOMEOSTASIS_V2_BLOCKED_REPLICATION_AT_<AUDITED_LAUNCH_MERGE_SHA>_MAX_2160_CENTS`

This handoff intentionally does not expand that template into an owner
statement. Documentation of the SHA is not authorization. Before any paid run,
Kev must supply the fully expanded phrase again in a new explicit message.

If and only if that happens, create a fresh branch directly from protected
execution head `059bc036d9ebb5103effd27e2262313078d2c5c1`. The proposed PR must add
exactly one file and no other byte:

`experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_AUTHORIZATION.md`

Opening the draft PR must not trigger the paid workflow; merging the reviewed
one-file PR into `agent/homeostasis-v2-blocked-replication-launch` is the only
intended trigger. Re-audit ancestry, diff, byte exactness, tariff date, CI, and
the user's current intent immediately before merge. Never base this PR on the
Claude handoff branch.

## Credentials and cost separation

Known GitHub Actions secret names:

- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`

Their values were not read, copied, exported, or placed in this handoff. Claude
Code authentication is separate. Prefer Claude subscription login for the
coding tool if the goal is to avoid API-credit billing; do not inject CapAge's
experiment key into Claude Code's environment.

Several historical workflows are manually dispatchable and some can spend.
Never run or rerun a provider workflow merely to test Claude Code access. Use
the dependency-free quality gate and local `--validate-only` commands.

## Validation baseline

The PR #37 replacement gate passed 65 locally available tests both with the
authorization file absent and with a phase-test copy present. Python compilation,
workflow parsing, frozen-plan validation, exact remote blob comparison,
mergeability, and GitHub Actions quality gate all passed. The remote launch
blobs were:

- workflow: `d362efc3dc1289b91732052f8fff68b3d83ac274`
- launch module: `8b543ebf4be38af772e688b77b92a2fa39fc8937`
- launch-gate record: `3e052cc7641c80c3f7df515ab27b96c6b2bd5cc2`
- launch tests: `56a2b1c140cf0fdd0d915c48d874c0a97607beb9`

Run the commands in `AGENTS.md` after cloning. They are unpaid. Stop if any
command attempts to construct a live provider client or use a credential.

## First Claude Code task

Use this exact starting request after `/context`:

```text
Read AGENTS.md and docs/CLAUDE_CODE_HANDOFF_2026-08-19.md completely. Inspect
the current branch, remote branch graph, open PRs, and protected replication
execution branch. Run only unpaid validation. Report any discrepancy between
the handoff and GitHub before proposing changes. Do not dispatch workflows,
touch authorization files, use provider credentials, or spend funds.
```

After that orientation, continue from the user's current instruction rather
than reviving older proposed work automatically.
