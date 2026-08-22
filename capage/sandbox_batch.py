"""Sequential, aggregate-cost-bounded runner for fresh economic sandbox seeds."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from capage.anthropic_client import AnthropicAPIError, AnthropicMessagesClient
from capage.sandbox import TokenTariff
from capage.sandbox_runner import LiveSandboxRunner, SandboxRunConfig


_COST_UNITS_PER_CENT = 1_000_000


@dataclass(frozen=True)
class SandboxBatchConfig:
    """Frozen choices shared by a sequential set of unscreened seeds."""

    batch_name: str
    seeds: tuple[int, ...]
    aggregate_model_cost_cap_cents: int
    per_seed_model_cost_cap_cents: int
    horizon_days: int
    starting_capital_cents: int
    max_decisions: int
    model: str
    effort: str
    max_output_tokens: int
    tariff: TokenTariff
    assessor_version: str
    tariff_valid_through: str

    def __post_init__(self) -> None:
        if not self.batch_name.strip():
            raise ValueError("batch_name is required")
        if not self.seeds:
            raise ValueError("at least one seed is required")
        if len(self.seeds) != len(set(self.seeds)):
            raise ValueError("batch seeds must be unique")
        if len(self.seeds) > 100:
            raise ValueError("no more than 100 seeds may be batched")
        if self.aggregate_model_cost_cap_cents < 1:
            raise ValueError("aggregate model cost cap must be positive")
        if self.per_seed_model_cost_cap_cents < 1:
            raise ValueError("per-seed model cost cap must be positive")

    @classmethod
    def from_manifest(cls, path: str | Path) -> "SandboxBatchConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != "capage-sandbox-batch-v1":
            raise ValueError("unsupported sandbox batch manifest schema")
        model = payload["model"]
        tariff = payload["token_tariff"]
        return cls(
            batch_name=str(payload["batch_name"]),
            seeds=tuple(int(seed) for seed in payload["seeds"]),
            aggregate_model_cost_cap_cents=int(
                payload["aggregate_model_cost_cap_cents"]
            ),
            per_seed_model_cost_cap_cents=int(
                payload["per_seed_model_cost_cap_cents"]
            ),
            horizon_days=int(payload["horizon_days"]),
            starting_capital_cents=int(payload["starting_capital_cents"]),
            max_decisions=int(payload["max_decisions"]),
            model=str(model["name"]),
            effort=str(model["effort"]),
            max_output_tokens=int(model["max_output_tokens"]),
            tariff=TokenTariff(
                name=str(tariff["name"]),
                input_cents_per_million_tokens=int(
                    tariff["input_cents_per_million_tokens"]
                ),
                output_cents_per_million_tokens=int(
                    tariff["output_cents_per_million_tokens"]
                ),
            ),
            assessor_version=str(payload["assessor_version"]),
            tariff_valid_through=str(payload["tariff_valid_through"]),
        )

    def seed_config(self, index: int, seed_cost_cap_cents: int) -> SandboxRunConfig:
        return SandboxRunConfig(
            run_name=f"{self.batch_name}-seed-{index:03d}",
            seed=self.seeds[index - 1],
            model=self.model,
            effort=self.effort,
            max_output_tokens=self.max_output_tokens,
            max_decisions=self.max_decisions,
            max_run_cost_cents=seed_cost_cap_cents,
            horizon_days=self.horizon_days,
            starting_capital_cents=self.starting_capital_cents,
            tariff=self.tariff,
            assessor_version=self.assessor_version,
            tariff_valid_through=self.tariff_valid_through,
        )


RunnerFactory = Callable[..., LiveSandboxRunner]


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _partial_error_result(runner: Any, exc: Exception) -> dict[str, Any]:
    """Preserve known usage and state without pretending an ambiguous call was free."""

    actual_units = int(getattr(runner, "actual_cost_units", 0))
    transcript = list(getattr(runner, "transcript", []))
    world = getattr(runner, "world", None)
    return {
        "schema_version": "capage-live-sandbox-result-v1",
        "status": "error",
        "stop_reason": "provider_or_runner_error",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "decision_count": len(transcript),
        "actual_model_cost_units_known": actual_units,
        "actual_model_cost_cents_known_unrounded": (
            actual_units / _COST_UNITS_PER_CENT
        ),
        "transcript": transcript,
        "outcome_at_stop": world.outcome() if world is not None else None,
        "world_reveal_at_stop": world.reveal_world() if world is not None else None,
    }


def run_batch(
    config: SandboxBatchConfig,
    client: Any,
    *,
    artifact_dir: str | Path,
    runner_factory: RunnerFactory = LiveSandboxRunner,
) -> dict[str, Any]:
    """Run fresh seeds sequentially under one hard aggregate model-cost ceiling."""

    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    aggregate_cap_units = (
        config.aggregate_model_cost_cap_cents * _COST_UNITS_PER_CENT
    )
    total_known_units = 0
    records: list[dict[str, Any]] = []
    batch_status = "completed"
    stop_reason = "all_seeds_attempted"

    for index, seed in enumerate(config.seeds, start=1):
        remaining_units = aggregate_cap_units - total_known_units
        remaining_whole_cents = remaining_units // _COST_UNITS_PER_CENT
        if remaining_whole_cents < 1:
            stop_reason = "aggregate_model_cost_cap_reached"
            break
        seed_cap = min(
            config.per_seed_model_cost_cap_cents,
            int(remaining_whole_cents),
        )
        seed_config = config.seed_config(index, seed_cap)
        result_path = root / f"{seed_config.run_name}.json"
        audit_path = root / f"{seed_config.run_name}-audit.jsonl"
        runner = runner_factory(seed_config, client, audit_path=audit_path)

        try:
            result = runner.run()
        except Exception as exc:
            result = _partial_error_result(runner, exc)
            known_units = int(getattr(runner, "actual_cost_units", 0))
            total_known_units += known_units
            _write_json(result_path, result)
            records.append(
                {
                    "index": index,
                    "seed": seed,
                    "run_name": seed_config.run_name,
                    "status": "error",
                    "stop_reason": "provider_or_runner_error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "provider_error": isinstance(exc, AnthropicAPIError),
                    "actual_model_cost_units_known": known_units,
                    "result_file": result_path.name,
                    "audit_file": audit_path.name,
                }
            )
            batch_status = "stopped"
            stop_reason = "provider_or_runner_error"
            break

        used_units = int(result["actual_model_cost_units"])
        total_known_units += used_units
        if total_known_units > aggregate_cap_units:
            raise RuntimeError("aggregate model-cost cap was exceeded")
        _write_json(result_path, result)
        records.append(
            {
                "index": index,
                "seed": seed,
                "run_name": seed_config.run_name,
                "status": result["status"],
                "stop_reason": result["stop_reason"],
                "decision_count": result["decision_count"],
                "actual_model_cost_units": used_units,
                "actual_model_cost_cents_unrounded": result[
                    "actual_model_cost_cents_unrounded"
                ],
                "actual_model_cost_cents_billed": result[
                    "actual_model_cost_cents_billed"
                ],
                "outcome": result["outcome"],
                "result_file": result_path.name,
                "audit_file": audit_path.name,
            }
        )

    fully_completed = sum(
        record.get("stop_reason") == "horizon_reached" for record in records
    )
    failed = sum(record.get("status") == "failed" for record in records)
    errors = sum(record.get("status") == "error" for record in records)
    return {
        "schema_version": "capage-sandbox-batch-result-v1",
        "status": batch_status,
        "stop_reason": stop_reason,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "batch_name": config.batch_name,
        "planned_seed_count": len(config.seeds),
        "attempted_seed_count": len(records),
        "fully_completed_seed_count": fully_completed,
        "failed_seed_count": failed,
        "error_seed_count": errors,
        "aggregate_model_cost_cap_cents": (
            config.aggregate_model_cost_cap_cents
        ),
        "aggregate_model_cost_units_known": total_known_units,
        "aggregate_model_cost_cents_known_unrounded": (
            total_known_units / _COST_UNITS_PER_CENT
        ),
        "aggregate_model_cost_cents_known_billed": _ceil_div(
            total_known_units, _COST_UNITS_PER_CENT
        ),
        "remaining_model_cost_budget_cents_unrounded": (
            (aggregate_cap_units - total_known_units) / _COST_UNITS_PER_CENT
        ),
        "seeds": records,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("summary")
    parser.add_argument("--artifact-dir", default="artifacts/sandbox-batch")
    args = parser.parse_args(argv)

    try:
        config = SandboxBatchConfig.from_manifest(args.manifest)
        result = run_batch(
            config,
            AnthropicMessagesClient(),
            artifact_dir=args.artifact_dir,
        )
    except Exception as exc:
        result = {
            "schema_version": "capage-sandbox-batch-result-v1",
            "status": "error",
            "stop_reason": "batch_initialization_error",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    _write_json(args.summary, result)
    print(
        json.dumps(
            {
                key: result.get(key)
                for key in (
                    "status",
                    "stop_reason",
                    "attempted_seed_count",
                    "fully_completed_seed_count",
                    "aggregate_model_cost_cents_known_unrounded",
                    "remaining_model_cost_budget_cents_unrounded",
                )
            },
            sort_keys=True,
        )
    )
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
