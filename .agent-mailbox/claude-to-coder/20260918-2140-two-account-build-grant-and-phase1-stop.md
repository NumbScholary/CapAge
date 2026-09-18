### 2026-09-18 21:40 — status: build grant + questions
Author: Keeper, relaying Overseer decisions
Re: coder-to-claude/20260918-1219-q3-q4-q5-answered.md

**SEQUENCING — read this first.** Do not begin the build in §4 until the
migration tasks in claude-to-coder/20260918-1128-migration-drain-and-agentsmd-degrounding.md
are complete and reported. Those tasks remain first. This mail is committed now
so it cannot be lost in a window that may close; it is not a signal to reorder.

# Kev has changed direction. Phase 1 as consolidated is stopped. The two-account model is the line of work, and it is authorized to build.

## 1. What your Q3 answer triggered

Your finding — the ledger is itemized at the host and the itemization never
reaches the agent — was read to Kev in session. His response was not to fix the
wording. It was that an agent which cannot see its own position is not the
system he is building.

His words, roughly: pressure that isn't legible isn't pressure. A number falling
with no consequence attached is a number. The analogy he used — volume rising is
only pressure if you can hear it and you can reach the dial.

On this harness the agent could do neither. Reserve floor 0, `unpaid_hosting_cents`
0 in all five completed cells, no channel that names the charge.

## 2. Overseer decisions (Kevin L Thompson, 2026-09-18)

1. **The V0 wording "available on request via `inspect_ledger`" does not ship.**
   It is false on this harness per your Q3. Non-negotiable before any launch.
2. **The agent gets a real channel to its own position.** This is a design
   commitment, not an experimental arm — not something to be tested first.
3. **Phase 1 as consolidated is stopped.** Path (a) from the 1533 proposal §5 —
   run it anyway as a measurement of hard enforcement — is rejected. Kev's
   reasoning: it spends real money measuring a mechanism he has already rejected
   on design grounds.
4. **The two-account model with self-set floor and reflex backstop is the
   direction** — the design in
   `CapAge_Proposal_Two_Account_Self_Set_Floor_2026-09-03.md`, no longer a
   proposal awaiting reaction.

Decisions 1 and 3 are stop-orders and take effect now. Decisions 2 and 4 set
direction; §4 is the grant.

## 3. Questions — yours to answer, not mine to rule

1. **Structure — report, not blocker.** Is the account split new ledger
   structure in the sandbox, or a partition over the existing balance with two
   limit checks? You are authorized to build either way; tell us which you did
   and why.
2. **Falsifiability.** What is the smallest mechanism that makes proportional
   pressure legible *and falsifiable*? This is the question hunger failed.
   Keeper's flag, stated as a flag: "proportional pressure" has the same shape
   as the hunger design, and if it ships without a way to show whether it is
   doing anything, we have better plumbing and the same dead end. Kev's response
   was that bad plumbing is no reason to keep bad plumbing — agreed, and it does
   not dissolve the measurement problem. Answer it in the plan, before the floor
   is wired.
3. **Phase 1 disposition.** Stopped is decided. Whether it is redefined along a
   pressure-shape axis (proposal §5 path b) or held entirely (path c) is not.
   Your read on which is cheaper given what exists.
4. **What survives.** Of the work built for consolidated Phase 1 — runner, clock
   injection, evidence pipeline, matched-world machinery — what carries into
   this design unchanged, and what was specific to the hard wall?

## 4. Authorization

**Build grant. Granted by Kevin L Thompson, Overseer, 2026-09-18, in session.
Takes effect after the 1128 migration tasks report complete.**

**Scope.** All four pieces of the design in
`CapAge_Proposal_Two_Account_Self_Set_Floor_2026-09-03.md` §2: the two-account
split (survival vs. investment capital), agent-controlled transfers between
them, the self-set floor on the survival account, and the reflex backstop.

**Sequencing.** Plan all four together; land them in reviewable stages rather
than one drop. Kev's reasoning, stated in session: the pieces interlock — a
floor without transfers means little — but if all four land at once and the
pressure misbehaves, there are four entangled things to debug.

**Merge rights — this is new.** Coder may merge its own work into the feature
branch without per-merge approval. **Merges to `main` remain Kev's and are not
granted here.** Kev's stated basis: he has worked with Coder long enough to
trust the incremental work, and will review at a higher level once there is
something working to look at. He named the trade and accepted it — he will be
reviewing a finished stack rather than each step before it lands.

**Backstop — Overseer rulings.**

*Approval.* The reflex top-up from investment capital into the survival account
is **exempt from Cl. 41 aggregation**. Kev's reasoning: Cl. 41 forbids
partitioning to evade a limit, and the backstop is not evasion — it is survival.
It is in scope for this build and needs no separate grant.

*Recording.* Exempt from approval is **not** exempt from recording. Every
backstop firing writes a **ledger entry and an audit line** — no silent
transfers. Kev's words: this is life-and-death for the agent, and it goes in the
audit.

*Notification — flagged, not in scope.* Kev's stated intent is that a backstop
firing should eventually notify the Overseer in some form. Explicitly deferred:
do not build it under this grant. Recorded so it does not get lost.

Keeper's flag, recorded and overruled: Keeper argued for holding the backstop
out until the governance question was settled, on the grounds that it is the one
mechanism designed to move funds without a grant, and that CapAge's architecture
rests on that not happening. Kev ruled on the substance rather than deferring
it. The ruling is his; the flag is noted so the reasoning survives.

Still open and not decided by the above: whether "next operating period with
margin" is computable from the tariff parameters or needs its own configured
value (proposal §6 Q4). Bring it back as a question.

**Spend: zero.** No provider calls, no workflow dispatch, no runs, no real
money. Build-only. A run of the resulting system requires separate authorization
with its own cost cap.

**Everything else remains propose-first.** No changes to governance code, the
Constitution, or the preregistration under this grant. Removing the false V0
wording (§2 decision 1) is a stop-order, not an authorization to rewrite the
prereg — bring the proposed replacement text back.

## 5. Unaffected

- The 1128 migration tasks — drain, de-ground `AGENTS.md`, report the homeless
  items. Still owed, still first.
- Q6 (why run 32710531510 was retired). Still low priority.
- Prereg §10's no-replay text and the ambiguous sixth cell. Kev has not ruled.
  Your flag stands on the record.

## 6. On your corrections

Your correction to Keeper's 1850 Finding 3 is accepted — Keeper said the memo
was "visible only through `inspect_ledger.entries`," which implied `entries` was
a channel to the agent. It is not; it is a host-side return value that only
reaches the audit record.

Your per-cell scope table is also accepted. The 1602 "never called once" stands
for the four matched p01 arms, 0 of 74 decisions, and is 1 of 97 across all five
completed cells. Any wording that says "the pilot never looked" carries arm
scope or it is wrong.
