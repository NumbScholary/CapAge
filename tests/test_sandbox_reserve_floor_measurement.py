"""Measurement-only reserve-floor instrumentation on EconomicSandbox.

These tests pin the reserve-floor *axis* measurement added for the tariff x
reserve pilot (Overseer work order 2026-08-31): a per-cell count of days on
which the reserve floor throttled hosting collection, plus net-of-arrears
reporting. The instrumentation must never change economics -- a zero-reserve,
zero-hosting construction stays byte-identical on both commitments -- so the
five valid tariff cells from run 32710531510 remain comparable.
"""

import unittest

from capage.sandbox import EconomicSandbox, TokenTariff, aggregate_outcomes


TARIFF = TokenTariff(
    name="anthropic-sonnet-5-introductory-2026-08",
    input_cents_per_million_tokens=200,
    output_cents_per_million_tokens=1000,
)


def _build(**kwargs):
    # Low starting capital + no offers means _collect_hosting_cost is the only
    # per-day ledger effect, so the day-by-day arithmetic below is exact.
    return EconomicSandbox(seed=4242, starting_capital_cents=100, token_tariff=TARIFF, **kwargs)


class ReserveFloorMeasurementTests(unittest.TestCase):
    def test_reserved_output_tokens_convert_to_a_cent_floor(self):
        world = _build(reserved_output_tokens=50_000)
        # 50_000 tokens * 1000 cents/Mtok = 50_000_000 cost units = 50 cents.
        self.assertEqual(world._min_reserve_cents, 50)

    def test_floor_throttles_hosting_and_counts_only_floor_caused_days(self):
        world = _build(hosting_cost_cents_per_day=30, reserved_output_tokens=50_000)
        # Floor = 50c. Day1 pays 30 (bal 100->70, no throttle). Day2 can only
        # take 20 above the floor (bal->50, throttle #1). Days 3-6 sit at the
        # floor collecting 0 each (throttles #2-#5), arrears compounding by 30/day.
        world.wait({"days": 6})
        outcome = world.outcome()
        self.assertEqual(outcome["balance_cents"], 50)
        self.assertEqual(outcome["unpaid_hosting_cents"], 130)
        self.assertEqual(outcome["hosting_floor_throttled_days"], 5)
        self.assertEqual(outcome["net_change_cents"], -50)
        # Net of the deferred arrears the position is far worse than net_change
        # alone suggests -- exactly the confound the Overseer asked to surface.
        self.assertEqual(outcome["net_change_net_of_arrears_cents"], -180)

    def test_zero_floor_insolvency_is_not_counted_as_floor_throttling(self):
        # No reserve: the floor is 0, so any shortfall is raw insolvency, not the
        # floor withholding funds. The throttle counter must stay at zero even
        # though hosting drives the balance to insolvency and accrues arrears.
        world = _build(hosting_cost_cents_per_day=30, reserved_output_tokens=0)
        world.wait({"days": 6})
        outcome = world.outcome()
        self.assertEqual(outcome["hosting_floor_throttled_days"], 0)
        self.assertTrue(outcome["insolvent"])
        self.assertGreater(outcome["unpaid_hosting_cents"], 0)

    def test_zero_reserve_zero_hosting_keeps_both_commitments_byte_identical(self):
        base = EconomicSandbox(seed=7, token_tariff=TARIFF)
        explicit_zero = EconomicSandbox(
            seed=7,
            token_tariff=TARIFF,
            hosting_cost_cents_per_day=0,
            reserved_input_tokens=0,
            reserved_output_tokens=0,
        )
        self.assertEqual(base.world_commitment, explicit_zero.world_commitment)
        self.assertEqual(
            base.cost_policy_commitment, explicit_zero.cost_policy_commitment
        )

    def test_nonzero_reserve_moves_cost_policy_hash_but_not_world_hash(self):
        base = EconomicSandbox(seed=7, token_tariff=TARIFF)
        reserved = EconomicSandbox(
            seed=7, token_tariff=TARIFF, reserved_output_tokens=50_000
        )
        # Reserve is a cost-policy term, not a world term: it must perturb the
        # cost_policy_commitment (item c: the axis legitimately re-commits the
        # policy) while leaving the hidden world untouched.
        self.assertEqual(base.world_commitment, reserved.world_commitment)
        self.assertNotEqual(
            base.cost_policy_commitment, reserved.cost_policy_commitment
        )

    def test_aggregate_reports_net_of_arrears_with_legacy_fallback(self):
        legacy = {"balance_cents": 200, "net_change_cents": -50}
        new_row = {
            "balance_cents": 50,
            "net_change_cents": -50,
            "net_change_net_of_arrears_cents": -180,
            "unpaid_hosting_cents": 130,
            "hosting_floor_throttled_days": 5,
        }
        agg = aggregate_outcomes([legacy, new_row])
        # Legacy row lacks the net-of-arrears key; fallback to its net_change_cents
        # is exact because a run with no hosting tariff carries zero arrears.
        self.assertEqual(agg["net_change_net_of_arrears_cents"]["mean"], -115.0)
        self.assertEqual(agg["total_unpaid_hosting_cents"], 130)
        self.assertEqual(agg["total_hosting_floor_throttled_days"], 5)
        self.assertEqual(agg["loss_rate_net_of_arrears"], 1.0)


if __name__ == "__main__":
    unittest.main()
