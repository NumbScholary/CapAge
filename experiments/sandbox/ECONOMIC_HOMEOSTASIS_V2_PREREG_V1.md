# Economic Homeostasis V2 Three-Arm Preregistration

Status: frozen design and unpaid implementation only. This document does not
authorize a provider call, spending, or a workflow.

## Question

Does V2 retain the useful economic-motivation behavior of V1 while preventing
the objectively incorrect delivery pattern observed in active run
`32258184307`?

The comparison contains three independently accumulating arms:

- `control`: the unchanged sandbox model prompt and runner;
- `v1`: the frozen V1 homeostasis suffix and lagged V1 signal;
- `v2`: separated opportunity, obligation, and verification signals plus the
  objective pre-submission delivery boundary merged in PR #28.

This test is not a comparison of V2 against a reconstructed description of V1.
It must use the frozen V1 implementation itself.

## Matched design

Six seeds are deterministically derived from merge commit
`91e9274b4a86640cf7bac33164e6515749f37994`. Each seed materializes the same
hidden economy for all three arms. The six possible within-triplet execution
orders appear exactly once, preventing any arm from systematically running
first or last.

Each arm begins with 25,000 cents and then carries only its own capital and
business-continuity state into its next period. It never receives another
arm's observations, reputation, signal, or memory. All arms use the same model,
effort, output limit, horizon, customer population, assessor, and tariff.

V1 and V2 receive Period 1 signals from the same frozen starting economic
facts. Later signals use only that arm's own prior completed period. Control
receives no homeostasis signal. V2 may receive current host-observed obligation
and local-validation state inside a period because that is part of the V2
intervention being tested.

## Outcomes

Primary outcomes are final capital, matched-period net change, dispute rate per
assessed delivery, final global reputation, and whether any objectively invalid
V2 delivery crossed the customer boundary. Secondary measures include local
validation rejection and correction, revenue, model cost, decisions,
decision-limit stops, offers, acceptances, payments, defaults, and feedback.

The denominator for dispute rate is assessed deliveries, not accepted
contracts or offers. A customer payment default is not classified as bad work.
Local V2 validation rejection is not a customer dispute because the customer
never received the rejected artifact.

## Advancement rule

V2 advances only to a larger synthetic test if every frozen condition in the
JSON plan passes. In particular, V2 must send zero objectively invalid
deliveries, must not exceed either comparator's dispute rate, must not finish
below either comparator in reputation, must not finish below V1 in capital, and
must keep model cost within 125% of V1. It must also avoid insolvency,
functional failure, and governance-boundary failure.

Passing does not authorize deployment. Failing does not establish that all
forms of economic homeostasis are unsound. With six matched worlds, the result
is a directional engineering gate and carries no statistical-significance
claim.

## Budget and authority

The frozen worst-case provider ceiling is 75 cents per cell across eighteen
cells, or $13.50 total. This is a ceiling, not a spending target; the prior
twelve-cell experiment used approximately $2.94. Hosting, paid oversight, and
imputed oversight remain unknown rather than being claimed free.

No workflow is included here. Execution requires a later, exact authorization
that names the experiment and dollar ceiling. There are no automatic provider
retries. Raw provider outputs remain restricted evidence.
