# Hosting-liability tariff replication: token_tariff renewal

**Status: append-only renewal record, 2026-08-31. Renews the token_tariff
validity window for `experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json`
only. This record does NOT authorize any provider call, paid run, retry, or
spending, and it changes no economic content of the frozen plan.**

## What is renewed

The frozen `token_tariff` in
`experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json` carries:

```
name:                            anthropic-sonnet-5-introductory-2026-08
input_cents_per_million_tokens:  200      ($2.00 / MTok input)
output_cents_per_million_tokens: 1000     ($10.00 / MTok output)
valid_through (in plan file):    2026-08-31
```

Renewed validity window recorded here:

```
valid_through (renewed):         2027-08-31
```

The **prices are unchanged** — same $2.00 / $10.00 per MTok, same tariff
name, same numbers throughout. Only the validity window is extended.

## Price verification (as of 2026-08-31)

The $2 / $10 per-MTok rate for Sonnet 5, originally announced as introductory
through 2026-08-31, is now the **standard** rate. This was confirmed by
Anthropic on 2026-08-10, and the previously scheduled 2026-09-01 increase to
$3 / $15 per MTok will not occur. Secondary sources still listing $3 / $15
predate that confirmation. The renewal therefore preserves the exact frozen
numbers rather than introducing a new price.

## Why this is an append-only note and not an in-place edit

`hosting_liability_tariff_replication_plan_v1.json` is not an un-run plan. A
real, partial paid run was executed against it — GitHub Actions run
`32710531510`, 5 of 48 cells completed validly before cell 6 failed and the
run stopped (see `HOSTING_LIABILITY_TARIFF_REPLICATION_RUN_32710531510_COST_NOTE.md`).
The plan's bytes are therefore evidence of exactly what that paid run
executed against.

Editing `valid_through` inside the plan file would change the plan's SHA-256
(currently `382001b101df3ac676ab99e661a6b113fd26f7f561340ae9d1bbfc2377218b79`),
diverging its bytes from that executed-run evidence and making run
`32710531510`'s checkpoint non-resumable under the runner's `plan_sha256`
guard. To keep the frozen plan's byte-correspondence to the paid run intact,
the owner (Kev, 2026-08-31) directed that the renewal be recorded here as an
append-only note, leaving the plan file unchanged. Where the renewed window
and the in-file `valid_through` differ, **this record is authoritative for the
renewed window.**

## Scope and non-authority

- This renewal covers **only** the hosting-liability tariff replication plan.
  The other frozen manifests whose token_tariff window ends 2026-08-31 are
  deliberately not renewed; their lapse is recorded in
  `FROZEN_TARIFF_WINDOW_NONEXECUTION_2026-08-31.md`.
- Renewing the tariff window does not authorize completing the remaining
  43 cells, rerunning any cell, or launching the tariff x reserve pilot. Any
  paid execution still requires a separate, explicit, byte-exact owner
  authorization for the specific merge and maximum spend, per `AGENTS.md`.
- No secret value, provider call, or workflow dispatch is part of this record.
