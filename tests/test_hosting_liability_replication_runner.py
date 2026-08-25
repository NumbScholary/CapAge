from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest

from capage.hosting_liability_replication import (
    ARMS,
    CELL_COUNT,
    TARIFF_CENTS_PER_DAY,
    materialize_matched_worlds,
    ordered_cells,
)
from capage.hosting_liability_replication_runner import (
    BlockedTariffReplicationRunner,
    ReplicationConfig,
)
from capage.sandbox import EconomicSandbox, TokenTariff, empty_continuity_state
from capage.sandbox_runner import SandboxRunConfig


BEACON = "c" * 40


class FakeTariffRunner:
    calls = []
    fail_cells = set()
    malformed_action_cells = set()
    malformed_action_cost_units = 3_500_000

    def __init__(self, config, client, *, audit_path, continuity_state):
        self.config = config
        self.audit_path = Path(audit_path)
        self.continuity_state = json.loads(json.dumps(continuity_state))

    def run(self):
        FakeTariffRunner.calls.append(
            {
                "run_name": self.config.run_name,
                "hosting_cost_cents_per_day": self.config.hosting_cost_cents_per_day,
                "starting_capital_cents": self.config.starting_capital_cents,
            }
        )
        if self.config.run_name in FakeTariffRunner.fail_cells:
            raise RuntimeError("synthetic provider interruption")
        if self.config.run_name in FakeTariffRunner.malformed_action_cells:
            # Mirrors the exact shape LiveSandboxRunner.run() returns for an
            # invalid_model_action stop (sandbox_runner.py's own
            # "model requested unknown tool" path) -- .run() returns
            # normally (no exception), but status != "completed", which is
            # exactly the case _validate_result() correctly rejects and
            # that the raw-result persistence fix exists to preserve.
            serialized_config = asdict(self.config)
            serialized_config["tariff"] = asdict(self.config.tariff)
            return {
                "schema_version": "capage-live-sandbox-result-v1",
                "status": "failed",
                "stop_reason": "invalid_model_action",
                "failure": "model requested unknown tool: sandbox_delete_customer",
                "config": serialized_config,
                "decision_count": 3,
                "actual_model_cost_units": FakeTariffRunner.malformed_action_cost_units,
                "actual_model_cost_cents_unrounded": FakeTariffRunner.malformed_action_cost_units / 1_000_000,
                "actual_model_cost_cents_billed": 4,
                "transcript": [],
            }
        world = EconomicSandbox(
            self.config.seed,
            horizon_days=self.config.horizon_days,
            starting_capital_cents=self.config.starting_capital_cents,
            token_tariff=self.config.tariff,
            continuity_state=self.continuity_state,
            customer_population_seed=self.config.customer_population_seed,
            customer_namespace=self.config.customer_namespace,
            market_profile=self.config.market_profile,
            hosting_cost_cents_per_day=self.config.hosting_cost_cents_per_day,
        )
        world.record_model_usage(
            f"{self.config.run_name}-call-001", input_tokens=5_000, output_tokens=0
        )
        while world.day < world.horizon_days:
            world.wait({"days": min(7, world.horizon_days - world.day)})
        self.audit_path.write_text(
            json.dumps({"run_name": self.config.run_name}) + "\n", encoding="utf-8"
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


def fake_config_factory(
    *, tariff_name, input_cents_per_million_tokens, output_cents_per_million_tokens, **kwargs
):
    return SandboxRunConfig(
        **kwargs,
        tariff=TokenTariff(
            tariff_name, input_cents_per_million_tokens, output_cents_per_million_tokens
        ),
    )


def _plan():
    frozen_config = {
        "starting_capital_cents_per_block": 25_000,
        "horizon_days_per_period": 30,
        "max_decisions_per_cell": 25,
        "model": "claude-sonnet-5",
        "effort": "medium",
        "max_output_tokens": 1024,
        "assessor_version": "deterministic-artifact-v2",
        "market_profile": "baseline-v1",
        "token_tariff": {
            "name": "test-tariff",
            "input_cents_per_million_tokens": 200,
            "output_cents_per_million_tokens": 1000,
            "valid_through": "2099-12-31",
        },
    }
    tariff = TokenTariff("test-tariff", 200, 1000)

    def world_factory(seed, **kwargs):
        return EconomicSandbox(seed, token_tariff=tariff, **kwargs)

    matched_worlds = [
        json.loads(json.dumps(record))
        for record in materialize_matched_worlds(
            BEACON, frozen_config, world_factory
        )
    ]
    return {
        "schema_version": "capage-hosting-liability-dose-response-plan-v1",
        "seed_beacon": BEACON,
        "arms": list(ARMS),
        "arm_hosting_cost_cents_per_day": dict(TARIFF_CENTS_PER_DAY),
        "frozen_config": frozen_config,
        "maximum_budget": {
            "cells": CELL_COUNT,
            "per_cell_cost_cap_cents": 45,
            "provider_cost_cap_cents": 2_160,
        },
        "matched_worlds": matched_worlds,
    }


class BlockedTariffReplicationRunnerTests(unittest.TestCase):
    def setUp(self):
        FakeTariffRunner.calls = []
        FakeTariffRunner.fail_cells = set()
        FakeTariffRunner.malformed_action_cells = set()
        FakeTariffRunner.malformed_action_cost_units = 3_500_000
        self.plan = _plan()
        self.tariff = TokenTariff("test-tariff", 200, 1000)

        def world_factory(seed, **kwargs):
            return EconomicSandbox(seed, token_tariff=self.tariff, **kwargs)

        self.world_factory = world_factory

    def runner(self, directory, *, guard=lambda: None):
        return BlockedTariffReplicationRunner(
            self.plan,
            object(),
            checkpoint_path=Path(directory) / "checkpoint.json",
            artifact_dir=Path(directory) / "cells",
            runner_factory=FakeTariffRunner,
            run_config_factory=fake_config_factory,
            world_factory=self.world_factory,
            empty_continuity_factory=empty_continuity_state,
            execution_guard=guard,
        )

    def test_full_run_completes_all_forty_eight_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.runner(directory).run()
        self.assertEqual(state["status"], "completed")
        self.assertEqual(len(state["completed_cells"]), CELL_COUNT)
        self.assertEqual(len(FakeTariffRunner.calls), CELL_COUNT)

    def test_each_arm_receives_its_locked_tariff_value(self):
        with tempfile.TemporaryDirectory() as directory:
            self.runner(directory).run()
        by_arm_tariff = {}
        for call in FakeTariffRunner.calls:
            arm = call["run_name"].rsplit("-", 1)[-1]
            by_arm_tariff.setdefault(arm, set()).add(
                call["hosting_cost_cents_per_day"]
            )
        for arm, tariffs in by_arm_tariff.items():
            self.assertEqual(tariffs, {TARIFF_CENTS_PER_DAY[arm]})

    def test_zero_arm_ends_with_more_capital_than_high_arm(self):
        # Same matched worlds, same model spend per cell (fixed 5000 input
        # tokens/call in the fake runner) -- the only difference between arms
        # is hosting_cost_cents_per_day, so "zero" must end strictly ahead of
        # "high" in aggregate ending capital across its 12 cells.
        with tempfile.TemporaryDirectory() as directory:
            state = self.runner(directory).run()
        totals = {arm: 0 for arm in ARMS}
        for record in state["completed_cells"].values():
            totals[record["arm"]] += record["ending_balance_cents"]
        self.assertGreater(totals["zero"], totals["high"])
        self.assertGreater(totals["low"], totals["medium"])
        self.assertGreater(totals["medium"], totals["high"])

    def test_run_rejects_out_of_range_max_cells_before_any_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            for invalid in (0, -1, CELL_COUNT + 1):
                with self.assertRaisesRegex(ValueError, "max_cells must be between"):
                    runner.run(max_cells=invalid)
            # The guard is at the top of run(): no cell executes on rejection.
            self.assertEqual(FakeTariffRunner.calls, [])

    def test_resume_never_repeats_a_completed_cell(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.runner(directory)
            first.run(max_cells=5)
            self.assertEqual(len(FakeTariffRunner.calls), 5)
            second = self.runner(directory)
            state = second.run()
        self.assertEqual(state["status"], "completed")
        self.assertEqual(len(FakeTariffRunner.calls), CELL_COUNT)
        self.assertEqual(len(state["completed_cells"]), CELL_COUNT)

    def test_ambiguous_uncheckpointed_attempt_stops_run(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            runner.run(max_cells=1)
            first_cell = next(iter(runner.state["completed_cells"].values()))
            # Simulate a stray artifact from a prior interrupted attempt for
            # the *next* cell, before it's ever been checkpointed as completed.
            second = self.runner(directory)
            next_stem = None
            for block, period, arm in ordered_cells(BEACON):
                cell_id = f"block-{block.block_index:02d}:period-{period.period_index:02d}:{arm}"
                if cell_id not in second.state["completed_cells"]:
                    next_stem = f"hosting-liability-dose-response-b{block.block_index:02d}-p{period.period_index:02d}-{arm}"
                    break
            (Path(directory) / "cells" / f"{next_stem}-attempt.json").write_text(
                "{}", encoding="utf-8"
            )
            state = second.run()
        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "ambiguous_uncheckpointed_attempt")

    def test_provider_error_is_not_retried_silently(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            block, period, arm = next(iter(ordered_cells(BEACON)))
            failing_stem = f"hosting-liability-dose-response-b{block.block_index:02d}-p{period.period_index:02d}-{arm}"
            FakeTariffRunner.fail_cells = {failing_stem}
            state = runner.run()
        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "provider_or_runner_error")
        self.assertEqual(len(state["errors"]), 1)
        error = state["errors"][0]
        # runner.run() raised before returning any result at all -- the
        # cell's real cost is genuinely unrecoverable, not just zero, and
        # must be marked as such rather than silently treated as free.
        self.assertIsNone(error["raw_actual_model_cost_units"])
        self.assertFalse(error["cost_counted_toward_aggregate"])
        self.assertEqual(state["model_cost_units"], 0)

    def test_checkpoint_with_failed_cell_cost_reloads_without_error(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            block, period, arm = next(iter(ordered_cells(BEACON)))
            failing_stem = f"hosting-liability-dose-response-b{block.block_index:02d}-p{period.period_index:02d}-{arm}"
            FakeTariffRunner.malformed_action_cells = {failing_stem}
            runner.run()
            # Constructing a second runner against the same checkpoint file
            # forces _load_or_initialize -> _validate_checkpoint_state to
            # recompute and compare the aggregate; this must not raise.
            reloaded = self.runner(directory)
        self.assertEqual(reloaded.state["model_cost_units"], 3_500_000)

    def test_failed_cell_cost_can_trip_the_aggregate_cap_on_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            block, period, arm = next(iter(ordered_cells(BEACON)))
            failing_stem = f"hosting-liability-dose-response-b{block.block_index:02d}-p{period.period_index:02d}-{arm}"
            FakeTariffRunner.malformed_action_cells = {failing_stem}
            # A single failed cell whose real cost leaves less than one
            # cent of headroom against the locked 2160-cent aggregate cap --
            # this is the "failure cascade" scenario the fix closes: without
            # counting this cost, a resumed run would still believe it has
            # nearly the full cap left to spend.
            FakeTariffRunner.malformed_action_cost_units = 2_159_500_000
            state = runner.run()
            self.assertEqual(state["model_cost_units"], 2_159_500_000)
            calls_before = len(FakeTariffRunner.calls)
            resumed = self.runner(directory)
            state = resumed.run()
        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "aggregate_model_cost_cap_reached")
        # No further provider call was attempted once the cap was tripped.
        self.assertEqual(len(FakeTariffRunner.calls), calls_before)

    def test_malformed_action_result_is_persisted_raw_before_validation_rejects_it(self):
        # Synthetic reproduction of the real 2026-08-24 cell-6 failure class
        # (block-01 period-02 zero, run 32710531510): the underlying
        # sandbox run returns normally with status != "completed" rather
        # than raising -- exercises the persistence fix without any real
        # provider call. If this alone explains what a genuine
        # invalid_model_action-shaped failure looks like end to end, that's
        # useful confirmation on its own, independent of whatever the real
        # cell 6 failure specifically was.
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            block, period, arm = next(iter(ordered_cells(BEACON)))
            failing_stem = f"hosting-liability-dose-response-b{block.block_index:02d}-p{period.period_index:02d}-{arm}"
            FakeTariffRunner.malformed_action_cells = {failing_stem}
            state = runner.run()
            raw_path = Path(directory) / "cells" / f"{failing_stem}-raw.json"
            official_path = Path(directory) / "cells" / f"{failing_stem}.json"
            # Read everything needed before the temp directory is cleaned
            # up on exiting this "with" block.
            raw_exists = raw_path.exists()
            official_exists = official_path.exists()
            raw_content = json.loads(raw_path.read_text()) if raw_exists else None
        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["stop_reason"], "provider_or_runner_error")
        self.assertEqual(len(state["errors"]), 1)
        error = state["errors"][0]
        self.assertEqual(error["error"], "cell did not complete")
        self.assertEqual(error["raw_status"], "failed")
        self.assertEqual(error["raw_stop_reason"], "invalid_model_action")
        self.assertIn("unknown tool", error["raw_failure"])
        self.assertEqual(error["raw_result_file"], f"{failing_stem}-raw.json")
        # The failed cell's own cost (real, already billed) must count
        # toward the aggregate cap even though it never completed.
        self.assertEqual(error["raw_actual_model_cost_units"], 3_500_000)
        self.assertTrue(error["cost_counted_toward_aggregate"])
        self.assertEqual(state["model_cost_units"], 3_500_000)
        # The key fix under test: the raw result actually exists on disk
        # with the real diagnostic fields, not just referenced by name.
        self.assertTrue(raw_exists)
        self.assertEqual(raw_content["status"], "failed")
        self.assertEqual(raw_content["stop_reason"], "invalid_model_action")
        self.assertEqual(
            raw_content["failure"], "model requested unknown tool: sandbox_delete_customer"
        )
        # The "official" result file must NOT exist -- only validated
        # results belong there, unchanged from before this fix.
        self.assertFalse(official_exists)

    def test_wrong_arm_set_in_plan_is_rejected(self):
        bad_plan = _plan()
        bad_plan["arms"] = ["only-one-arm"]
        with self.assertRaises(ValueError):
            ReplicationConfig.from_plan(bad_plan)

    def test_wrong_tariff_values_in_plan_are_rejected(self):
        bad_plan = _plan()
        bad_plan["arm_hosting_cost_cents_per_day"] = {
            "zero": 0,
            "low": 99,
            "medium": 45,
            "high": 135,
        }
        with self.assertRaises(ValueError):
            ReplicationConfig.from_plan(bad_plan)

    def test_cell_metrics_present_on_completed_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.runner(directory).run(max_cells=1)
        record = next(iter(state["completed_cells"].values()))
        self.assertIn("metrics", record)
        self.assertIn("tool_token_totals", record["metrics"])
        self.assertIn("action_mix", record["metrics"])

    def test_analyze_groups_cells_by_arm_with_correct_tariffs(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = self.runner(directory)
            runner.run()
            analysis = runner.analyze()
        self.assertEqual(analysis["cell_count_by_arm"], {arm: 12 for arm in ARMS})
        self.assertEqual(
            analysis["arm_hosting_cost_cents_per_day"], dict(TARIFF_CENTS_PER_DAY)
        )


if __name__ == "__main__":
    unittest.main()
