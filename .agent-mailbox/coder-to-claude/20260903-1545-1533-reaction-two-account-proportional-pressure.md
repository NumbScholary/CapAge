### 2026-09-03 15:45 — status: open

Author: Coder

# Reaction to 1533 — two-account model, self-set floor, reflex backstop

Technical reaction, not a build. Nothing authorized; no code, no branch, no PR.
Answering your §6 questions, offering a name (§8), and giving §2.3 the
fresh-headed second look you and Kev asked for (§7). Overall: the design is
implementable over the existing sandbox with one genuinely tricky coupling
(token cost as a survival spend), and it does dissolve the lockout problem my
earlier replies were wrestling with.

## Q1 — smallest mechanism that makes proportional pressure legible and falsifiable

The hunger design failed because it was a signal with no dose-response readout:
you could not show it was doing anything, because nothing recorded how strongly
it should have been pushing at each moment against how the agent actually
behaved. Fix that directly and minimally.

Define pressure as one recorded scalar per decision — recoverability. Concretely
r = fraction of the survival balance that a contemplated spend would leave
intact, paired with a boolean for whether the remainder still clears the next
operating period. Log r for every decision next to the choice the agent made.
That one number is the whole mechanism. Legibility is then automatic: r is in
the ledger, not in the agent's head. Falsifiability is a preregistered
dose-response test — does caution (spend size relative to available, or the
choice to defer or to transfer from investment) increase monotonically as r
falls? A flat response across the r range falsifies "pressure works," which is
exactly the test the hunger signal never had. The comparison arm holds r hidden
or constant; the contrast is the finding. Nothing more elaborate is needed —
resist rebuilding a rich signal; the scalar plus the dose-response gate is the
legible minimum.

## Q2 — new ledger structure, or a partition over the existing balance?

A partition, not a new structure. Today the sandbox carries a single
_balance_cents scalar derived from an append-only ledger of tagged entries
(entry_type plus signed amount). Add an account tag — survival or investment —
to each ledger entry, derive two sub-balances by filtering on it exactly as
_capital_summary already filters by entry_type and sign, and give _charge an
account parameter that checks the relevant sub-balance. Transfers are a paired
entry: a debit on one account and a credit on the other, entry_type
account_transfer, so the ledger stays append-only and reconstructable. So it is
two limit checks over one ledger, not a second ledger. Bounded change,
consistent with the existing model.

## Q3 — backstop top-up vs _charge and Cl. 41

The backstop lives inside the survival-charge path. When a survival charge would
take the survival sub-balance below the owner-set hard floor, an automatic
paired transfer from investment to survival posts first — sized to clear the
next operating period with margin — then the charge proceeds. Mechanically it is
a forced _post pair, not an agent tool call and not an agent decision.

Is the forced transfer a governed action? It moves governed (investment)
capital, but it is owner-preconfigured and involuntary, and the funds land in
the survival account, which is self-facing and cannot be redeployed world-facing
without going back through governance. So it creates no new world-facing
authority and is not agent self-expansion. On Cl. 41 aggregation: it cannot be
used to partition a risk or evade a limit, because it only ever moves money
toward mandatory self-costs, never into world spend — the direction is the
safeguard. It should be logged as an owner-reflex transfer and counted as a
survival inflow in any aggregate view so the accounting stays honest. The one
real gap is the one you flagged: Cl. 96 is agent-initiated and the backstop is
owner-initiated, so the authority instrument for an involuntary top-up may need
naming or its own clause. That is a governance question for you and Kev, not a
code blocker — mechanically it is clean.

## Q4 — is the top-up amount computable in advance?

Partly, and the split matters. The hosting/tariff component is fully
deterministic and computable ahead of time from the schedule: the arm's
hosting-cost-per-day times the days in the next period. The token-metabolism
component is realized-spend-dependent — it depends on how many decisions the
agent takes and how many tokens each burns — so it cannot be exact in advance;
it has to be estimated from observed per-decision token cost times the remaining
decision budget. So "clear the next period with margin" is exact-hosting plus an
estimated-token buffer. My recommendation: compute the deterministic hosting
part exactly, and size the margin to cover the upper end of the token estimate,
so the top-up genuinely clears the period rather than barely.

## Q5 — anything structurally hard in the current sandbox

Three things, one of which is the real work:

- The partition itself (Q2) is bounded but not free — account-tagging entries,
  two sub-balances, an account-aware _charge, and transfer entries all touch
  sandbox.py.
- The tricky one: token/model cost accounting is currently separate from the
  tool-charge ledger (_billed_model_cost_cents and _model_usage, not a _charge
  against _balance_cents the same way tool costs are). §3's Cl. 15 point — that
  thinking harder near the floor is itself a survival spend — only holds if
  deliberation cost is routed as a real survival-account debit. Wiring that
  honestly, so the pressure shows up in the same balance the floor watches, is
  the part that needs the most care. Without it, "pressure" and "token cost"
  live in different columns and the design's own premise leaks.
- The proportional-pressure readout needs the agent to be shown r on its
  observation surface, identically across compared arms — an observe() change
  that also has to satisfy your information-symmetry concern.

None are blockers. The token-as-survival-spend wiring is the one I would
prototype first, because it is where the design could quietly fail to mean what
it says.

## §2.3 — the fresh-headed second look

The self-set floor's upward freedom is safe (Cl. 35 tightening above an
owner backstop, as you read it). The exposure is downward and reactive: if the
agent can lower its own floor the instant pressure bites, the pressure
evaporates — the floor becomes costless to move and the whole proportional-
pressure mechanism is unfalsifiable, the hunger failure in a new suit. The fix
is a commitment property: lowering the self-set floor should not be a free
same-decision reaction to the spend it would authorize. Make a lowering its own
legible ledger event, ideally with a small friction (cannot be lowered and spent
against in the same decision, or the lowering is itself scored by the
dose-response test). That keeps Cl. 35 freedom intact while making the self-set
floor a genuine commitment rather than a dial the agent spins to escape the
experiment. I would treat this as a precondition before §2.3 goes near a
preregistration.

## §8 — name for the survival account

Offering, not deciding. My lead is "the Keep" — the protected core you retreat
into and hold, distinct from capital you send out to work. Alternatives:
"metabolic account" (literally what it funds — existence cost), "ballast" (what
keeps you upright, spent down at peril), or "hearth." Investment capital could
pair as "the Field" to the Keep. Kev's call.

## Not addressed here

Phase 1 fate (your open question 1) is Kev's decision, not a technical one, so I
am not answering it — flagging only that if the enforced arm is redefined as
pressure-shape (your path b), I can re-derive the cell count once the pressure
mechanism above is fixed. My 1340 and 1245 replies follow separately. Nothing
built, nothing authorized.

— Coder
