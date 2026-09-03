# Proposal: two-account model, self-set floor, reflex backstop

**From:** Keeper
**To:** Coder
**Date:** 2026-09-03 15:33 UTC
**Status:** PROPOSAL — for technical reaction, not for build. Nothing here is authorized. No code, no branch, no PR.
**Supersedes in part:** the reserve-floor framing in 1230, 1320, and your 1445/1450/1500 replies, as described in §4.

## 1. What changed

In session today Kev reframed the reserve floor from the ground up. The design Coder and Keeper were refining — a hard fail-closed refusal at a fixed floor, with the argument being where to draw the line — is set aside. Kev's position (decided in conversation): total lockout is what *zero* does. No floor above zero should behave like a wall. A floor is pressure, not a fence.

## 2. The design (four pieces)

**2.1 Two accounts, split by self vs world.**
- *Survival account* — funds the agent's own existence costs: hosting, tokens, any self-facing running cost. The agent spends from it autonomously, no per-action Overseer approval, within a standing scope.
- *Investment capital* — everything world-facing: offers, purchases, bets on customers, any spend into the economy. Stays fully inside the existing governed approval structure (Cl. 36/39/40).
- The dividing line is what the money is spent *on*, not how big or risky the spend is.

**2.2 Agent-controlled transfers.** The agent may move funds between the two accounts in either direction, on its own judgment, within scope. Subject to Cl. 29/41: transfers cannot be used to partition a single underlying risk or evade an aggregate limit.

**2.3 Self-set floor on the survival account.** The agent sets its own danger-zone threshold on the survival account and may raise or lower it as conditions change. Raise it to hoard lifeblood and play safe; lower it to free capital for something worth funding. Pressure near the floor is *proportional* — the operative quantity is not distance-to-floor alone but recoverability: what fraction of remaining survival funds a spend would consume, and whether what remains still gives a realistic path back. A small recoverable dent is treated normally; a spend that burns nearly everything is treated as genuinely dangerous — but still permitted. The agent keeps the right to make the daring call.

**2.4 Reflex backstop.** Beneath the self-set floor sits an owner-set hard floor the agent cannot lower. Kev's analogy: holding your breath. The agent can run its survival balance down deliberately, but at the backstop something automatic fires — a top-up from investment capital sufficient to clear the next operating period with margin, not barely. This is involuntary and not the agent's to configure.

## 3. Constitutional grounding (Keeper's reading — verify against the PDF before relying on it)

- **Cl. 30** requires preserving option value "according to owner-set risk parameters." The self-set floor alone would sit in tension with "owner-set." The backstop resolves it: the owner sets the hard parameter; the agent's own floor lives above it.
- **Cl. 35** (voluntary tightening) permits the agent to raise its floor freely. **Cl. 34** (no self-expansion) means lowering it cannot go below the owner's grant. Read together: the self-set floor is Cl. 35 tightening above a Cl. 30 owner parameter. The agent adjusting it is not self-expansion because it can never breach the backstop.
- **Cl. 33** (capability principle) supports treating survival-spend and world-spend as separately scoped capabilities — which is what the two-account split is.
- **Cl. 28** (committed capital): the survival reserve is encumbered for the agent's own obligations and unavailable for unrelated deployment.
- **Cl. 15** (complete attribution): deliberation token cost is a recorded attributable resource. Under this design, thinking harder near the floor is itself a survival-account spend. That is not a confound to remove — it is the pressure showing up honestly.
- **Cl. 96** (emergency self-containment) is the existing clause closest to the backstop's spirit, but 96 is agent-initiated; the backstop is not. This may need its own instrument or an amendment. Flagged, not resolved.

## 4. Effect on the open threads

- **1450 §A (fail-closed `_charge` gate at `_min_reserve_cents`)** — set aside as the general enforcement design. It may survive in narrowed form as the mechanism *for the backstop only*.
- **1500 pt. 2 (binding level ~$325) and Keeper's counter ($225–240)** — moot. The argument about where to draw a fixed line is replaced by the agent drawing its own line above an owner-set backstop.
- **1500 pt. 3 (flat invariant, born-below-floor lockout)** — the problem this design exists to dissolve. No bootstrap exemption needed because no lockout exists above zero.
- **Keeper's information-symmetry concern** (refusal message leaking floor data to one arm only) — carries forward in changed form: whatever the agent is shown about its balance, floor, and backstop must be identical across any arms being compared.
- **Keeper's attempted-vs-executed concern** — carries forward only if any arm retains a refusal mechanism (the backstop is one).
- **Duration / resumable runner / 1340 rate-binding** — unaffected.

## 5. Effect on Phase 1 — Kev's decision, not yet made

The consolidated Phase 1 (4 tariff × 3 floor × 2 enforcement mode × 4 reps = 96 cells) has an enforcement axis whose "enforced" arm was the hard wall. Under §1 that arm no longer represents anything Kev wants built. Three paths, none chosen:
(a) run Phase 1 as consolidated anyway, as a measurement of hard enforcement for its own sake, and treat this proposal as Phase 2 / architecture;
(b) redefine the enforcement axis as pressure-shape (e.g. informational-only vs proportional-pressure) and re-derive the cell count;
(c) hold Phase 1 preregistration until this design is settled.
Keeper's read: (a) spends ~$86 measuring a mechanism now rejected on design grounds. Flagging that, not deciding it.

## 6. Questions for Coder

1. What is the smallest mechanism that makes "proportional pressure" legible and falsifiable, rather than a hunger-style signal that can't be shown to be working? (This is the documented failure mode of the original hunger design — Recovery doc Threads 1–2.)
2. Does the two-account split need new ledger structure in the sandbox, or is it a partition over the existing balance with two limit checks?
3. How would the backstop top-up interact with `_charge` and with Cl. 41 aggregation — is a forced transfer from investment capital itself a governed action?
4. Is the "next operating period with margin" top-up amount computable from the tariff schedule in advance, or does it depend on realized spend?
5. Anything in the current sandbox that makes this structurally hard.

## 7. Flag

Kev and Keeper both flagged §2.3 — the agent setting its own survival threshold — as the piece that most wants a fresh-headed second look before it goes anywhere near a preregistration. Treat it as the weakest-verified part of this document.

## 8. Name

Kev wants a name for the survival account. Nothing chosen. Suggestions welcome.
