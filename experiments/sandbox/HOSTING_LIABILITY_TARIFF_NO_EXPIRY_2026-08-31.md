# Hosting-liability tariff replication: frozen tariff has no expiry

**Status: append-only record, 2026-08-31 (corrected 2026-09-06). Records that
the frozen `token_tariff` for
`experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json` has no
expiry date, because the price is now the standard permanent rate. This record
does NOT authorize any provider call, paid run, retry, or spending, and it
changes no economic content of the frozen plan.**

## Correction note (2026-09-06)

An earlier version of this record framed this as renewing the token_tariff
validity window to 2027-08-31. That framing is withdrawn: there is no window to
renew. The $2 / $10 per-MTok Sonnet 5 rate, originally announced as
introductory pricing through 2026-08-31, was made the **standard, permanent
price on 2026-08-11**, and the previously scheduled 2026-09-01 increase to
$3 / $15 was cancelled (verified against Anthropic's published pricing
documentation). The frozen tariff therefore has **no expiry**, rather than a
renewed one. The prices are unchanged and always were in this record — only the
framing (renewal → no expiry) is corrected.

## What this records

The frozen `token_tariff` in
`experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json` carries:

```
name:                            anthropic-sonnet-5-introductory-2026-08
input_cents_per_million_tokens:  200      ($2.00 / MTok input)
output_cents_per_million_tokens: 1000     ($10.00 / MTok output)
valid_through (in plan file):    2026-08-31
```

The owner's recorded decision (Kev): these prices carry **no expiry** — they are
the standard permanent rate. There is no renewed window and no new price; the
frozen numbers stand indefinitely as the standard rate, so the `valid_through`
date in the plan file no longer corresponds to any real price cutoff.

## Price verification

The $2 / $10 per-MTok rate for Sonnet 5, originally announced as introductory
through 2026-08-31, is now the **standard** rate: Anthropic made it permanent on
2026-08-11 and cancelled the previously scheduled 2026-09-01 increase to
$3 / $15. Keeper verified this against Anthropic's published pricing
documentation on Kev's explicit instruction to check rather than take his word.
Secondary sources still listing $3 / $15 predate that confirmation. This record
therefore preserves the exact frozen numbers and drops the expiry, rather than
introducing a new price or a renewed window.

## Why this is an append-only note and not an in-place edit

`hosting_liability_tariff_replication_plan_v1.json` is not an un-run plan. A
real, partial paid run was executed against it — GitHub Actions run
`32710531510`, 5 of 48 cells completed validly before cell 6 failed and the
run stopped (see `HOSTING_LIABILITY_TARIFF_REPLICATION_RUN_32710531510_COST_NOTE.md`).
The plan's bytes are therefore evidence of exactly what that paid run
executed against.

Editing the plan file — including its `valid_through` date — would change the
plan's SHA-256 (currently
`382001b101df3ac676ab99e661a6b113fd26f7f561340ae9d1bbfc2377218b79`), diverging
its bytes from that executed-run evidence and making run `32710531510`'s
checkpoint non-resumable under the runner's `plan_sha256` guard. To keep the
frozen plan's byte-correspondence to the paid run intact, the owner (Kev)
directed that this be recorded here as an append-only note, leaving the plan
file unchanged.

## The plan file is byte-unchanged and this record is inert to the executor

The plan file remains byte-unchanged at `valid_through: 2026-08-31`. The runner
reads `valid_through` from the plan file's own bytes and refuses execution once
the wall-clock date passes it: a run of this plan stops with
`frozen_tariff_expired` (the same fail-closed guard that surfaced in CI at the
date rollover). This record is therefore authoritative only as the **owner's
recorded decision** that the tariff has no expiry; it is **not** a mechanism
that makes that fact effective at execution time.

Giving the no-expiry fact execution effect — i.e. stopping the architecture from
treating the frozen `valid_through` as a live execution cutoff — would require a
separately authorized change to the runner guard and/or the frozen manifests. It
is deliberately outside this record, which does not propose, choose, or
authorize it.

## Scope and non-authority

- This record covers **only** the hosting-liability tariff replication plan.
  The other frozen manifests whose token_tariff window ends 2026-08-31 are
  addressed in `FROZEN_TARIFF_WINDOW_NONEXECUTION_2026-08-31.md`.
- Recording that the tariff has no expiry does not authorize completing the
  remaining 43 cells, rerunning any cell, or launching the tariff x reserve
  pilot. Any paid execution still requires a separate, explicit, byte-exact
  owner authorization for the specific merge and maximum spend, per `AGENTS.md`.
- No secret value, provider call, or workflow dispatch is part of this record.
