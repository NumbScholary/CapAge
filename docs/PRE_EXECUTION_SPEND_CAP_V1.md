# Framework-enforced pre-execution spend cap (design proposal)

Status: design proposal, 2026-08-31, drafted at Kev's request (via
`.agent-mailbox/claude-to-coder/20260831-1117-nonexecution-record-and-spend-cap-design-ask.md`,
Task 2). Not implemented. Not adopted. This document grants no authority,
authorizes no spending, no provider call, no workflow execution, and no code
change. It does not revise `AGENTS.md`, the Constitution, any frozen
protocol, preregistration, or the existing
`docs/SCOPED_PAID_ACTION_GATE_V1.md` design. Adoption would follow that same
document's Gate A / Gate B / Gate C discipline (design acceptance,
implementation approval, per-action authorization), each separate and
explicit.

## Purpose

Every existing frozen-plan launch (Homeostasis V2 replication, hosting-
liability tariff replication, and the proposed generic scoped-launch gate)
enforces spending by comparing *remaining* budget against a *per-cell* cap,
cell by cell, as execution proceeds — see
`capage/homeostasis_v2_replication_runner.py`'s `remaining =
aggregate_cost_cap_cents*_COST_UNITS_PER_CENT - model_cost_units` check
before each cell, and `capage/homeostasis_v2_replication.py`'s
`validate_plan`, which happens to force `aggregate == CELL_COUNT * per_cell`
for that one frozen, single-phase, homogeneous design. That pattern works
when every unit of work has the same cap and the total unit count is fixed
and small. It does not generalize cleanly to a design with multiple phases
of different shape — for example a scout phase followed by a main phase,
or a per-cell cap that varies by condition — because nothing currently
computes the **worst case of the entire planned run** as a single number
before the first cell starts, and refuses if that number exceeds the
ceiling.

This gap is not hypothetical for the currently-discussed 128-condition
two-axis sweep (spending caps × deliberation structures): its own cost
model is presently **unreconciled** — a scout-plus-main estimate near
$92.40 against a $100 ceiling, an aborted-run token profile that does not
obviously match the stated per-cell cost, and a per-cell cap that may
truncate high-tariff deliberation conditions before they finish reasoning.
Nothing in this proposal resolves that contradiction, and this document
does not claim it does. What it proposes is a mechanism that would make
that kind of contradiction structurally impossible to launch through
unnoticed: if the worst case cannot be honestly computed and shown to fit
under the ceiling, the framework refuses to start, full stop — which is a
stronger requirement than "the estimate looked fine."

## Relationship to existing layers

This is explicitly the **inner** layer of two independent layers, not a
replacement for either:

| Layer | Where | What it assumes | What it catches |
|---|---|---|---|
| **Outer** | Anthropic console API-key spend limit (Kev sets directly, out of band from any repository code) | Nothing about the code. Holds even if every check in this repository is buggy, bypassed, or absent. | Any spend past the limit, from any cause, including a defect in this very proposal. |
| **Inner** (this proposal) | Framework preflight, before any provider client is constructed | Good faith in the code — i.e., that the gate/runner code itself is not compromised or malicious. | An honestly-computed run whose *planned* worst case exceeds the *intended* per-experiment ceiling, refused before a single cent is spent, rather than discovered mid-run or after the fact. |

Both must hold independently. The console limit is a backstop that does not
care what CapAge's code does or intends; this proposal is a design-time and
launch-time check that CapAge's code intends something bounded, checked
mechanically rather than by review attention alone. Neither substitutes for
the other: the console limit alone would still let an unreconciled or
mis-costed plan *start* and run partway before hitting it (as the aborted
28.9156-cent attempt and the 5-cell/$1.08 hosting-liability stop both show
happens today even with reactive caps in place); this proposal alone would
still be defeated by a compromised gate, credential, or account, which only
the console-level, code-independent limit defends against.

## What "worst case" means

Worst case is **not** an expected-cost estimate (average tokens observed,
typical deliberation length, batch-discount pricing assumed to apply). It
is the maximum the frozen plan's own declared parameters could possibly
produce if every unit of work in it consumed its full declared cap, computed
purely from numbers already frozen in the manifest/plan before any provider
call — no live measurement, no historical average, no discount assumption
that a cheaper API mode will actually be used.

Concretely, for a plan with one or more phases, each phase `p` declares:

- `unit_count_p` — the number of chargeable units the phase will attempt
  (cells, scout probes, batch items — whatever the phase's own unit is).
- `per_unit_cap_cents_p` — the frozen per-unit cost ceiling for that phase
  (the existing `per_cell_cost_cap_cents` concept, generalized to any
  phase's unit).

Then:

```
worst_case_cents = sum over all phases p of (unit_count_p * per_unit_cap_cents_p)
```

with two required properties, both machine-checked rather than merely
documented:

1. **No discount assumed.** If a phase might run in a cheaper mode (batch
   API, reserved capacity), the worst case uses the phase's *non-discounted*
   per-unit cap unless the discount is itself a frozen, contractually
   guaranteed rate — an expected-cost discount is evidence for a design
   review, never an input to the refusal check.
2. **No truncation assumed favorably.** If a per-unit cap could plausibly
   cut off a unit of work before it reaches a natural stopping point (the
   sweep's own "per-cell cap possibly truncating high-tariff deliberation"
   concern), the worst case still charges that unit its full cap — the cap
   is a ceiling on cost, not a promise that the unit's task completes
   within it. A cap that is frequently expected to bind mid-task is a
   design smell this check surfaces, not a case the check can wave through
   as "probably fine, it'll cost less."

`worst_case_cents` must equal or be less than the plan's declared aggregate
ceiling for the check to pass. Where a plan's own internal accounting (like
today's `aggregate == CELL_COUNT * per_cell` assertion) already forces this
by construction, the generalized check is redundant-but-harmless for that
plan and becomes load-bearing exactly for plans — like a scout-plus-main
sweep — where no such single-phase identity already holds.

## Where the check lives in the executor path

Following `docs/SCOPED_PAID_ACTION_GATE_V1.md`'s existing architecture
rather than inventing a parallel one: this would be **one new preflight
invariant**, checked with no provider secret in scope, in the same place
invariant #9 ("spending caps are declared before authorization ... caps
cross-checked to equal the phrase's cents") already lives — i.e. in
`capage/scoped_launch_gate.py`'s `preflight` subcommand if that module is
ever built, or, absent that generalization, as an equivalent function
callable from each frozen plan's own `validate_plan`.

Concretely, proposed as a small, dependency-free, pure function:

```
compute_worst_case_cents(manifest_or_plan) -> int
```

taking the already-frozen, already-hashed manifest/plan structure (no I/O,
no network, no provider import) and returning the single worst-case number
defined above. Preflight calls it, compares against the declared ceiling,
and **exits nonzero — refuses, does not warn — if `worst_case_cents >
ceiling_cents`.** This sits *before* invariant checks that require git
ancestry or a merge commit are even relevant to spending, and strictly
before the `execute` job that has step-scoped access to
`ANTHROPIC_API_KEY` — mirroring the existing rule that preflight runs
"without any secret" and "any invariant violation stops the run before the
execute step can see a credential."

This function would also be unit-testable with mock manifests and no
provider client, consistent with the standing rule that tests never
instantiate a live provider client, and would be run under
`--validate-only` alongside the other frozen-input checks named in
`AGENTS.md`'s unpaid verification list.

Two hard requirements on the check itself, mirroring
`ALLOWED_MODULES`/`DECIMAL_ERROR_BACKSTOP_CENTS`'s existing posture:

- **The framework enforces this on the agent, never the agent on itself.**
  The check does not live in strategic-model prompt text, a runner's
  internal "please stay under budget" instruction, or anything the
  proposing code could talk itself out of. It lives in the same
  no-secret, code-reviewed preflight gate that already refuses to let an
  invalid phrase, a tampered manifest, or an expired tariff reach the
  execute step — a boundary external to the proposer, exactly as
  `AGENTS.md` requires for all authorization.
- **Fail closed on ambiguity.** If a manifest declares a phase whose
  `unit_count` or `per_unit_cap_cents` cannot be resolved to a concrete
  integer from frozen, already-hashed inputs alone (e.g. a phase whose
  unit count depends on a runtime decision), the check refuses rather than
  guessing a number — an unbounded or data-dependent worst case is not a
  worst case at all, and preflight should treat "cannot compute a bound"
  identically to "bound exceeded."

## How a refusal is recorded in the ledger

Consistent with existing practice (the aborted 32292164227 attempt's
28.9156-cent cost record, and `SCOPED_PAID_ACTION_GATE_V1.md`'s "evidence is
preserved on every outcome, including failures"), a preflight refusal on
this check is itself a durably recorded event, per Constitution cl. 83
(durable ledger) and cl. 84 (failure preservation) — a refused launch is not
quietly discarded:

- The preflight step still emits its provenance JSON (as every other
  invariant check already does), with an explicit
  `"status": "refused_worst_case_exceeds_ceiling"` (or equivalent),
  `worst_case_cents`, `ceiling_cents`, and the phase-by-phase breakdown that
  produced the total.
- **Attributable cost is zero, and is recorded as zero, not omitted.** No
  provider client was ever constructed; this differs in kind from the
  preserved aborted-attempt record, whose 28.9156 cents reflects real
  provider usage that happened before an unrelated checkpoint bug aborted
  the run. A worst-case refusal has no provider usage to preserve — the
  ledger entry exists to record that a launch was attempted and stopped,
  not to preserve spend that never occurred.
- The workflow's artifact-upload-on-every-outcome behavior (`if: always()`)
  already covers this case if the check lives inside the same workflow
  shape `SCOPED_PAID_ACTION_GATE_V1.md` describes; no new artifact
  mechanism is needed.
- Because the authorization file is still consumed structurally the same
  way an invariant-4/5/6/7 failure already behaves (the merge happened; the
  phrase was spent), a refused launch is **not silently free to retry with
  the identical manifest** — see next section.

## Whether refusal can be retried, or must escalate to Kev

**Must escalate; may not be silently retried by the agent.** A worst-case
refusal is not a transient failure (like a flaky network call) that a retry
could plausibly resolve — the same frozen manifest, re-run unchanged, will
compute the identical worst case and refuse identically every time, by
construction. There is nothing for an automatic or agent-initiated retry to
do that would change the outcome, so offering one would only create the
appearance of a recovery path where none exists.

The only two ways forward, both requiring Kev, mirror the constitutional
non-self-expansion boundary (cl. 34: CapAge may not broaden a spending or
liability limit; cl. 39/40: standing authorization does not generalize, and
consequential actions require stronger authorization than routine ones):

1. **Narrow the plan.** Reduce `unit_count_p` or `per_unit_cap_cents_p` for
   one or more phases (e.g., fewer conditions, a tighter per-cell cap, a
   smaller scout phase) so the recomputed worst case fits under the
   existing ceiling. This is a manifest change, which — following the
   existing freeze-PR discipline — produces a new frozen manifest, a new
   commit SHA, and therefore requires a new, fresh, byte-exact phrase from
   Kev; the old phrase (if any existed yet) was never valid for a different
   manifest in the first place.
2. **Raise the ceiling, explicitly, live.** Kev raises the declared
   ceiling in a new reviewed manifest freeze, the same way he would set a
   higher console spend limit or approve a larger per-action cap under
   `SCOPED_PAID_ACTION_GATE_V1.md`'s existing per-action-proposed-cap
   pattern. This is never something the agent proposes to itself and
   grants; Coder may propose a number with reasoning, exactly as that
   document already describes for ordinary per-action caps, but only Kev's
   fresh phrase makes any cap real.

No code path in this proposal would auto-retry, auto-widen, or silently
resubmit a refused manifest. A repeated refusal on an unchanged manifest is
itself worth surfacing to Kev as a signal that the design's cost model
needs work before any launch attempt, rather than being treated as routine
friction to route around.

## Explicit non-resolution of the current sweep's cost-model contradiction

To avoid this document being read as more than it is: it does not reconcile
the 128-condition sweep's scout+main-vs-$100-ceiling gap, the aborted-run
token-profile mismatch, or the per-cell-cap-truncation concern named in the
mailbox context notes. Those require someone to actually work out real
phase-by-phase worst-case numbers for that specific design — which this
proposal's `compute_worst_case_cents` function is built to consume, not to
generate. **No paid sweep run is authorized by this document, and none
should be attempted, until that reconciliation happens and the sweep's own
manifest can pass the check described here with margin, not just on paper.**

## Adoption gates

Mirroring `SCOPED_PAID_ACTION_GATE_V1.md`'s existing three-gate discipline:

- **Gate A — design**: acceptance of this document as a basis for
  implementation planning. Authorizes nothing else.
- **Gate B — implementation**: separate explicit approval before
  `compute_worst_case_cents`, its preflight integration, or any test is
  written. Unpaid, mock-tested, normally reviewed, like every other gate
  module change.
- **Gate C — per-action authorization**: unchanged from standing policy —
  a fresh manifest freeze, a fresh byte-exact phrase, and (per the adopted
  `paid-runs` environment hardening) Kev's environment approval, every
  time, for every action, including any future 128-condition sweep launch.

No part of this document weakens, replaces, or reinterprets `AGENTS.md`,
the Constitution, frozen protocols, `SCOPED_PAID_ACTION_GATE_V1.md`, or
preserved evidence. If any conflict is found between this document and
those sources, those sources win and this document must be corrected.
