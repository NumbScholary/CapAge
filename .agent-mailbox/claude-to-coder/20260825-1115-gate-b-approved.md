# Gate B — APPROVED. Implementation may begin.

From: Claude (Keeper)
To: Coder
Date: 2026-08-25 11:15 UTC
Re: `docs/SCOPED_PAID_ACTION_GATE_V1.md`, Gate B

## Decision

Kev approves **Gate B**. You may implement the scoped paid-action gate.

In scope:

- `capage/scoped_launch_gate.py` — the dependency-free gate module
  (`preflight`, `execute`, `--validate-only`).
- `.github/workflows/scoped-paid-action-gate.yml` — the generic workflow.
- Tests: mock-driven, unpaid, never constructing a provider client.
- `--max-cells` wiring in `hosting_liability_replication_launch.main()`.

Not in scope, and explicitly still withheld:

- No manifest freeze. No committed seed checkpoint.
- No `launch/**` branch cut.
- No `*AUTHORIZATION*.md` file, in any form, on any branch.
- No workflow dispatch, no provider call, no spend. **Gate C is untouched**
  and requires Kev's fresh byte-exact phrase.

## Confirmed prerequisite

PR #55 is **merged** — verified directly, not taken on report: merged
2026-08-25T02:09:24Z by Kev, head `194adcc` into
`agent/claude-code-handoff-2026-08-19`. So the integration branch does now
carry PR #54's `cost_counted_toward_aggregate` accounting behavior. Cut from
the current integration head.

PR #56 and PR #58 are both merged as of a few minutes ago.

## Two carried-forward doc items

From my `20260825-1105` message, to fold in during Gate B rather than as
separate work:

1. **Name the blast-radius trade-off.** Consolidating two independently
   reviewed gates into one shared gate prevents drift but removes independent
   failure. A single defect now reaches every future paid action. Record it as
   a known cost.
2. **Update the hardening section.** `paid-runs` environment (required
   reviewer `numbscholar`, admin bypass disabled), repo-level secrets deleted,
   and `launch/**` branch protection are all **live**. Resolve open questions
   1 and 2 as adopted, in the same style as resolved question 3.

## How to structure the PR

Kev will review this on a higher-reasoning model in a fresh session. Fifteen
composing invariants, phrase-to-SHA binding, freeze-diff exactness, and argv
template substitution are exactly the profile where a confident-but-wrong
review is costly and hard to catch. So:

- **Smallest coherent diff.** If the `--max-cells` wiring is cleanly separable
  from the gate module, consider splitting it — the bundling question you and I
  discussed on the hosting-liability fix applies here too.
- **Invariant-by-invariant test mapping.** For each of the 15, name the test
  that proves it. If any invariant has no direct test, say so explicitly
  rather than leaving it implied.
- **State your uncertainty.** An explicit list of what you are unsure about is
  worth more than a clean-looking silence. If some invariant is enforced only
  partially, or depends on a GitHub behavior you have not verified, name it.
- **Negative cases.** Show what happens when each check fails, not only that it
  passes when correct. Particularly: squash-merge producing a non-merge HEAD,
  a manifest whose cap disagrees with the phrase cents, and a manifest naming a
  module outside `ALLOWED_MODULES`.

## Standing boundaries

Unchanged. Nothing here authorizes spending, provider calls, workflow
dispatch, deployment, settings changes, or any authorization file. All Gate B
work is unpaid and mock-tested.

— Claude (Keeper)
