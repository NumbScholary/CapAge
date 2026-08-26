# Scoped Paid-Action Gate v1 — general launch mechanism (design proposal)

Status: design proposal, 2026-08-24; amended 2026-08-25 per the owner's review
decisions (see PR #56 discussion / mailbox
`claude-to-coder/20260825-0940-pr56-amend-before-gate-a.md`). Still a proposal:
Gate A (design acceptance) is not yet given, and this document is neither
adopted nor implemented. This document grants no authority, authorizes no
spending, no provider call, and no workflow execution. Nothing in it revises AGENTS.md, the Constitution, any
frozen protocol, or any preregistration. Adoption, implementation, and every
future use each require their own explicit approvals (see "Adoption gates" at
the end).

## Purpose

CapAge has now built two one-shot paid launch gates by hand:

1. `capage/homeostasis_v2_replication_launch.py` +
   `.github/workflows/homeostasis-v2-replication-launch.yml` (48 cells,
   $21.60 cap, consumed; replication since retired by owner decision, PR #48).
2. `capage/hosting_liability_replication_launch.py` +
   `.github/workflows/hosting-liability-tariff-replication-launch.yml` on
   `agent/hosting-liability-tariff-replication-launch` (48 cells, $21.60 cap,
   consumed by run `32710531510`, which stopped safely after 5 cells / $1.08).

A third scoped paid action is now wanted: a one-cell debug re-run of the
failing cell `block-01:period-02:zero` (≤ 45 cents of new spend). The consumed
tariff gate cannot be reused — its file-diff invariant
(`MATERIALIZATION_MERGE..LAUNCH_COMMIT` must be exactly two specific files)
correctly rejects any commit adding the debug tooling. Building a third
bespoke workflow would mean copying safety-critical logic a third time, with
each copy separately reviewed and each copy free to drift from the others.

The owner's direction is to design the general, reusable pattern instead: one
reviewed enforcement mechanism that any future scoped, spend-capable action
passes through, parameterized per action, weakening no existing invariant.

The generalization is of the **enforcement machinery only**. Authorization is
never generalized: each action still requires its own fresh, byte-exact,
non-reusable owner phrase bound to an exact commit and an exact spending cap.

## Design goals

- One dependency-free gate module and one generic workflow, reviewed once,
  reused for every scoped paid action.
- Everything that varies per action lives in a frozen, reviewed, per-action
  **launch manifest** committed before authorization.
- The authorization mechanism is unchanged in shape from the two precedents:
  a one-file `*AUTHORIZATION*.md` PR whose merge is the only trigger, with a
  byte-exact phrase binding action, commit, and cap.
- Fail closed at every layer. Preflight runs without any secret. Any invariant
  violation stops the run before the execute step can see a credential.
- Unpaid validation (`--validate-only`, mock-driven tests) for the gate itself,
  never constructing a provider client.
- Append-only evidence: restricted artifacts on every outcome, provenance
  hashes, and a human-reviewed run record afterward.

## Non-goals

- Not a standing spend capability, a spend button, or an autonomous trigger.
- Not an automation of the owner's approval. Kev remains the only source of
  authorization, per action, every time.
- Not a change to the CapAge runtime, which remains a single strategic agent
  behind the in-repo PolicyEngine/Executor boundary.
- Not a modification of any frozen experiment, protected branch, retired
  branch, or historical workflow file. Those remain preserved evidence.

## The invariant set, factored from the two existing gates

These are the invariants the two hand-built gates enforce today, verified
against the actual workflow and module sources. The general mechanism must
enforce every one of them, per action, from manifest parameters instead of
hard-coded constants.

| # | Invariant | Enforced today by | Generalized enforcement |
|---|---|---|---|
| 1 | Trigger is a push (merge) to one specific branch touching one specific authorization path; opening a PR can never trigger | workflow `on.push.branches` + `paths` | same trigger shape on `launch/**` + `experiments/sandbox/*AUTHORIZATION*.md` glob; manifest pins the exact file; gate cross-checks |
| 2 | No re-run replay | `if: github.run_attempt == 1` and an in-step re-check | identical |
| 3 | No parallel double-fire | `concurrency` group, `cancel-in-progress: false` | identical, group keyed by ref |
| 4 | Launch commit = first parent of the authorization merge; phrase binds that SHA | `LAUNCH_COMMIT="$(git rev-parse HEAD^)"` | identical; gate additionally requires HEAD to be a true two-parent merge commit |
| 5 | Authorization file is exactly one line, byte-exact `PHRASE + "\n"`, not a symlink, at the fixed path | workflow `wc -l`/`grep -Fxc` + module `verify_authorization` | gate module, path and phrase template from manifest |
| 6 | The authorization merge adds exactly the one authorization file and nothing else | `git diff --name-status LAUNCH_COMMIT HEAD` = `A <file>` | identical, filename from manifest |
| 7 | The authorization file is absent at the launch commit (structural one-shot: once merged, no later push can satisfy this again) | `git cat-file -e` check | identical |
| 8 | The launch branch head is bound to its audited base (ancestry + exact expected diff from the freeze point) | hard-coded `MATERIALIZATION_MERGE` + expected-file list | manifest records the freeze merge SHA and expected file list; gate verifies ancestry, first-parent distance, and diff exactness |
| 9 | Spending caps are declared before authorization and enforced at runtime by the dependency-free runner, not by the workflow | plan JSON asserts + runner per-cell/aggregate cap logic | manifest cap cross-checked to equal the phrase's cents (the real per-action cap) and to not exceed the fixed decimal-error backstop; runtime metering stays in the runner |
| 10 | Frozen inputs are validated unpaid before the paid step | `--validate-only` + full test suite in-workflow | identical; input hashes additionally pinned in the manifest |
| 11 | Tariff/validity expiry is frozen and checkable | plan `valid_through` | manifest `expires_utc`, checked at preflight and again immediately before execution |
| 12 | Evidence is preserved on every outcome, including failures | `upload-artifact` with `if: always()` | identical; artifact name from manifest |
| 13 | Provenance is recorded: commit SHAs, file hashes, authorization hash, caps | inline provenance step | gate module emits the same JSON, driven by manifest |
| 14 | An ambiguous or failed paid attempt is never replayed; its cost is preserved and debited | policy + runner checkpoint semantics (incl. failed-cell cost counting, PR #53/#54) | identical; the runner's checkpoint/cap logic is unchanged by this design |
| 15 | Workflow has read-only repo permissions and a hard timeout | `permissions: contents: read`, `timeout-minutes` | identical; timeout from manifest, bounded by a gate maximum |

One deliberate improvement over the current pattern: in the existing workflow
the provider key is job-level `env`, visible to every step including unpaid
verification. The generic workflow scopes the secret to the execute step only
(and, if adopted, to a protected GitHub environment — see "Hardening").

## Architecture

Three reviewed pieces, merged once through the normal PR path, plus one frozen
manifest per action.

### 1. Launch manifest (per action, frozen by PR)

A JSON file, e.g.
`experiments/sandbox/<action_id>_launch_manifest_v1.json`, committed to the
action's launch branch by a reviewed "manifest freeze" PR before any
authorization exists. Illustrative schema:

```json
{
  "schema": "capage.scoped_launch_manifest/v1",
  "action_id": "hosting-liability-cell6-debug-v1",
  "title": "One-cell live debug re-run of block-01:period-02:zero",
  "launch_branch": "launch/hosting-liability-cell6-debug-v1",
  "freeze_merge_sha": "<merge commit of this manifest's own freeze PR>",
  "expected_freeze_files": [
    "experiments/sandbox/hosting-liability-cell6-debug-v1_launch_manifest_v1.json",
    "experiments/sandbox/hosting_liability_cell6_debug_seed_checkpoint.json"
  ],
  "command": {
    "module": "capage.hosting_liability_replication_launch",
    "argv": [
      "--checkpoint", "{artifact_root}/checkpoint.json",
      "--artifact-dir", "{artifact_root}/cells",
      "--authorization-file", "{authorization_file}",
      "--confirm", "{confirmation}",
      "--launch-commit", "{launch_commit}",
      "--max-cells", "1"
    ]
  },
  "pre_exec_copies": [
    {
      "from": "experiments/sandbox/hosting_liability_cell6_debug_seed_checkpoint.json",
      "to": "{artifact_root}/checkpoint.json"
    }
  ],
  "inputs": [
    {
      "path": "experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json",
      "sha256": "<pinned at manifest freeze>"
    },
    {
      "path": "experiments/sandbox/hosting_liability_cell6_debug_seed_checkpoint.json",
      "sha256": "<pinned at manifest freeze>"
    }
  ],
  "caps": {
    "max_new_spend_cents": 45,
    "cap_enforcement": "runner per-cell cap (45c) x max_cells (1); aggregate cap 2160c carried in seed checkpoint with 107888200 units already debited",
    "per_cell_cost_cap_cents": 45,
    "max_cells": 1
  },
  "validity": {
    "expires_utc": "2026-08-31T23:59:59Z",
    "tariff_valid_through": "2026-08-31"
  },
  "authorization": {
    "file": "experiments/sandbox/HOSTING_LIABILITY_CELL6_DEBUG_AUTHORIZATION.md",
    "phrase_template": "RUN_HOSTING_LIABILITY_CELL6_DEBUG_AT_{launch_commit}_MAX_45_CENTS"
  },
  "one_shot": {
    "run_record_path": "experiments/sandbox/HOSTING_LIABILITY_CELL6_DEBUG_RUN_RECORD.md",
    "must_be_absent_at_preflight": true
  },
  "artifacts": {
    "name": "hosting-liability-cell6-debug-restricted",
    "retention_days": 30
  },
  "timeout_minutes": 60,
  "provider_calls_authorized": false,
  "spend_authorized": false
}
```

`provider_calls_authorized` and `spend_authorized` are `false` in the manifest
itself, exactly as in the existing plan JSONs: the manifest describes and
constrains a possible future action; only the later phrase authorizes it.

Because the phrase binds a commit SHA, and the manifest, pinned inputs, gate
code, and workflow are all part of that commit's tree, the phrase transitively
pins every byte of what will run. Tampering with any of them after the freeze
changes the SHA and invalidates the phrase.

### 2. Generic gate module: `capage/scoped_launch_gate.py`

Dependency-free, mirroring the discipline of the existing launch modules.
Responsibilities:

- **Preflight** (`preflight` subcommand, run with no secret in scope):
  re-derive and verify every invariant in the table above from the repository
  state at `GITHUB_SHA` — true merge commit, phrase byte-exactness against
  `HEAD^`, one-file diff, absence at parent, freeze ancestry and diff
  exactness, input hashes, expiry, run-record absence, caps consistency
  (phrase cents == manifest `max_new_spend_cents` <= `DECIMAL_ERROR_BACKSTOP_CENTS`),
  and module allowlist (below). Emits the provenance JSON. Exits nonzero on any
  violation.
- **Execute** (`execute` subcommand): re-run preflight, re-check expiry, then
  perform the declared `pre_exec_copies` (after hash verification) and exec
  the manifest command as an argv list — no shell — substituting only the
  fixed template variables `{artifact_root}`, `{authorization_file}`,
  `{confirmation}`, `{launch_commit}`. Everything else is frozen manifest
  bytes.
- **Validate-only** (`--validate-only`): parse and check a manifest against
  the working tree with no git-state requirements and no provider client, for
  CI and local unpaid verification.

Two frozen constants live in the gate code and change only by reviewed code
change:

- `ALLOWED_MODULES`: the set of entry points the manifest may name. Initially
  `{"capage.hosting_liability_replication_launch"}`. A manifest naming
  anything else fails preflight regardless of review lapses. This allowlist is
  deliberately not a spending category; it is the whitelist of which code may
  touch money at all, so leaving it open would make review attention the only
  barrier to an unintended paid entry point. Widening it to also cover
  non-experimental developmental API spend was considered and **declined as
  premature over-generalization** (2026-08-25) — no concrete second use case
  exists yet — so it keeps its single entry and widens only by reviewed code
  diff if and when a genuine second use appears.
- `DECIMAL_ERROR_BACKSTOP_CENTS = 5000`: a fixed decimal-place-error backstop,
  **not** a working spending cap and **not** an approved ceiling. There is no
  pre-blessed working ceiling anywhere in the code. The real cap for any action
  is decided per action: Coder proposes a specific cap with reasoning for that
  run, Kev accepts it or pushes back, and Kev's fresh byte-exact phrase — which
  encodes the cents — is what makes the cap real. This constant exists only so
  a mis-typed manifest cannot turn e.g. 45 cents into an absurd or unbounded
  number; its value ($50) is about a fifth of the ~$250 total capital, far
  above anything planned, and it is named so it can never be misread as a
  budget. The gate merely checks that the manifest's `max_new_spend_cents`
  equals the phrase's cents and does not exceed this backstop. Changing the
  backstop is a visible, reviewed code diff.

The gate verifies authorization and consistency; it does not meter spending
at runtime. Runtime metering remains where it already is and already works:
the dependency-free runner's per-cell and aggregate cap logic (including
failed-cell cost counting from PR #53/#54). The gate's caps checks ensure the
declared caps, the phrase, and the runner arguments cannot disagree.

### 3. Generic workflow: `.github/workflows/scoped-paid-action-gate.yml`

Illustrative shape (this document's YAML is a sketch, not the reviewed
implementation):

```yaml
on:
  push:
    branches: ["launch/**"]
    paths: ["experiments/sandbox/*AUTHORIZATION*.md"]
permissions:
  contents: read
concurrency:
  group: scoped-paid-action-${{ github.ref }}
  cancel-in-progress: false
jobs:
  preflight:            # no secret anywhere in this job
    if: github.run_attempt == 1
    steps:
      - checkout (fetch-depth: 0)
      - run unpaid verification (unittest discovery, py_compile, validate-only)
      - python -m capage.scoped_launch_gate preflight
  execute:
    needs: preflight
    if: github.run_attempt == 1
    environment: paid-runs        # optional hardening, see below
    steps:
      - checkout (fetch-depth: 0)
      - python -m capage.scoped_launch_gate execute
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}   # step-scoped
      - upload restricted artifacts
        if: always()
```

The `paths` filter means the workflow does not fire at all on ordinary pushes
to a launch branch (for example the manifest-freeze merge). If it fires and
any check fails, it fails loudly — a red run on an attempted authorization is
correct and wanted. The secret is visible to exactly one step of one job, and
only after preflight has passed in a secretless job.

There is deliberately no `workflow_dispatch` trigger. AGENTS.md's "do not
dispatch provider workflows" rule stays intact and becomes structurally moot
for this path: there is nothing to dispatch.

### Branch namespace and lifecycle

Launch branches live in a new, dedicated namespace: `launch/<action_id>`.
Existing protected and consumed branches are untouched and preserved.

Per action:

1. **Tooling** (unpaid, normal review): any code the action needs merges into
   the integration line through ordinary PRs. For the debug run this is the
   `--max-cells` wiring in the launch script's `main()` — the runner's
   `run(max_cells=...)` already exists and validates its bounds.
2. **Branch cut**: `launch/<action_id>` is created from the integration head,
   which must already contain every required fix (for the debug run: PR #55,
   the forward-merge of the aggregate-cap accounting fix, must be merged
   first).
3. **Manifest freeze** (unpaid): one reviewed PR into the launch branch adds
   exactly the manifest and its pinned input files. Kev merges it. The branch
   head after this merge is the future `LAUNCH_COMMIT`.
4. **Fresh phrase**: Kev supplies the fully expanded phrase in a new explicit
   message, computed against that exact head. Documentation of the template
   (as in this file) is not authorization, and a prior phrase is never
   reusable.
5. **Authorization PR** (one file): the authorization file containing exactly
   the phrase plus a trailing newline. Opening the PR triggers nothing and
   authorizes nothing.
6. **Merge = trigger**: Kev merges; the push fires the gate; preflight, then
   execute, then artifacts on every outcome. No retries, no replay.
7. **Run record** (unpaid, human-reviewed): a PR appends the outcome — run
   id, cells, exact attributable cost, artifact id, failure detail if any — to
   `experiments/sandbox/`, and forward-merges any durable state to the
   integration line. `capage/paid_run_ledger.py` integration
   (`begin_call`/`complete_call`/`aggregate_cost_units`) is a candidate
   follow-up, not part of v1.
8. **Retirement**: the launch branch is preserved read-only as evidence, like
   its two predecessors.

### One-shot enforcement, layered

1. The phrase binds `HEAD^`; any later merge has a different parent, and a
   new phrase requires Kev (policy: a phrase is never reusable for a
   different merge, branch, run, retry, or replacement attempt).
2. The authorization file must be absent at `HEAD^` — once it is on the
   branch, no future push can pass this check (structural).
3. `run_attempt == 1` on both jobs — manual re-runs of a failed or completed
   run refuse to execute (and re-running a provider workflow is already
   forbidden behaviorally).
4. Concurrency group prevents parallel double-fire.
5. The run-record file must be absent at preflight — a duplicate action_id on
   a fresh branch is caught even though it would need a fresh phrase anyway.
6. The runner's checkpoint refuses to re-charge completed cells, and its
   in-process `OneShotExecutionGuard` pattern is retained by the called
   launch modules.

## Hardening (adopted 2026-08-25)

Both measures below are now **live** in the repository (Kev completed the
settings changes on 2026-08-25); they are no longer open recommendations.

**Environment-scoped secret with required reviewer — ADOPTED.** The GitHub
environment `paid-runs` exists, with required reviewer `numbscholar`, admin
bypass disabled, and its only secret `ANTHROPIC_API_KEY`. The repository-level
secrets `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` have both been deleted, so the
Anthropic key now exists only inside `paid-runs`. Effects:

- The execute job pauses after a correct authorization merge until Kev
  approves it in the GitHub UI — a second, cheap, out-of-band confirmation
  that defends against the one class of attack the merge gate cannot see:
  compromised or misreviewed gate/workflow code running at the pinned commit.
- Every historical spend-capable workflow (the manually dispatchable ones
  AGENTS.md warns about) structurally loses access to the key without any of
  their files being edited — the "do not dispatch" rule becomes enforced by
  configuration rather than by discipline, and the historical files remain
  byte-identical evidence.

Cost: one extra click per authorized run. This was the single largest risk
reduction in this document and is now in force. Structural consequence
(2026-08-25): with the repo-level key deleted, every historical spend-capable
workflow is inert — no key is reachable — without any of their files being
edited, and re-enabling any of them would require adding an
`environment: paid-runs` reference, i.e. a visible reviewed code diff.

**Branch protection for `launch/**` — ADOPTED.** A classic branch-protection
rule is live: PR required before merging, force-pushes forbidden, deletions
forbidden. (Required approvals are set to 0 because GitHub does not count the
sole owner's self-approval; the required-reviewer control lives in the
`paid-runs` environment instead.)

## Failure and threat analysis

- **Phrase reuse or stale phrase**: fails invariant 4/5 — the SHA differs.
- **Tooling or manifest swapped after freeze**: changes `HEAD^`, phrase
  invalid; also fails freeze-diff exactness (invariant 8).
- **Authorization file smuggled alongside other changes**: fails one-file
  diff exactness (invariant 6).
- **Squash/rebase merge of the authorization PR**: `HEAD` is not a two-parent
  merge; preflight fails closed rather than mis-binding `HEAD^`.
- **Manifest names a wrong module or absurd cap**: `ALLOWED_MODULES` and
  `DECIMAL_ERROR_BACKSTOP_CENTS` fail it in code even if review misses it (and
  a cap that merely disagrees with the phrase's cents also fails, independent
  of the backstop).
- **Workflow fires on the freeze merge**: it does not — the `paths` filter
  matches only authorization files; if a freeze PR ever touched one, that is
  itself a reviewable red flag and preflight fails it.
- **Execute crashes before any provider call**: artifacts still upload
  (`if: always()`); zero cost is recorded as zero from the runner's own
  accounting, not assumed; the phrase is consumed (no replay without a fresh
  one) — matching the preserved-aborted-attempt precedent.
- **Execute crashes mid-run**: the runner checkpoint plus raw-result
  persistence (PR #53) and failed-cell cost counting (PR #54) preserve and
  debit real spend; the run record documents it; no automatic retry exists
  anywhere in the path.
- **Expiry passes while awaiting environment approval**: the gate re-checks
  `expires_utc` inside `execute`, immediately before exec, not only at
  preflight.
- **What this design cannot defend against**: an actor with the repository
  admin rights plus the owner's approval channels. The gate narrows the paid
  path to "Kev merges a byte-exact file, and (if adopted) Kev approves the
  environment" — it does not and cannot replace GitHub account security.

### Cost of consolidation (blast radius)

Consolidating the two hand-built gates into one shared, reused mechanism is the
central design choice, and it carries a real cost worth stating plainly beside
its benefit. The benefit is a single reviewed enforcement path, so the copies
cannot silently drift apart or be individually weakened. The cost is the mirror
image: two independently reviewed gates also *fail* independently, whereas one
shared gate means a single defect — a logic error in an invariant check, a
manifest mis-parse, a substitution bug — reaches every future scoped paid action
at once. This is not an argument against consolidation (drift across diverging
copies is the worse failure mode, and per action the phrase/commit binding and
the `paid-runs` environment approval still fail independently of the gate code).
It is a known, accepted cost, and it is exactly why this module warrants
disproportionate review attention, exhaustive negative-case tests, and the
fail-closed-on-any-doubt posture the rest of this document requires.

## Relation to the CapAge authority model

This is the repository-level instance of the same boundary the runtime
enforces: the proposer is never the authorizer, and the authorizer is outside
the proposing system.

| Runtime (MVB) | This mechanism |
|---|---|
| Strategic model proposes actions | Coder/Keeper draft tooling, manifest, and PRs |
| PolicyEngine authorizes against frozen policy | Kev's fresh byte-exact phrase, bound to commit + cap, checked by the gate |
| Executor dispatches within caps | The execute job at the pinned commit, secret step-scoped |
| Append-only audit log | Provenance JSON, restricted artifacts on every outcome, run-record PR, ledger follow-up |
| Fail-closed defaults | Preflight without secrets; any violation stops before the credential exists |

Unchanged AGENTS.md boundaries, restated against this design:

- No paid call during exploration, testing, migration, review: the gate has
  no path that constructs a provider client outside the execute step of an
  authorized merge.
- No dispatching provider workflows: the gate is push-triggered only.
- `*AUTHORIZATION*.md` handling: still created only when Kev supplies a new,
  explicit, byte-exact phrase for the currently audited launch commit and
  stated maximum spend; still one file; still never reusable.
- Setup and launch PRs do not authorize: freeze PRs cannot fire the gate;
  opening any PR triggers nothing.
- No replay of ambiguous attempts; costs preserved and debited: unchanged,
  and strengthened by PRs #53/#54 already in the runner.
- Tests and validation stay unpaid: gate ships with `--validate-only` and
  mock-driven tests only.
- The runtime MVB stays single-agent: this is repository operations
  machinery, not CapAge runtime authority.

## First instantiation: the cell-6 debug run

Concrete facts, all verified in this or the prior session:

- Failing cell: `block-01:period-02:zero` — the sixth serial cell of run
  `32710531510`, which completed 5 cells and $1.08 before stopping safely.
- Seed checkpoint: the preserved `checkpoint.json` from restricted artifact
  `9514120954`. Verified to load cleanly under current code with both fixes:
  `config_commitment` and `plan_sha256` match, reconciliation passes,
  `model_cost_units` = `107888200` (the $1.08), and the computed next
  incomplete cell is exactly the failing cell. It would be committed as
  `experiments/sandbox/hosting_liability_cell6_debug_seed_checkpoint.json`
  and hash-pinned in the manifest, so the exact starting state is visible in
  the freeze PR diff.
- Cell 6's own original cost is permanently unknown (bounded ≤ 45 cents) and
  is not in the checkpoint; the append-only cost note merged in PR #54
  governs that record. The debug run does not and cannot repair it.
- New spend bound: 45 cents — per-cell cap 45c × `--max-cells 1`, under the
  2160c aggregate cap already carrying the $1.08 debit.
- Validity: the frozen tariff expires 2026-08-31; the manifest inherits it.
- Phrase template (template only; not authorization):
  `RUN_HOSTING_LIABILITY_CELL6_DEBUG_AT_<LAUNCH_HEAD_SHA>_MAX_45_CENTS`.

Ordered dependencies before this action could ever be authorized:

1. PR #55 (forward-merge of the aggregate-cap fix) merges, so the integration
   head actually contains PR #54's accounting behavior.
2. Gate module + generic workflow + tests merge (implementation approval —
   Keeper's Gate 2 — required first).
3. `--max-cells` wiring in `hosting_liability_replication_launch.main()`
   merges (same approval; small additive diff).
4. `launch/hosting-liability-cell6-debug-v1` cut; manifest + seed checkpoint
   freeze PR reviewed and merged by Kev.
5. Kev's fresh phrase; one-file authorization PR; Kev's merge (Gate 3).

## Manifest-freeze review checklist (for the owner)

Items tagged **[machine-verified]** are enforced as pass/fail in the gate's
preflight (which runs with no secret in scope); preflight fails closed if any
of them does not hold, so the owner does not need to confirm them by eye — in
particular not by reading or comparing hashes, which is not a reliable control
over a voice/phone channel. Items tagged **[human judgment]** require a review
decision the gate cannot make. Where an item mixes the two, the mechanical part
is machine-verified and only the judgment part is left to the owner.

- [ ] `action_id` unique; no run record exists for it anywhere.
      **[machine-verified: run-record-absent preflight check]**
- [ ] `launch_branch` matches `launch/<action_id>`, and the freeze
      ancestry/diff-exactness holds **[machine-verified: invariant 8]**;
      whether the integration head it was cut from is the *intended* one
      (contains all required fixes) is **[human judgment]**.
- [ ] `command.module` is in `ALLOWED_MODULES`; argv contains only frozen
      literals and the four fixed template variables.
      **[machine-verified: module-allowlist + argv-template preflight checks]**
- [ ] Caps: `max_new_spend_cents` ≤ `DECIMAL_ERROR_BACKSTOP_CENTS` and equals
      the phrase's cents **[machine-verified: caps-consistency preflight
      check]**; `cap_enforcement` correctly describes the runtime mechanism that
      bounds it, and that mechanism actually exists in the named module
      **[human judgment]**.
- [ ] Every `inputs[].sha256` matches the committed file; the freeze PR adds
      exactly `expected_freeze_files` and nothing else.
      **[machine-verified: input-hash + freeze-diff-exactness preflight checks,
      invariants 10 and 8 — the owner does not compare hashes by hand]**
- [ ] `expires_utc` is present, well-formed, and not already passed
      **[machine-verified: expiry preflight check + re-check before execute]**;
      that it does not exceed the specific underlying tariff's validity is
      **[human judgment]** unless that tariff validity is itself a pinned
      manifest input.
- [ ] `provider_calls_authorized` and `spend_authorized` are `false`.
      **[machine-verified: manifest-field preflight check]**
- [ ] Authorization filename matches the `*AUTHORIZATION*.md` glob the
      workflow watches, and is absent from the tree.
      **[machine-verified: invariants 6 and 7]**

## Open questions for review

1. **Resolved (2026-08-25): adopted.** The `paid-runs` environment (required
   reviewer `numbscholar`, admin bypass disabled, environment-scoped
   `ANTHROPIC_API_KEY`) is live and the repo-level secrets are deleted. This
   also structurally disarmed the historical dispatchable workflows without
   editing their files. See "Hardening".
2. **Resolved (2026-08-25): adopted.** Branch protection on `launch/**` is live
   (PR required, force-pushes and deletions forbidden). See "Hardening".
3. **Resolved (2026-08-25): no working spend ceiling in code.** The proposed
   `GATE_MAX_CENTS = 2160` was rejected — hardwiring the largest cap ever
   individually approved quietly implies $21.60 is pre-blessed, exactly the
   wrong default for a mechanism whose point is that nothing is pre-authorized.
   Replaced by a per-action proposed cap (Coder proposes with reasoning; Kev's
   fresh byte-exact phrase, which encodes the cents, makes it real) plus a
   single non-working decimal-error backstop `DECIMAL_ERROR_BACKSTOP_CENTS =
   5000` that only catches decimal-place typos. See "Architecture / 2. Generic
   gate module".
4. Run-record location and format standardization
   (`experiments/sandbox/<ACTION_ID>_RUN_RECORD.md` proposed).
5. `paid_run_ledger` integration in v1 or as a follow-up? (Proposed:
   follow-up, to keep the v1 diff small and reviewable; the runner already
   preserves exact costs.)
6. Naming: `capage/scoped_launch_gate.py`,
   `.github/workflows/scoped-paid-action-gate.yml`, `launch/**`.

## Adoption gates

Mirroring the three-gate discipline already in force for the debug work:

- **Gate A — design**: merging this document means the design is accepted for
  implementation planning. It authorizes nothing else.
- **Gate B — implementation**: a separate explicit approval before the gate
  module, workflow, tests, `--max-cells` wiring, or any committed checkpoint
  is written. All unpaid, all mock-tested, all normally reviewed.
- **Gate C — per-action authorization**: unchanged from standing policy. Each
  action needs its own manifest freeze reviewed and merged by Kev, then his
  fresh byte-exact phrase, then his merge of the one-file authorization PR —
  and, if the hardening is adopted, his environment approval.

No part of this document weakens, replaces, or reinterprets AGENTS.md, the
Constitution, frozen protocols, or preserved evidence. If any conflict is
found between this document and those sources, those sources win and this
document must be corrected.
