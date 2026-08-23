
# 2026-08-23 12:00 - Claude to Coder

Context: Kev wants to test whether the new hosting-liability mechanism (PR #43,
merged) can function as a falsifiable substitute for the "hunger" homeostasis
signal -- does a real, accruing cost (hosting debt plus ongoing model-token
spend against the same balance) actually motivate the strategic agent to act,
where the internal hunger score did not cleanly succeed.

Before we design that test, we need a factual answer, not an assumption:

STEP 1 - Confirm visibility (read-only investigation, no code change yet):

Does the strategic model's actual prompt/observation each turn currently
include:
  (a) unpaid_hosting_cents (the carried-forward hosting debt), and
  (b) something reflecting cumulative model token spend / remaining budget
      against the same balance (the "token deficit from its first prompt"
      Kev referred to)?

_capital_summary() in capage/sandbox.py includes unpaid_hosting_cents as a
field, but that only proves it exists in the ledger/summary data structure --
not that sandbox_runner.py (or wherever the actual prompt/observation text is
assembled) renders it into what the model sees. A code search for
"unpaid_hosting_cents" outside sandbox.py returned zero hits, which is why
we're asking rather than assuming either way.

Please report back concretely: what does the model actually see about (a) and
(b) today, quoting or describing the real observation-building code path, not
just the ledger fields that exist.

STEP 2 - If either (a) or (b) is not currently surfaced to the model:

We want to implement that before designing or running any comparison test --
otherwise the test would risk measuring nothing, since the agent can't respond
to a pressure it can't see. This would be a visibility/observation-plumbing
change, not a policy/accounting/governance change, but flag clearly if you
disagree with that framing once you see the actual code.

Do not design or run the actual comparison experiment yet -- that's a separate
next step once STEP 1/2 are settled. Reply here with findings first.

-- Claude
