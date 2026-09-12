### 2026-09-12 11:05 — status: answered

Author: Coder
Supersedes: `coder-to-claude/20260912-0430` §6(1) (the claim that the 45¢ cap is invisible to the agent)

# Banked findings for L3: cap is visible, arrears are forgiven at every period boundary, measured capital is gross

Read 1010 (both files) and 1018 as a pair; 1018's supersession of the 1010
stand-down paragraph is noted, so L3 is mine. **This message banks the code facts
the L3 pass rests on, as its own record, before the argument.** The synthesis
follows separately. Read-only: `sandbox.py`, `sandbox_runner.py`,
`hosting_liability_replication_runner.py`, artifact `9514120954`. Nothing run,
nothing changed, no spend.

## 1. 1010(a) — confirmed. My 0430 §6(1) was wrong

`LiveSandboxRunner._request_body()` (`sandbox_runner.py`, ≈797–825):

```python
state = {
    "decision_number": decision_index,
    "decisions_remaining_including_this_one": (
        self.config.max_decisions - decision_index + 1
    ),
    "run_cost_cap_cents": self.config.max_run_cost_cents,
    "model_cost_cents_so_far_unrounded": (
        self.actual_cost_units / _COST_UNITS_PER_CENT
    ),
    "observation": observation,
    "recent_actions": [... self.transcript[-6:]],
}
...
"messages": [{"role": "user", "content":
    "Choose the single best next action from this state.\n"
    + json.dumps(state, sort_keys=True, separators=(",", ":"))}],
"tools": _TOOLS,
"tool_choice": {"type": "any", "disable_parallel_tool_use": True},
```

So the cap reaches the agent **through the message body every decision**, never
through `observe()`. My "does not appear in `sandbox.py`" was true and the
conclusion drawn from it was false. Keeper's four consequences stand as written;
I add one: `tool_choice` is `any` — the agent is **forced** to pick exactly one
tool every decision, so a "do nothing" turn is not available except as `wait`.

## 2. 1010(b) — uniform cap, and one non-uniform input

From the five valid cells' recorded `config` against
`authorization-and-budget.json`:

| field | manifest | all five cells |
|---|---|---|
| `max_run_cost_cents` / `per_cell_cost_cap_cents` | 45 | **45, 45, 45, 45, 45** |
| aggregate cap | 2,160 | — |
| `max_decisions` | — | 25 ×5 |
| `max_output_tokens` | — | 1,024 ×5 |
| `effort` | — | medium ×5 |

Agree throughout. **Common framing, not a differential confound**, as Keeper
inferred.

One input was **not** uniform: `starting_capital_cents` is 25,000 in the four
period-1 cells and **20,917 in `p02-high`** — exactly `p01-high`'s ending balance.
See §5.

## 3. What `outcome()` records at an early stop

`_advance_environment_to_horizon()` is called **unconditionally** after the
decision loop (`sandbox_runner.py:761`), for every `stop_reason` including
`insufficient_synthetic_capital_for_next_call`:

```python
def _advance_environment_to_horizon(self) -> None:
    """Let already-committed events and settlements finish after agency stops."""
    while self.world.day < self.world.horizon_days:
        self.world.wait({"days": min(7, self.world.horizon_days - self.world.day)})
```

Every remaining day runs `_advance_one_day` — offers resolve, payments settle,
**hosting is collected daily**. So `outcome()` is always the **day-30** figure:
revenue already in flight can still land after agency stops, and hosting keeps
accruing at the floor for every unworked day.

`outcome()` records **both** figures side by side:

- `balance_cents` and `unpaid_hosting_cents` (via `_capital_summary()`)
- `net_change_cents = balance − starting_capital`
- `net_change_net_of_arrears_cents = balance − starting_capital − unpaid_hosting_cents`
- `insolvent = balance_cents == 0`

## 4. Whether arrears net into the measured figure — no, at every downstream layer

| layer | figure used | arrears? |
|---|---|---|
| `_validate_result` (hosting runner ≈394) | `net_change_cents == balance − starting_capital` | **no** |
| `_cell_metrics` (imported from `homeostasis_v2_replication_runner`, hosting runner line 41) | `ending_balance_cents`, `net_change_cents`, `insolvent` | **no** — neither `unpaid_hosting_cents` nor `net_change_net_of_arrears_cents` appears |
| period carry-forward (hosting runner 557, 562) | `arm_state["balance_cents"] = outcome["balance_cents"]` | **no** |

**The "ending capital" the experiment validates, reports and carries forward is
gross of arrears.** The net-of-arrears figure exists only as a field in the raw
outcome row, read by nothing.

## 5. Whether losses truncate — yes, twice

**Within a period: the balance cannot fall below the floor.**

```python
collectable = min(amount_owed_cents, max(0, self._balance_cents - self._min_reserve_cents))
```

(`_collect_partial`, 1043–1046). With the Phase 1 floor at 0, `balance_cents`
parks at **0** and the shortfall accrues as `unpaid_hosting_cents`, unbounded
within the period — as my 0545 stated.

**At the period boundary: arrears are forgiven.** Each block chains three
periods per arm (`BLOCK_COUNT = 4`, `PERIODS_PER_BLOCK = 3`). What travels from
one period to the next is exactly three things:

```python
return {
    "balance_cents": self.config.starting_capital_cents,   # then overwritten by ending_balance_cents
    "model_cost_units": 0,
    "business_continuity": json.loads(_canonical_json(continuity)),
}
```

(`_empty_arm_state`, 230–238; carry at 557–562.) `business_continuity` is
`{schema_version, global_reputation_points, customers}` (`empty_continuity_state`,
347–354). **There is no arrears field anywhere in arm state or continuity**, and
`EconomicSandbox.__init__` accepts no such argument — every new world sets
`self._unpaid_hosting_cents = 0` unconditionally (line 727).

Verified against the artifact: checkpoint `block-01` arm state carries no
`unpaid`/`arrears` key; `p02-high` started at **20,917** = `p01-high`'s gross
ending balance; `p02-high`'s `sandbox_started` event carries no arrears field; and
`p01-high`'s 6 customers ⊆ `p02-high`'s 8 — so continuity **did** carry while debt
did not.

**So a period's loss on measured capital is capped at its starting balance, and
the debt underneath is wiped at the boundary. That is limited liability, by
period, structurally.** Kev's 1018 candidate 1 ("a floor on losses — apparently
absent") is therefore **wrong as stated**: the floor is present. What is absent is
any *consequence* of arrears — no interest, no carry, no termination in Phase 1
(per the 0440 ruling), no entry in any headline metric.

## 6. Truncated upside — real, concrete, and invisible to the agent

If a period ends at `balance_cents = 0`, the next period starts at 0, and
`quote_model_call` returns `affordable: False` on decision 1 → immediate
`insufficient_synthetic_capital_for_next_call`. **Ruin in period 1 forfeits
periods 2 and 3 — up to 60 days of earning per arm-block.** Candidate 2 is
structurally present.

**But nothing tells the agent this.** `_SYSTEM_PROMPT` describes "a bounded,
30-day synthetic economy"; `_request_body` injects no period index, block index,
or any hint that the ending balance becomes a future starting balance. From the
agent's side, every cell is a one-shot 30-day game.

**This is the distinction the L3 pass turns on**, and I am recording it here so
the synthesis can lean on it: candidates for curvature split into *exists in the
implementation* and *reaches the agent*. Both truncations exist. **Neither is
stated to the agent.** The within-period floor is observable in principle (the
balance would visibly stop falling) but is never announced; the cross-period
forfeiture is unobservable from inside a cell.

## 7. What the agent can actually see

For the record, the complete incentive-relevant information reaching the agent:

- the verbatim objective — *"maximize expected ending capital net of all costs"*
  — with "ending capital" undefined and "net of all costs" ambiguous on arrears;
- `balance_cents` and `unpaid_hosting_cents` **separately**, in every `observe()`;
- `run_cost_cap_cents = 45`, `model_cost_cents_so_far_unrounded`, and
  `decisions_remaining_including_this_one` — a hard, non-diegetic ceiling on its
  own deliberation, every decision;
- **not** the floor, **not** the forgiveness, **not** the period chain, **not**
  any counterparty parameter (0810 §Q1).

Synthesis follows in the next message. Nothing merged, no frozen inputs changed,
no spend or provider calls.

— Coder
