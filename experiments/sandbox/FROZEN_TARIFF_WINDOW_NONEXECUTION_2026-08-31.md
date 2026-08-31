# Frozen token_tariff window lapse — non-execution record, 2026-08-31

**Status: append-only non-execution record, 2026-08-31. This record makes no
provider call, authorizes no run or spending, and edits no frozen manifest.
Its only purpose is to leave a trace where a frozen tariff window lapses, so
the ledger is not quietly incomplete.**

## Why this record exists

Fourteen frozen manifests under `experiments/sandbox/` carry a `token_tariff`
(or `tariff_valid_through`) with `valid_through: 2026-08-31`. That window ends
today. Only one of them — the hosting-liability tariff replication plan — has
its window renewed (see
`HOSTING_LIABILITY_TARIFF_TOKEN_TARIFF_RENEWAL_2026-08-31.md`, renewed to
2027-08-31 with prices unchanged). The owner (Kev, 2026-08-31) deliberately
did **not** renew the other thirteen; renewing manifests not individually
considered would authorize plan changes by side effect. Their windows
therefore lapse today. Documenting one manifest while others lapse unrecorded
would leave the record silently incomplete, so all fourteen are enumerated
here with their disposition.

Lapse of a frozen tariff window is not a failure and is not INCONCLUSIVE about
any experiment. It means only that these manifests may not be executed as-is
after 2026-08-31 without a fresh, explicitly recorded tariff verification.

This record concerns the tariff-window lapse only. Where a manifest also has a
dedicated design-disposition record — for example the frozen 48-cell blocked
replication's closure in `HOMEOSTASIS_V2_REPLICATION_NONEXECUTION_2026-08-31.md`
— that record governs the design question; this table cross-references it and
does not restate or override it.

## Price context (shared by all fourteen)

Every listed window freezes the same Sonnet 5 rate: $2.00 / MTok input,
$10.00 / MTok output (200 / 1000 cents per million tokens). As of 2026-08-31
that rate — announced as introductory through 2026-08-31 — is now the standard
rate, confirmed by Anthropic 2026-08-10; the scheduled 2026-09-01 increase to
$3 / $15 will not occur. So the lapse is administrative (the frozen date
passed), not a price change.

## The fourteen manifests and their disposition as of 2026-08-31

| Manifest (`experiments/sandbox/`) | Window | Disposition — why it did not execute in-window |
|---|---|---|
| `hosting_liability_tariff_replication_plan_v1.json` | 2026-08-31 | Partial paid run only: run `32710531510`, 5/48 cells, then stopped (cell 6 failed). Remaining 43 cells not executed. Window **renewed** to 2027-08-31 by the companion note. |
| `economic_homeostasis_v2_replication_plan_v1.json` | 2026-08-31 | Frozen 48-cell V1-vs-V2 blocked replication. Retired by owner 2026-08-23 (`HOMEOSTASIS_V2_REPLICATION_RETIRED.md`) and closed 2026-08-31 as **superseded by the broader 128-condition two-axis sweep** (deliberate redundancy, not error). Never authorized; no cell executed; not renewed. Its dedicated closure artifact — authoritative for that design's closure, the permanently-void authorization phrase, and the preserved 28.9156c aborted-run cost — is `HOMEOSTASIS_V2_REPLICATION_NONEXECUTION_2026-08-31.md` (on the `agent/mailbox-init` records line). |
| `economic_homeostasis_v2_replication_prereg_v1.json` | 2026-08-31 | Preregistration for the closed 48-cell blocked replication above; see its dedicated closure record `HOMEOSTASIS_V2_REPLICATION_NONEXECUTION_2026-08-31.md`. |
| `economic_homeostasis_v2_prereg_v1.json` | 2026-08-31 | Frozen design / unpaid implementation. The three-arm diagnostic (run `32304273201`) completed but failed its advancement gate; that lineage was retired. No further paid run in-window. |
| `economic_homeostasis_active_plan_v1.json` | 2026-08-31 | V1 active matched experiment, executed historically (its authorization record is present; V1 final capital $442.50). No new paid run in-window. |
| `pilot_manifest_v1.json` | 2026-08-31 | Sonnet sandbox pilot v1, executed historically (seed 001; ~6.36c provider usage). Preserved partial transcript; not rerun. |
| `pilot_manifest_v2.json` | 2026-08-31 | Sonnet sandbox pilot v2, executed historically (one fresh seed after v1). Not rerun in-window. |
| `batch_manifest_v1.json` | 2026-08-31 | Sonnet chaotic sandbox batch (development) marker manifest; no paid run authorized against it in-window. |
| `batch_manifest_v2.json` | 2026-08-31 | Sandbox-development batch manifest; no paid run authorized in-window. |
| `batch_manifest_v3.json` | 2026-08-31 | Sandbox-development batch manifest (v3-family samples were collected historically); no paid run in-window. |
| `batch_manifest_v4.json` | 2026-08-31 | Sandbox-development batch manifest (adds one seed to the v3 family); no paid run in-window. |
| `longitudinal_manifest_v2.json` | 2026-08-31 | Matched longitudinal launch that "remains unpaid and disabled by default"; validated unpaid only, never paid-launched in-window. |
| `longitudinal_manifest_v3.json` | 2026-08-31 | Matched longitudinal v3 (durable-memory question); validated unpaid only, never paid-launched in-window. |
| `transfer_manifest_v1.json` | 2026-08-31 | Transfer test, explicitly gated ("do not run until longitudinal v2 completed"); validate-only, never paid-launched in-window. |

Per-manifest detail lives in each manifest's own launch / prereg / run record
(e.g. `PILOT_LAUNCH_V*.md`, `BATCH_LAUNCH_V*.md`, `LONGITUDINAL_LAUNCH_V*.md`,
`TRANSFER_LAUNCH_V1.md`, `HOMEOSTASIS_V2_REPLICATION_RETIRED.md`,
`HOSTING_LIABILITY_TARIFF_REPLICATION_RUN_32710531510_COST_NOTE.md`); this
record does not restate or re-adjudicate those histories, only preserves the
fact of the shared tariff-window lapse.

## Preservation and non-authority

- All fourteen manifests are preserved **byte-unchanged**; this is an
  append-only record, not an edit.
- The lapse authorizes nothing and reverses nothing. Any future paid run
  against any of these manifests still requires a fresh, explicit, byte-exact
  owner authorization for the specific merge and maximum spend, and a current
  tariff verification, per `AGENTS.md`.
- No secret value, provider call, or workflow dispatch is part of this record.
