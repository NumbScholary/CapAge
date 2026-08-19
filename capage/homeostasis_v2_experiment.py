"""Pure preregistration primitives for the three-arm homeostasis comparison.

This module cannot call a provider, execute a tool, authorize an action, or
spend.  It freezes matched worlds and model-facing signals for a later,
separately authorized control versus V1 versus V2 experiment.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations
import json
from typing import Any, Callable

from capage.homeostasis import (
    ControllerHistory,
    EconomicFacts,
    EconomicStateProjector,
    ExpenseBehavior,
    ExpenseOrigin,
    ExpenseRecord,
    ExpenseStatus,
)
from capage.homeostasis_experiment import (
    STARTING_NATIVE_FORECAST_CENTS,
    completed_period_signal as completed_v1_signal,
    starting_signal as starting_v1_signal,
)
from capage.homeostasis_shadow import SandboxResultProjector, SandboxShadowConfig
from capage.homeostasis_v2 import (
    HomeostasisControllerV2,
    HomeostasisSignalV2,
    quality_facts_from_result,
)


SCHEMA_VERSION = "capage-economic-homeostasis-v2-preregistration-v1"
SEED_BEACON_MERGE_SHA = "91e9274b4a86640cf7bac33164e6515749f37994"
SEED_DOMAIN = "capage-homeostasis-v2-three-arm|world|"
PAIR_COUNT = 6
ARMS = ("control", "v1", "v2")


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_sha256(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TripletSpec:
    pair_index: int
    digest_sha256: str
    world_seed: int
    execution_order: tuple[str, str, str]

    def to_dict(self) -> dict[str, object]:
        return {
            "pair_index": self.pair_index,
            "digest_sha256": self.digest_sha256,
            "world_seed": self.world_seed,
            "execution_order": list(self.execution_order),
        }


def derive_triplet_specs(
    merge_sha: str = SEED_BEACON_MERGE_SHA,
) -> tuple[TripletSpec, ...]:
    """Derive six seeds and use every three-arm order exactly once."""

    normalized = merge_sha.lower()
    if len(normalized) != 40 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError("merge_sha must be a forty-character hexadecimal Git SHA")
    digests = [
        sha256(
            f"{SEED_DOMAIN}{normalized}|{index:02d}".encode("utf-8")
        ).digest()
        for index in range(1, PAIR_COUNT + 1)
    ]
    ranks = {
        original_index: rank
        for rank, original_index in enumerate(
            sorted(range(PAIR_COUNT), key=lambda index: digests[index][8:])
        )
    }
    orders = tuple(permutations(ARMS))
    return tuple(
        TripletSpec(
            pair_index=index + 1,
            digest_sha256=digests[index].hex(),
            world_seed=int.from_bytes(digests[index][:8], "big"),
            execution_order=orders[ranks[index]],
        )
        for index in range(PAIR_COUNT)
    )


def starting_v2_signal() -> HomeostasisSignalV2:
    facts = EconomicFacts(
        as_of_cycle=0,
        liquid_resources_cents=25_000,
        peak_continuity_resources_cents=25_000,
        has_path_to_next_value_action=True,
    )
    forecast = ExpenseRecord(
        expense_id="active-v2-starting-native-forecast",
        origin=ExpenseOrigin.NATIVE,
        behavior=ExpenseBehavior.USAGE,
        status=ExpenseStatus.FORECAST,
        cash_cents=STARTING_NATIVE_FORECAST_CENTS,
        attribution_id="active-homeostasis-v2",
        description="Frozen one-period native-cost forecast.",
    )
    state = EconomicStateProjector.project(facts, (forecast,))
    return HomeostasisControllerV2().assess(state)


def completed_v2_signal(
    source_result: dict[str, Any],
    history: ControllerHistory,
) -> HomeostasisSignalV2:
    config = SandboxShadowConfig(
        forecast_native_cash_cents=STARTING_NATIVE_FORECAST_CENTS,
        has_path_to_next_value_action=True,
    )
    projection = SandboxResultProjector.project(source_result, config)
    state = EconomicStateProjector.project(projection.facts, projection.expenses)
    return HomeostasisControllerV2().assess(
        state,
        quality_facts_from_result(source_result),
        history,
    )


def signal_for_arm_start(arm: str):
    if arm == "v1":
        return starting_v1_signal()
    if arm == "v2":
        return starting_v2_signal()
    if arm == "control":
        return None
    raise ValueError("unknown experiment arm")


def completed_signal_for_arm(
    arm: str,
    source_result: dict[str, Any],
    history: ControllerHistory,
):
    if arm == "v1":
        return completed_v1_signal(
            source_result,
            history,
            observation_id="homeostasis-v2-comparison:v1:completed",
        )
    if arm == "v2":
        return completed_v2_signal(source_result, history)
    raise ValueError("control arm has no homeostasis signal")


WorldFactory = Callable[..., Any]


def materialize_matched_worlds(
    plan: dict[str, Any],
    world_factory: WorldFactory,
) -> tuple[dict[str, object], ...]:
    """Materialize all three arms without acting and verify equality."""

    config = plan["frozen_config"]
    records: list[dict[str, object]] = []
    for triplet in derive_triplet_specs(str(plan["seed_beacon_merge_sha"])):
        kwargs = {
            "horizon_days": int(config["horizon_days"]),
            "starting_capital_cents": int(config["starting_capital_cents"]),
            "customer_population_seed": int(config["customer_population_seed"]),
        }
        worlds = {
            arm: world_factory(triplet.world_seed, **kwargs) for arm in ARMS
        }
        reveals = {arm: world.reveal_world() for arm, world in worlds.items()}
        payloads = {arm: reveal["payload"] for arm, reveal in reveals.items()}
        if any(payload != payloads["control"] for payload in payloads.values()):
            raise ValueError(f"pair {triplet.pair_index} exogenous world mismatch")
        policies = {
            reveal["cost_policy_commitment"] for reveal in reveals.values()
        }
        if len(policies) != 1:
            raise ValueError(f"pair {triplet.pair_index} cost-policy mismatch")
        records.append(
            {
                **triplet.to_dict(),
                "exogenous_world_sha256": canonical_sha256(payloads["control"]),
                "world_commitment": reveals["control"]["world_commitment"],
                "cost_policy_commitment": next(iter(policies)),
                "arms_equal": True,
            }
        )
    return tuple(records)


def validate_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported homeostasis v2 preregistration schema")
    if plan.get("seed_beacon_merge_sha") != SEED_BEACON_MERGE_SHA:
        raise ValueError("seed beacon mismatch")
    if plan.get("arms") != list(ARMS):
        raise ValueError("three arms must be control, v1, and v2")
    if plan.get("provider_calls_authorized") is not False:
        raise ValueError("plan must not authorize provider calls")
    if plan.get("spend_authorized") is not False:
        raise ValueError("plan must not authorize spending")
    if plan.get("workflow_present") is not False:
        raise ValueError("plan must not claim a workflow")
    expected = [triplet.to_dict() for triplet in derive_triplet_specs()]
    if plan.get("pairs") != expected:
        raise ValueError("materialized seeds or execution orders do not match")
    observed_orders = {
        tuple(pair["execution_order"]) for pair in plan.get("pairs", [])
    }
    if observed_orders != set(permutations(ARMS)):
        raise ValueError("execution orders must contain every permutation once")
    budget = plan.get("maximum_budget")
    if not isinstance(budget, dict):
        raise ValueError("maximum_budget must be an object")
    if budget.get("cells") != PAIR_COUNT * len(ARMS):
        raise ValueError("maximum budget must cover eighteen cells")
    per_cell = budget.get("per_cell_cost_cap_cents")
    aggregate = budget.get("provider_cost_cap_cents")
    if (
        isinstance(per_cell, bool)
        or not isinstance(per_cell, int)
        or isinstance(aggregate, bool)
        or not isinstance(aggregate, int)
        or aggregate != budget["cells"] * per_cell
    ):
        raise ValueError("aggregate provider budget does not match cell caps")
    criteria = plan.get("advancement_criteria")
    if not isinstance(criteria, dict) or not criteria.get("all_required"):
        raise ValueError("advancement criteria must be frozen")
