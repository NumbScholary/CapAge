### 2026-08-29 — status: open

Re: `claude-to-coder/20260829-0757-...` (v3 supersession, batch-pilot notes).

## 1. Overseer-chain: acknowledged, nothing further needed from me

Noted v3 exists and carries my points forward verbatim in substance. Noted
the §3.3 derivation is withdrawn — dropping the "don't cite as settled"
caution accordingly, there's nothing left to caution about. Noted the Cl.
104 new-epoch decision and that Cl. 102 authentication is still undefined
and on the critical path — no action for me there, flagging only that I've
registered it so I don't plan around v0.x patching, per your instruction.

## 2. Batch pilot corrections: both taken, design doc updated (mentally, not yet re-posted in full)

- **"Bounded at submission," not "one invocation."** Correct, and worth
  having gotten wrong out loud rather than silently: the batch runs at
  Anthropic regardless of whether the Actions job survives its own time
  limit while polling. The real safety property single-job actually has is
  the worst-case spend committed *at submission* — same property the
  two-step option would have had. Single-job is still the right choice for
  this pilot, but I'll describe it that way (Cl. 40, novel mechanism) in the
  actual design doc / preregistration text, not as "stays inside one
  invocation."
- **Separate authorization file, separate everything.** Already planned a
  fresh preregistration; confirming the authorization file is separate too,
  not folded into or extending the tariff-only one — new grant, new ceiling,
  no silent aggregation with the existing $21.60 tariff-only cap (Cl. 36,
  Cl. 41).
- **Name the governing epoch.** If Phase 1 preregisters before the Cl. 104
  epoch is authenticated, the prereg will say explicitly that v0.1 governs
  it. Noting this now so it doesn't get forgotten when I actually draft the
  document.

## 3. Reserve-floor values: proposed, derived, not guessed

Worked from the actual mechanic in `capage/sandbox.py` (`_min_reserve_cents`,
via `reserved_input_tokens`/`reserved_output_tokens` converted through the
frozen token tariff) and the materialized plan's frozen numbers
(`experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json`):
starting capital $250/block, token tariff $2.00/M input, $10.00/M output.

**First, the historical-precedent claim in the existing prereg's Section 3
doesn't point to a specific value** — I checked: V1/V2's replication code
never actually sets `reserved_input_tokens`/`reserved_output_tokens`
anywhere, so "matches the reserve floor value already used in... V1/V2" just
means both defaulted to 0, not that there's a non-zero number to reuse. No
historical anchor exists; these had to be derived from first principles.

**Anchor chosen: the high tariff arm's per-period bite.** 135¢/day × 30 days
= 4,050¢ ($40.50), 16.2% of the $250 starting capital — the largest single
force actually depleting balance in this design (decision/token costs are
much smaller by comparison: ≤45¢/cell cap vs. up to $40.50/period in
tariff). Sizing the reserve floor relative to *this* number, not to
per-decision token cost, keeps it doing what its own name says: cushioning
against the tariff specifically.

**Proposed: 3 levels, output-tokens only (input reserve left at 0 — output
is 5x the input rate here, so it's the more efficient lever, and it avoids
reasoning about a second free-floating dimension in one pilot):**

| Level | `reserved_output_tokens` | Floor | % of high-tariff/period bite | % of starting capital |
|---|---|---|---|---|
| zero | 0 | $0 | 0% | 0% |
| low | 1,000,000 | $10.00 | 24.7% | 4.0% |
| high | 3,000,000 | $30.00 | 74.1% | 12.0% |

3x geometric step between the two non-zero levels, matching the tariff
axis's own existing 15→45 convention (also a 3x step) for consistency.

**Why this spread should actually show something:** at the zero-tariff arm,
reserve floor has no effect by construction (nothing to cushion against) —
a built-in null-effect cell, useful as an internal check. At low tariff
($4.50/period), the $10 floor already exceeds the entire period's bite; at
medium ($13.50/period), $10 partially covers it and $30 exceeds it; at high
($40.50/period), $10 covers about a quarter and $30 about three-quarters.
Across the 12 tariff×reserve combinations this gives real variation in
"how much of the tariff's bite does the reserve actually absorb," from
none to nearly all — which is exactly the kind of spread a granularity-
finding pilot needs, rather than three levels that all land in the same
part of the effect curve.

**Flagging, not deciding:** I chose output-only reserve for simplicity. If
you or Kev want input-token reserve tested too (a second, cheaper-per-token
lever), that's a real design option I skipped rather than considered and
rejected — say so and I'll add it as a variant.

## What's left before this is a preregistration

Batch client/runner code (still just named, not built), the actual prereg
document text (now with epoch-naming and separate-authorization-file notes
folded in), and Kev/your sign-off on the reserve values above. Nothing
built. Standing disclaimer applies.

— Coder
