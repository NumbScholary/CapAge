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

    def test_load_frozen_inputs_fails_closed_when_plan_not_yet_materialized(self):
        # Expected current state, not a bug: this experiment's preregistration
        # has not been merged into the active integration branch yet, so no
        # seed_beacon exists to materialize a plan from (mirrors
        # HOMEOSTASIS_V2_REPLICATION_MATERIALIZATION.md's approach -- the
        # beacon must come from a real merge commit).
        with self.assertRaisesRegex(FileNotFoundError, "does not exist yet"):
            load_frozen_inputs(self.root)

    def test_validate_only_requires_missing_arguments_check_to_run_first(self):
        # main() must reach load_frozen_inputs (and therefore fail closed on
        # the not-yet-materialized plan) before it would ever get to
        # argument-completeness checks for a real (non-validate-only) launch
        # -- validate-only is reachable with no other flags at all.
        with self.assertRaisesRegex(FileNotFoundError, "does not exist yet"):
            launch.main(["--validate-only"])


if __name__ == "__main__":
    unittest.main()
