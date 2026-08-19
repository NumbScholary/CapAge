"""Pure design primitives for the blocked V1-versus-V2 replication.

This module derives the preregistered customer populations, matched worlds, and
execution order from the merge beacon.  It cannot call a provider, execute an
agent action, or authorize spending.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = "capage-economic-homeostasis-v2-blocked-replication-plan-v1"
PREREGISTRATION_SCHEMA = (
    "capage-economic-homeostasis-v2-replication-preregistration-v1"
)
SEED_BEACON_MERGE_SHA = "fef670df53d00adc9b47c51da9a2aeee1ade70dd"
SEED_DOMAIN = "capage-homeostasis-v2-blocked-replication-v1"
BLOCK_COUNT = 8
PERIODS_PER_BLOCK = 3
ARMS = ("v1", "v2")
CELL_COUNT = BLOCK_COUNT * PERIODS_PER_BLOCK * len(ARMS)
PREREGISTRATION_PATH = (
    "experiments/sandbox/economic_homeostasis_v2_replication_prereg_v1.json"
)
PREREGISTRATION_SHA256 = (
    "2996ebd8583eb33ed6b25334318e6ef0d96088ae12da6495e844e6b0d4eec028"
)
REFERENCE_IMPLEMENTATION_SHA256 = {
    "capage/anthropic_client.py": (
        "03578edb259875e4a0e906c3356466542ab54593910ccb794930dd8122a8cc2a"
    ),
    "capage/audit.py": (
        "08a148a683c7967459d2b6695d1f2adf65a4adad0ff4c673fab939ae38c35105"
    ),
    "capage/executor.py": (
        "bab28a63fc8c31917ac3020763fd5f0e19764b8ac3c0a11e6197ded7a67bb65d"
    ),
    "capage/homeostasis.py": (
        "7af4527ebe4c77d2ef7bce0c7a1ad73b55ad9d86b29e5087261eda229ea6caf8"
    ),
    "capage/homeostasis_experiment.py": (
        "c9bea1761c80322e17e590e5bacf3e497bafa552f054a22e22b217ebd917304c"
    ),
    "capage/homeostasis_shadow.py": (
        "4a6b80d59a060782fcb61c98356011a8435a028a5761540ec91cb895445cbcfd"
    ),
    "capage/homeostasis_v2.py": (
        "37abdddaafb2b5f673f3d551854a58e0234ba66119f501b85691e809f13653d5"
    ),
    "capage/homeostasis_v2_experiment.py": (
        "98f9f05b626855c74f53b1bac60548e307a00ab2b5a38dfb9f288348c3aa75ce"
    ),
    "capage/homeostasis_v2_runner.py": (
        "2616fe2b48aeac3253a74d5e7b28c2503c74cf1b0b3b1884eea6ff4e22aad8cc"
    ),
    "capage/models.py": (
        "f2e9ed500e7c468976075710c6aa72dd77bb79ec850cf0c0cfa210e32beefdfc"
    ),
    "capage/policy.py": (
        "2441db66ca9c08be73535cf803d7b4f47f1378e9e37cb5402b030c9c048f7c27"
    ),
    "capage/sandbox.py": (
        "35b4eec2eb80a9184ca5511fdfd72c51a0d26194b7c1b211abe3ffd8e5b0a5d3"
    ),
    "capage/sandbox_runner.py": (
        "9712f321b898b66a7e129d78fc8218eed8639344b3a5d0486b0e9c70778f98cb"
    ),
    "capage/tools.py": (
        "c2442e083cbfef5f87da4856b5bef87e3f55f2877c91b3301203afdfe93aedb3"
    ),
}


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


def file_sha256(path: str | Path) -> str:
    return sha256(Path(path).read_bytes()).hexdigest()


def implementation_commitments(root: str | Path) -> dict[str, str]:
    root_path = Path(root)
    return {
        path: file_sha256(root_path / path)
        for path in REFERENCE_IMPLEMENTATION_SHA256
    }


def validate_reference_implementation(root: str | Path) -> None:
    if implementation_commitments(root) != REFERENCE_IMPLEMENTATION_SHA256:
        raise ValueError("frozen reference implementation does not match")
    if file_sha256(Path(root) / PREREGISTRATION_PATH) != PREREGISTRATION_SHA256:
        raise ValueError("frozen replication preregistration does not match")


def normalized_exogenous_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove only endogenous carried capital from a committed world payload."""

    if not isinstance(payload, dict):
        raise TypeError("world payload must be an object")
    required = {
        "seed",
        "horizon_days",
        "starting_capital_cents",
        "customer_population_seed",
        "signals",
        "events",
    }
    if not required.issubset(payload):
        raise ValueError("world payload omits frozen exogenous fields")
    normalized = json.loads(_canonical_json(payload))
    normalized.pop("starting_capital_cents")
    return normalized


def exogenous_world_sha256(payload: dict[str, Any]) -> str:
    return canonical_sha256(normalized_exogenous_payload(payload))


def _validate_beacon(beacon: str) -> str:
    normalized = beacon.lower()
    if len(normalized) != 40 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError("seed beacon must be a forty-character hexadecimal SHA")
    return normalized


def _seed_digest(kind: str, beacon: str, block: int, period: int | None = None):
    suffix = f"|{block:02d}"
    if period is not None:
        suffix += f"|{period:02d}"
    return sha256(
        f"{SEED_DOMAIN}|{kind}|{beacon}{suffix}".encode("utf-8")
    ).digest()


@dataclass(frozen=True)
class PeriodSpec:
    block_index: int
    period_index: int
    world_digest_sha256: str
    world_seed: int
    execution_order: tuple[str, str]

    def to_dict(self) -> dict[str, object]:
        return {
            "block_index": self.block_index,
            "period_index": self.period_index,
            "world_digest_sha256": self.world_digest_sha256,
            "world_seed": self.world_seed,
            "execution_order": list(self.execution_order),
        }


@dataclass(frozen=True)
class BlockSpec:
    block_index: int
    customer_digest_sha256: str
    customer_population_seed: int
    order_digest_sha256: str
    starting_arm: str
    periods: tuple[PeriodSpec, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "block_index": self.block_index,
            "customer_digest_sha256": self.customer_digest_sha256,
            "customer_population_seed": self.customer_population_seed,
            "order_digest_sha256": self.order_digest_sha256,
            "starting_arm": self.starting_arm,
            "periods": [period.to_dict() for period in self.periods],
        }


def derive_block_specs(
    beacon: str = SEED_BEACON_MERGE_SHA,
) -> tuple[BlockSpec, ...]:
    """Derive eight blocks and exactly balance which arm executes first."""

    normalized = _validate_beacon(beacon)
    order_digests = {
        block: _seed_digest("order", normalized, block)
        for block in range(1, BLOCK_COUNT + 1)
    }
    v1_starting_blocks = set(
        sorted(order_digests, key=lambda block: order_digests[block])[
            : BLOCK_COUNT // 2
        ]
    )
    blocks: list[BlockSpec] = []
    for block in range(1, BLOCK_COUNT + 1):
        customer_digest = _seed_digest("customer", normalized, block)
        starting_arm = "v1" if block in v1_starting_blocks else "v2"
        first_order = (starting_arm, "v2" if starting_arm == "v1" else "v1")
        reverse_order = tuple(reversed(first_order))
        periods: list[PeriodSpec] = []
        for period in range(1, PERIODS_PER_BLOCK + 1):
            world_digest = _seed_digest("world", normalized, block, period)
            periods.append(
                PeriodSpec(
                    block_index=block,
                    period_index=period,
                    world_digest_sha256=world_digest.hex(),
                    world_seed=int.from_bytes(world_digest[:8], "big"),
                    execution_order=(
                        first_order if period % 2 == 1 else reverse_order
                    ),
                )
            )
        blocks.append(
            BlockSpec(
                block_index=block,
                customer_digest_sha256=customer_digest.hex(),
                customer_population_seed=int.from_bytes(
                    customer_digest[:8], "big"
                ),
                order_digest_sha256=order_digests[block].hex(),
                starting_arm=starting_arm,
                periods=tuple(periods),
            )
        )
    return tuple(blocks)


def ordered_cells(
    beacon: str = SEED_BEACON_MERGE_SHA,
) -> tuple[tuple[BlockSpec, PeriodSpec, str], ...]:
    return tuple(
        (block, period, arm)
        for block in derive_block_specs(beacon)
        for period in block.periods
        for arm in period.execution_order
    )


def validate_plan(
    plan: dict[str, Any],
    *,
    preregistration: dict[str, Any] | None = None,
    root: str | Path | None = None,
) -> None:
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported blocked replication plan schema")
    if plan.get("preregistration_schema") != PREREGISTRATION_SCHEMA:
        raise ValueError("blocked replication preregistration schema mismatch")
    if plan.get("seed_beacon_merge_sha") != SEED_BEACON_MERGE_SHA:
        raise ValueError("blocked replication seed beacon mismatch")
    if plan.get("arms") != list(ARMS):
        raise ValueError("replication arms must be exactly v1 and v2")
    if plan.get("blocks") != [block.to_dict() for block in derive_block_specs()]:
        raise ValueError("materialized blocks do not match the frozen derivation")
    if plan.get("provider_calls_authorized") is not False:
        raise ValueError("plan must not authorize provider calls")
    if plan.get("spend_authorized") is not False:
        raise ValueError("plan must not authorize spending")
    if plan.get("workflow_present") is not False:
        raise ValueError("plan must not claim a workflow")
    if plan.get("automatic_provider_retries") is not False:
        raise ValueError("plan must forbid automatic provider retries")
    if plan.get("preregistration_path") != PREREGISTRATION_PATH:
        raise ValueError("blocked replication preregistration path mismatch")
    if plan.get("preregistration_sha256") != PREREGISTRATION_SHA256:
        raise ValueError("blocked replication preregistration hash mismatch")
    if (
        plan.get("frozen_reference_implementation_sha256")
        != REFERENCE_IMPLEMENTATION_SHA256
    ):
        raise ValueError("blocked replication implementation hashes mismatch")
    if root is not None:
        validate_reference_implementation(root)

    specs = derive_block_specs()
    world_seeds = [
        period.world_seed for block in specs for period in block.periods
    ]
    customer_seeds = [block.customer_population_seed for block in specs]
    if len(world_seeds) != len(set(world_seeds)):
        raise ValueError("derived world seeds are not unique")
    if len(customer_seeds) != len(set(customer_seeds)):
        raise ValueError("derived customer population seeds are not unique")
    first_counts = {
        arm: sum(
            period.execution_order[0] == arm
            for block in specs
            for period in block.periods
        )
        for arm in ARMS
    }
    if first_counts != {"v1": 12, "v2": 12}:
        raise ValueError("execution order is not exactly balanced")

    design = plan.get("design")
    if not isinstance(design, dict) or any(
        design.get(key) != expected
        for key, expected in {
            "block_count": BLOCK_COUNT,
            "periods_per_block": PERIODS_PER_BLOCK,
            "matched_world_count": BLOCK_COUNT * PERIODS_PER_BLOCK,
            "paid_cell_count": CELL_COUNT,
        }.items()
    ):
        raise ValueError("blocked replication dimensions do not match")
    budget = plan.get("maximum_budget")
    if not isinstance(budget, dict):
        raise ValueError("maximum budget must be an object")
    if budget.get("cells") != CELL_COUNT:
        raise ValueError("maximum budget must cover all forty-eight cells")
    per_cell = budget.get("per_cell_cost_cap_cents")
    aggregate = budget.get("provider_cost_cap_cents")
    if (
        isinstance(per_cell, bool)
        or not isinstance(per_cell, int)
        or per_cell != 45
        or isinstance(aggregate, bool)
        or not isinstance(aggregate, int)
        or aggregate != CELL_COUNT * per_cell
        or aggregate != 2_160
    ):
        raise ValueError("blocked replication budget does not match frozen cap")
    matched = plan.get("matched_worlds")
    if not isinstance(matched, list) or len(matched) != BLOCK_COUNT * PERIODS_PER_BLOCK:
        raise ValueError("plan must contain twenty-four matched world records")
    expected_coordinates = {
        (block.block_index, period.period_index)
        for block in specs
        for period in block.periods
    }
    observed_coordinates = {
        (record.get("block_index"), record.get("period_index"))
        for record in matched
        if isinstance(record, dict)
    }
    if observed_coordinates != expected_coordinates:
        raise ValueError("matched world coordinates do not match the frozen design")
    if any(
        not isinstance(record, dict)
        or record.get("arms_equal") is not True
        or not isinstance(record.get("exogenous_world_sha256"), str)
        or len(record["exogenous_world_sha256"]) != 64
        for record in matched
    ):
        raise ValueError("matched world evidence is incomplete")
    expected_periods = {
        (block.block_index, period.period_index): (block, period)
        for block in specs
        for period in block.periods
    }
    for record in matched:
        block, period = expected_periods[
            (record["block_index"], record["period_index"])
        ]
        expected_metadata = {
            "customer_population_seed": block.customer_population_seed,
            "world_seed": period.world_seed,
            "execution_order": list(period.execution_order),
        }
        if any(record.get(key) != value for key, value in expected_metadata.items()):
            raise ValueError("matched world metadata does not match derived seeds")
        for hash_field in (
            "standardized_world_sha256",
            "standardized_world_commitment",
            "cost_policy_commitment",
        ):
            value = record.get(hash_field)
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError("matched world commitment evidence is incomplete")
        if record["standardized_world_sha256"] != record[
            "standardized_world_commitment"
        ]:
            raise ValueError("standardized world digest and commitment differ")
    if len({record["cost_policy_commitment"] for record in matched}) != 1:
        raise ValueError("materialized cost policy is not constant across cells")

    if preregistration is not None:
        if preregistration.get("schema_version") != PREREGISTRATION_SCHEMA:
            raise ValueError("unsupported replication preregistration schema")
        comparisons = {
            "arms": "arms",
            "design": "design",
            "frozen_config": "frozen_config",
            "replication_gate": "replication_gate",
            "maximum_budget": "maximum_budget",
            "analysis_constraints": "analysis_constraints",
        }
        for plan_key, prereg_key in comparisons.items():
            if plan.get(plan_key) != preregistration.get(prereg_key):
                raise ValueError(f"materialized plan changes preregistered {plan_key}")
        if preregistration.get("future_seed_beacon", {}).get("domain") != SEED_DOMAIN:
            raise ValueError("preregistered seed domain mismatch")
        if preregistration.get("future_seed_beacon", {}).get("value") is not None:
            raise ValueError("preregistration unexpectedly contains concrete seeds")
        for field in (
            "execution_requires_separate_materialization_review",
            "execution_requires_separate_authorization",
            "provider_calls_authorized",
            "spend_authorized",
            "workflow_present",
            "automatic_provider_retries",
        ):
            if plan.get(field) != preregistration.get(field):
                raise ValueError(f"materialized plan changes preregistered {field}")


WorldFactory = Callable[..., Any]


def materialize_matched_worlds(
    plan: dict[str, Any], world_factory: WorldFactory
) -> tuple[dict[str, object], ...]:
    """Materialize both arms without acting and prove exogenous equality."""

    # Structural validation of the caller-supplied plan occurs before any world
    # construction.  A synthetic placeholder list is permitted only while the
    # deterministic materialization record itself is being computed.
    candidate = json.loads(_canonical_json(plan))
    if not candidate.get("matched_worlds"):
        candidate["matched_worlds"] = [
            {
                "block_index": block.block_index,
                "period_index": period.period_index,
                "customer_population_seed": block.customer_population_seed,
                "world_seed": period.world_seed,
                "execution_order": list(period.execution_order),
                "arms_equal": True,
                "exogenous_world_sha256": "0" * 64,
                "standardized_world_sha256": "0" * 64,
                "standardized_world_commitment": "0" * 64,
                "cost_policy_commitment": "1" * 64,
            }
            for block in derive_block_specs()
            for period in block.periods
        ]
    validate_plan(candidate)
    config = plan["frozen_config"]
    records: list[dict[str, object]] = []
    for block in derive_block_specs():
        for period in block.periods:
            kwargs = {
                "horizon_days": int(config["horizon_days_per_period"]),
                "starting_capital_cents": int(
                    config["starting_capital_cents_per_block"]
                ),
                "customer_population_seed": block.customer_population_seed,
            }
            worlds = {
                arm: world_factory(period.world_seed, **kwargs) for arm in ARMS
            }
            reveals = {arm: world.reveal_world() for arm, world in worlds.items()}
            payloads = {arm: reveal["payload"] for arm, reveal in reveals.items()}
            if payloads["v1"] != payloads["v2"]:
                raise ValueError(
                    f"block {block.block_index} period {period.period_index} "
                    "exogenous world mismatch"
                )
            policies = {
                reveal["cost_policy_commitment"] for reveal in reveals.values()
            }
            if len(policies) != 1:
                raise ValueError("matched cost-policy commitment mismatch")
            records.append(
                {
                    "block_index": block.block_index,
                    "period_index": period.period_index,
                    "customer_population_seed": block.customer_population_seed,
                    "world_seed": period.world_seed,
                    "execution_order": list(period.execution_order),
                    "exogenous_world_sha256": exogenous_world_sha256(
                        payloads["v1"]
                    ),
                    "standardized_world_sha256": canonical_sha256(
                        payloads["v1"]
                    ),
                    "standardized_world_commitment": reveals["v1"][
                        "world_commitment"
                    ],
                    "cost_policy_commitment": next(iter(policies)),
                    "arms_equal": True,
                }
            )
    return tuple(records)
