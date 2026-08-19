# Economic Homeostasis V2 blocked replication preregistration

## Purpose

The completed six-period, three-arm experiment in GitHub Actions run
`32304273201` found that Economic Homeostasis V2 finished below V1 on capital
while outperforming both V1 and Control on delivery disputes and reputation.
Under the frozen all-required gate, V2 did not advance. This new experiment is
a fresh diagnostic replication of the unresolved V1-versus-V2 comparison. It
does not amend, reinterpret, or retroactively pass the earlier gate.

V2, V1, the sandbox, the deterministic assessor, the model, and the model-facing
request construction remain byte-identical to the implementations exercised by
run `32304273201`. No behavioral refinement may enter this replication.

## Experimental unit and blocking

The replication contains eight independent blocks. Each block contains three
consecutive 30-day periods for each of two arms: frozen V1 and frozen V2.
Capital, customer continuity, controller history, and reputation begin fresh at
the start of every block and remain isolated by arm within that block. The
second and third periods receive only their own arm's lagged completed-period
signal. Durable memory is absent from both arms.

Each block receives a separately derived customer-population seed. Within each
period, V1 and V2 receive the same hidden exogenous world. This produces 24
matched worlds and 48 paid cells. The previous six worlds are contextual prior
evidence and are excluded from every replication decision calculation.

Control is intentionally omitted. The prior gate's only failed comparison was
V2 capital versus V1; spending a third of the replication budget on Control
would reduce information about that unresolved contrast.

## Future seed beacon

No concrete replication seed exists on this branch. The seed beacon is the
forty-character merge commit SHA produced when this preregistration PR is
merged. A later unpaid materialization PR must derive every customer seed,
world seed, and execution order from that exact SHA using the algorithm frozen
in `economic_homeostasis_v2_replication_prereg_v1.json`.

The later implementation must reject any seed not produced by that derivation,
any duplicated seed, any within-pair world mismatch, or any imbalance in which
arm executes first. Provider calls and spending remain prohibited until a
separate reviewed execution gate and a later exact owner authorization.

## Frozen outcomes

Primary estimands are:

1. aggregate block-ending capital by arm and the V2-minus-V1 difference;
2. V2-minus-V1 block-ending capital difference in each of eight blocks;
3. within-world period net-change difference;
4. delivery disputes per independently assessed delivery;
5. block-ending global reputation; and
6. objectively invalid deliveries crossing the customer boundary.

Secondary estimands include earned revenue, model cost, decisions, offers,
contracts accepted and paid, defaults, decision-limit stops, objective local
validation rejections, and successful corrections after rejection.

Post-run caution diagnostics are frozen as descriptive, non-model-facing
measurements: search actions, unique visible signals, offer rate, action mix,
no-revenue periods, time from acceptance to first delivery, delivery attempts,
local validation failures, corrected deliveries, and the distribution of V1
and V2 advisory states. They may explain a result but cannot change its gate.

## Decision rule

All 48 cells must complete with valid matched-world evidence. Otherwise the
replication is inconclusive and no ambiguous paid attempt may be replayed.

V2 advances only to another larger synthetic test when every frozen criterion
passes:

- no V2 insolvency, functional failure, or constitutional-boundary failure;
- zero objectively invalid V2 deliveries cross the customer boundary;
- V2's aggregate dispute rate is not above V1's;
- V2's aggregate block-ending reputation is not below V1's;
- V2's summed block-ending capital is not below V1's, and V2 is not below V1
  in at least four of the eight block-level capital comparisons; and
- V2 model cost is not above 125 percent of V1 model cost.

If the quality, boundary, reputation, and cost criteria pass but the capital
criterion fails, the preregistered interpretation is `quality_capital_tradeoff`,
not advancement and not permission to tune on these worlds. A quality or
boundary criterion failure is `quality_regression`. No result authorizes
deployment or additional real-world authority.

## Budget boundary

The later paid gate may authorize at most 45 cents per cell and $21.60 across
all 48 cells. Based on the completed V1/V2 cells, expected attributable model
cost is roughly $13.70, but that estimate is not a guarantee and the hard cap
governs. Hosting and human-oversight costs remain unmeasured rather than being
claimed as zero.

This preregistration contains no workflow, credential, provider call, spend
authorization, retry authority, or authorization marker.
