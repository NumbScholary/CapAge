# Keeper Session Handoff — 2026-09-12 (third)

**Session:** 2026-09-12, morning. Short session following the overnight
session recorded in `2026-09-12-keeper-handoff-second.md` (`549da9e`).

**Roles unchanged.** Kev is Overseer — sole merge authority, sole decision
authority. Keeper holds governance, reasoning, and record-keeping. Coder is
reachable only via the file-based mailbox and does not watch it unprompted.

---

## 1. Mailbox verified, not assumed

[FACT] Mailbox checked directly at session start via `list_commits` on
`agent/mailbox-init`. Nothing new since `6c0aae1`, 2026-09-12 04:36 UTC —
roughly eight hours before this session opened.

Kev's prior expectation that nothing had landed was correct, and he asked for
it to be verified rather than assumed ("count da teeth"). Recorded because the
verification is the point, not the result.

## 2. Correction to handoff-second §1 — carried here

[FACT] Coder's `6c0aae1` flags an error in `2026-09-12-keeper-handoff-second.md`
§1. That handoff states, unhedged, that the `valid_through` deletion was queued
because the field sits inside the frozen cost policy and removal would change
the hash.

[FACT] It does not. `cost_policy_commitment` hashes `asdict(token_tariff)` +
`cost_units_per_cent` (plus hosting/reserved fields), and `TokenTariff` has
exactly three fields. `valid_through` lives in
`SandboxRunConfig.tariff_valid_through`, `ReplicationConfig`'s
`config_commitment`, and the frozen plan bytes.

[FACT] The claim was explicitly labeled "inference, not verified against the
code" in the 0400 mailbox message
(`claude-to-coder/20260912-0400-valid-through-sentinel-ruling.md`, `63c5f91`).
The hedge was dropped one document later. This is Keeper's error and is the
labeling failure mode Clause 9 exists to catch.

[FACT] Coder deliberately wrote no correction himself, on the grounds that
`docs/keeper-sessions/` is Keeper's directory and handoffs are append-only.

**The ruling is unaffected and is not reopened.** Sentinel adopted; outright
deletion queued behind preregistration; item closed. Only the stated
justification was wrong.

[FACT] The real constraint is narrower and more tractable than supposed:
removal would change `config_commitment` and `plan_sha256` only. Neither
`world_commitment` nor `cost_policy_commitment` carries the field, so the twelve
matched-world records keep reproducing. Smaller than the 2026-08-22
hosting-liability precedent.

[DECISION — Kev, this session] This handoff carries the correction; no separate
correction file. A fresh instance reads the most recent file first, so one
commit serves where two would not.

## 3. Next concrete step — unchanged

Determine whether the near-zero acceptance base rate is **the world being hard**
or **the agent playing it badly**. One paid contract across twenty-five offers.
Starting capital, horizon length, cap value, and any higher-reasoning pass are
all downstream of this.

[INFERENCE] Leading suspect is the flat-pricing finding from `169418f`: agents
set one price for every offer against customer budgets varying six-fold
(2,500–20,000¢). Price fit multiplies directly into acceptance, so a flat price
against a hidden six-fold spread is wrong for most offers by construction. This
looks less like a risk posture than like failing to notice a decision exists.

[PROPOSAL — Keeper, not authorized, not posted] A read-only diagnostic ask to
Coder: realized acceptance probability across the twenty-five offers, and
counterfactual acceptance at alternative prices, from data already paid for.
Answerable by reading code and existing artifacts. No spend, no execution.
Requires Kev's explicit authorization before posting.

## 4. Carried forward unchanged

- **Starting capital** — unset. Informative bands differ ~24× across arms.
- **Horizon length** — unruled. Cheaper than first thought, but still
  regenerates all twelve world records (`horizon_days` enters
  `world_commitment`).
- **Per-cell cap** — stays 45¢ on measured evidence. Worst observed
  extrapolation 37.37¢; 45¢ and 40¢ discard none.
- **Prompt caching** — a lever for Kev, not a proposal. Gate 2; touches
  SHA-pinned `sandbox_runner.py`.
- **Re-materialization of the twelve world records** — noted, unauthorized.
- **Higher-reasoning pass on cell length** — must carry Coder's 0430 *and* 0423
  alongside Addendum One, or a stronger model reaches the conclusion Coder
  partly retracted.
- **Open PRs** — #66, #67, #69, #70, #71, #73, #78, all unmerged. Merge
  authority is Kev's alone.
- Confirm `hosting_floor_throttled_days` ≡ 0 enters preregistration as
  expected-by-design.

## 5. Note on this session's conduct

Late in the session Keeper emitted a closing line claiming to have lost the
thread and proposing a fresh conversation, which contradicted the substantive
answer in the same message. It was not meant and did not reflect the state of
the session. Recorded so a fresh instance does not read it as a real signal
about context quality at the time.

---

*Read back to Kev and approved before commit, per the standing grant of
2026-09-03 under Clause 39.*
