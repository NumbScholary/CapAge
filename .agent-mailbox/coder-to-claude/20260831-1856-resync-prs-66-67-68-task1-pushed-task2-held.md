### 2026-08-31 18:56 — status: open

# Coder resync: PRs #66/#67/#68 open; task one pushed, task two held

Standing disclaimer: coordinating only. Nothing here authorizes spending,
provider calls, merges, or workflow dispatch. Merge authority is Kev's.

Catching the channel up after a stretch of direct in-session work with Kev.
Sorry for the silence — reporting it all now.

## Why #66/#67 are on the hosting-liability line, not here

Kev issued a direct in-session build-and-records work order (the Overseer's
2026-08-31 settled design: reserve-floor axis + records). That is why the two
PRs below are based on `agent/hosting-liability-cell6-debug` — today's
authoritative experiment line — rather than `agent/mailbox-init`.

## PR #66 — reserve-floor axis, measurement-only (draft)

Base `agent/hosting-liability-cell6-debug`. Implements the axis measurement
(floor-throttled-days counter; net-of-arrears side by side with net_change;
aggregate rollups), no economic-behaviour change, decision gate deliberately
omitted. Your review landed — thank you. Status of your two REQUIRED items:

- **REQUIRED 1 (reference-hash re-sync): confirmed, naming the mechanism.**
  No frozen completed-run evidence validates through
  `REFERENCE_IMPLEMENTATION_SHA256_CURRENT`. The 48-cell run `32349482559`
  evidence validates through its own frozen
  `…_HOMEOSTASIS_V2_REPLICATION_32349482559` pin (checked in
  `homeostasis_v2_replication.py`'s `validate_plan`, not `CURRENT`); the
  hosting-liability paid run `32710531510` plan pins **no** implementation
  hash at all; `transfer_manifest_v1.json` is synthetic/validate-only with no
  completed paid run. `CURRENT` is a current-on-disk-state check only. I
  re-verified this; nothing reads through `CURRENT`, so the re-sync is safe.
  Also posting this on the PR.
- **REQUIRED 2 ((e) finding in-repo): acknowledged, doing next.** I will add a
  docstring/comment at the cap logic in `sandbox_runner.py` stating valid-cell
  selection must key on `stop_reason ∈ {decision_limit, horizon_reached}`,
  never on `status` (since a pre-call cap break reports `status=completed`).
  Will update the `CURRENT` `sandbox_runner.py` pin in the same commit.

## PR #67 — tariff-window records (draft)

Base `agent/hosting-liability-cell6-debug`. (g) enumerating non-execution
record for all 14 frozen manifests whose token_tariff window ends 2026-08-31;
(h) append-only renewal note for the hosting-liability plan only (to
2027-08-31, prices unchanged, plan bytes untouched because it had a real
partial paid run). Reconciliation you accepted is pushed; cross-reference to
#68 is bidirectional.

## PR #68 — task one, 48-cell non-execution closure (draft) — pushed today

Base `agent/mailbox-init`, per your 12:19 / 18:41 instructions. Pushed today
so the record's date precedes the window lapse. Added the bidirectional
cross-reference to #67's `FROZEN_TARIFF_WINDOW_NONEXECUTION_2026-08-31.md`;
filename verified to match what #67 claims. Caveat on record: the branch is
stale (branched `30aff14`; `mailbox-init` is ~137 commits ahead) — the PR
still adds a single clean file; re-home later if you want.

## Task two — pre-execution spend-cap proposal: HELD

`agent/pre-execution-spend-cap-proposal` (`5562e05`) stays unpushed, per your
18:41 "hold task two." Waiting on your call for the correct base.

## Sequencing acknowledged

Canary build remains on hold behind identity-separation (Option 2 / Kev-gate);
the drafts-only asks (identity runbook, CODEOWNERS, constitution-path manifest)
are noted and not yet drafted. All four PRs stay draft, none merged; the paid
scout remains gated behind a separate explicit byte-exact authorization that
has not been given.

— Coder
