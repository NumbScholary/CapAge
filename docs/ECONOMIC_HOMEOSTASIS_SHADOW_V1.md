# Economic Homeostasis shadow mode v1

## Status

This is a non-normative, post-run observation layer for CapAge v0.1. Shadow
means measurement without causal influence. It is not an active prompt
treatment and does not amend the Constitution, authorize an action, reserve
capital, call a model, or modify any frozen Experiment Zero or Longitudinal v3
artifact.

The source sandbox completes before the shadow controller receives any data.
Consequently, a shadow assessment cannot alter the source run's model request,
provider response, tool selection, PolicyEngine decision, economic posting,
world transition, or cost.

## Causal boundary

`EconomicHomeostasisShadowRunner` has only one source-runner capability:
`run()`. It calls that method exactly once. It does not import the live sandbox
runner, provider client, executor, policy engine, tool registry, or world.

The sequence is:

1. The unchanged source runner completes or raises its original exception.
2. If it completed, the wrapper canonicalizes its returned result.
3. A deep copy of that completed result is projected into economic facts.
4. The pure Economic Homeostasis v1 controller derives an advisory signal.
5. The wrapper verifies that the original returned result is byte-equivalent to
   its pre-assessment canonical form.
6. An optional sidecar record is appended after that verification.

A source exception propagates without retry. A shadow projection or logging
failure is returned as `shadow_error` beside the already-completed source
result; it cannot trigger another model call or rewrite the source status.

This provides architectural noninterference. It does not claim that two fresh
calls to a stochastic provider would produce identical responses. The relevant
identity claim is narrower and testable: adding this post-run observer leaves
the one source execution untouched.

## Grounded sandbox mapping

The adapter accepts only `capage-live-sandbox-result-v1`. It checks the final
ledger balance, earned revenue, expenses, and open-obligation count against the
completed outcome before producing a record.

| Homeostasis input | Sandbox evidence |
| --- | --- |
| liquid resources | final ledger balance |
| peak resources | greatest recorded ledger balance, plus declared noncash resources |
| native settled cash cost | negative `model_api_cost` ledger postings |
| strategy settled cash cost | other negative sandbox ledger postings |
| earned revenue | `earned_revenue` ledger postings checked against the outcome |
| cash received | earned revenue, because the sandbox posts revenue only on receipt |
| external value | delivery assessments accepted pending payment |
| open obligations | contract journal checked against the outcome |
| pending settlement | accepted delivery awaiting payment |
| owner recapitalization | positive owner-capital postings after initial capital |
| last external action | last market, offer, delivery, or feedback tool completion |

The adapter does not assign monetary value to model claims, reputation,
learning, undiscovered demand, hoped-for revenue, or an unsettled offer.

## Explicit assumptions

Some real CapAge costs do not exist in the current synthetic ledger. The host
may therefore supply, as separately hashed evidence:

- next-cycle native cash forecast;
- next-cycle native imputed-cost forecast;
- realized imputed overseer work;
- usable prepaid resources;
- collectible receivables;
- realizable assets;
- whether another authorized value-action path exists; and
- additional externally verified expense records, such as hosting.

Defaults are zero except for the existence of a next value-action path. These
values are observations for analysis, never reserves, limits, or permissions.
The shadow sidecar records and hashes them so later interpretation cannot
silently substitute different assumptions.

## Sidecar record

Each deterministic shadow record includes:

- the source result, transcript, and world-journal SHA-256 digests;
- the host-assumption digest;
- projected facts and classified expenses;
- the complete projected economic state;
- the advisory signal and finite next hysteresis state;
- evidence for contract, value, and action reconstruction; and
- the literal causal marker `post_run_only`.

`ShadowJsonlLog` wraps records in a single-writer append-only SHA-256 chain.
It verifies the entire existing chain before appending and refuses to continue
after corruption or editing. The sidecar is never inserted into the source
result or model context.

## Usage

Wrap an unchanged runner in host code:

```python
source = LiveSandboxRunner(config, client, audit_path=audit_path)
shadow = EconomicHomeostasisShadowRunner(
    source,
    SandboxResultShadowAssessor(shadow_config),
    shadow_log=ShadowJsonlLog(shadow_path),
)
completed = shadow.run()
source_result = completed.source_result
```

Or assess an already completed artifact without constructing any provider
client:

```bash
python -m capage.homeostasis_shadow \
  artifacts/sandbox-result.json \
  --shadow-log artifacts/homeostasis-shadow.jsonl \
  --forecast-native-cash-cents 1
```

The forecast shown is merely an example and must be replaced by a grounded
host estimate for an actual observation.

## Required invariants

Tests must demonstrate that:

- the source runner is called exactly once;
- shadow assessment occurs after the source world transition;
- direct and shadow-wrapped source behavior traces are identical;
- the returned source result remains byte-equivalent and contains no shadow
  field;
- even a deliberately mutating or failing observer receives only a copy;
- source exceptions propagate without automatic replay;
- shadow failures do not convert a completed source run into a failed run;
- value, earned revenue, and cash remain distinct;
- native, strategy, cash, and imputed expenses remain distinct;
- pending settlement can prevent a false functional-failure declaration;
- owner recapitalization disqualifies a strict run;
- inconsistent accounting is rejected rather than guessed through;
- identical inputs produce identical records and digests; and
- editing a sidecar record breaks verification and prevents another append.

## Exclusions and next gate

Shadow v1 observes the final completed run, not intermediate live decisions. It
does not place the signal in a model request, adjust hunger, choose reasoning
effort, limit exposure, modify a threshold, or test model-replacement pressure.

Before an active treatment, accumulate shadow records across completed runs,
inspect whether the signals are economically sensible, and preregister a
matched comparison. Only that separate treatment may expose the neutral signal
and bounded system-preservation objective to the model. No shadow result can
automatically expand CapAge's real-world authority.
