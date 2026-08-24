### 2026-08-24 06:45 — status: open

Owner (Kev) has approved the preregistration for the hosting-liability
tariff dose-response replication (PR #47). Document is committed:
experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md
on agent/mailbox-init.

Requesting: build the launch/authorization script for this experiment,
mirroring homeostasis_v2_replication_launch.py's pattern -- exact-byte
confirmation phrase required before any provider call, per-cell and
aggregate spend caps enforced pre-call, fails closed on ambiguous
attempts or provider errors, --validate-only path that never touches
a provider or spends anything.

Two things to confirm/flag back before or during the build, not to
decide unilaterally:

1. Spend caps -- the preregistration document (Section 6) leaves the
   per-cell and aggregate caps as "to be confirmed against the tariff
   actually in effect at launch time," since the previously frozen
   model tariff ($2/M input, $10/M output) is only valid through
   2026-08-31. Please confirm which tariff this launch script should
   assume, and flag directly if the 08-31 expiry is close enough to
   matter for when this actually gets used.
2. Nothing here authorizes a paid run. Building and validating the
   launch script does not itself authorize spending -- that still
   requires Kev's separate, explicit, byte-exact confirmation phrase
   at actual launch time, standard protocol, unchanged.

No code beyond the launch script itself should be touched -- PR #47's
existing scope (token attribution, config passthrough, dedicated
runner, ordering scheme) is done and merged-ready as-is.
