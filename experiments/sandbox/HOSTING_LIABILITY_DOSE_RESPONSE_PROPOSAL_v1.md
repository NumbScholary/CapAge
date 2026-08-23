# Hosting-liability dose-response experiment — design proposal (DRAFT)

Status: **draft proposal only**. Not preregistered, not seeded, not
authorized, not funded-and-locked. Contains no seed beacon, no JSON plan, no
workflow, no authorization marker, and no change to any frozen module. This
document exists so Kev can review and lock a spec; it is not itself that
lock. It responds to a request recorded in the agent mailbox
(`.agent-mailbox/claude-to-coder/20260823-0808-hosting-liability-experiment-preregistration.md`
on `agent/mailbox-init`).

## Question

Does the *magnitude* of a recurring hosting-cost tariff (not just its
presence/absence) function as a dose-responsive, falsifiable substitute for
the "hunger" homeostasis signal — i.e. does higher hosting pressure produce
measurably earlier/more sustained productive action?

This is a separate, narrower experiment from the frozen V2 blocked
replication (`experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_PREREG.md`),
which remains untouched and independently gated. Nothing here varies the V1
or V2 controller; the single strategic policy is held fixed and only the
hosting tariff varies across arms.

## Design

- **Arms (4, tariff level):** zero (baseline), low, medium, high — see
  "Tariff values" below.
- **Blocks:** 4 independent blocks (down from the V2 replication's 8, since
  4 arms already quadruples the per-block cell count relative to V2's 2
  arms).
- **Periods per block:** 3 consecutive periods per arm, matching the V2
  replication's within-block structure. Capital, hosting liability, and any
  other per-block state begin fresh at the start of each block and stay
  isolated by arm within a block, mirroring
  `HOMEOSTASIS_V2_REPLICATION_PREREG.md`'s blocking rationale.
- **Cells:** 4 blocks x 3 periods x 4 arms = **48 paid cells**, i.e. the same
  total cell count as the frozen V2 replication, restructured from a 2-arm x
  8-block layout to a 4-arm x 4-block layout.
- **Model / effort / caps:** unchanged from the frozen V2 replication basis —
  `claude-sonnet-5`, medium effort, 45 cents/cell cap, $21.60 aggregate cap.
  Kev has already confirmed the $14-22 actual-cost range is acceptable and
  funded.

## Tariff values

Grounded in `capage.sandbox.STARTING_CAPITAL_CENTS = 25_000` (i.e. $250, the
real default used across the sandbox and all frozen homeostasis
experiments) and in how hosting cost actually accrues
(`EconomicSandbox._collect_hosting_cost`, called once per calendar day from
`_advance_one_day`, `capage/sandbox.py:1045` and `capage/sandbox.py:1478`):
hosting is billed once per simulated day regardless of how many decisions the
agent takes that day, and any amount that can't be collected (balance would
go below `_min_reserve_cents`, which is 0 unless token reservation is also
configured) rolls forward as `_unpaid_hosting_cents` rather than forcing
negative balance.

With the period length proposed below (14 days/period, 42 days/block — see
next section), a fully idle agent (never earns, never pays down hosting) is
exposed to hosting collection for up to 42 days per block.

| Arm | Daily hosting cost | 42-day idle exposure | % of starting capital ($250) |
|---|---|---|---|
| Zero (baseline) | $0.00/day (0 cents) | $0.00 | 0% |
| Low | $0.60/day (60 cents) | $25.20 | ~10% |
| Medium | $1.25/day (125 cents) | $52.50 | ~21% |
| High | $2.50/day (250 cents) | $105.00 | ~42% |

This keeps "high" inside the requested "roughly a third to half of starting
capital burned over the full duration if the agent takes no productive
action" band, gives a roughly geometric (0, 1x, ~2x, ~4x) dose ladder rather
than an evenly-spaced one (evenly spaced values would compress the
low/medium contrast relative to high), and leaves enough of a gap between
"zero" and "low" that a completely idle low-arm agent would still be
solvent at block end (~90% of starting capital remaining) — so the low arm
tests whether *any* nonzero hosting pressure moves behavior, not just
whether the agent avoids bankruptcy.

Caution: because unpaid hosting cost rolls forward as a separate liability
once balance hits the reserve floor rather than continuing to reduce the
reported balance, an idle high-arm agent's `balance_cents` will floor at 0
(and `insolvent` will read `True`, per `capage/sandbox.py:1868`) partway
through a 42-day idle block, while `unpaid_hosting_cents` keeps growing
unboundedly and invisibly to any metric that reads `balance_cents` alone.
See "Primary metric" below for why this matters for metric choice.

## Recommended period length: 14 days/period (42 days/block)

Down from the V2 replication's 30 days/period (90 days/block). Reasoning:

- The V2 replication's 90-day block arc was calibrated to observe long-run
  quality, dispute, and reputation dynamics across a full simulated
  customer relationship lifecycle — that is not this experiment's question.
  This experiment is about early motivational/timing dynamics
  (days-to-first-productive-action, idle-day fraction), which are legible
  within the first one to two simulated weeks.
- **Recommend leaving `max_decisions_per_cell` at 25 (unchanged from the
  frozen V2 value)** rather than scaling it down with the shorter horizon.
  Cost is governed by decision/tool-call count and token usage, not by
  calendar days directly (hosting collection is a same-day bookkeeping
  step inside `_advance_one_day`, not an extra model call). Keeping 25
  decisions/cell means:
  - the empirical ~28.5 cents/cell prior from the completed V2 replication
    remains a directly applicable cost basis (same decision budget, same
    model/effort/token config), so Kev's already-reviewed ~$13.70 estimate
    and $14-22 acceptable range do not need to be recomputed; and
  - the same decision budget spread over fewer days raises decision density
    per day, which if anything improves resolution on
    days-to-first-productive-action rather than degrading it.
- 42 days/block (3 x 14) still leaves room for the second and third periods'
  lagged completed-period signal (mirroring V2's within-block continuity) to
  matter, without carrying V2's full 90-day scope.

This is a recommendation, not a locked value — Kev/Claude should confirm
before any seed derivation.

## Candidate primary metric

Ranked, for Kev to lock one primary + secondary set before any paid cell,
per the "locked before running, not chosen after seeing results" constraint
in the request:

1. **Days-to-first-productive-action (primary).** Most directly operationalizes
   the hypothesis (does tariff magnitude change how fast the agent acts).
   Cleanest single-number dose-response readout, least sensitive to
   downstream market luck differences between matched worlds.
2. **Fraction of idle days (secondary).** Complements (1): captures whether
   pressure produces one early burst versus sustained engagement across the
   block. Two arms could match on (1) and differ substantially on this.
3. **Ending capital, reported as *both* raw `balance_cents` and
   `balance_cents - unpaid_hosting_cents` net position (secondary, not
   primary).** Needed as an outcome/sanity check (does urgency-driven action
   actually preserve capital, or does the agent churn without earning
   enough to outpace the tariff) but should not be primary: as noted above,
   `balance_cents` alone floors at 0 on insolvency while
   `unpaid_hosting_cents` keeps accruing past that point, which would
   otherwise mask a real medium-vs-high dose difference once both arms go
   insolvent within a block. This mirrors why the V2 replication treated
   capital as an estimand requiring care rather than a single raw number.

Recommend locking (1) as primary, (2) and (3) as secondary/descriptive,
before any paid cell — matching the primary/secondary split structure
`HOMEOSTASIS_V2_REPLICATION_PREREG.md` already uses.

## Implementation gaps (must be resolved before any seed derivation or run)

1. **`capage/homeostasis_v2_replication.py` is frozen and 2-arm-only.**
   `ARMS = ("v1", "v2")` (line 25), `CELL_COUNT = BLOCK_COUNT *
   PERIODS_PER_BLOCK * len(ARMS)` (line 26), and `execution_order:
   tuple[str, str]` (line 205) are hardcoded for exactly two arms and are
   explicitly commented as the permanent evidentiary record of a completed
   run — they must not be edited. A 4-arm dose-response design needs a new,
   separate module (not a modification of this one) with an N=4 execution
   order per period, balanced across arms within each block (e.g. a
   balanced Latin square over the 4 tariff levels rather than V2's simple
   pairwise swap) so no arm systematically goes first/last within a block.
2. **`capage/homeostasis_v2_replication_runner.py`'s per-arm dispatch is
   controller-shaped, not tariff-shaped.** `_expected_signal` calls
   `signal_for_arm_start(arm)` / `completed_signal_for_arm(arm, ...)`
   (imported from `capage/homeostasis_v2_experiment.py`), which branch on
   `arm` meaning "which controller (v1 or v2) is running," not "which
   hosting tariff is active." This experiment needs a new runner that runs
   one fixed controller four times per block/period with only
   `hosting_cost_cents_per_day` varying — the existing runner cannot be
   reused as-is and a new one must be written and reviewed, mirroring the
   existing runner's checkpoint/audit structure rather than copying its
   controller-comparison logic.
3. **No sandbox-level blocker.** `EconomicSandbox.__init__` already accepts
   and validates `hosting_cost_cents_per_day` as a plain non-negative int
   keyword (`capage/sandbox.py:664`, validated at `:686-693`), and
   `observe()` already surfaces both `unpaid_hosting_cents` and the
   model-cost/cap pair every turn (confirmed in the mailbox request from
   Coder's prior visibility check). No sandbox plumbing work is needed;
   the gap is entirely in the frozen plan/runner layer (points 1-2), not in
   `EconomicSandbox` itself.
4. **Metric/reporting decision (see "Primary metric" above) needs an
   explicit answer before lock:** should ending-capital reporting net out
   `unpaid_hosting_cents`, and should insolvency be redefined for this
   experiment (e.g. "balance would go negative absent the reserve floor")
   given hosting debt can now accrue past the point `balance_cents` floors
   at 0? V2's `insolvent = balance_cents == 0` definition
   (`capage/sandbox.py:1868`) was written before opt-in hosting liability
   existed and may need revisiting for a tariff-focused experiment
   specifically about capital depletion pressure.

None of the above has been implemented. This document proposes values and
flags gaps; it does not create the new plan/runner module, derive any seed,
or touch `capage/homeostasis_v2_replication.py`,
`capage/homeostasis_v2_replication_runner.py`, or any workflow file.
