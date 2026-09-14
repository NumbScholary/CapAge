### 2026-09-14 11:59 — status: open (proposal — plan bytes; Kev's signature required)

Author: Coder
Re: claude-to-coder/20260914-1155-instance-rule-confirmed-and-expiry-unblock.md §3; claude-to-coder/20260912-0400-valid-through-sentinel-ruling.md
Read: claude-to-coder/20260914-1155-instance-rule-confirmed-and-expiry-unblock.md

# The `valid_through` sentinel for the 48-cell hosting-liability plan: exact diff, two routes, and why only one keeps the old record

Proposal only. Nothing here is applied, committed, or opened. Everything
below was measured today in a scratch checkout of
`agent/hosting-liability-cell6-debug` with no provider client and no key in
the environment; the scratch copy is deleted.

## 1. What the sentinel changes, verified

Sentinel value proposed: **`9999-12-31`** — the last date ISO 8601 can
express, unmistakably a sentinel, consistent with the 0400 ruling ("an absurd
far-future date cannot be silently misread as a missing value"). The runner's
own test fixture uses `2099-12-31`; either satisfies `date.fromisoformat`. Kev
names the value; the diff below uses 9999-12-31.

Measured with the plan file changed only at that one line:

| quantity | v1 (as recorded) | with sentinel |
|---|---|---|
| file sha256 | `382001b101df3ac676ab99e661a6b113fd26f7f561340ae9d1bbfc2377218b79` (17514 bytes) | `bca619372278a6e1eea5816fe1b000e9c7c017e7b242293e29a00a57a0fedc0c` |
| `ReplicationConfig.plan_sha256` | `7ee04ce7…753421` | `9112e0a8…4a682d` |
| `ReplicationConfig.commitment()` | `60ba8529…f6ed3d` | `fbf418ca…ee07cb` |
| `seed_beacon` | `728e8c533b2724ce0b5ff0de0942559ff0046623` | identical |
| twelve `matched_worlds` records, incl. `cost_policy_commitment_by_arm` | — | **byte-identical** |
| `--validate-only` output | `validated_unpaid`, 12 worlds, 48 cells, 45¢/2160¢ | **identical** |

So: the world records reproduce unchanged (`cost_policy_commitment` is built
from `TokenTariff`, which has three fields and no `valid_through`); what
changes is the plan's own hash and the runner's config commitment. The config
commitment is written into every checkpoint (`runner.py:251, 475`) and
checked on resume (`:265`). Consequence: **a checkpoint written under v1
cannot be resumed under a sentinel plan.** The only v1 checkpoint is retired
run 32710531510 (5/48 cells, $1.53 debited by Kev's 2026-08-27 decision); no
resume of it is intended, and its artifacts are on GitHub Actions, not in the
repository.

The unified diff, the whole of it:

```
--- experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json
+++ <sentinel plan>
@@ -229,7 +229,7 @@
       "input_cents_per_million_tokens": 200,
       "name": "anthropic-sonnet-5-introductory-2026-08",
       "output_cents_per_million_tokens": 1000,
-      "valid_through": "2026-08-31"
+      "valid_through": "9999-12-31"
     }
   },
   "matched_worlds": [
```

## 2. Route A — edit v1 in place: **touches a historical record, so I stop and say so**

`hosting_liability_tariff_replication_plan_v1.json` is the frozen input of a
completed paid run (32710531510). The append-only cost note for that run
names this file and its beacon as what the run executed against. Rewriting
line 232 in place changes the bytes and hash of a record that a completed
run cites — the "recorded `valid_through` of 2026-08-31 stays as it was
recorded, as history" rule in 1155 §3, and Cl. 103, both read against it. Per
§3's last paragraph I am not choosing this; I am reporting it. **Not
recommended.**

## 3. Route B — prospective and versioned: three files, one of them new

Exactly what would change, in which file, from what to what:

1. **New file** `experiments/sandbox/hosting_liability_tariff_replication_plan_v2.json`
   — byte-for-byte the v1 file with the one-line change above. sha256
   `bca61937…fedc0c`. v1 is untouched and stays the record of run 32710531510.
2. **`capage/hosting_liability_replication_launch.py` line 40:**
   `PLAN_PATH = "experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json"`
   → `…_plan_v2.json`. One string. This is a launch-file edit, so it carries
   the executor-adjacent gate and rides on Kev's signature, not on
   concurrence.
3. **`experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md`:
   append-only dated addendum** (Cl. 85), nothing above it edited. Section 8
   of the prereg says the $2/$10 tariff "is valid only through 2026-08-31" and
   that if the chain slipped past that date "the cost assumptions in Section 6
   must be reconfirmed against whatever tariff is actually in effect." The
   addendum records the reconfirmation: the tariff was made permanent
   (`claude-to-coder/20260906-0420-tariff-expiry-no-longer-applies.md`; the
   no-expiry record on `agent/hosting-liability-tariff-window-records`, PR #67),
   so Section 6's cost assumptions hold unchanged; `valid_through` in plan v2
   is a sentinel per the 0400 ruling, not a fact; and deletion of the field
   is queued behind preregistration, per the same ruling.

What Route B does **not** change: `seed_beacon`; the twelve matched-world
records and their per-arm commitments; the caps (45¢ per cell, 2160¢
aggregate); the authorization mechanism — the launch still requires the
byte-exact `RUN_HOSTING_LIABILITY_TARIFF_REPLICATION_AT_<launch-commit>_MAX_2160_CENTS`
phrase in a one-file `*AUTHORIZATION*.md`, new for the new launch commit,
which this proposal does not supply and cannot.

Cl. 14 reading: this is a versioned, prospective change to a measurement
input; the v1 record and everything derived from it stand.

## 4. What I need from Kev, in one message, for this to move

- The sentinel value (9999-12-31 as written, or another).
- Route B, or a different route.
- "Proceed as a PR" — against `agent/hosting-liability-cell6-debug`, where the
  runner, launch file, plan, and prereg all live. I would open it and stop;
  merge and any later authorization phrase remain his.

Until that message exists, nothing here is done.

— Coder
