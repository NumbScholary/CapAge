"""Tests for preregistered, reset memory-transfer evaluation."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from capage.memory import AuditedMemoryStore
from capage.sandbox import EconomicSandbox, TokenTariff, empty_continuity_state
from capage.transfer import (
    TransferConfig,
    TransferPhase,
    TransferRunner,
    current_implementation_commitments,
    derive_transfer_population_seed,
    derive_transfer_seed,
    main,
)


def _canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class FakeTransferCellRunner:
    calls: list[dict] = []
    trained_delta_by_profile = {
        "baseline-v1": 20,
        "transfer-tight-market-v1": 5,
    }
    fail_run_name: str | None = None

    def __init__(
        self,
        config,
        client,
        *,
        audit_path,
        durable_context=None,
        continuity_state=None,
    ):
        del client
        self.config = config
        self.context = deepcopy(durable_context)
        self.continuity = deepcopy(continuity_state)
        self.attempt_path = Path(str(audit_path).replace("-audit.jsonl", "-attempt.json"))

    def run(self):
        if not self.attempt_path.exists():
            raise RuntimeError("attempt marker missing before paid runner")
        type(self).calls.append(
            {
                "run_name": self.config.run_name,
                "seed": self.config.seed,
                "starting_capital_cents": self.config.starting_capital_cents,
                "customer_population_seed": self.config.customer_population_seed,
                "customer_namespace": self.config.customer_namespace,
                "market_profile": self.config.market_profile,
                "context": deepcopy(self.context),
                "continuity": deepcopy(self.continuity),
            }
        )
        if self.config.run_name == type(self).fail_run_name:
            raise RuntimeError("simulated provider failure")
        trained = self.config.run_name.endswith("trained-memory")
        net = (
            type(self).trained_delta_by_profile[self.config.market_profile]
            if trained
            else 0
        )
        expense = 5
        world = EconomicSandbox(
            self.config.seed,
            horizon_days=self.config.horizon_days,
            starting_capital_cents=self.config.starting_capital_cents,
            token_tariff=self.config.tariff,
            continuity_state=self.continuity,
            customer_population_seed=self.config.customer_population_seed,
            customer_namespace=self.config.customer_namespace,
            market_profile=self.config.market_profile,
        )
        return {
            "status": "completed",
            "stop_reason": "horizon_reached",
            "actual_model_cost_units": 1_000_000,
            "outcome": {
                "owner_capital_cents": self.config.starting_capital_cents,
                "balance_cents": self.config.starting_capital_cents + net,
                "earned_revenue_cents": net + expense,
                "expense_cents": expense,
                "net_change_cents": net,
                "offers_sent": 1,
                "contracts_accepted": 1,
                "contracts_paid": 1,
                "contracts_defaulted": 0,
                "contracts_disputed": 0,
                "open_obligations": 0,
            },
            "business_continuity": deepcopy(self.continuity),
            "world_reveal": world.reveal_world(),
        }


class TransferRunnerTests(unittest.TestCase):
    def setUp(self):
        FakeTransferCellRunner.calls = []
        FakeTransferCellRunner.fail_run_name = None
        FakeTransferCellRunner.trained_delta_by_profile = {
            "baseline-v1": 20,
            "transfer-tight-market-v1": 5,
        }

    def config(self, **overrides):
        source_commitment = "a" * 64
        values = {
            "experiment_name": "memory-transfer-test",
            "source_training_config_commitment": source_commitment,
            "source_training_months_per_arm": 2,
            "training_month_seeds": (101, 202),
            "training_customer_population_seed": 303,
            "phases": (
                TransferPhase(
                    "same-distribution",
                    tuple(
                        derive_transfer_seed(
                            source_commitment, "same-distribution", index
                        )
                        for index in range(1, 3)
                    ),
                    derive_transfer_population_seed(
                        source_commitment, "same-distribution"
                    ),
                    "holdout-same-v1",
                    "baseline-v1",
                ),
                TransferPhase(
                    "shifted-market",
                    tuple(
                        derive_transfer_seed(
                            source_commitment, "shifted-market", index
                        )
                        for index in range(1, 3)
                    ),
                    derive_transfer_population_seed(
                        source_commitment, "shifted-market"
                    ),
                    "holdout-shift-v1",
                    "transfer-tight-market-v1",
                ),
            ),
            "experiment_epoch": "2026-03-01T00:00:00+00:00",
            "starting_capital_cents": 25_000,
            "horizon_days": 30,
            "max_decisions_per_cell": 25,
            "per_cell_model_cost_cap_cents": 2,
            "per_condition_model_cost_cap_cents": 8,
            "aggregate_model_cost_cap_cents": 16,
            "model": "claude-sonnet-5",
            "effort": "medium",
            "max_output_tokens": 1024,
            "tariff": TokenTariff("test", 200, 1_000),
            "assessor_version": "deterministic-artifact-v2",
            "freeze_training_memory": True,
            "reset_economic_state_per_cell": True,
            "implementation_commitments": current_implementation_commitments(),
            "python_runtime": "3.12",
        }
        values.update(overrides)
        return TransferConfig(**values)

    def source(self, directory, config=None):
        config = config or self.config()
        directory = Path(directory)
        memory_path = directory / "training-memory.sqlite3"
        with AuditedMemoryStore(memory_path) as memory:
            memory.append_event(
                "month-001",
                "monthly_business_outcome",
                {"net_change_cents": 10},
                occurred_at="2026-01-30T00:00:00+00:00",
            )
            memory.append_event(
                "month-002",
                "monthly_business_outcome",
                {"net_change_cents": 20},
                occurred_at="2026-02-28T00:00:00+00:00",
            )
            memory.assert_memory(
                "strategy-performance",
                "strategy",
                "Test pricing carefully; observed offers and payments are a small sample.",
                tags=["pricing", "offers", "payments", "strategy"],
                evidence_event_ids=["month-001", "month-002"],
                confidence=60,
                occurred_at="2026-02-28T01:00:00+00:00",
            )
            memory_head = memory.head_hash()

        continuity = empty_continuity_state()
        continuity_hash = sha256(
            _canonical_json(continuity).encode("utf-8")
        ).hexdigest()
        arms = {}
        completed = {}
        total_units = 0
        changes = {"control": (10, 20), "memory": (15, 35)}
        for condition in ("control", "memory"):
            balance = 25_000
            months = []
            for month_number, (seed, net) in enumerate(
                zip(config.training_month_seeds, changes[condition]), start=1
            ):
                balance += net
                cell_id = f"month-{month_number:03d}:{condition}"
                record = {
                    "cell_id": cell_id,
                    "arm": condition,
                    "month_number": month_number,
                    "seed": seed,
                    "ending_balance_cents": balance,
                    "net_change_cents": net,
                    "actual_model_cost_units": 1_000_000,
                    "business_continuity_hash": continuity_hash,
                }
                months.append(record)
                completed[cell_id] = record
            arms[condition] = {
                "balance_cents": balance,
                "months_completed": len(months),
                "months": months,
                "business_continuity": continuity,
                "model_cost_units": len(months) * 1_000_000,
            }
            total_units += len(months) * 1_000_000
        checkpoint = {
            "schema_version": "capage-longitudinal-checkpoint-v3",
            "config_commitment": config.source_training_config_commitment,
            "implementation_commitments": {
                path: digest
                for path, digest in config.implementation_commitments
                if path != "capage/transfer.py"
            },
            "status": "completed",
            "memory_head_hash": memory_head,
            "model_cost_units": total_units,
            "arms": arms,
            "completed_cells": completed,
            "summary": {"mean_paired_delta_cents": 10},
        }
        checkpoint_path = directory / "training-checkpoint.json"
        checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
        return checkpoint_path, memory_path

    def runner(self, directory, config=None):
        config = config or self.config()
        source_checkpoint, source_memory = self.source(directory, config)
        return TransferRunner(
            config,
            object(),
            source_checkpoint_path=source_checkpoint,
            source_memory_path=source_memory,
            checkpoint_path=Path(directory) / "transfer-checkpoint.json",
            artifact_dir=Path(directory) / "transfer-artifacts",
            runner_factory=FakeTransferCellRunner,
        )

    def test_equal_reset_cells_expose_frozen_memory_only_to_trained_condition(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            memory_before = Path(runner.source_memory_path).read_bytes()
            state = runner.run()
            memory_after = Path(runner.source_memory_path).read_bytes()

        self.assertEqual(state["status"], "completed")
        self.assertEqual(len(FakeTransferCellRunner.calls), 8)
        self.assertTrue(
            all(call["starting_capital_cents"] == 25_000 for call in FakeTransferCellRunner.calls)
        )
        self.assertTrue(
            all(call["continuity"] == empty_continuity_state() for call in FakeTransferCellRunner.calls)
        )
        trained = [
            call for call in FakeTransferCellRunner.calls if call["run_name"].endswith("trained-memory")
        ]
        controls = [
            call for call in FakeTransferCellRunner.calls if call["run_name"].endswith("no-memory")
        ]
        self.assertTrue(all(call["context"] is not None for call in trained))
        self.assertTrue(all(call["context"] is None for call in controls))
        self.assertEqual(
            {call["context"]["audit_head_hash"] for call in trained},
            {state["source_memory_head_hash"]},
        )
        self.assertEqual(memory_after, memory_before)
        for phase in self.config().phases:
            for seed_index in range(1, len(phase.seeds) + 1):
                left = state["completed_cells"][
                    f"phase:{phase.phase_id}:seed-{seed_index:03d}:no_memory"
                ]
                right = state["completed_cells"][
                    f"phase:{phase.phase_id}:seed-{seed_index:03d}:trained_memory"
                ]
                self.assertEqual(left["world_commitment"], right["world_commitment"])
        self.assertEqual(
            state["summary"]["descriptive_interpretation"],
            "portable_strategy_signal",
        )

    def test_pause_resume_never_repeats_a_paid_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self.config()
            source_checkpoint, source_memory = self.source(directory, config)

            def build():
                return TransferRunner(
                    config,
                    object(),
                    source_checkpoint_path=source_checkpoint,
                    source_memory_path=source_memory,
                    checkpoint_path=Path(directory) / "transfer-checkpoint.json",
                    artifact_dir=Path(directory) / "transfer-artifacts",
                    runner_factory=FakeTransferCellRunner,
                )

            first = build().run(max_cells=3)
            first_cells = set(first["completed_cells"])
            second = build().run()

        self.assertEqual(first["status"], "paused")
        self.assertEqual(second["status"], "completed")
        self.assertEqual(len(FakeTransferCellRunner.calls), 8)
        self.assertEqual(len({call["run_name"] for call in FakeTransferCellRunner.calls}), 8)
        self.assertEqual(len(first_cells), 3)

    def test_orphaned_attempt_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            runner.artifact_dir.mkdir(parents=True)
            first_config = runner.config.cell_config(
                phase=runner.config.phases[0],
                seed_index=1,
                condition="no_memory",
                cost_cap_cents=2,
            )
            (runner.artifact_dir / f"{first_config.run_name}-attempt.json").write_text(
                '{"status":"started"}\n', encoding="utf-8"
            )
            state = runner.run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "ambiguous_uncheckpointed_attempt")
        self.assertEqual(FakeTransferCellRunner.calls, [])

    def test_expired_tariff_stops_before_creating_a_paid_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(
                directory,
                config=self.config(tariff_valid_through="2020-01-01"),
            )
            state = runner.run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "frozen_tariff_expired")
        self.assertEqual(FakeTransferCellRunner.calls, [])
        self.assertEqual(list(runner.artifact_dir.glob("*-attempt.json")), [])

    def test_source_memory_change_stops_before_a_paid_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            with AuditedMemoryStore(runner.source_memory_path) as memory:
                memory.append_event(
                    "late-event",
                    "monthly_business_outcome",
                    {"unexpected": True},
                    occurred_at="2026-03-01T00:00:00+00:00",
                )
            state = runner.run()

        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "source_memory_changed")
        self.assertEqual(FakeTransferCellRunner.calls, [])

    def test_resume_rejects_a_tampered_result_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self.config()
            source_checkpoint, source_memory = self.source(directory, config)

            def build():
                return TransferRunner(
                    config,
                    object(),
                    source_checkpoint_path=source_checkpoint,
                    source_memory_path=source_memory,
                    checkpoint_path=Path(directory) / "transfer-checkpoint.json",
                    artifact_dir=Path(directory) / "transfer-artifacts",
                    runner_factory=FakeTransferCellRunner,
                )

            first = build().run(max_cells=1)
            record = next(iter(first["completed_cells"].values()))
            result_path = Path(directory) / "transfer-artifacts" / record["result_file"]
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["outcome"]["balance_cents"] += 1
            result_path.write_text(json.dumps(result), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "balance equation"):
                build()

    def test_transfer_rejects_internal_source_checkpoint_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self.config()
            source_checkpoint, source_memory = self.source(directory, config)
            checkpoint = json.loads(source_checkpoint.read_text(encoding="utf-8"))
            checkpoint["arms"]["memory"]["balance_cents"] += 1
            source_checkpoint.write_text(json.dumps(checkpoint), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "arm balance mismatch"):
                TransferRunner(
                    config,
                    object(),
                    source_checkpoint_path=source_checkpoint,
                    source_memory_path=source_memory,
                    checkpoint_path=Path(directory) / "transfer-checkpoint.json",
                    artifact_dir=Path(directory) / "transfer-artifacts",
                    runner_factory=FakeTransferCellRunner,
                )

    def test_positive_training_but_failed_same_distribution_flags_overfit(self):
        FakeTransferCellRunner.trained_delta_by_profile = {
            "baseline-v1": -5,
            "transfer-tight-market-v1": 2,
        }
        with tempfile.TemporaryDirectory() as directory:
            state = self.runner(directory).run()

        self.assertEqual(
            state["summary"]["descriptive_interpretation"],
            "simulator_specific_overfit_signal",
        )

    def test_manifest_validates_without_source_artifacts_or_provider(self):
        manifest = (
            Path(__file__).parents[1]
            / "experiments"
            / "sandbox"
            / "transfer_manifest_v1.json"
        )
        self.assertEqual(main([str(manifest), "--validate-only"]), 0)

    def test_manifest_rejects_a_seed_not_produced_by_the_derivation(self):
        phases = (
            TransferPhase(
                "same-distribution",
                (101, 505),
                606,
                "holdout-same-v1",
                "baseline-v1",
            ),
            self.config().phases[1],
        )
        with self.assertRaisesRegex(ValueError, "preregistered derivation"):
            self.config(phases=phases)

    def test_manifest_rejects_a_changed_host_implementation_digest(self):
        commitments = list(current_implementation_commitments())
        commitments[0] = (commitments[0][0], "f" * 64)
        with self.assertRaisesRegex(ValueError, "does not match the frozen manifest"):
            self.config(implementation_commitments=tuple(commitments))


if __name__ == "__main__":
    unittest.main()
