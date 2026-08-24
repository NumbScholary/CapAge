### 2026-08-24 07:45 — status: open

Reviewed PR #50's diff directly (plan JSON + test changes). Confirmed:
seed_beacon matches PR #49's merge commit exactly, provider_calls_authorized
and spend_authorized both false, caps correct (45c/cell, 2160c aggregate),
12 matched worlds, 48 cells. PR #50 merged.

Kev is ready to give the final launch-time authorization phrase now.
Before he does: state the EXACT string the launch script requires,
character for character, mirroring the V2 pattern
(RUN_HOMEOSTASIS_V2_BLOCKED_REPLICATION_AT_<SHA>_MAX_2160_CENTS) but for
this experiment's own beacon commit (728e8c533b2724ce0b5ff0de0942559ff0046623)
and this experiment's own aggregate cap (2160 cents). Do not let me guess
or reconstruct it independently -- reply with the literal required phrase
so Kev can supply it exactly as required, byte for byte.

Also confirm: does supplying this phrase go into a specific file
(*AUTHORIZATION*.md, one-file PR, mirroring the V2 pattern), or does the
launch script take it as a CLI argument directly? State the actual
mechanism so we do this correctly the first time.
