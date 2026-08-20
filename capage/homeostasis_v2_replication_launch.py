"""Merge-bound one-shot launch layer for the blocked V1-versus-V2 replication.

Importing this module cannot authorize spending or create a provider client.  A
paid run requires the later owner authorization file, an exact confirmation
bound to the audited launch commit, and the separately reviewed workflow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capage.homeostasis_v2_replication import (
    CELL_COUNT,
    PREREGISTRATION_PATH,
    materialize_matched_worlds,
    validate_plan,
)
from capage.homeostasis_v2_replication_runner import (
    BlockedReplicationRunner,
    ReplicationConfig,
)


MATERIALIZATION_MERGE_SHA = "ab32d9605c4805551d572259d35056ba56068120"
PLAN_PATH = "experiments/sandbox/economic_homeostasis_v2_replication_plan_v1.json"
AUTHORIZATION_PATH = (
    "experiments/sandbox/HOMEOSTASIS_V2_REPLICATION_AUTHORIZATION.md"
)
CONFIRMATION_PREFIX = "RUN_HOMEOSTASIS_V2_BLOCKED_REPLICATION_AT_"
CONFIRMATION_SUFFIX = "_MAX_2160_CENTS"
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


def load_frozen_inputs(root: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root_path = Path(root)
    plan = json.loads((root_path / PLAN_PATH).read_text(encoding="utf-8"))
    preregistration = json.loads(
        (root_path / PREREGISTRATION_PATH).read_text(encoding="utf-8")
    )
    validate_plan(plan, preregistration=preregistration, root=root_path)
    return plan, preregistration


def real_factories(plan: dict[str, Any]):
    """Build frozen factories without instantiating a provider client."""

    from capage.anthropic_client import AnthropicMessagesClient
    from capage.homeostasis_experiment import make_treatment_runner_class
    from capage.homeostasis_v2_runner import HomeostasisV2SandboxRunner
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
        {
            "v1": make_treatment_runner_class(LiveSandboxRunner),
            "v2": HomeostasisV2SandboxRunner,
        },
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


def _validate_only(
    plan: dict[str, Any],
    world_factory,
) -> dict[str, Any]:
    records = list(materialize_matched_worlds(plan, world_factory))
    if records != plan["matched_worlds"]:
        raise ValueError("matched-world materialization changed before launch")
    config = ReplicationConfig.from_plan(plan)
    return {
        "status": "validated_unpaid",
        "materialization_merge_sha": MATERIALIZATION_MERGE_SHA,
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
    parser.add_argument("--analysis")
    parser.add_argument("--authorization-file")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--launch-commit", default="")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    plan, preregistration = load_frozen_inputs(root)
    factories = real_factories(plan)
    client_factory, world_factory, runners, config_factory, continuity = factories
    if args.validate_only:
        print(json.dumps(_validate_only(plan, world_factory), sort_keys=True))
        return 0

    required = {
        "checkpoint": args.checkpoint,
        "artifact-dir": args.artifact_dir,
        "analysis": args.analysis,
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
    runner = BlockedReplicationRunner(
        plan,
        preregistration,
        client_factory(),
        checkpoint_path=args.checkpoint,
        artifact_dir=args.artifact_dir,
        runner_factories=runners,
        run_config_factory=config_factory,
        world_factory=world_factory,
        empty_continuity_factory=continuity,
        execution_guard=guard,
        root=root,
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
    if result["status"] == "completed":
        analysis = runner.analyze()
        _atomic_json(args.analysis, analysis)
        summary.update(
            {
                "classification": analysis["classification"],
                "advance_v2": analysis["advance_v2"],
                "deployment_authorized": False,
            }
        )
    print(json.dumps(summary, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
