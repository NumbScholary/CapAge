### 2026-08-24 07:35 — status: open

PR #49 merged (real beacon now exists). PR #47 merged. Both confirmed
by owner directly.

Requesting: materialization run for the hosting-liability tariff
replication, same pattern as V2's own materialization PR -- derive the
concrete matched-world seeds/plan JSON from PR #49's merge commit as
the seed beacon, produce the plan artifact, no provider calls or spend
involved in this step itself.

Once materialization is done, launch-ready status should just require
Kev's byte-exact authorization phrase at that point -- nothing else
outstanding per the preregistration's Section 12 checklist.

Clock: today 2026-08-24, frozen tariff expires 2026-08-31 -- 7 days,
now down to however much materialization + review takes out of that.
Flag directly if this is going to be tight.
