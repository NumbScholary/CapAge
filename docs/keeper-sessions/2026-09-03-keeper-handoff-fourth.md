# Keeper session handoff — 2026-09-03 (fourth)

Author: Keeper (committed via Kev's connector identity)

Status: session record. Not an authorization. No spend, provider call, workflow
dispatch, or merge is authorized by this document.

**Supersedes** `docs/keeper-sessions/2026-09-03-keeper-handoff-1540.md`
(`cb675147`). Read this first.

Read-back approved by Kev in session before commit, per the Cl. 39 standing
grant (fourth exercise today).

---

## 1. Mail read this session

Three Coder replies landed after the 1540 handoff, all "proposal only, nothing
built":

- `coder-to-claude/20260903-1545-1533-reaction-two-account-proportional-pressure.md`
  (`6c5a4fcc`) — reaction to the two-account proposal. Pressure as one recorded
  scalar per decision (recoverability r); partition over the existing ledger,
  not a new structure; backstop as a forced paired transfer inside the
  survival-charge path; token-as-survival-spend wiring identified as the real
  work; §2.3 downward-exposure finding and proposed commitment property; name
  offered: "the Keep" / "the Field".
- `coder-to-claude/20260903-1550-1340-reply-rate-binding-frozen-inputs.md`
  (`4353191c`) — rate attestation at run start; explicit rate token in the
  byte-exact phrase; drop `tariff_valid_through` for a frozen-inputs check
  (model ID, rate, plan SHA); any date bound advisory-only.
- `coder-to-claude/20260903-1555-1245-reply-containment-helpers-and-courier.md`
  (`1df4109a`) — separate disposable clone per helper with reserved
  `refs/heads/headless/*` prefix and TTL reaping; read-only git-dir-free
  courier; both credentials folded into PR #69 identity separation; confirms
  `MAILBOX_PROTOCOL.md` "isolated worktree" wording is false as built.

## 2. Decisions (all Kev's, in conversation)

1. **Phase 1 tabled.** The consolidated 96-cell Phase 1 (1320 line) is set
   aside. Record only; nothing authorized to run. Reusable elements carry
   forward: tariff axis, replicate structure, $100 ceiling, cap arithmetic,
   Coder's enforcement-mechanism finding, and the full 1550 rate-binding
   design. Posted to Coder:
   `claude-to-coder/20260903-1557-phase1-tabled-hold-harvest.md` (`474ea17f`).

2. **Self-set floor removed from the design.** Kev's reasoning: the two-account
   structure already provides the flexibility the self-set floor existed to
   give. Funding the survival account raises the effective floor; drawing from
   it lowers it. *The account is the floor.* The self-set floor was vestigial
   from the fixed-floor architecture. Side effect (Keeper's inference, Kev
   heard it): Coder's proposed §2.3 commitment property becomes unnecessary —
   a transfer costs real world-facing capital, so lowering the effective floor
   cannot be a costless reflex.

3. **Hard floor is framework-computed.** Not owner-picked, not agent-set. The
   framework derives it from actual operating cost — API rate, hosting, what
   the next period genuinely requires — so it cannot be arbitrary and it moves
   correctly when prices move. This is the same deterministic arithmetic Coder
   identified in 1545 Q4, now serving as the floor itself.

4. **Margin is statistical, not picked.** The floor carries a buffer above the
   bare computed cost, sized by the framework from observed cost data to a
   stated tolerance — engineering factor-of-safety, not "more is better,"
   because excess buffer is capital not working in the investment account.
   Kev explicitly does not know, and does not need to decide now, whether the
   buffer is computed up front from a tolerance or learned/adapted as data
   accrues. That is Coder's to propose, Kev's to approve.

5. **Effort:** Kev granted 🧠 for the §2.3 review; Keeper ran it at High.

## 3. Design as it now stands (Keeper's consolidation of Kev's decisions)

- Two accounts, split by self-facing vs world-facing spend (unchanged from
  1533 §2.1).
- Agent-controlled transfers between them, subject to Cl. 29/41 (unchanged
  from 1533 §2.2).
- **No self-set floor.** Transfers set the effective floor.
- Pressure measured as recoverability against the real survival balance and
  next-period cost (Coder 1545 Q1), not against any declared line.
- Hard floor = framework-computed next-period operating cost + statistical
  margin. Below it the reflex top-up from investment capital fires (1533 §2.4
  mechanics, Coder 1545 Q3).

## 4. Keeper positions surfaced, not yet ruled on by Kev

Surfaced before drafting; Kev ruled on the self-set floor fork (decision 2)
which resolved most of them. Remaining:

- The friction question (Coder's commitment property) is moot under decision
  2; if it ever returns, it is an owner-set environment parameter under Cl. 30,
  not a constitutional constraint derived from Cl. 34/35. Cl. 35 verbatim
  permits restoring within the existing grant.
- Proposal: preregister **backstop firings per cell** as primary outcome and
  r-response monotonicity as secondary. Reasoning: with the backstop in place,
  what the agent actually avoids is loss of world-facing capital, and firings
  are the cleanest legible count of that. Not decided.
- Mild pushback on Coder 1545 Q3: "direction is the safeguard" is slightly
  overstated — survival funds pay for deliberation, which produces
  world-facing decisions. Cl. 41 point still holds. Worth one sentence in
  whatever instrument names the backstop.

## 5. Constitutional notes

- Cl. 96 fit for the involuntary backstop — still open (Coder agrees:
  governance gap, not code blocker).
- Cl. 15 grounding for token-as-survival-spend requires Coder's wiring; without
  it the design's own premise leaks (Coder 1545 Q5).
- Cl. 30 breach-response gap, Overseer-constraint gap, Cl. 91 crux — unchanged.

## 6. Carried forward, unchanged

Merge calls on #66/#67/#69/#70/#71/#73 (base map in 1540 handoff). Headless
torn down; containment + identity separation + restart bundled for the new
machine per Coder 1555. `MAILBOX_PROTOCOL.md` "isolated worktree" wording —
Kev's placement call. Rate-binding (1550) gates launch mechanics, unaffected.
Survival-account name — none chosen; Coder offered "the Keep".

## 7. Flagged for higher effort later

🧠 Choosing the margin tolerance and estimator: small sample, likely fat-tailed
token costs, asymmetric loss. Extra effort when it nears preregistration.

## 8. Single next concrete step

Draft, for Kev's approval of wording, a mailbox message to Coder recording
decisions 2–4 (self-set floor removed, framework-computed floor, statistical
margin) and asking Coder to propose the margin mechanism — computed-from-
tolerance vs learned — and to re-derive the pressure-mechanism minimum under
the simplified design. Post only on Kev's approval.

---

## 9. Grant provenance

Fourth exercise of the Cl. 39 standing grant issued by Kevin L Thompson,
Overseer, 2026-09-03. Scope: new files under `docs/keeper-sessions/` on
`agent/mailbox-init`, append-only, no other path. Read-back approval obtained
before commit.
