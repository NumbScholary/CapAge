from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import capage.hosting_liability_replication_launch as launch
from capage.hosting_liability_replication_launch import (
    AGGREGATE_COST_CAP_CENTS,
    AUTHORIZATION_PATH,
    CONFIRMATION_PREFIX,
    CONFIRMATION_SUFFIX,
    OneShotExecutionGuard,
    expected_confirmation,
    load_frozen_inputs,
    verify_authorization,
)


LAUNCH_COMMIT = "1" * 40


class HostingLiabilityLaunchGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parents[1]

    def _authorized_root(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        path = root / AUTHORIZATION_PATH
        path.parent.mkdir(parents=True)
        phrase = expected_confirmation(LAUNCH_COMMIT)
        path.write_bytes((phrase + "\n").encode("utf-8"))
        return temporary, root, path, phrase

    def test_confirmation_suffix_matches_locked_aggregate_cap(self):
        # 45 cents/cell x 48 cells = 2160 cents, confirmed with Kev
        # (2026-08-24), matching the V2 replication's own numbers exactly.
        self.assertEqual(AGGREGATE_COST_CAP_CENTS, 2_160)
        self.assertEqual(CONFIRMATION_SUFFIX, "_MAX_2160_CENTS")

    def test_confirmation_is_bound_to_exact_launch_commit_and_budget(self):
        phrase = expected_confirmation(LAUNCH_COMMIT)
        self.assertEqual(
            phrase,
            CONFIRMATION_PREFIX + LAUNCH_COMMIT + CONFIRMATION_SUFFIX,
        )
        for invalid in ("", "A" * 40, "0" * 39, "g" * 40):
            with self.assertRaisesRegex(ValueError, "forty-character SHA"):
                expected_confirmation(invalid)

    def test_authorization_must_be_byte_exact_at_fixed_path(self):
        temporary, root, path, phrase = self._authorized_root()
        with temporary:
            verify_authorization(root, path, phrase, LAUNCH_COMMIT)
            path.write_bytes((phrase + "\n\n").encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "byte-exact"):
                verify_authorization(root, path, phrase, LAUNCH_COMMIT)

    def test_wrong_confirmation_and_wrong_path_fail_closed(self):
        temporary, root, path, phrase = self._authorized_root()
        with temporary:
            with self.assertRaisesRegex(ValueError, "merge-bound"):
                verify_authorization(root, path, "wrong", LAUNCH_COMMIT)
            alternate = root / "authorization.md"
            alternate.write_bytes((phrase + "\n").encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "fixed repository path"):
                verify_authorization(root, alternate, phrase, LAUNCH_COMMIT)

    def test_missing_authorization_fails_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            phrase = expected_confirmation(LAUNCH_COMMIT)
            guard = OneShotExecutionGuard(
                directory,
                Path(directory) / AUTHORIZATION_PATH,
                phrase,
                LAUNCH_COMMIT,
            )
            with self.assertRaisesRegex(ValueError, "authorization file is absent"):
                guard()

    def test_guard_cannot_be_consumed_twice(self):
        temporary, root, path, phrase = self._authorized_root()
        with temporary:
            guard = OneShotExecutionGuard(root, path, phrase, LAUNCH_COMMIT)
            guard.validate()
            guard()
            with self.assertRaisesRegex(RuntimeError, "already been consumed"):
                guard()

    def test_cli_rejects_before_provider_client_construction(self):
        client_factory = Mock(side_effect=AssertionError("client constructed"))
        fake_factories = (client_factory, object(), object(), object(), object())
        phrase = expected_confirmation(LAUNCH_COMMIT)
        with (
            patch.object(launch, "real_factories", return_value=fake_factories),
            patch.object(
                launch,
                "load_frozen_inputs",
                return_value={"seed_beacon": "a" * 40},
            ),
            patch.object(
                launch.OneShotExecutionGuard,
                "validate",
                side_effect=ValueError("synthetic authorization rejection"),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "authorization rejection"):
                launch.main(
                    [
                        "--checkpoint",
                        "/tmp/unused-checkpoint.json",
                        "--artifact-dir",
                        "/tmp/unused-cells",
                        "--authorization-file",
                        AUTHORIZATION_PATH,
                        "--confirm",
                        phrase,
                        "--launch-commit",
                        LAUNCH_COMMIT,
                    ]
                )
        client_factory.assert_not_called()

    def test_authorization_path_is_fixed(self):
        self.assertEqual(
            AUTHORIZATION_PATH,
            "experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_AUTHORIZATION.md",
        )

    def test_load_frozen_inputs_loads_the_real_materialized_plan(self):
        # As of 2026-08-24: PR #49 (preregistration) and PR #47 (code) are
        # both merged, and materialization has run against PR #49's own
        # merge commit as the seed beacon -- mirrors
        # HOMEOSTASIS_V2_REPLICATION_MATERIALIZATION.md's approach exactly.
        # This is no longer the "not yet materialized" state.
        plan = load_frozen_inputs(self.root)
        self.assertFalse(plan["provider_calls_authorized"])
        self.assertFalse(plan["spend_authorized"])
        self.assertEqual(plan["maximum_budget"]["provider_cost_cap_cents"], 2_160)
        self.assertEqual(plan["maximum_budget"]["per_cell_cost_cap_cents"], 45)
        self.assertEqual(len(plan["matched_worlds"]), 12)

    def test_validate_only_returns_validated_unpaid_against_the_real_plan(self):
        result = launch.main(["--validate-only"])
        self.assertEqual(result, 0)

    def test_real_factories_recompute_all_matched_worlds_without_provider(self):
        from capage.hosting_liability_replication import materialize_matched_worlds

        plan = load_frozen_inputs(self.root)
        _, world_factory, runner_class, _, _ = launch.real_factories(plan)
        recomputed = [
            dict(r)
            for r in materialize_matched_worlds(
                plan["seed_beacon"], plan["frozen_config"], world_factory
            )
        ]
        self.assertEqual(recomputed, plan["matched_worlds"])
        self.assertIsNotNone(runner_class)


if __name__ == "__main__":
    unittest.main()
