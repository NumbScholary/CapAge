"""Tests for multi-seed orchestration and its shared cost boundary."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from capage.anthropic_client import AnthropicAPIError
from capage.sandbox import EconomicSandbox, TokenTariff
from capage.sandbox_batch import SandboxBatchConfig, run_batch


class FakeRunner:
    caps = []
    calls = 0
    error_on_call = None

    def __init__(self, config, client, *, audit_path):
        del client, audit_path
        self.config = config
        self.actual_cost_units = 0
        self.transcript = []
        self.world = EconomicSandbox(
            config.seed,
            horizon_days=config.horizon_days,
            starting_capital_cents=config.starting_capital_cents,
            token_tariff=config.tariff,
        )
        type(self).caps.append(config.max_run_cost_cents)

    def run(self):
        type(self).calls += 1
        if type(self).error_on_call == type(self).calls:
            raise AnthropicAPIError("Anthropic API returned HTTP 402")
        self.actual_cost_units = min(
            23_500_000,
            self.config.max_run_cost_cents * 1_000_000,
        )
        return {
            "status": "completed",
            "stop_reason": "horizon_reached",
            "decision_count": 4,
            "actual_model_cost_units": self.actual_cost_units,
            "actual_model_cost_cents_unrounded": self.actual_cost_units / 1_000_000,
            "actual_model_cost_cents_billed": (
                self.actual_cost_units + 999_999
            ) // 1_000_000,
            "outcome": self.world.outcome(),
        }


class SandboxBatchTests(unittest.TestCase):
    def setUp(self):
        FakeRunner.caps = []
        FakeRunner.calls = 0
        FakeRunner.error_on_call = None

    def config(self, **overrides):
        values = {
            "batch_name": "test-batch",
            "seeds": (11, 22, 33, 44),
            "aggregate_model_cost_cap_cents": 50,
            "per_seed_model_cost_cap_cents": 40,
            "horizon_days": 7,
            "starting_capital_cents": 25_000,
            "max_decisions": 5,
            "model": "claude-sonnet-5",
            "effort": "medium",
            "max_output_tokens": 2048,
            "tariff": TokenTariff("test", 200, 1000),
            "assessor_version": "deterministic-artifact-v1",
            "tariff_valid_through": "",
        }
        values.update(overrides)
        return SandboxBatchConfig(**values)

    def test_shared_cap_reduces_later_seed_allowances(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_batch(
                self.config(),
                object(),
                artifact_dir=directory,
                runner_factory=FakeRunner,
            )

        self.assertEqual(FakeRunner.caps, [40, 26, 3])
        self.assertEqual(result["attempted_seed_count"], 3)
        self.assertEqual(result["stop_reason"], "aggregate_model_cost_cap_reached")
        self.assertEqual(result["aggregate_model_cost_units_known"], 50_000_000)
        self.assertLessEqual(
            result["aggregate_model_cost_cents_known_unrounded"],
            result["aggregate_model_cost_cap_cents"],
        )

    def test_provider_error_stops_batch_without_retry(self):
        FakeRunner.error_on_call = 2
        with tempfile.TemporaryDirectory() as directory:
            result = run_batch(
                self.config(aggregate_model_cost_cap_cents=200),
                object(),
                artifact_dir=directory,
                runner_factory=FakeRunner,
            )

        self.assertEqual(FakeRunner.calls, 2)
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["stop_reason"], "provider_or_runner_error")
        self.assertTrue(result["seeds"][1]["provider_error"])
        self.assertIn("HTTP 402", result["seeds"][1]["error"])

    def test_duplicate_seeds_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            self.config(seeds=(11, 11))


if __name__ == "__main__":
    unittest.main()
