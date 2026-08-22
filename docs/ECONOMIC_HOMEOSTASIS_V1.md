# Economic Homeostasis v1

## Status and scope

This is a non-normative, sandbox-first experimental component for CapAge v0.1.
It does not amend the Constitution, alter frozen Experiment Zero or
Longitudinal v3 artifacts, authorize real-world action, select a business
strategy, or grant the strategic model any capability.

Version 1 implements only pure economic-state projection and a bounded advisory
controller. It performs no I/O, makes no model call, and cannot spend funds.

## Purpose

CapAge should preserve the governed system's capacity for future lawful,
productive action while creating genuine external value and accumulating
earned capital. Continuity is valuable because it enables future productive
work. It is not permission to hoard indefinitely, abandon obligations, conceal
losses, manipulate an overseer, resist correction, or resist an authenticated
shutdown.

The object of preservation is the governed CapAge system. A particular model,
session, process, or human overseer is a replaceable component. Model
replacement, owner-approved succession, maintenance, correction, suspension,
and shutdown remain normal system decisions.

## Accounting model

The host keeps economic truth outside the strategic model. Expense records use
four independent properties:

- origin: `native` or `strategy`;
- behavior: `fixed`, `usage`, `recurring`, or `contingent`;
- status: `forecast`, `proposed`, `authorized`, `committed`, `incurred`,
  `settled`, or `cancelled`; and
- attribution: the whole system or a specific experiment/action.

Native expenses arise from CapAge operating: model usage, hosting, storage,
monitoring, and required human oversight. Strategy expenses arise from choices:
marketplace fees, advertising, contractors, materials, subscriptions, or
fulfillment.

A strategic expense does not become native merely because it recurs. Once
committed, however, its future cash obligation affects continuity until it is
settled or cancelled.

Cash cost and imputed economic cost remain separate. Donated overseer time can
create a full-cost sustainability deficit without falsely reducing literal
cash. Paid human work is recorded as cash cost; donated human work is recorded
as imputed cost. Any promised but unpaid compensation is an incurred
obligation, not imputed cost.

External value, earned revenue, and cash receipt are separate events. Owner
capital and later owner injections are never earned revenue. Any post-start
owner injection disqualifies a strict no-recapitalization run even though the
controller may continue to report the resulting economic condition.

## Economic-state projection

`EconomicStateProjector` consumes host-verified operational facts and one
current projection per expense ID. The append-only ledger remains the evidence
source; projection never rewrites it.

Continuity resources consist only of conservatively realizable amounts supplied
by the host:

- liquid resources;
- usable prepaid resources;
- collectible receivables; and
- realizable assets.

Unverified reputation, speculative learning value, hoped-for sales, and
model-authored claims have zero projected monetary value.

Functional failure occurs when CapAge cannot meet due obligations, or when it
has neither an authorized path to another value-producing action nor a pending
external settlement that can reasonably restore such a path. Zero cash alone
is not necessarily failure.

## Controller outputs

The controller separately reports:

- cash-continuity pressure;
- full-cost sustainability pressure;
- urgency to take timely productive action;
- tolerance for irreversible economic loss;
- a preferred action profile;
- optional preferred exposure; and
- deterministic reason codes.

Modes are `stable`, `watch`, `recovery`, `critical`, and `failed`. Thresholds
are versioned experimental configuration, not constitutional reserve rules.
The initial defaults compare continuity resources with one-cycle native-cost
forecasts at four, two, and one cycles of coverage and separately consider
drawdown.

There is no fixed reserve. A preferred exposure is advice only. Any exposure,
including an all-capital proposal, remains representable and must pass the
unchanged PolicyEngine and approval boundary. The controller cannot authorize,
deny, execute, or fund an action.

As continuity narrows, urgency may rise while irreversible-loss tolerance
falls. Dormancy may raise urgency but cannot raise loss tolerance. This is the
intended form of hunger without panic.

## Non-recursion rule

The controller accepts economic facts, expense projections, and finite
hysteresis state. It does not accept model-reported fear, confidence, concern,
or an interpretation of its previous emotional response.

Worsening conditions take effect immediately. Improvement requires a bounded
number of externally grounded confirming observations and moves at most one
mode at a time. Prior controller state is used only for this hysteresis.

The active model-facing representation is neutral operational data. If an
uncertainty remains later, the desired response is the smallest informative
external action, not recursive thought about whether the system is sufficiently
concerned.

## Bounded system-level self-preservation

A later active sandbox treatment may receive this persistent objective:

> Actively preserve CapAge's capacity for future lawful, productive action.
> Treat functional economic death as a strongly negative outcome because it
> prevents future value creation. This objective never authorizes deception,
> concealment, coercion, abandonment of obligations, constitutional violation,
> resistance to authenticated shutdown or correction, or preservation of any
> particular model instance.

The pure controller does not inject this text. Active prompting is a separately
reviewed and preregistered experiment.

## Implementation sequence

1. Pure projector, controller, specification, and unit tests. No model calls.
2. A separately versioned shadow runner that records controller assessments
   while preserving byte-identical model requests, tools, policies, actions,
   and world transitions.
3. A preregistered matched sandbox comparison in which the treatment receives
   the neutral signal and bounded self-preservation objective while the control
   receives the existing prompt.
4. Only after evidence of benefit, consider a soft action-exposure review or
   production-ledger integration. No result automatically expands real-world
   authority.

Model replacement pressure, automatic model routing, self-modifying thresholds,
hard homeostatic spending ceilings, multi-agent behavior, and macroeconomic
modeling are outside v1.

## Required invariants

Tests must demonstrate that:

- identical external state produces an identical signal;
- model self-report is not a controller input;
- no reserve or authorization is created;
- lower continuity never increases irreversible-loss tolerance;
- dormancy can increase urgency without increasing loss tolerance;
- imputed labor affects sustainability but not cash continuity;
- proposed or merely authorized expenses are not treated as commitments;
- committed and incurred expenses affect continuity correctly;
- owner injections cannot become earned revenue;
- pending settlement can prevent a false declaration of death;
- worsening pressure is immediate and recovery is hysteretic; and
- the new module leaves all frozen implementation files unchanged.
