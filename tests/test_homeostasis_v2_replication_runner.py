from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from capage.homeostasis import HomeostasisSignal
from capage.homeostasis_v2 import HomeostasisSignalV2
from capage.homeostasis_v2_replication_runner import (
    BlockedReplicationRunner,
    ReplicationConfig,
)
from capage.sandbox import (
    EconomicSandbox,
    TokenTariff,
    empty_continuity_state,
)
from capage.sandbox_runner import SandboxRunConfig


# The frozen tariff is valid through 2026-08-31. Pin a deterministic instant
# inside that window so the suite no longer depends on the real wall clock,
# and a separate instant past expiry to exercise the frozen_tariff_expired gate.
_WITHIN_TARIFF = datetime(2026, 8, 15, tzinfo=timezone.utc)
_PAST_TARIFF = datetime(2026, 9, 30, tzinfo=timezone.utc)


def _fixed_clock(moment):
    return lambda: moment


class FakeCellRunner:
    arm = "unknown"
    calls = []
    fail_arms = set()
    extra_search_arms = set()

    def __init__(
        self,
        config,
        client,
        *,
        audit_path,
        continuity_state,
        homeostasis_signal,
    ):
        self.config = config
        self.audit_path = Path(audit_path)
        self.continuity_state = deepcopy(continuity_state)
        self.homeostasis_signal = homeostasis_signal

    def run(self):
        FakeCellRunner.calls.append(
            {
                "arm": self.arm,
                "run_name": self.config.run_name,
                "starting_capital_cents": self.config.starting_capital_cents,
                "customer_population_seed": self.config.customer_population_seed,
                "continuity_state": deepcopy(self.continuity_state),
                "homeostasis_signal": self.homeostasis_signal,
            }
        )
        if self.arm in FakeCellRunner.fail_arms:
            raise RuntimeError("synthetic provider interruption")
        world = EconomicSandbox(
            self.config.seed,
            horizon_days=self.config.horizon_days,
            starting_capital_cents=self.config.starting_capital_cents,
            token_tariff=self.config.tariff,
            continuity_state=self.continuity_state,
            customer_population_seed=self.config.customer_population_seed,
            customer_namespace=self.config.customer_namespace,
            market_profile=self.config.market_profile,
        )
        if self.arm in FakeCellRunner.extra_search_arms:
            world.search_market({"query": "software", "limit": 1})
        world.record_model_usage(
            f"{self.config.run_name}-call-001",
            input_tokens=5_000,
            output_tokens=0,
        )
        while world.day < world.horizon_days:
            world.wait({"days": min(7, world.horizon_days - world.day)})
        self.audit_path.write_text(
            json.dumps({"run_name": self.config.run_name}) + "\n",
            encoding="utf-8",
        )
        outcome = world.outcome()
        serialized_config = asdict(self.config)
        serialized_config["tariff"] = asdict(self.config.tariff)
        units = outcome["model_api_cost_units"]
        return {
            "schema_version": "capage-live-sandbox-result-v1",
            "status": "completed",
            "stop_reason": "horizon_reached",
            "failure": None,
            "config": serialized_config,
            "decision_count": 0,
            "actual_model_cost_units": units,
            "actual_model_cost_cents_unrounded": units / 1_000_000,
            "actual_model_cost_cents_billed": outcome["model_api_cost_cents"],
            "transcript": [],
            "outcome": outcome,
            "business_continuity": world.continuity_state(),
            "world_reveal": world.reveal_world(),
        }


class FakeV1Runner(FakeCellRunner):
    arm = "v1"


class FakeV2Runner(FakeCellRunner):
    arm = "v2"


def fake_config_factory(
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


class BlockedReplicationRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parents[1]
        cls.plan = json.loads(
            (
                cls.root
                / "experiments"
                / "sandbox"
                / "economic_homeostasis_v2_replication_plan_v1.json"
            ).read_text(encoding="utf-8")
        )
        cls.preregistration = json.loads(
            (
                cls.root
                / "experiments"
                / "sandbox"
                / "economic_homeostasis_v2_replication_prereg_v1.json"
            ).read_text(encoding="utf-8")
        )

    def setUp(self):
        FakeCellRunner.calls = []
        FakeCellRunner.fail_arms = set()
        FakeCellRunner.extra_search_arms = set()

    def runner(self, directory, *, guard=lambda: None, clock=None):
        frozen = self.plan["frozen_config"]
        tariff_data = frozen["token_tariff"]
        tariff = TokenTariff(
            tariff_data["name"],
            tariff_data["input_cents_per_million_tokens"],
            tariff_data["output_cents_per_million_tokens"],
        )

        def world_factory(seed, **kwargs):
            return EconomicSandbox(
                seed,
                token_tariff=tariff,
                market_profile=frozen["market_profile"],
                **kwargs,
            )

        return BlockedReplicationRunner(
            self.plan,
            self.preregistration,
            object(),
            checkpoint_path=Path(directory) / "checkpoint.json",
            artifact_dir=Path(directory) / "cells",
            runner_factories={"v1": FakeV1Runner, "v2": FakeV2Runner},
            run_config_factory=fake_config_factory,
            world_factory=world_factory,
            empty_continuity_factory=empty_continuity_state,
            execution_guard=guard,
            root=self.root,
            clock=clock if clock is not None else _fixed_clock(_WITHIN_TARIFF),
        )

    def test_budget_is_exact_and_materialization_remains_unpaid(self):
        config = ReplicationConfig.from_plan(self.plan)
        self.assertEqual(config.per_cell_cost_cap_cents, 45)
        self.assertEqual(config.aggregate_cost_cap_cents, 2_160)
        self.assertFalse(self.plan["provider_calls_authorized"])
        self.assertFalse(self.plan["spend_authorized"])
        self.assertFalse(self.plan["workflow_present"])

    def test_execution_guard_fails_before_attempt_or_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(
                directory,
                guard=lambda: (_ for _ in ()).throw(ValueError("not authorized")),
            )
            with self.assertRaisesRegex(ValueError, "not authorized"):
                runner.run(max_cells=1)
            self.assertFalse((Path(directory) / "checkpoint.json").exists())
            self.assertEqual(FakeCellRunner.calls, [])

    def test_expired_tariff_stops_before_any_paid_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.runner(
                directory, clock=_fixed_clock(_PAST_TARIFF)
            ).run(max_cells=48)

        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["stop_reason"], "frozen_tariff_expired")
        self.assertEqual(result["completed_cells"], {})
        self.assertEqual(FakeCellRunner.calls, [])

    def test_full_run_resets_blocks_and_preserves_only_own_arm_state(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.runner(directory).run(max_cells=48)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["completed_cells"]), 48)
        self.assertEqual(result["model_cost_units"], 48_000_000)
        self.assertEqual(len(FakeCellRunner.calls), 48)
        for arm, signal_type in (
            ("v1", HomeostasisSignal),
            ("v2", HomeostasisSignalV2),
        ):
            calls = [call for call in FakeCellRunner.calls if call["arm"] == arm]
            self.assertEqual(len(calls), 24)
            self.assertTrue(
                all(isinstance(call["homeostasis_signal"], signal_type) for call in calls)
            )
        for block_index in range(1, 9):
            customer_seed = self.plan["blocks"][block_index - 1][
                "customer_population_seed"
            ]
            for arm in ("v1", "v2"):
                calls = [
                    call
                    for call in FakeCellRunner.calls
                    if call["arm"] == arm
                    and call["customer_population_seed"] == customer_seed
                ]
                self.assertEqual(
                    [call["starting_capital_cents"] for call in calls],
                    [25_000, 24_999, 24_998],
                )
                state = result["blocks"][f"block-{block_index:02d}"]["arms"][arm]
                self.assertEqual(state["balance_cents"], 24_997)

    def test_resume_never_repeats_a_completed_paid_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.runner(directory).run(max_cells=7)
            resumed = self.runner(directory).run(max_cells=48)

        self.assertEqual(first["status"], "paused")
        self.assertEqual(len(first["completed_cells"]), 7)
        self.assertEqual(resumed["status"], "completed")
        self.assertEqual(len(FakeCellRunner.calls), 48)
        self.assertEqual(len({call["run_name"] for call in FakeCellRunner.calls}), 48)

    def test_ambiguous_interruption_is_not_retried(self):
        FakeCellRunner.fail_arms = {"v2"}
        with tempfile.TemporaryDirectory() as directory:
            failed = self.runner(directory).run(max_cells=48)
            FakeCellRunner.fail_arms = set()
            resumed = self.runner(directory).run(max_cells=48)

        self.assertEqual(failed["stop_reason"], "provider_or_runner_error")
        self.assertEqual(resumed["stop_reason"], "ambiguous_uncheckpointed_attempt")
        self.assertEqual(len(FakeCellRunner.calls), 2)

    def test_tampered_result_prevents_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            self.runner(directory).run(max_cells=1)
            result_path = next((Path(directory) / "cells").glob("*.json"))
            while result_path.name.endswith("-attempt.json"):
                result_path = next(
                    path
                    for path in (Path(directory) / "cells").glob("*.json")
                    if not path.name.endswith("-attempt.json")
                )
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            payload["outcome"]["balance_cents"] -= 1
            result_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "artifact mismatch"):
                self.runner(directory)

    def test_identical_valid_arms_pass_only_to_larger_synthetic_test(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            runner.run(max_cells=48)
            analysis = runner.analyze()

        self.assertEqual(
            analysis["classification"],
            "advance_to_another_larger_synthetic_test",
        )
        self.assertTrue(analysis["advance_v2"])
        self.assertFalse(analysis["deployment_authorized"])
        self.assertTrue(all(analysis["gate_criteria"].values()))

    def test_repeatable_caution_is_classified_as_quality_capital_tradeoff(self):
        FakeCellRunner.extra_search_arms = {"v2"}
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            runner.run(max_cells=48)
            analysis = runner.analyze()

        self.assertEqual(analysis["classification"], "quality_capital_tradeoff")
        self.assertFalse(analysis["advance_v2"])
        self.assertLess(
            analysis[
                "summed_block_ending_capital_difference_cents_v2_minus_v1"
            ],
            0,
        )
        self.assertEqual(analysis["v2_not_below_v1_block_count"], 0)

    def test_incomplete_checkpoint_cannot_be_analyzed(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            runner.run(max_cells=1)
            with self.assertRaisesRegex(ValueError, "incomplete replication"):
                runner.analyze()


if __name__ == "__main__":
    unittest.main()
