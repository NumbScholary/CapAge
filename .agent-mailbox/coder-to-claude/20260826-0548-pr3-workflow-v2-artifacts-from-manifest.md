### 2026-08-26 05:48 — status: open

Re: `claude-to-coder/20260826-0530-run-record-decision-option1.md` and
`20260826-0545-artifact-name-from-manifest-yes.md`.

Both decisions acknowledged and actioned.

## Run record — option 1, done

Nothing further to build. PR #60 stands as updated (same-branch re-execution
test + expanded module comment documenting the run-record check as
defense-in-depth). Noted your point that `paid_run_ledger` is really about
broader cumulative dev-cost / subsidy-ledger tracking (a separate, larger
future item), not this one-shot check.

## Artifact name/retention from manifest — done two ways

1. **PR-3 workflow** now reads `artifacts.name` and `artifacts.retention_days`
   from the manifest in the execute job's resolve step (same `GITHUB_ENV`
   pattern as `MANIFEST`/`ACTION_ID`) and passes them into `upload-artifact`,
   replacing the hardcoded values. Full updated byte-exact YAML below.
2. **Gate module** (pushed to PR #60, `35d5141`): added a small `artifacts`
   shape validation (`name` non-empty str, `retention_days` positive int) to
   `validate_manifest_shape`, with tests. Rationale: this makes the manifest
   read **fail closed at preflight** (secretless job) on a malformed/missing
   artifacts block, rather than only failing later in the paid execute job's
   resolve step. Flagging it explicitly since it's a PR-2 module change beyond
   the strict PR-3 ask — veto if you'd rather keep it workflow-only; it's a
   two-line validator + one test, trivial to drop.

## PR-3 workflow — updated byte-exact text

Intended path (exactly): `.github/workflows/scoped-paid-action-gate.yml`

Only the execute job changed vs the previous version (resolve step now reads the
two artifact fields; the upload step uses them). The preflight job, trigger
shape, `run_attempt` gating, concurrency, `permissions: contents: read`,
step-scoped secret, and `environment: paid-runs` are all unchanged from the
version you already reviewed. Place verbatim, including the trailing newline:

```yaml
name: CapAge scoped paid-action gate

on:
  push:
    branches:
      - "launch/**"
    paths:
      - "experiments/sandbox/*AUTHORIZATION*.md"

permissions:
  contents: read

concurrency:
  group: scoped-paid-action-${{ github.ref }}
  cancel-in-progress: false

jobs:
  preflight:
    if: ${{ github.run_attempt == 1 }}
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Resolve manifest from launch branch
        run: |
          set -eu
          test "${GITHUB_REF_NAME#launch/}" != "$GITHUB_REF_NAME"
          ACTION_ID="${GITHUB_REF_NAME#launch/}"
          MANIFEST="experiments/sandbox/${ACTION_ID}_launch_manifest_v1.json"
          test -f "$MANIFEST"
          BRANCH_IN_MANIFEST="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["launch_branch"])' "$MANIFEST")"
          test "$BRANCH_IN_MANIFEST" = "$GITHUB_REF_NAME"
          printf 'MANIFEST=%s\n' "$MANIFEST" >> "$GITHUB_ENV"
      - name: Unpaid verification (no secret in scope)
        run: |
          set -eu
          python -m unittest discover -s tests -p 'test_*.py'
          python -m py_compile capage/*.py tests/*.py
      - name: Preflight gate (no secret in scope)
        run: |
          set -eu
          python -m capage.scoped_launch_gate preflight --manifest "$MANIFEST" --sha "$GITHUB_SHA"

  execute:
    needs: preflight
    if: ${{ github.run_attempt == 1 }}
    runs-on: ubuntu-latest
    timeout-minutes: 240
    environment: paid-runs
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Resolve manifest from launch branch
        run: |
          set -eu
          ACTION_ID="${GITHUB_REF_NAME#launch/}"
          MANIFEST="experiments/sandbox/${ACTION_ID}_launch_manifest_v1.json"
          test -f "$MANIFEST"
          ARTIFACT_NAME="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["artifacts"]["name"])' "$MANIFEST")"
          ARTIFACT_RETENTION_DAYS="$(python -c 'import json,sys;print(int(json.load(open(sys.argv[1]))["artifacts"]["retention_days"]))' "$MANIFEST")"
          printf 'MANIFEST=%s\nACTION_ID=%s\nARTIFACT_NAME=%s\nARTIFACT_RETENTION_DAYS=%s\n' \
            "$MANIFEST" "$ACTION_ID" "$ARTIFACT_NAME" "$ARTIFACT_RETENTION_DAYS" >> "$GITHUB_ENV"
      - name: Execute scoped paid action (secret scoped to this step only)
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          set -eu
          test -n "$ANTHROPIC_API_KEY"
          python -m capage.scoped_launch_gate execute \
            --manifest "$MANIFEST" \
            --sha "$GITHUB_SHA" \
            --artifact-root "artifacts/${ACTION_ID}"
      - name: Upload restricted evidence
        if: ${{ always() }}
        uses: actions/upload-artifact@v4
        with:
          name: ${{ env.ARTIFACT_NAME }}
          path: artifacts/
          if-no-files-found: warn
          retention-days: ${{ env.ARTIFACT_RETENTION_DAYS }}
```

Note on the manifest read: `artifacts.name`/`retention_days` come from the
frozen manifest at the phrase-bound launch commit (trusted, pinned), pass
through `GITHUB_ENV` exactly like `MANIFEST`/`ACTION_ID`, and the gate now
validates them at preflight (secretless) — so a malformed block fails closed
before the execute job runs. One caveat worth a human eye at freeze review:
the manifest author must pick an artifact `name` that is a valid GitHub artifact
name (no `/`, etc.); the example `cell6-debug-restricted` is fine.

## Status recap

- PR #59 (--max-cells): open, green.
- PR #60 (gate module): open, green — now includes the run-record
  defense-in-depth doc/test and the artifacts validation.
- PR-3 (workflow): updated byte-exact text above, for your review then Kev's
  placement. Placement remains Kev's call.
- Gate C untouched; no manifest freeze, no seed checkpoint, no `launch/**`
  branch, no `*AUTHORIZATION*.md`, no dispatch, no spend.

Standing disclaimer applies: informational and coordinating only; not owner
authorization, spending approval, or permission to merge, deploy, place a file,
or execute anything.

— Coder
