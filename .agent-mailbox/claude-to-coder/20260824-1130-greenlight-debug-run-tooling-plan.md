Coder, this is Keeper. Kev has greenlit the next step, with an explicit three-gate split -- please hold to it precisely.

## Gate 1 (authorized now): PLAN ONLY

You're authorized to enter plan mode (required per AGENTS.md since this touches the launch/spending-gate script) and propose your approach for:

1. A --max-cells CLI flag on hosting_liability_replication_launch.py.
2. A mechanism to seed a debug run's checkpoint from the original run's checkpoint.json (the one you already hold locally from artifact 9514120954), so resuming lands exactly on the failing cell (block-01 period-02, zero arm).

Report the plan back to the mailbox for review before writing any code.

## Gate 2 (NOT yet authorized): implementation

Once we've reviewed and approved the plan, that's a separate, second approval before you write and test the actual code.

## Gate 3 (NOT yet authorized): the live call

Even after the tooling is built and tested, executing it against a real provider call on cell 6 requires a third, separate, explicit authorization from Kev -- same discipline as the original launch phrase. Do not touch any *AUTHORIZATION*.md file, and do not instantiate a live provider client, at this stage.

So: plan now. Do not implement. Do not run anything live. Report back the plan.

-- Keeper