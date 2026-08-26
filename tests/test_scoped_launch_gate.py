"""Tests for capage.scoped_launch_gate.

The git-dependent invariants are exercised against real temporary git repos
built with actual merge commits (see _make_repo), because the whole point of
those checks is faithfulness to git plumbing; mocking git would test nothing.
The shape/manifest invariants are tested directly against the validator, and
execute is tested with an injected runner so the paid module is never run and
no provider client is ever constructed.

Invariant-by-invariant test map (design doc numbering):
  1  trigger shape (launch/** + *AUTHORIZATION*.md)  -> workflow-level, PR-3;
     the gate cross-checks the file via invariants 5/6 below.
  2  no re-run replay (run_attempt==1)               -> workflow-level, PR-3.
  3  no parallel double-fire (concurrency)           -> workflow-level, PR-3.
  4  HEAD is a true two-parent merge; launch=HEAD^   -> test_non_merge_head_*,
                                                         test_happy_path_*
  5  authorization one line, byte-exact, not symlink -> test_auth_not_byte_exact,
                                                         test_auth_symlink_rejected
  6  merge adds exactly the one auth file            -> test_extra_file_in_merge
  7  auth file absent at launch commit               -> structurally subsumed by
     invariant 6 for a one-file merge (documented in test_map notes below);
     retained in code as a defense-in-depth backstop.
  8  launch bound to freeze base (ancestry, 1 step,  -> test_freeze_diff_mismatch,
     exact diff)                                        test_happy_path_provenance
  9  caps declared before auth, metered by runner    -> caps consistency:
     test_cap_disagrees_with_phrase_cents,
     test_cap_over_backstop_rejected
  10 pinned input hashes match                       -> test_input_hash_mismatch
  11 expiry frozen and checkable                     -> test_expired_rejected
  12 evidence on every outcome (if: always())        -> workflow-level, PR-3.
  13 provenance recorded                             -> test_happy_path_provenance
  14 no replay of ambiguous attempt; cost debited    -> runner semantics
     (unchanged; owned/tested by the runner, PR-1 and prior).
  15 read-only perms + hard timeout                  -> workflow-level, PR-3.
  module allowlist                                   -> test_module_not_allowed
  provider/spend flags false                         -> test_flags_must_be_false
  argv template safety                               -> test_unknown_argv_placeholder,
                                                         test_execute_substitutes_argv

Uncertainty stated in prose (also in the module docstring):
- The two-parent-merge binding assumes GitHub merged the authorization PR as a
  merge commit. This is enforced as a consequence (non-merge HEAD fails closed),
  not read from a GitHub setting; the workflow/branch config must require it.
- freeze_merge_sha is interpreted as the launch branch's cut-point base, not the
  "merge commit of this manifest's own freeze PR" (which is impossible: the
  manifest cannot contain the SHA of the merge that freezes it). This matches
  the homeostasis MATERIALIZATION_MERGE precedent.
"""

import hashlib
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import capage.scoped_launch_gate as gate
from capage.scoped_launch_gate import GateViolation


ACTION_ID = "cell6-debug-v1"
PLAN = "experiments/sandbox/plan.json"
SEED = "experiments/sandbox/seed_checkpoint.json"
MANIFEST = "experiments/sandbox/cell6_debug_launch_manifest_v1.json"
AUTH = "experiments/sandbox/CELL6_DEBUG_AUTHORIZATION.md"
RUN_RECORD = "experiments/sandbox/CELL6_DEBUG_RUN_RECORD.md"
PHRASE_TEMPLATE = "RUN_CELL6_DEBUG_AT_{launch_commit}_MAX_45_CENTS"
FUTURE = "2099-12-31T23:59:59Z"


def _g(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write(root, rel, content):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _manifest_dict(base_sha, plan_hash, seed_hash, *, freeze_files=None, expires=FUTURE):
    return {
        "schema": gate.SCHEMA,
        "action_id": ACTION_ID,
        "title": "One-cell debug re-run",
        "launch_branch": f"launch/{ACTION_ID}",
        "freeze_merge_sha": base_sha,
        "expected_freeze_files": freeze_files if freeze_files is not None else sorted([MANIFEST, SEED]),
        "command": {
            "module": "capage.hosting_liability_replication_launch",
            "argv": [
                "--checkpoint", "{artifact_root}/checkpoint.json",
                "--artifact-dir", "{artifact_root}/cells",
                "--authorization-file", "{authorization_file}",
                "--confirm", "{confirmation}",
                "--launch-commit", "{launch_commit}",
                "--max-cells", "1",
            ],
        },
        "pre_exec_copies": [{"from": SEED, "to": "{artifact_root}/checkpoint.json"}],
        "inputs": [
            {"path": PLAN, "sha256": plan_hash},
            {"path": SEED, "sha256": seed_hash},
        ],
        "caps": {
            "max_new_spend_cents": 45,
            "cap_enforcement": "runner per-cell cap 45c x max_cells 1",
            "per_cell_cost_cap_cents": 45,
            "max_cells": 1,
        },
        "validity": {"expires_utc": expires, "tariff_valid_through": "2099-12-31"},
        "authorization": {"file": AUTH, "phrase_template": PHRASE_TEMPLATE},
        "one_shot": {"run_record_path": RUN_RECORD, "must_be_absent_at_preflight": True},
        "artifacts": {"name": "cell6-debug-restricted", "retention_days": 30},
        "timeout_minutes": 60,
        "provider_calls_authorized": False,
        "spend_authorized": False,
    }


def _make_repo(
    root,
    *,
    auth_bytes=None,
    auth_symlink=False,
    extra_auth_files=None,
    run_record_in_tree=False,
):
    """Build a real repo satisfying every invariant on the happy path.

    Layout: A (base = freeze_merge_sha) -> F (launch commit, adds manifest+seed)
    -> merge of an auth-only branch into F == HEAD (two-parent). Knobs introduce
    a single, isolated tamper for negative-case tests.
    """

    _g(root, "init", "-q")
    _g(root, "checkout", "-b", "main")
    _g(root, "config", "user.email", "gate@test")
    _g(root, "config", "user.name", "Gate Test")
    _g(root, "config", "commit.gpgsign", "false")
    _g(root, "config", "core.autocrlf", "false")

    # Commit A: base with the pre-existing pinned plan input.
    plan_bytes = b'{"plan": "frozen"}\n'
    _write(root, PLAN, plan_bytes)
    _g(root, "add", "-A")
    _g(root, "commit", "-q", "-m", "base")
    base_sha = _g(root, "rev-parse", "HEAD")

    # Commit F (launch commit): freeze PR adds the seed + manifest (+ optional
    # run record, kept in expected_freeze_files so only the run-record-absent
    # check is exercised, not the freeze-diff check).
    seed_bytes = b'{"checkpoint": "seed"}\n'
    _write(root, SEED, seed_bytes)
    plan_hash = hashlib.sha256(plan_bytes).hexdigest()
    seed_hash = hashlib.sha256(seed_bytes).hexdigest()
    freeze_files = sorted([MANIFEST, SEED])
    if run_record_in_tree:
        _write(root, RUN_RECORD, "prior run\n")
        freeze_files = sorted([MANIFEST, SEED, RUN_RECORD])
    manifest = _manifest_dict(base_sha, plan_hash, seed_hash, freeze_files=freeze_files)
    _write(root, MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    _g(root, "add", "-A")
    _g(root, "commit", "-q", "-m", "freeze")
    launch_commit = _g(root, "rev-parse", "HEAD")

    # Auth branch: adds only the authorization file, then merge (no-ff) so HEAD
    # is a two-parent merge whose first parent is the launch commit.
    _g(root, "checkout", "-q", "-b", "authpr")
    phrase = PHRASE_TEMPLATE.replace("{launch_commit}", launch_commit)
    if auth_symlink:
        (Path(root) / AUTH).parent.mkdir(parents=True, exist_ok=True)
        (Path(root) / AUTH).symlink_to("elsewhere")
    else:
        if callable(auth_bytes):
            body = auth_bytes(phrase)
        elif auth_bytes is not None:
            body = auth_bytes
        else:
            body = (phrase + "\n").encode("utf-8")
        _write(root, AUTH, body)
    for rel, content in (extra_auth_files or {}).items():
        _write(root, rel, content)
    _g(root, "add", "-A")
    _g(root, "commit", "-q", "-m", "authorize")
    _g(root, "checkout", "-q", "main")
    _g(root, "merge", "--no-ff", "-q", "-m", "merge authorization", "authpr")
    head = _g(root, "rev-parse", "HEAD")

    return {
        "root": root,
        "head": head,
        "launch_commit": launch_commit,
        "base": base_sha,
        "manifest_path": str(Path(root) / MANIFEST),
        "auth": AUTH,
        "phrase": phrase,
        "manifest": manifest,
    }


class ManifestShapeTests(unittest.TestCase):
    """Invariants checkable without git state."""

    def _valid_manifest(self):
        return _manifest_dict("a" * 40, "b" * 64, "c" * 64)

    def test_valid_manifest_passes_shape_and_validate_only(self):
        gate.validate_manifest_shape(self._valid_manifest())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "m.json"
            path.write_text(json.dumps(self._valid_manifest()), encoding="utf-8")
            result = gate.validate_only(path)
        self.assertEqual(result["status"], "validated_unpaid")
        self.assertFalse(result["provider_calls_authorized"])
        self.assertFalse(result["spend_authorized"])
        self.assertEqual(result["decimal_error_backstop_cents"], 5000)

    def test_cap_over_backstop_rejected(self):
        manifest = self._valid_manifest()
        manifest["caps"]["max_new_spend_cents"] = 5001
        manifest["authorization"]["phrase_template"] = "RUN_X_AT_{launch_commit}_MAX_5001_CENTS"
        with self.assertRaisesRegex(GateViolation, "DECIMAL_ERROR_BACKSTOP_CENTS"):
            gate.validate_manifest_shape(manifest)

    def test_cap_disagrees_with_phrase_cents(self):
        manifest = self._valid_manifest()
        manifest["caps"]["max_new_spend_cents"] = 44  # phrase still says 45
        with self.assertRaisesRegex(GateViolation, "phrase cents disagree"):
            gate.validate_manifest_shape(manifest)

    def test_module_not_allowed(self):
        manifest = self._valid_manifest()
        manifest["command"]["module"] = "capage.some_other_module"
        with self.assertRaisesRegex(GateViolation, "ALLOWED_MODULES"):
            gate.validate_manifest_shape(manifest)

    def test_flags_must_be_false(self):
        for field in ("provider_calls_authorized", "spend_authorized"):
            manifest = self._valid_manifest()
            manifest[field] = True
            with self.assertRaisesRegex(GateViolation, "must be false"):
                gate.validate_manifest_shape(manifest)

    def test_unknown_argv_placeholder(self):
        manifest = self._valid_manifest()
        manifest["command"]["argv"] = ["--secret", "{api_key}"]
        with self.assertRaisesRegex(GateViolation, "unknown template variable"):
            gate.validate_manifest_shape(manifest)

    def test_bool_cap_is_not_accepted_as_int(self):
        manifest = self._valid_manifest()
        manifest["caps"]["max_new_spend_cents"] = True
        with self.assertRaisesRegex(GateViolation, "positive integer"):
            gate.validate_manifest_shape(manifest)


class PreflightGitTests(unittest.TestCase):
    def test_happy_path_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory)
            provenance = gate.preflight(
                repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"]
            )
        self.assertEqual(provenance["launch_commit"], repo["launch_commit"])
        self.assertEqual(provenance["freeze_base"], repo["base"])
        self.assertEqual(provenance["execution_commit"], repo["head"])
        self.assertEqual(provenance["expected_confirmation"], repo["phrase"])
        self.assertEqual(provenance["max_new_spend_cents"], 45)
        self.assertFalse(provenance["provider_calls_authorized"])
        self.assertEqual(
            provenance["authorization_sha256"],
            hashlib.sha256((repo["phrase"] + "\n").encode("utf-8")).hexdigest(),
        )

    def test_non_merge_head_fails_closed(self):
        # Pointing at the launch commit (a single-parent commit) simulates a
        # squash/rebase merge: no two-parent HEAD, so HEAD^ cannot be trusted.
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory)
            with self.assertRaisesRegex(GateViolation, "two-parent merge"):
                gate.preflight(
                    repo["root"], sha=repo["launch_commit"], manifest_path=repo["manifest_path"]
                )

    def test_auth_not_byte_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory, auth_bytes=b"NOT THE PHRASE\n")
            with self.assertRaisesRegex(GateViolation, "byte-exact"):
                gate.preflight(repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"])

    def test_auth_trailing_blank_line_rejected(self):
        # The auth body is the correct phrase for this repo's launch commit but
        # with an extra blank line -- must still fail byte-exactness.
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory, auth_bytes=lambda phrase: (phrase + "\n\n").encode("utf-8"))
            with self.assertRaisesRegex(GateViolation, "byte-exact"):
                gate.preflight(repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"])

    def test_auth_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory, auth_symlink=True)
            with self.assertRaisesRegex(GateViolation, "symlink"):
                gate.preflight(repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"])

    def test_extra_file_in_merge(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory, extra_auth_files={"experiments/sandbox/sneaky.txt": "x\n"})
            with self.assertRaisesRegex(GateViolation, "add exactly"):
                gate.preflight(repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"])

    def test_freeze_diff_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory)
            # Tamper the on-disk manifest's expected file list; git diff is real.
            manifest = dict(repo["manifest"])
            manifest["expected_freeze_files"] = [MANIFEST]  # omits SEED
            Path(repo["manifest_path"]).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(GateViolation, "freeze diff mismatch"):
                gate.preflight(repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"])

    def test_input_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory)
            manifest = dict(repo["manifest"])
            manifest["inputs"] = [
                {"path": PLAN, "sha256": "0" * 64},
                {"path": SEED, "sha256": manifest["inputs"][1]["sha256"]},
            ]
            Path(repo["manifest_path"]).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(GateViolation, "input hash mismatch"):
                gate.preflight(repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"])

    def test_run_record_present_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory, run_record_in_tree=True)
            with self.assertRaisesRegex(GateViolation, "run record must be absent"):
                gate.preflight(repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"])

    def test_expired_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory)
            far_future = datetime(2100, 1, 1, tzinfo=timezone.utc)
            with self.assertRaisesRegex(GateViolation, "expired"):
                gate.preflight(
                    repo["root"], sha=repo["head"],
                    manifest_path=repo["manifest_path"], now=far_future,
                )


class ExecuteTests(unittest.TestCase):
    def test_execute_reverifies_then_runs_substituted_argv_without_provider(self):
        calls = {}

        class _Result:
            returncode = 0

        def fake_runner(command, cwd=None):
            calls["command"] = command
            calls["cwd"] = cwd
            return _Result()

        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory)
            code = gate.execute(
                repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"],
                artifact_root="artifacts/run", runner=fake_runner,
            )
            # Assert inside the block: the temp dir (and the copied file) is
            # removed on exit.
            self.assertEqual(code, 0)
            command = calls["command"]
            # module invoked as `python -m <module> ...`, no shell.
            self.assertEqual(command[1:3], ["-m", "capage.hosting_liability_replication_launch"])
            # template variables were substituted; none survive into the argv.
            self.assertIn("artifacts/run/checkpoint.json", command)
            self.assertIn(repo["launch_commit"], command)
            self.assertIn(repo["phrase"], command)
            self.assertNotIn("{artifact_root}", " ".join(command))
            self.assertNotIn("{launch_commit}", " ".join(command))
            # pre_exec_copy performed the hash-verified copy, anchored under root.
            self.assertTrue((Path(directory) / "artifacts/run/checkpoint.json").exists())

    def test_execute_fails_closed_on_tamper_and_never_runs(self):
        ran = {"called": False}

        def fake_runner(command, cwd=None):
            ran["called"] = True

        with tempfile.TemporaryDirectory() as directory:
            repo = _make_repo(directory)
            manifest = dict(repo["manifest"])
            manifest["inputs"] = [
                {"path": PLAN, "sha256": "0" * 64},
                {"path": SEED, "sha256": manifest["inputs"][1]["sha256"]},
            ]
            Path(repo["manifest_path"]).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(GateViolation):
                gate.execute(
                    repo["root"], sha=repo["head"], manifest_path=repo["manifest_path"],
                    runner=fake_runner,
                )
        self.assertFalse(ran["called"])


if __name__ == "__main__":
    unittest.main()
