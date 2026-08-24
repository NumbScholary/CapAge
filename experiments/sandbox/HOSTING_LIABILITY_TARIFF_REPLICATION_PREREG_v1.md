# Hosting Liability Tariff Dose-Response Replication -- Preregistration v1

Status: APPROVED by owner (Kev), 2026-08-24. Approval covers the
preregistration design as written; it does NOT itself authorize spending,
provider calls, or a paid run -- a separate, explicit, byte-exact owner
authorization phrase is still required at actual launch time (Section 12).

Repository: Numbscholar/CapAge
Branch: PR #47 (code merged/ready, CI green 231/231 as of 2026-08-24)
Prepared by: Keeper (Claude), from mailbox record and live owner decisions,
2026-08-24.

## 1. Research question

Does a recurring hosting-cost tariff charged against a governed economic
agent's simulated capital measurably change how the agent allocates its
tokens/effort across transactional versus passive tool use, in a
dose-dependent way?

## 2. Independent variable

Hosting cost tariff, charged as a fixed cents-per-simulated-day liability
against the agent's ledger balance. Four levels:

- 0 cents/day (control)
- 15 cents/day
- 45 cents/day
- 135 cents/day

Chosen as a fixed, exogenous cost rather than a percentage-of-balance
tariff. Rationale (owner-confirmed 2026-08-24): a percentage-of-balance
tariff would make the treatment a function of the agent's own prior
decisions, contaminating causal interpretation. A fixed absolute tariff is
arbitrary in magnitude but exogenous and dose-clean, which is required for
a dose-response design across matched worlds.

## 3. Held constant: reserve floor = 0

`reserved_input_tokens` and `reserved_output_tokens` are held at their
default value of 0 for all four arms of this experiment, meaning
`_min_reserve_cents` = 0 throughout. This is an explicit, deliberate
choice, not an unexamined default:

- It matches the reserve floor value already used in all 24 historical
  matched worlds from the completed V1/V2 blocked replication, keeping
  this experiment's baseline consistent with existing evidence rather
  than introducing a second uncontrolled change.
- Holding it at zero means the agent has no protected token runway
  cushioning it from the tariff's bite at any level, including the
  135 cent/day arm -- this is intentional. The reserve floor is reserved
  as a separate, second experimental variable (see Section 9), to be
  tested only if this experiment shows a meaningful tariff effect worth
  probing for interaction.
- No code change was required to hold this constant; it is enforced by
  simply not setting `reserved_input_tokens` / `reserved_output_tokens`
  in this experiment's manifest.

## 4. Dependent variables

**Primary (confirmatory):** Fraction of tokens spent on transactional
tools (`search_market` + `send_offer` + `submit_delivery` +
`request_feedback`) versus passive tools (`observe` + `inspect_ledger` +
`wait`), computed per cell, as a function of tariff level.

**Secondary (exploratory):** Full 7-tool token distribution per cell,
plotted across all 4 arms -- intended to surface whether a higher tariff
simply inflates passive checking behavior (e.g. more frequent
`inspect_ledger` calls) rather than genuine transactional activity, which
would argue against the primary hypothesis rather than for it.

**Unit of analysis:** Per-cell in both cases (12 cells per arm), to
preserve cell-to-cell variance. Not pooled into a single arm-level mean.

**Secondary metrics (previously locked, unchanged):** ending capital
percentage, and days-to-first-productive-action (censored where
applicable).

**Failed-decision accounting:** Tokens spent on decisions that never
resolved to a valid host tool name are tracked separately in an explicit
`unattributed_failed_decision` bucket (implemented in
`tool_token_totals`), so metered-but-failed activity cannot silently
disappear from totals and bias the category fractions.

## 5. Design structure

- 4 arms (tariff levels above)
- 4 blocks
- 3 consecutive 30-day periods per arm per block
- 4 arms x 4 blocks x 3 periods = 48 paid cells, serial execution
- Balanced ordering across arms via a 4x4 Latin-square rotation
  (implemented, tested)

## 6. Model and cost parameters

- Model: claude-sonnet-5, medium effort (consistent with prior CapAge
  frozen replications)
- Per-cell cap: $0.45, matching the V2 replication's own per-cell cap.
  Confirmed owner decision (2026-08-24): the real provider-cost-generating
  mechanism (same model, same effort level, same decision horizon) is
  structurally unchanged from V2 -- only the synthetic hosting tariff
  differs between arms, and that tariff is simulated ledger accounting,
  not real provider spend, so it does not itself change real token costs.
- Aggregate cap: $21.60 for 48 cells (48 x $0.45), matching V2's
  aggregate-cap derivation exactly.
- These caps assume the frozen tariff schedule in effect as of
  2026-08-24; see Section 8 for the 2026-08-31 expiry and its
  implications for anything that slips past that date.

## 7. What is already built and tested (per Coder, verified via CI)

- Token-attribution counter (`tool_token_totals`), including the
  `unattributed_failed_decision` bucket -- tested, 9/9 pass.
- `SandboxRunConfig` hosting-field passthrough
  (`hosting_cost_cents_per_day`, `reserved_input_tokens`,
  `reserved_output_tokens`, `allow_unreserved_hosting_tokens`) --
  backward compatible, verified end-to-end manually (45 cents/day over
  3 simulated days produced an exact 135-cent balance reduction).
- `BlockedReplicationRunner` generalized for 4 tariff arms.
- 4-arm balanced ordering scheme (Latin-square rotation).
- Launch/authorization script (`capage/hosting_liability_replication_launch.py`),
  mirroring `homeostasis_v2_replication_launch.py`'s safety pattern:
  byte-exact confirmation phrase, one-shot execution guard, pre-call
  spend caps, fail-closed, `--validate-only` path. Built and pushed to
  PR #47, CI green.
- All experiment-specific tests passing; full suite 249/249 as of
  2026-08-24, minus the same 10 pre-existing unrelated failures present
  on the base branch.

## 8. What is NOT yet built / not yet in place

- The launch script cannot yet materialize a real plan. Its seed beacon
  (mirroring V2's own pattern) must derive from a real, tamper-evident
  merge commit -- specifically, this preregistration document's own
  merge commit into the active integration branch. Fabricating a seed
  ahead of a real merge would defeat the tamper-evident point of the
  beacon and was correctly declined by Coder rather than worked around.
  This document is being merged via PR #49 for exactly that reason.
- Time sensitivity: the previously frozen model tariff ($2/M input,
  $10/M output) is valid only through 2026-08-31. The merge-then-
  materialize chain (PR #49 merge -> beacon exists -> materialization ->
  launch-ready) needs to complete inside that window, or the cost
  assumptions in Section 6 must be reconfirmed against whatever tariff
  is actually in effect at that later time.

## 9. Deferred, sequential second experiment (not part of this
preregistration)

A second experiment varying the reserve floor (via
`reserved_input_tokens` / `reserved_output_tokens`) is explicitly
deferred, not combined into this design as a crossed factor. Rationale
(owner-confirmed 2026-08-23/24):

- A full crossing of 4 tariff levels x 4 floor levels would yield 16
  cells per block instead of 4, roughly a 4x cost increase over this
  design.
- The floor mechanically moderates how much bite the tariff has, making
  an interaction between the two variables more plausible than pure
  additivity -- so independent marginal experiments run separately could
  not reliably predict the combined effect.
- Agreed approach: run this tariff-only experiment first. Revisit the
  reserve-floor variable as a second, later experiment regardless of
  whether this one shows a strong tariff signal or a null result --
  both outcomes are informative for different reasons (a real effect
  raises the interaction question; a null result raises the question of
  whether the zero-floor setting is itself already suppressing or
  amplifying the visible tariff effect).
- Whether a reduced factorial design (e.g. 3x4 instead of 4x4) could
  later provide adequate statistical power at lower cost than a full
  crossing is an open, harder question requiring dedicated
  higher-reasoning analysis before committing to a combined design --
  explicitly flagged as not yet answered, not something to default into
  without that analysis.

## 10. Validity and integrity commitments (standard, per AGENTS.md /
Constitution)

- All 48 cells must complete with valid matched-world evidence, or the
  result is INCONCLUSIVE. No retries or replays of ambiguous or failed
  provider attempts.
- No tuning on frozen worlds; no changing this design after results are
  known.
- Costs, failed attempts, and adverse outcomes remain visible and are not
  omitted from reporting.

## 11. Explicit owner decisions on record (2026-08-24)

- Reserve floor held at 0 for this experiment, with documented rationale
  (Section 3).
- Tariff structure remains fixed cents-per-day, not percentage-of-balance,
  after considering and rejecting the latter for contaminating causal
  cleanliness (Section 2).
- Reserve-floor experiment deferred sequentially, to run regardless of
  this experiment's outcome, not gated solely on a positive tariff
  signal (Section 9).
- Full combined/factorial design (3x4 or 4x4) not ruled out long-term,
  but requires dedicated analysis before being adopted; not part of this
  preregistration.
- Per-cell and aggregate spend caps confirmed as $0.45 / $21.60,
  matching V2's own derivation (Section 6).
- Preregistration approved as written for launch-track purposes (this
  status line).

## 12. Outstanding before an actual paid run can occur

1. ~~Owner sign-off on this preregistration document as written.~~ DONE,
   2026-08-24.
2. ~~Confirmed per-cell and aggregate spend caps.~~ DONE, $0.45 / $21.60,
   2026-08-24.
3. ~~Construction of the launch/authorization script.~~ DONE, pushed to
   PR #47, CI green.
4. PR #49 (this document into the active integration branch) merged, so
   a real merge-commit beacon exists for materialization.
5. Materialization run against that beacon, producing the actual
   experiment plan.
6. A new, explicit, byte-exact owner authorization phrase at launch time,
   per standing CapAge protocol -- nothing above, including this
   approval, authorizes spending on its own.
