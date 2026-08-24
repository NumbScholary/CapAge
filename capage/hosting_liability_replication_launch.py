"""Merge-bound one-shot launch layer for the hosting-liability tariff
dose-response replication.

Importing this module cannot authorize spending or create a provider client.
A paid run requires the later owner authorization file, an exact
confirmation bound to the audited launch commit, and (unlike
homeostasis_v2_replication_launch.py, whose plan JSON already exists) a
materialized plan file that does not exist yet -- see "What this cannot do
yet" below.

Structurally mirrors homeostasis_v2_replication_launch.py's safety pattern
(byte-exact merge-bound confirmation phrase, one-shot execution guard,
pre-call spend caps, fail-closed on ambiguity) with two deliberate
differences: a single runner_factory rather than a per-arm dict (this
experiment has no signal-variant axis, see
hosting_liability_replication_runner.py's own module docstring), and no
frozen historical-run constant to validate the plan against, since there is
no completed prior run of this specific experiment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capage.hosting_liability_replication import (
    AGGREGATE_COST_CAP_CENTS,
    CELL_COUNT,
    materialize_matched_worlds,
    validate_plan,
)
from capage.hosting_liability_replication_runner import (
    BlockedTariffReplicationRunner,
    ReplicationConfig,
)


PLAN_PATH = "experiments/sandbox/hosting_liability_tariff_replication_plan_v1.json"
PREREGISTRATION_PATH = (
    "experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md"
)
AUTHORIZATION_PATH = (
    "experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_AUTHORIZATION.md"
)
CONFIRMATION_PREFIX = "RUN_HOSTING_LIABILITY_TARIFF_REPLICATION_AT_"
CONFIRMATION_SUFFIX = f"_MAX_{AGGREGATE_COST_CAP_CENTS}_CENTS"
_COST_UNITS_PER_CENT = 1_000_000


def _commit_sha(value: str) -> str:
    if (
        len(value) != 40
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError("launch commit must be a lowercase forty-character SHA")
    return value


def expected_confirmation(launch_commit: str) -> str:
    """Return the only confirmation that can authorize this launch commit."""

    return f"{CONFIRMATION_PREFIX}{_commit_sha(launch_commit)}{CONFIRMATION_SUFFIX}"


def verify_authorization(
    root: str | Path,
    authorization_file: str | Path,
    confirmation: str,
    launch_commit: str,
) -> None:
    """Fail closed unless a byte-exact, merge-bound owner statement is present."""

    root_path = Path(root).resolve()
    expected_path = root_path / AUTHORIZATION_PATH
    candidate = Path(authorization_file)
    if not candidate.is_absolute():
        candidate = root_path / candidate
    if candidate.is_symlink() or candidate.resolve() != expected_path.resolve():
        raise ValueError("authorization must use the fixed repository path")
    expected = expected_confirmation(launch_commit)
    if confirmation != expected:
        raise ValueError("exact merge-bound paid-run confirmation is required")
    try:
        content = candidate.read_bytes()
    except FileNotFoundError as exc:
        raise ValueError("later owner authorization file is absent") from exc
    if content != (expected + "\n").encode("utf-8"):
        raise ValueError("owner authorization file is not byte-exact")


class OneShotExecutionGuard:
    """Validate authorization once and reject a second execution in-process."""

    def __init__(
        self,
        root: str | Path,
        authorization_file: str | Path,
        confirmation: str,
        launch_commit: str,
    ) -> None:
        self.root = Path(root)
        self.authorization_file = Path(authorization_file)
        self.confirmation = confirmation
        self.launch_commit = launch_commit
        self._used = False

    def validate(self) -> None:
        verify_authorization(
            self.root,
            self.authorization_file,
            self.confirmation,
            self.launch_commit,
        )

    def __call__(self) -> None:
        if self._used:
            raise RuntimeError("one-shot execution guard has already been consumed")
        self.validate()
        self._used = True


def load_frozen_inputs(root: str | Path) -> dict[str, Any]:
    """Load and validate the materialized plan.

    Raises FileNotFoundError with a clear message if the plan has not been
    materialized yet -- see this module's docstring and README/mailbox for
    why that's expected right now, not a bug.
    """

    root_path = Path(root)
    plan_file = root_path / PLAN_PATH
    if not plan_file.exists():
        raise FileNotFoundError(
            f"{PLAN_PATH} does not exist yet -- this experiment's preregistration "
            "has not been merged into the active integration branch, so no "
            "seed_beacon exists to materialize matched worlds from. See "
            "hosting_liability_replication.py's docstring: the beacon must come "
            "from a real, reviewed merge commit (mirroring "
            "HOMEOSTASIS_V2_REPLICATION_MATERIALIZATION.md's approach), not be "
            "fabricated ahead of that merge."
        )
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    # No preregistration cross-check here: unlike the V2 replication (which
    # has both a frozen prereg JSON and a plan JSON, cross-validated),
    # HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md is markdown, not a
    # structured document with fields to compare against programmatically.
    # validate_plan()'s internal-consistency checks (arms, budget, blocks
    # reproducing the plan's own seed_beacon) are what's enforced here.
    validate_plan(plan)
    return plan


def real_factories(plan: dict[str, Any]):
    """Build frozen factories without instantiating a provider client."""

    from capage.anthropic_client import AnthropicMessagesClient
    from capage.sandbox import EconomicSandbox, TokenTariff, empty_continuity_state
    from capage.sandbox_runner import LiveSandboxRunner, SandboxRunConfig

    config = ReplicationConfig.from_plan(plan)
    tariff = TokenTariff(
        config.tariff_name,
        config.input_cents_per_million_tokens,
        config.output_cents_per_million_tokens,
    )

    def world_factory(seed, **kwargs):
        return EconomicSandbox(
            seed,
            token_tariff=tariff,
            market_profile=config.market_profile,
            **kwargs,
        )

    def config_factory(
        *,
        tariff_name,
        input_cents_per_million_tokens,
        output_cents_per_million_tokens,
        **kwargs,
    ):
        return SandboxRunConfig(
            **kwargs,
            tariff=TokenTariff(
                tariff_name,
                input_cents_per_million_tokens,
                output_cents_per_million_tokens,
            ),
        )

    return (
        AnthropicMessagesClient,
        world_factory,
        LiveSandboxRunner,
        config_factory,
        empty_continuity_state,
    )


def _atomic_json(path: str | Path, payload: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)


def _validate_only(plan: dict[str, Any], world_factory) -> dict[str, Any]:
    records = list(
        materialize_matched_worlds(
            plan["seed_beacon"], plan["frozen_config"], world_factory
        )
    )
    if records != plan["matched_worlds"]:
        raise ValueError("matched-world materialization changed before launch")
    config = ReplicationConfig.from_plan(plan)
    return {
        "status": "validated_unpaid",
        "matched_worlds": len(records),
        "paid_cells_if_later_authorized": CELL_COUNT,
        "per_cell_cost_cap_cents": config.per_cell_cost_cap_cents,
        "aggregate_cost_cap_cents": config.aggregate_cost_cap_cents,
        "provider_calls_authorized_by_validation": False,
        "spend_authorized_by_validation": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--authorization-file")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--launch-commit", default="")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    plan = load_frozen_inputs(root)
    client_factory, world_factory, runner_class, config_factory, continuity = (
        real_factories(plan)
    )
    if args.validate_only:
        print(json.dumps(_validate_only(plan, world_factory), sort_keys=True))
        return 0

    required = {
        "checkpoint": args.checkpoint,
        "artifact-dir": args.artifact_dir,
        "authorization-file": args.authorization_file,
        "confirm": args.confirm,
        "launch-commit": args.launch_commit,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise SystemExit("paid launch omitted required arguments: " + ", ".join(missing))

    guard = OneShotExecutionGuard(
        root,
        args.authorization_file,
        args.confirm,
        args.launch_commit,
    )
    guard.validate()
    runner = BlockedTariffReplicationRunner(
        plan,
        client_factory(),
        checkpoint_path=args.checkpoint,
        artifact_dir=args.artifact_dir,
        runner_factory=runner_class,
        run_config_factory=config_factory,
        world_factory=world_factory,
        empty_continuity_factory=continuity,
        execution_guard=guard,
    )
    result = runner.run()
    summary = {
        "status": result["status"],
        "stop_reason": result["stop_reason"],
        "completed_cells": len(result["completed_cells"]),
        "model_cost_cents_unrounded": (
            result["model_cost_units"] / _COST_UNITS_PER_CENT
        ),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
