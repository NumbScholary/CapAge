"""Pure design primitives for the four-arm hosting-liability tariff replication.

This module derives the preregistered matched worlds and execution order for
the dose-response experiment (tariff level: zero/low/medium/high) from the
seed beacon. It cannot call a provider, execute an agent action, or authorize
spending.

Deliberately separate from capage/homeostasis_v2_replication.py: that module
is built specifically around comparing two homeostasis SIGNAL variants (v1 vs
v2), not an abstract "arm" concept -- BlockedReplicationRunner's arm-specific
signal dispatch (_expected_signal / signal_for_arm_start) has no equivalent
need here, since all four tariff arms use an identical signal/prompt setup
and vary only in hosting_cost_cents_per_day. Reusing that module's arms-agnostic
generic helpers (canonical_sha256, exogenous_world_sha256) where they apply;
not touching or importing anything v1/v2-specific.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable

from capage.homeostasis_v2_replication import (
    canonical_sha256,
    exogenous_world_sha256,
)


SCHEMA_VERSION = "capage-hosting-liability-dose-response-plan-v1"
PREREGISTRATION_SCHEMA = "capage-hosting-liability-dose-response-preregistration-v1"

# Distinct from homeostasis_v2_replication.SEED_DOMAIN on purpose: this
# experiment's seeds must never collide with or be derivable from the V2
# replication's, even though the underlying derivation shape is similar.
SEED_DOMAIN = "capage-hosting-liability-dose-response-v1"

BLOCK_COUNT = 4
PERIODS_PER_BLOCK = 3

# Locked via .agent-mailbox (2026-08-23 15:00/15:30 entries): geometric
# 3x-step tariff spacing, high tier burns ~48.6% of starting capital over
# the full 90-day (4 blocks would be per-arm; each arm sees 4 blocks x 3
# periods = 12 periods = 360 days lifetime, but each INDIVIDUAL cell/period
# is the 30-day unit the tariff-burn math in the proposal was computed
# against per block: 3 periods/block x 30 days = 90 days/block).
ARMS = ("zero", "low", "medium", "high")
TARIFF_CENTS_PER_DAY = {
    "zero": 0,
    "low": 15,
    "medium": 45,
    "high": 135,
}
CELL_COUNT = BLOCK_COUNT * PERIODS_PER_BLOCK * len(ARMS)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def file_sha256(path: str | Path) -> str:
    return sha256(Path(path).read_bytes()).hexdigest()


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
    return sha256(f"{SEED_DOMAIN}|{kind}|{beacon}{suffix}".encode("utf-8")).digest()


@dataclass(frozen=True)
class PeriodSpec:
    block_index: int
    period_index: int
    world_digest_sha256: str
    world_seed: int
    execution_order: tuple[str, str, str, str]

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
    execution_order: tuple[str, str, str, str]
    periods: tuple[PeriodSpec, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "block_index": self.block_index,
            "customer_digest_sha256": self.customer_digest_sha256,
            "customer_population_seed": self.customer_population_seed,
            "execution_order": list(self.execution_order),
            "periods": [period.to_dict() for period in self.periods],
        }


def derive_block_specs(beacon: str) -> tuple[BlockSpec, ...]:
    """Derive four blocks with exactly balanced arm order via a 4x4 Latin square.

    Block count (4) equals arm count (4) by design: a cyclic rotation of the
    arm tuple, one rotation per block, gives every arm each of the four
    ordinal positions (1st/2nd/3rd/4th) exactly once across the four blocks.
    Order is held constant across a block's three periods (rather than also
    rotating within-block) since the four-block rotation alone already
    achieves exact balance -- each arm ends up in each position exactly
    BLOCK_COUNT // len(ARMS) * PERIODS_PER_BLOCK = 1 * 3 = 3 times across the
    whole design (12 periods total, 4 positions x 3 = 12). Which arm starts
    each block's rotation is itself derived from the beacon, not fixed at
    ARMS's own order, so the mapping from block index to starting arm is
    still unpredictable before the beacon exists.
    """

    normalized = _validate_beacon(beacon)
    start_digests = {
        block: _seed_digest("start", normalized, block)
        for block in range(1, BLOCK_COUNT + 1)
    }
    # Rank blocks by digest to decide each block's rotation offset (0..3),
    # each offset used exactly once -- this is what makes the assignment
    # beacon-dependent rather than a fixed block-index-to-offset mapping.
    offset_for_block = {
        block: rank
        for rank, block in enumerate(
            sorted(start_digests, key=lambda block: start_digests[block])
        )
    }
    blocks: list[BlockSpec] = []
    for block in range(1, BLOCK_COUNT + 1):
        offset = offset_for_block[block]
        order = tuple(ARMS[(i + offset) % len(ARMS)] for i in range(len(ARMS)))
        customer_digest = _seed_digest("customer", normalized, block)
        periods: list[PeriodSpec] = []
        for period in range(1, PERIODS_PER_BLOCK + 1):
            world_digest = _seed_digest("world", normalized, block, period)
            periods.append(
                PeriodSpec(
                    block_index=block,
                    period_index=period,
                    world_digest_sha256=world_digest.hex(),
                    world_seed=int.from_bytes(world_digest[:8], "big"),
                    execution_order=order,
                )
            )
        blocks.append(
            BlockSpec(
                block_index=block,
                customer_digest_sha256=customer_digest.hex(),
                customer_population_seed=int.from_bytes(
                    customer_digest[:8], "big"
                ),
                execution_order=order,
                periods=tuple(periods),
            )
        )
    return tuple(blocks)


def ordered_cells(
    beacon: str,
) -> tuple[tuple[BlockSpec, PeriodSpec, str], ...]:
    return tuple(
        (block, period, arm)
        for block in derive_block_specs(beacon)
        for period in block.periods
        for arm in period.execution_order
    )


def validate_balanced_order(beacon: str) -> None:
    """Raise unless every arm appears in every ordinal position exactly
    (BLOCK_COUNT // len(ARMS)) * PERIODS_PER_BLOCK times."""

    specs = derive_block_specs(beacon)
    expected_per_position = (BLOCK_COUNT // len(ARMS)) * PERIODS_PER_BLOCK
    position_counts = {arm: [0] * len(ARMS) for arm in ARMS}
    for block in specs:
        for period in block.periods:
            for position, arm in enumerate(period.execution_order):
                position_counts[arm][position] += 1
    for arm, counts in position_counts.items():
        if any(count != expected_per_position for count in counts):
            raise ValueError(
                f"execution order is not exactly balanced for arm {arm!r}: "
                f"{counts}"
            )


WorldFactory = Callable[..., Any]


def materialize_matched_worlds(
    beacon: str,
    frozen_config: dict[str, Any],
    world_factory: WorldFactory,
) -> tuple[dict[str, object], ...]:
    """Materialize all four arms without acting; prove exogenous equality.

    Unlike the V2 replication's equivalent, cost_policy_commitment is
    expected to DIFFER by arm here (hosting_cost_cents_per_day is exactly
    what varies between arms) -- only the exogenous world payload (signals,
    events, seeds) is required to match across arms, not the cost policy.
    """

    validate_balanced_order(beacon)
    specs = derive_block_specs(beacon)
    records: list[dict[str, object]] = []
    for block in specs:
        for period in block.periods:
            kwargs = {
                "horizon_days": int(frozen_config["horizon_days_per_period"]),
                "starting_capital_cents": int(
                    frozen_config["starting_capital_cents_per_block"]
                ),
                "customer_population_seed": block.customer_population_seed,
            }
            worlds = {
                arm: world_factory(
                    period.world_seed,
                    hosting_cost_cents_per_day=TARIFF_CENTS_PER_DAY[arm],
                    **kwargs,
                )
                for arm in ARMS
            }
            reveals = {arm: world.reveal_world() for arm, world in worlds.items()}
            payloads = {arm: reveal["payload"] for arm, reveal in reveals.items()}
            reference_arm = ARMS[0]
            for arm in ARMS[1:]:
                if payloads[arm] != payloads[reference_arm]:
                    raise ValueError(
                        f"block {block.block_index} period {period.period_index} "
                        f"exogenous world mismatch between arm {reference_arm!r} "
                        f"and {arm!r}"
                    )
            policy_commitments = {
                arm: reveal["cost_policy_commitment"] for arm, reveal in reveals.items()
            }
            if len(set(policy_commitments.values())) != len(ARMS):
                raise ValueError(
                    "cost policy commitments must differ across all four tariff "
                    "arms (that is the manipulated variable) -- found a collision"
                )
            records.append(
                {
                    "block_index": block.block_index,
                    "period_index": period.period_index,
                    "customer_population_seed": block.customer_population_seed,
                    "world_seed": period.world_seed,
                    "execution_order": list(period.execution_order),
                    "exogenous_world_sha256": exogenous_world_sha256(
                        payloads[reference_arm]
                    ),
                    "standardized_world_sha256": canonical_sha256(
                        payloads[reference_arm]
                    ),
                    "cost_policy_commitment_by_arm": dict(
                        sorted(policy_commitments.items())
                    ),
                    "arms_exogenously_equal": True,
                }
            )
    return tuple(records)
