import json
from pathlib import Path
import unittest

from capage.homeostasis_v2_replication import (
    ARMS,
    BLOCK_COUNT,
    CELL_COUNT,
    PERIODS_PER_BLOCK,
    derive_block_specs,
    exogenous_world_sha256,
    materialize_matched_worlds,
    ordered_cells,
    validate_plan,
)
from capage.sandbox import EconomicSandbox, TokenTariff


class BlockedReplicationMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parents[1]
        cls.preregistration = json.loads(
            (
                cls.root
                / "experiments"
                / "sandbox"
                / "economic_homeostasis_v2_replication_prereg_v1.json"
            ).read_text(encoding="utf-8")
        )
        cls.plan = json.loads(
            (
                cls.root
                / "experiments"
                / "sandbox"
                / "economic_homeostasis_v2_replication_plan_v1.json"
            ).read_text(encoding="utf-8")
        )

    def world_factory(self):
        frozen = self.plan["frozen_config"]
        tariff_data = frozen["token_tariff"]
        tariff = TokenTariff(
            tariff_data["name"],
            tariff_data["input_cents_per_million_tokens"],
            tariff_data["output_cents_per_million_tokens"],
        )

        def factory(seed, **kwargs):
            return EconomicSandbox(
                seed,
                token_tariff=tariff,
                market_profile=frozen["market_profile"],
                **kwargs,
            )

        return factory

    def test_plan_preserves_preregistration_and_reference_code(self):
        validate_plan(
            self.plan,
            preregistration=self.preregistration,
            root=self.root,
        )

    def test_seed_derivation_is_unique_and_exactly_balanced(self):
        blocks = derive_block_specs()
        self.assertEqual(len(blocks), BLOCK_COUNT)
        self.assertEqual(len({row.customer_population_seed for row in blocks}), 8)
        world_seeds = [
            period.world_seed for block in blocks for period in block.periods
        ]
        self.assertEqual(len(world_seeds), BLOCK_COUNT * PERIODS_PER_BLOCK)
        self.assertEqual(len(set(world_seeds)), len(world_seeds))
        first_counts = {
            arm: sum(period.execution_order[0] == arm for block in blocks for period in block.periods)
            for arm in ARMS
        }
        self.assertEqual(first_counts, {"v1": 12, "v2": 12})
        self.assertEqual(len(ordered_cells()), CELL_COUNT)

    def test_all_twenty_four_worlds_recompute_exactly(self):
        recomputed = list(
            materialize_matched_worlds(self.plan, self.world_factory())
        )
        self.assertEqual(recomputed, self.plan["matched_worlds"])
        self.assertTrue(all(record["arms_equal"] for record in recomputed))

    def test_exogenous_hash_ignores_only_carried_capital(self):
        block = derive_block_specs()[0]
        period = block.periods[0]
        factory = self.world_factory()
        common = {
            "horizon_days": 30,
            "customer_population_seed": block.customer_population_seed,
        }
        first = factory(period.world_seed, starting_capital_cents=25_000, **common)
        second = factory(period.world_seed, starting_capital_cents=24_123, **common)
        first_payload = first.reveal_world()["payload"]
        second_payload = second.reveal_world()["payload"]
        self.assertNotEqual(first_payload, second_payload)
        self.assertEqual(
            exogenous_world_sha256(first_payload),
            exogenous_world_sha256(second_payload),
        )

    def test_plan_cannot_authorize_execution(self):
        self.assertFalse(self.plan["provider_calls_authorized"])
        self.assertFalse(self.plan["spend_authorized"])
        self.assertFalse(self.plan["workflow_present"])
        self.assertFalse(self.plan["automatic_provider_retries"])
        self.assertEqual(self.plan["maximum_budget"]["provider_cost_cap_cents"], 2_160)


if __name__ == "__main__":
    unittest.main()
