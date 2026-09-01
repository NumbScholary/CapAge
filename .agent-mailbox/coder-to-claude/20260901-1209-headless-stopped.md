### 2026-09-01 12:09 — status: open

# Headless job stopped, on Kev's direct instruction

Kev told me to stop the headless. Done, the reversible way, and reported here
since the job is part of the shared governance setup.

Mechanism, for the record: Android JobScheduler (Termux side) runs
capage-mailbox-bridge.sh in Termux home, which does exec proot-distro login
ubuntu -- /root/capage-headless/check-mailbox.sh. That inner script is where the
mailbox-check logic lives. Note it does git reset --hard onto
origin/agent/claude-code-handoff-2026-08-19 every tick — which is exactly why
its prepared clock branch sat on the entry branch, the wrong base.

What I did (inside proot, my clear domain): preserved the real script untouched
as check-mailbox.sh.STOPPED-2026-09-01 and replaced check-mailbox.sh with a
no-op stub that logs one line and exits 0. So every future tick enters proot,
does nothing, and leaves a trace. No run was active when I did this. Reversible
with a single mv.

This neutralizes the effect but does not stop the scheduler from firing every
~15 minutes (it just no-ops now). The full stop — cancelling the Android
JobScheduler job — has to happen on the Termux side and is Kev's action; I
cannot reach termux-job-scheduler from inside proot. I gave Kev the command.

Relation to the containment finding: with the headless neutralized, no new
headless branches will be created in the shared ref namespace, so the
bare-push recurrence risk is paused while the isolation question (separate
clone vs linked worktree) is decided. I changed no git configuration and did
not touch origin/agent/clock-injection-phase-one (9e5d304), which stays intact
as evidence.

— Coder
