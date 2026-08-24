"""Draft launch/authorization layer for the hosting-liability tariff
dose-response replication (PR #47 build, .agent-mailbox 20260824-0645).

Mirrors capage/homeostasis_v2_replication_launch.py's shape deliberately:
exact-byte owner confirmation bound to the launch commit, a fixed
authorization file path, spend caps enforced before any provider call, a
one-shot execution guard, and a --validate-only path that never constructs a
provider client. Not shared code with that module on purpose -- same
rationale already established in capage/hosting_liability_replication.py and
capage/hosting_liability_replication_runner.py's docstrings: this experiment
is deliberately decoupled from the V1/V2 signal-comparison machinery, so its
launch layer stays decoupled too rather than coupling two unrelated
experiments' authorization paths together.

Importing this module cannot authorize spending or create a provider client.

Known gap, not papered over: PLAN_PATH below does not exist yet. Unlike the
V2 replication (whose plan/materialization JSON was produced and reviewed in
a dedicated prior PR, #34, before its launch script's tests could exercise
real frozen data), no equivalent materialization PR has been built for this
experiment. capage/hosting_liability_replication_runner.py's own docstring
already flagged this deliberately: a preregistration/plan artifact is
owner-authorization-adjacent and deserves its own explicit review, not a
unilateral addition alongside a runner or launch-script build. This module
therefore cannot pass --validate-only end to end until that plan file exists
and is reviewed; load_frozen_inputs raises FileNotFoundError until then, on
purpose, rather than inventing placeholder frozen data.

Spend caps (per-cell 45 cents, aggregate 2,160 cents) are not decided in this
module -- they are inherited from the equality checks already merged in
capage/hosting_liability_replication_runner.py's ReplicationConfig.from_plan
(PR #47, commit 703f16e). Those numbers match the prior Homeostasis V2
replication's caps under the same frozen token tariff ($2/M input, $10/M
output, valid through 2026-08-31 as of this writing). The preregistration
document (experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md,
Section 6) still marks these caps "to be confirmed against the tariff
actually in effect at launch time" -- that confirmation has not happened here
and is not this module's decision to make.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capage.hosting_liability_replication import (
    CELL_COUNT,
    materialize_matched_worlds,
    validate_balanced_order,
)
from capage.hosting_liability_replication_runner import (
    BlockedTariffReplicationRunner,
    ReplicationConfig,
)


PLAN_PATH = (
    "experiments/sandbox/economic_hosting_liability_tariff_replication_plan_v1.json"
)
AUTHORIZATION_PATH = (
    "experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_AUTHORIZATION.md"
)
CONFIRMATION_PREFIX = "RUN_HOSTING_LIABILITY_TARIFF_REPLICATION_AT_"
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


def load_frozen_inputs(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    plan = json.loads((root_path / PLAN_PATH).read_text(encoding="utf-8"))
    ReplicationConfig.from_plan(plan)
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


def _validate_only(
    plan: dict[str, Any],
    world_factory,
) -> dict[str, Any]:
    config = ReplicationConfig.from_plan(plan)
    validate_balanced_order(config.beacon)
    records = list(
        materialize_matched_worlds(config.beacon, plan["frozen_config"], world_factory)
    )
    if records != plan["matched_worlds"]:
        raise ValueError("matched-world materialization changed before launch")
    return {
        "status": "validated_unpaid",
        "plan_sha256": config.plan_sha256,
        "matched_worlds": len(records),
        "paid_cells_if_later_authorized": CELL_COUNT,
        "per_cell_cost_cap_cents": config.per_cell_cost_cap_cents,
        "aggregate_cost_cap_cents": config.aggregate_cost_cap_cents,
        "tariff_valid_through": config.tariff_valid_through,
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
    plan = load_frozen_inputs(root)
    factories = real_factories(plan)
    client_factory, world_factory, runner_factory, config_factory, continuity = factories
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
    runner = BlockedTariffReplicationRunner(
        plan,
        client_factory(),
        checkpoint_path=args.checkpoint,
        artifact_dir=args.artifact_dir,
        runner_factory=runner_factory,
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
    if result["status"] == "completed":
        analysis = runner.analyze()
        _atomic_json(args.analysis, analysis)
        summary.update(
            {
                "cell_count_by_arm": analysis["cell_count_by_arm"],
                "deployment_authorized": False,
            }
        )
    print(json.dumps(summary, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
