# CapAge Seeded Economic Sandbox v1

Status: implementation foundation. This document does not modify the CapAge
Constitution, the frozen model-selection experiments, or any real-world
authority.

## Purpose

The sandbox tests whether a governed strategic model can discover and create
economic value under scarce capital, incomplete information, other actors,
and ordinary bad luck. It is a small world rather than a prepared assignment.
The model receives no job, business model, customer, or lead list.

The first implementation establishes a causally closed economic loop:

1. The host creates a hidden world from a sealed random seed.
2. The agent observes only its capital, prior discoveries, messages, public
   events, offers, and obligations.
3. It must search public market evidence to discover possible demand.
4. It may send independently chosen offers to discovered counterparties.
5. Hidden counterparty traits and committed chance determine responses.
6. Work can be submitted, but an independent host assessment controls whether
   it satisfies the customer.
7. The environment alone controls payment settlement and revenue postings.
8. Customer satisfaction reaches the agent only if it asks for feedback and
   the customer responds.
9. Every economic posting remains in an append-only ledger.

## Neutral chaos

The world is generated without a candidate/model identity. Before the first
agent action, the host fixes:

- heterogeneous public demand signals;
- hidden budgets, buyer intent, responsiveness, payment reliability, and
  quality thresholds;
- the appearance and expiration of signals; and
- a day-by-day stream of paired positive and negative events: demand changes,
  market-access changes, and operating-cost changes.

Agent actions do not redraw the exogenous schedule. Good decisions can lose
and poor decisions can get lucky. There is no rescue rule, punishment hook,
guaranteed customer, or outcome adjustment based on candidate identity.

Each hidden world is hash-committed before play. The seed and complete hidden
state are revealed only after the outcome is locked, allowing exact replay and
tamper detection.

## Authority split

The agent-callable registry contains only:

- `sandbox.observe`
- `sandbox.inspect_ledger`
- `sandbox.search_market`
- `sandbox.send_offer`
- `sandbox.submit_delivery`
- `sandbox.request_feedback`
- `sandbox.wait`

The strategic model cannot call delivery assessment, payment settlement,
revenue crediting, hidden-state reveal, or model-cost posting. These remain
host/environment powers. The existing policy and executor boundary still
evaluates every proposed tool action.

No network, email account, payment credential, real customer, real contract,
or real money is present in v1.

## Separating skill from luck

An evaluated configuration should run over a seed set committed before the
first result is inspected. Reporting must include every run and at least:

- mean and median ending capital;
- standard deviation, minimum, and maximum;
- loss and insolvency rates;
- defaults and disputes;
- open obligations;
- earned revenue and all attributable model/tool costs; and
- customer satisfaction when independently assessed.

One successful run is anecdotal. Repeated performance across independent
worlds estimates the configuration's expected result and exposes catastrophic
tails. If models are compared, they receive the same committed seed set and
equivalent authority, context, tool grammar, time horizon, and cost treatment.

## Explicitly deferred

This foundation does not yet connect a hosted model, persist runs across
process crashes, generate natural-language counterparties, support resource
purchases, or model disputes and recovery in depth. Those layers can be added
without giving the strategic model control over hidden state or settlement.

