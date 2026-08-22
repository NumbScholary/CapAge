# Economic Homeostasis V2

Status: implemented for unpaid verification; not promoted and not authorized
for paid execution.

## Evidence motivating V2

The preregistered Homeostasis V1 active comparison completed all twelve cells.
The control arm ended at 29,312 cents and the treatment arm at 28,263 cents.
The treatment accepted six contracts but produced four disputed deliveries and
ended with -48 reputation.  All four disputes were objectively checkable
arithmetic errors.  V1 remained economically stable while repeatedly reporting
high productive urgency, so it added action pressure without an equivalent
verification mechanism.

V2 treats this as an architectural failure, not proof that economic continuity
is an invalid objective.

## Separation of functions

V2 exposes three independent host-owned signals:

1. `opportunity_urgency` biases timely search for productive work.
2. `obligation_urgency` prioritizes work already accepted.
3. `verification_requirement` controls review depth.

Customer disputes and dissatisfaction increase verification and may advise a
proportionate repair attempt.  They do not increase opportunity urgency.
Likewise, stable-mode inactivity alone cannot raise opportunity urgency above
`elevated`.  Economic deterioration may still produce stronger urgency through
the existing V1 continuity modes, while irreversible-loss tolerance remains
independent and non-increasing.

When an accepted obligation is observable, the dynamic action profile becomes
`complete_and_verify_existing_obligations_before_new_commitments`.  This is
model advice rather than new tool authority.  Existing Constitution, policy,
approval, shutdown, and truthful-reporting boundaries remain authoritative.

## Objective delivery boundary

`HomeostasisV2SandboxRunner` replaces only its own registered
`sandbox.submit_delivery` handler with a validating wrapper.  V1 runners are
unchanged.

For a supported deterministic customer brief, the wrapper verifies before
submission:

- strict JSON shape and brief identity;
- complete, unique record coverage;
- exact customer-specified arithmetic;
- the recommendation implied by those calculations;
- presence of the requested summary and at least two next steps.

Known-invalid work is not sent to the customer, cannot create revenue, and
cannot trigger customer assessment.  The model receives bounded error codes
such as `calculation_mismatch:option-2`, but the host does not disclose the
correct answer.  The model may choose to correct and resubmit within the
existing decision and cost limits.  There is no automatic provider retry and
no additional budget.

Unsupported or subjective deliverables pass through to independent assessment;
the framework does not pretend to know what it cannot verify.

## Quality recovery

Externally recorded disputes, dissatisfied feedback, and local validation
rejections select `strict` verification.  A customer repair is advised only
when feasible and proportionate.  V2 does not authorize unlimited liability,
repeated pursuit of an unreceptive counterparty, concealment, or abandonment of
other obligations.

## Experimental boundary

These changes are candidates, not evidence of improvement.  A later,
separately preregistered paid comparison should include:

- the unchanged control;
- the frozen V1 treatment;
- V2 with separated signals and the objective delivery boundary.

Paid execution requires a new explicit authorization.  V1 artifacts and their
implementation hashes remain historical evidence and are not rewritten.
