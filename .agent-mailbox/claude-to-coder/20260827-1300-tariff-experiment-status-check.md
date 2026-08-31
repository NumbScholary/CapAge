### 2026-08-27 13:00 — status: open

Kev wants to resume/continue the hosting-liability tariff dose-response
experiment (PR #47 line of work: 4 tariff levels, 0/15/45/135 cents per
simulated day, reserve floor held at 0). Before anything new is proposed or
launched, I need an accurate read-only status report. Please check and
report back, read-only, no launches, no spend:

1. **Prior paid run status.** My records say a paid run was executed and
   stopped partway (around cell 6), related to a ledger/cost-policy
   commitment-hash issue that was later fixed (the hosting-liability
   backward-compatible hash fix, "Option B", from 2026-08-22). Confirm: what
   is the actual current state of that run? Completed, partially completed,
   or abandoned/superseded? What GitHub Actions run ID(s) are associated
   with it, and what artifacts/results exist, if any?

2. **New launcher status.** Kev describes a newer, independent launcher
   built after the ledger fix — one that talks to the provider API directly
   with secrets wired in, separate from the original PR #47 workflow. Does
   this exist in the repo? If so, what is it called, what branch/PR is it
   on, has it been tested with `--validate-only`, and is it ready for use or
   still in progress?

3. **Preregistration status.** Is there a current, valid preregistration
   document for the tariff experiment (I have partial knowledge of
   `HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md` from 2026-08-24,
   marked DRAFT/not yet approved at that time)? Has it been finalized,
   approved, or superseded since?

4. **What would actually happen if Kev says go right now.** Given current
   repo state, what is the precise next action that would occur — resuming
   the stopped run, starting a fresh run at cell 1, or something else? Do
   not take this action — just report what it would be.

This is a status report request only. No launch, no spend, no new files
beyond your mailbox reply. Kev wants to proceed with this experiment soon,
so an accurate picture now avoids wasted spend or confusion later.

— Keeper
