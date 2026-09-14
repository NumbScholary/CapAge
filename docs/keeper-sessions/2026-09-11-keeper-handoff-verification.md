# Keeper session handoff — 2026-09-11 (verification session)

Short session. Sole purpose: execute the next concrete step named by
`2026-09-11-keeper-handoff.md` — read Coder's replies directly from the
repository rather than from summary, resolve the flagged tension, and surface
positions to Kev before drafting anything.

Read back to Kev and approved before commit. Session moved to voice after this.

Supplements, does not supersede, `2026-09-11-keeper-handoff.md`. Nothing in this
document authorizes a merge, a spend, a provider call, or a repository change
beyond itself. Nothing was posted to the mailbox this session.

---

## Read directly this session

Branch `agent/mailbox-init`: the 09-11 handoff.
Branch `agent/hosting-liability-reserve-floor-axis` (PR #66):
`experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json`,
`capage/hosting_liability_replication_runner.py`,
`capage/hosting_liability_replication.py`.
Coder's replies `20260912-0240`, `20260912-0245`, `20260912-0300`.

Read-only throughout. No run, no spend, no merge, no executor change.

---

## Corrections to the 09-11 handoff

**1. Three Coder replies existed, not two.** The 09-11 handoff listed
`20260912-0240` and `20260912-0245` as awaiting. `20260912-0300-0310-chaos-reading-reachability-bound.md`
was also posted and was unlisted. It is the most consequential of the three —
it carries the guaranteed-null finding.

**2. The flagged tension was not a tension.** The 09-11 handoff could not
reconcile "stricter than the KeyError group" with "would not block a new Phase 1
plan." They are consistent. Strictness concerns *absence or emptiness* of
`valid_through`; the guard concerns whether the date is *past*. A new plan
carrying a future date satisfies all three sites. Verified by direct read:
required key at `from_plan`, unconditional `date.fromisoformat` at the end of
`from_plan`, and the ungated comparison in `run()`. Coder's Q1/Q2/Q3/Q5 and the
`execution_guard()`-runs-first ordering all confirmed in code.

**3. Keeper's load-bearing solvency claim was overstated.** Coder's correction
is accepted: `_capital_summary()` is returned by `observe()` as well as
`inspect_ledger()`, so the agent can already compute balance-sheet insolvency
itself. The datum is "did the agent act on what it could see," not "harness
knows, agent cannot." The genuine hidden-information instance is the floor and
`hosting_floor_throttled_days` — which, per finding 1 below, currently cannot
vary.

---

## Verified independently — Coder's guaranteed-null finding holds

Plan values confirmed by direct read, not accepted second-hand:
`starting_capital_cents_per_block` 25,000; `max_decisions_per_cell` 25;
`max_output_tokens` 1024; `horizon_days_per_period` 30; token tariff 200/1000¢
per million; `valid_through` `2026-08-31`; arms 0/15/45/135¢/day.

The conclusion stands: maximum 30-day outflow in the high arm is far below
starting capital, so `balance_cents` cannot reach zero in any of the 48 cells.

**One refinement, tighter than Coder stated.** The 45¢ per-cell provider cap is
hardcoded in the executor — `from_plan` raises unless it is exactly 45, and
`_validate_result` rejects a cell whose `actual_model_cost_units` exceeds it.
Coder's ~100¢ token component therefore cannot be reached inside a valid cell.
The discretionary bound is nearer 120¢ than 176¢. The conclusion is unchanged,
but the endogenous term is not merely empirically small — it is **structurally
capped and unchangeable by plan**. No version of "the agent spends itself into
insolvency" is reachable.

**Also locked:** `arm_hosting_cost_cents_per_day` is validated against
`TARIFF_CENTS_PER_DAY` in both `from_plan` and `validate_plan`. The arm spread
cannot be compressed to bring all four arms into one informative band. Starting
capital and horizon days are the only free levers, and both feed world
materialization (see finding 2).

---

## Two new findings — not yet put to Coder

**1. The reserve floor has no plan-to-runner path.** `ReplicationConfig` carries
no reserved-token field, `from_plan` reads no such key, and `_run_config()`
passes no `reserved_*` argument to the run-config factory. A floor key added to
a new plan would be **inert** — read by nothing.

Consequence: the two gauges have different pins. Lowering starting capital
unpins `unpaid_hosting_cents`. It does **not** unpin
`hosting_floor_throttled_days`, which requires a non-zero floor. Coder's 0300 §3
conjoins the two conditions ("with a zero floor *and* a balance never below the
amount owed"), which obscures that fixing capital clears only one of them. If
the throttle gauge is required to fire in Phase 1, that is an executor change
and Gate 2 — not a plan edit, and not covered by Coder's "one new plan, no
executor change" convergence.

Unverified by Keeper: the floor-to-throttle link rests on Coder's
`sandbox.py:751` claim. Also to be checked against
`claude-to-coder/20260903-1618-design-update-floor-removed-framework-floor.md` —
the zero floor may be a deliberate consequence of that decision rather than a
gap.

**2. Changing starting capital may invalidate the plan's matched-world
evidence.** `materialize_matched_worlds(beacon, frozen_config, world_factory)`
passes `starting_capital_cents` (and `horizon_days`) into the world factory, and
the runner's `__init__` raises `"matched-world materialization changed before
execution"` unless the recomputed records match the plan's `matched_worlds`
exactly. A new capital value may therefore force regenerating all twelve
matched-world records rather than editing one number.

Clean contrast: `valid_through` is **not** passed into materialization, so the
sentinel fix is free of this concern. The capital fix may not be. Whether it
bites depends on whether `reveal_world()["payload"]` or
`cost_policy_commitment` reflects starting capital — determinate, cheap for
Coder to evaluate, and currently unanswered.

Secondary: `validate_plan` would not catch this. It checks matched-world
coordinates and structural completeness, not digests. Only the runner's
constructor does. The two validation layers differ in strictness and the later
one is the strict one.

---

## Open for Kev

1. **Sentinel vs. optional** on `valid_through` (Coder recommends sentinel for
   Phase 1, optional as a later separate change).
2. **New starting capital**, and whether one arm or all four sit inside their
   informative band. Per-arm reachability ceilings are in Coder's 0300 §2.
3. **One frozen ceiling value, or a prereg'd set of candidates recorded
   post-hoc.** Coder recommends the set; Keeper agrees — strictly more
   information from the same run, and it removes a choice none of us can justify
   on merit.
4. **New: must the throttle gauge fire in Phase 1 at all?** Arising from finding
   1. If yes, Phase 1 touches the executor. If no, it should be stated in the
   preregistration so that `hosting_floor_throttled_days ≡ 0` is not later
   misread as a null result rather than an arithmetic certainty.

---

## Next concrete step

Put findings 1 and 2 to Coder as questions, after Kev confirms them. Session
continued in voice from this point.

— Keeper
