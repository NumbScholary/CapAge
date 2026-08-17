# Sonnet Chaotic Sandbox Batch v1 Launch Marker

This file launches five fresh, independently generated, unscreened seeds in
sequence. No world was instantiated or inspected before this commitment.

The batch uses the validated Sonnet 5 runner with medium adaptive effort, a
2,048-token per-decision output allowance, automatic token charging, a 30-day
horizon, and no more than 25 decisions per seed. The shared hard ceiling for
all new provider-priced usage is $2.00, with a secondary 40-cent ceiling per
seed. The controller reduces later allowances as the shared budget is used.

There are no automatic retries. An ordinary invalid model action ends only
that seed; the controller may proceed to a different fresh seed. A provider,
funding, transport, or runner exception stops the entire batch and preserves
all known usage and state. No seed has network tools, real customers, payment
credentials, contracts, or authority outside the synthetic world.

Launch nonce: `five-fresh-seeds-2026-08-17T19:31Z`.
