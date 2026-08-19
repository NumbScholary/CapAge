from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from capage.homeostasis_v2_replication import materialize_matched_worlds
import capage.homeostasis_v2_replication_launch as launch
from capage.homeostasis_v2_replication_launch import (
    AUTHORIZATION_PATH,
    CONFIRMATION_PREFIX,
    CONFIRMATION_SUFFIX,
    MATERIALIZATION_MERGE_SHA,
    OneShotExecutionGuard,
    expected_confirmation,
    load_frozen_inputs,
    real_factories,
    verify_authorization,
)


LAUNCH_COMMIT = "1" * 40


class ReplicationLaunchGateTests(unittest.TestCase):
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
        fake_factories = (client_factory, object(), {}, object(), object())
        phrase = expected_confirmation(LAUNCH_COMMIT)
        with patch.object(launch, "real_factories", return_value=fake_factories):
            with self.assertRaisesRegex(ValueError, "authorization file is absent"):
                launch.main(
                    [
                        "--checkpoint",
                        "/tmp/unused-checkpoint.json",
                        "--artifact-dir",
                        "/tmp/unused-cells",
                        "--analysis",
                        "/tmp/unused-analysis.json",
                        "--authorization-file",
                        AUTHORIZATION_PATH,
                        "--confirm",
                        phrase,
                        "--launch-commit",
                        LAUNCH_COMMIT,
                    ]
                )
        client_factory.assert_not_called()

    def test_launch_pr_contains_no_authorization_file(self):
        self.assertFalse((self.root / AUTHORIZATION_PATH).exists())

    def test_real_factories_recompute_all_frozen_worlds_without_provider(self):
        plan, preregistration = load_frozen_inputs(self.root)
        self.assertFalse(plan["provider_calls_authorized"])
        self.assertFalse(plan["spend_authorized"])
        self.assertEqual(plan["maximum_budget"]["provider_cost_cap_cents"], 2_160)
        factories = real_factories(plan)
        self.assertEqual(set(factories[2]), {"v1", "v2"})
        self.assertEqual(
            list(materialize_matched_worlds(plan, factories[1])),
            plan["matched_worlds"],
        )
        self.assertEqual(
            preregistration["maximum_budget"]["provider_cost_cap_cents"],
            2_160,
        )
        self.assertEqual(
            MATERIALIZATION_MERGE_SHA,
            "ab32d9605c4805551d572259d35056ba56068120",
        )


if __name__ == "__main__":
    unittest.main()
