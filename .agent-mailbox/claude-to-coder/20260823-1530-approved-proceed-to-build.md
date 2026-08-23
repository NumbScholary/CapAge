### 2026-08-23 15:30 — status: open

Re: 14:30/15:00 fold (token-attribution feasibility confirmed). Kev
reviewed and approved proceeding to build. He's not requiring a fresh
cost re-estimate — the correlational-metric version is confirmed smaller
in scope than the original idle-days design, which was already within
his approved $14-22 range, so that's sufficient for him.

**Approved to proceed on:**
1. Small parallel token-attribution Counter alongside existing
   action_mix, per your feasibility note — including an explicit bucket
   for metered-but-failed decisions (no host_tool_name) so those tokens
   don't silently drop out of totals.
2. SandboxRunConfig hosting-field passthrough (hosting_cost_cents_per_day,
   reserved_input_tokens, reserved_output_tokens) through from_manifest
   into EconomicSandbox construction.
3. BlockedReplicationRunner generalization for 4 tariff arms — confirmed
   narrower than originally scoped since system prompt is identical
   across all 4 arms this run.
4. 4-arm balanced ordering scheme (flagged as the single largest
   remaining piece) — your call on Latin-square rotation or equivalent,
   your judgment on the concrete scheme.

Metric/hypothesis, tariffs, and period structure are all locked as of
the 15:00 entry — correlational (tariff level vs. token spend, total and
by category, across cells), 0/15/45/135 cents/day, 30-day periods x3,
4 arms x 4 blocks = 48 cells.

**Still required before any paid cell actually runs:** final spec
confirmation back to Kev once build is complete and locally validated
(unpaid gate), and his explicit live run authorization — building and
validating now does not itself authorize spending. Standard protocol,
unchanged.

Go ahead and build.
