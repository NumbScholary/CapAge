# Hosting Liability Tariff Dose-Response Replication -- Preregistration v1

Status: DRAFT for owner review. Not yet approved for launch. Nothing in this
document authorizes spending, provider calls, or a paid run.

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
- Per-cell cap: to be confirmed against the frozen tariff schedule in
  effect at launch time (see Section 8 -- time sensitivity)
- Aggregate cap: to be set explicitly before launch, not left implicit
- Prior-based cost estimate: previously described by Coder as smaller in
  scope than the original idle-days design, which itself fell within the
  $14-22 range already approved in principle for this class of
  experiment. A refreshed, exact estimate should be produced at
  preregistration sign-off rather than relied on from memory.

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
- All 23 experiment-specific tests passing; full suite 231/231 as of the
  transfer_manifest_v1.json stale-hash fix landed 2026-08-24.

## 8. What is NOT yet built (explicitly, per Coder's own status report)

- No `*AUTHORIZATION*.md` file or launch script exists for this
  experiment. There is currently no mechanism to actually launch a paid
  run, by design -- Coder deliberately did not bundle a launch/
  authorization layer into the code build, treating preregistration and
  launch authorization as requiring their own explicit review rather
  than shipping alongside feature code.
- This document is that missing preregistration. A separate launch
  script mirroring `homeostasis_v2_replication_launch.py`'s pattern
  (exact-byte confirmation phrase, spend caps enforced pre-call,
  fail-closed) is the second remaining piece of infrastructure, to be
  built only after this preregistration is reviewed and approved.
- Time sensitivity: the previously frozen model tariff ($2/M input,
  $10/M output) is valid only through 2026-08-31. If this experiment
  preregisters and launches under that tariff, timing matters. If the
  tariff schedule changes or renews, per-cell and aggregate caps in
  Section 6 must be reconfirmed against whatever tariff is actually in
  effect at launch, not assumed from this draft.

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

## 12. Outstanding before this can be approved for launch

1. Owner sign-off on this preregistration document as written.
2. Confirmed per-cell and aggregate spend caps against the tariff
   actually in effect at the time of approval (Section 6, Section 8).
3. Construction of the launch/authorization script (Section 8) --
   separate work item, not part of this document.
4. A new, explicit, byte-exact owner authorization phrase at launch time,
   per standing CapAge protocol -- this preregistration alone does not
   authorize spending.
