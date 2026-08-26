"""Generic, reusable enforcement gate for scoped paid actions.

Design: docs/SCOPED_PAID_ACTION_GATE_V1.md. Importing or running this module
cannot authorize spending or construct a provider client. It re-derives and
verifies, from repository git state, the invariants that the two hand-built
launch gates enforced individually -- driven by a per-action launch manifest
instead of hard-coded constants. Only a later, byte-exact owner authorization
phrase (bound to an exact launch commit and an exact cap) can authorize a run,
and even then only through the ``execute`` subcommand invoked by the reviewed
workflow with the step-scoped secret.

GitHub-merge-method assumption (stated here in prose so it survives a test
refactor). The one-shot binding relies on the authorization PR being merged as
a *true merge commit*, so that ``HEAD`` has exactly two parents and ``HEAD^``
(its first parent) is the audited launch commit the phrase is bound to. A
squash or rebase merge produces a single-parent ``HEAD``; the gate treats that
as a violation and fails closed rather than mis-binding ``HEAD^``. The reviewed
workflow / branch settings must therefore require a merge-commit merge for the
launch branch; the gate enforces the *consequence*, not the repository setting.

Interpretation of ``freeze_merge_sha`` (flagged, see the PR description). The
design document's manifest comment describes this field as "the merge commit of
this manifest's own freeze PR", which cannot literally hold: the manifest is
frozen *by* that merge, so it cannot contain the resulting SHA. The only
self-consistent reading -- and the one matching the working
``MATERIALIZATION_MERGE`` precedent in the homeostasis-v2 launch workflow -- is
that ``freeze_merge_sha`` is the commit the launch branch was cut from: the
audited base sitting exactly one first-parent step below the launch commit,
whose diff to the launch commit is exactly ``expected_freeze_files``. That is
what this gate verifies.

Two frozen constants change only by reviewed code change:

- ``ALLOWED_MODULES``: which entry points a manifest may name. Not a spending
  category -- the whitelist of which code may touch money at all.
- ``DECIMAL_ERROR_BACKSTOP_CENTS``: a decimal-place-typo backstop, NOT a working
  spending cap and NOT an approved ceiling. The real per-action cap is whatever
  the owner's byte-exact phrase encodes; this only stops a mistyped manifest
  from turning e.g. 45 cents into an absurd number.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "capage.scoped_launch_manifest/v1"
ALLOWED_MODULES = frozenset({"capage.hosting_liability_replication_launch"})
DECIMAL_ERROR_BACKSTOP_CENTS = 5000

_TEMPLATE_VARIABLES = frozenset(
    {"{artifact_root}", "{authorization_file}", "{confirmation}", "{launch_commit}"}
)
_PLACEHOLDER_RE = re.compile(r"\{[a-z_]+\}")
_CENTS_RE = re.compile(r"_MAX_(\d+)_CENTS$")
_SHA_RE = re.compile(r"\A[0-9a-f]{40}\Z")  # git commit SHA-1
_SHA256_RE = re.compile(r"\A[0-9a-f]{64}\Z")  # content digest


class GateViolation(Exception):
    """A fail-closed invariant violation. Never raised for a valid launch."""


def _require(condition: Any, message: str) -> None:
    if not condition:
        raise GateViolation(message)


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA_RE.match(value))


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.match(value))


# --------------------------------------------------------------------------- #
# git helpers (dependency-free; the gate shells out to git, nothing else)
# --------------------------------------------------------------------------- #
def _git(root: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise GateViolation(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def _git_bytes(root: str | Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode != 0:
        raise GateViolation(
            f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}"
        )
    return result.stdout


def _tree_mode(root: str | Path, commit: str, path: str) -> str | None:
    """Return the git tree mode for path at commit, or None if absent."""

    result = _git(root, "ls-tree", commit, "--", path, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.split()[0]


def _blob_sha256_at(root: str | Path, commit: str, path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{path}"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise GateViolation(f"pinned input missing at execution commit: {path}")
    return hashlib.sha256(result.stdout).hexdigest()


# --------------------------------------------------------------------------- #
# manifest (the no-git half: reused by validate-only and by preflight)
# --------------------------------------------------------------------------- #
def _parse_expiry(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise GateViolation(f"unparseable validity.expires_utc: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def validate_manifest_shape(manifest: Any) -> None:
    """Check everything that does not require git state. Fail closed."""

    _require(isinstance(manifest, dict), "manifest must be a JSON object")
    _require(manifest.get("schema") == SCHEMA, f"manifest schema must be {SCHEMA}")

    action_id = manifest.get("action_id")
    _require(isinstance(action_id, str) and action_id, "action_id must be a non-empty string")
    _require(
        manifest.get("launch_branch") == f"launch/{action_id}",
        "launch_branch must be launch/<action_id>",
    )
    _require(_is_sha(manifest.get("freeze_merge_sha")), "freeze_merge_sha must be a 40-char lowercase SHA")

    freeze_files = manifest.get("expected_freeze_files")
    _require(
        isinstance(freeze_files, list)
        and freeze_files
        and all(isinstance(name, str) and name for name in freeze_files),
        "expected_freeze_files must be a non-empty list of paths",
    )

    command = manifest.get("command")
    _require(isinstance(command, dict), "command must be an object")
    module = command.get("module")
    _require(module in ALLOWED_MODULES, f"command.module {module!r} is not in ALLOWED_MODULES")
    argv = command.get("argv")
    _require(
        isinstance(argv, list) and all(isinstance(token, str) for token in argv),
        "command.argv must be a list of strings",
    )
    for token in argv:
        for placeholder in _PLACEHOLDER_RE.findall(token):
            _require(
                placeholder in _TEMPLATE_VARIABLES,
                f"argv contains unknown template variable {placeholder}",
            )

    inputs = manifest.get("inputs")
    _require(isinstance(inputs, list) and inputs, "inputs must be a non-empty list")
    for entry in inputs:
        _require(
            isinstance(entry, dict)
            and isinstance(entry.get("path"), str)
            and _is_sha256(entry.get("sha256")),
            "each input needs a path and a 64-char sha256",
        )

    caps = manifest.get("caps")
    _require(isinstance(caps, dict), "caps must be an object")
    cents = caps.get("max_new_spend_cents")
    _require(isinstance(cents, int) and not isinstance(cents, bool) and cents > 0,
             "caps.max_new_spend_cents must be a positive integer")
    _require(
        cents <= DECIMAL_ERROR_BACKSTOP_CENTS,
        f"caps.max_new_spend_cents {cents} exceeds "
        f"DECIMAL_ERROR_BACKSTOP_CENTS {DECIMAL_ERROR_BACKSTOP_CENTS}",
    )

    authorization = manifest.get("authorization")
    _require(isinstance(authorization, dict), "authorization must be an object")
    auth_file = authorization.get("file")
    _require(
        isinstance(auth_file, str) and auth_file.endswith(".md") and "AUTHORIZATION" in auth_file,
        "authorization.file must be an *AUTHORIZATION*.md path",
    )
    template = authorization.get("phrase_template")
    _require(
        isinstance(template, str) and "{launch_commit}" in template,
        "authorization.phrase_template must contain {launch_commit}",
    )
    for placeholder in _PLACEHOLDER_RE.findall(template):
        _require(
            placeholder == "{launch_commit}",
            f"phrase_template contains unexpected placeholder {placeholder}",
        )
    match = _CENTS_RE.search(template)
    _require(match is not None, "phrase_template must end with _MAX_<cents>_CENTS")
    _require(
        int(match.group(1)) == cents,
        "phrase cents disagree with caps.max_new_spend_cents",
    )

    validity = manifest.get("validity")
    _require(
        isinstance(validity, dict) and isinstance(validity.get("expires_utc"), str),
        "validity.expires_utc must be present",
    )
    _parse_expiry(validity["expires_utc"])

    one_shot = manifest.get("one_shot")
    _require(
        isinstance(one_shot, dict) and isinstance(one_shot.get("run_record_path"), str),
        "one_shot.run_record_path must be present",
    )

    _require(manifest.get("provider_calls_authorized") is False,
             "provider_calls_authorized must be false in the manifest")
    _require(manifest.get("spend_authorized") is False,
             "spend_authorized must be false in the manifest")


def load_manifest(path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_manifest_shape(manifest)
    return manifest


def expected_phrase(manifest: dict[str, Any], launch_commit: str) -> str:
    _require(_is_sha(launch_commit), "launch_commit must be a 40-char lowercase SHA")
    return manifest["authorization"]["phrase_template"].replace("{launch_commit}", launch_commit)


def _require_not_expired(manifest: dict[str, Any], now: datetime | None = None) -> None:
    now = now or datetime.now(timezone.utc)
    expiry = _parse_expiry(manifest["validity"]["expires_utc"])
    _require(now <= expiry, f"action expired at {manifest['validity']['expires_utc']}")


# --------------------------------------------------------------------------- #
# preflight (the git half): re-derive every invariant, emit provenance
# --------------------------------------------------------------------------- #
def _launch_commit_from_merge_head(root: str | Path, sha: str) -> str:
    """HEAD must be a true two-parent merge; return its first parent."""

    tokens = _git(root, "rev-list", "--parents", "-n", "1", sha).stdout.split()
    # tokens == [<commit>, <parent1>, <parent2>, ...]
    _require(
        len(tokens) == 3,
        "authorization HEAD is not a two-parent merge commit "
        "(a squash/rebase merge fails closed here rather than mis-binding HEAD^)",
    )
    launch_commit = tokens[1]
    _require(_is_sha(launch_commit), "could not resolve the first-parent launch commit")
    return launch_commit


def preflight(
    root: str | Path,
    sha: str | None = None,
    manifest_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Verify every invariant from git state. Raise GateViolation on any."""

    root = Path(root)
    _require(manifest_path is not None, "a manifest path is required")
    manifest = load_manifest(manifest_path)
    if sha is None:
        sha = _git(root, "rev-parse", "HEAD").stdout.strip()

    # Invariant 4: HEAD is a real merge; launch commit is its first parent.
    launch_commit = _launch_commit_from_merge_head(root, sha)

    auth_file = manifest["authorization"]["file"]

    # Invariant 5: authorization is a regular file (not a symlink), present at
    # HEAD, byte-exact phrase + "\n" (which also makes it exactly one line).
    mode = _tree_mode(root, sha, auth_file)
    _require(mode is not None, f"authorization file absent at HEAD: {auth_file}")
    _require(mode != "120000", "authorization file must not be a symlink")
    phrase = expected_phrase(manifest, launch_commit)
    content = _git_bytes(root, "show", f"{sha}:{auth_file}")
    _require(
        content == (phrase + "\n").encode("utf-8"),
        "authorization file is not the byte-exact phrase followed by a single newline",
    )

    # Invariant 6: the merge adds exactly the one authorization file.
    diff = _git(root, "diff", "--name-status", launch_commit, sha).stdout.strip()
    _require(
        diff == f"A\t{auth_file}",
        f"the authorization merge must add exactly {auth_file} and nothing else",
    )

    # Invariant 7: the authorization file is absent at the launch commit.
    _require(
        _tree_mode(root, launch_commit, auth_file) is None,
        "authorization file must be absent at the launch commit (structural one-shot)",
    )

    # Invariant 8: launch commit is bound to its audited freeze base -- ancestry,
    # exactly one first-parent step, and an exact expected file diff.
    freeze = manifest["freeze_merge_sha"]
    ancestor = _git(root, "merge-base", "--is-ancestor", freeze, launch_commit, check=False)
    _require(ancestor.returncode == 0, "freeze_merge_sha is not an ancestor of the launch commit")
    distance = _git(
        root, "rev-list", "--first-parent", "--count", f"{freeze}..{launch_commit}"
    ).stdout.strip()
    _require(
        distance == "1",
        f"launch commit must be exactly one first-parent step from the freeze base (got {distance})",
    )
    observed = sorted(
        line for line in _git(root, "diff", "--name-only", freeze, launch_commit).stdout.splitlines() if line
    )
    expected = sorted(manifest["expected_freeze_files"])
    _require(observed == expected, f"freeze diff mismatch: expected {expected}, observed {observed}")

    # Invariant 10: pinned input hashes match the blobs at the execution commit.
    input_hashes: dict[str, str] = {}
    for entry in manifest["inputs"]:
        actual = _blob_sha256_at(root, sha, entry["path"])
        _require(actual == entry["sha256"], f"input hash mismatch for {entry['path']}")
        input_hashes[entry["path"]] = actual

    # Defense-in-depth (design doc, layered one-shot #5): the run record must
    # not yet exist. This is NOT the primary one-shot -- that is structural,
    # via the phrase binding to HEAD^ and the authorization file's
    # absence-at-parent (invariants 4/5/6/7), which reject any second execution
    # on the same launch branch regardless of this check. The run record is
    # written by the human-reviewed post-run PR (design doc, lifecycle step 7),
    # not by this gate; it primarily catches a duplicate action_id re-run on a
    # *fresh* branch once that record has merged to the integration line -- a
    # case that already needs a fresh owner phrase. The gate does not commit
    # anything back (every workflow here is contents: read); an automated
    # write-back would require contents: write and is a separate owner decision.
    run_record = manifest["one_shot"]["run_record_path"]
    _require(
        _tree_mode(root, sha, run_record) is None,
        f"run record must be absent at preflight: {run_record}",
    )

    # Invariant 11: not expired at preflight.
    _require_not_expired(manifest, now=now)

    # Invariant 13: provenance.
    return {
        "action_id": manifest["action_id"],
        "execution_commit": sha,
        "launch_commit": launch_commit,
        "freeze_base": freeze,
        "authorization_file": auth_file,
        "authorization_sha256": hashlib.sha256((phrase + "\n").encode("utf-8")).hexdigest(),
        "expected_confirmation": phrase,
        "module": manifest["command"]["module"],
        "max_new_spend_cents": manifest["caps"]["max_new_spend_cents"],
        "decimal_error_backstop_cents": DECIMAL_ERROR_BACKSTOP_CENTS,
        "input_sha256": input_hashes,
        "expires_utc": manifest["validity"]["expires_utc"],
        "provider_calls_authorized": False,
        "spend_authorized": False,
    }


# --------------------------------------------------------------------------- #
# execute: re-run preflight, re-check expiry, copy, then exec the argv (no shell)
# --------------------------------------------------------------------------- #
def _substitute(token: str, substitutions: dict[str, str]) -> str:
    for key, value in substitutions.items():
        token = token.replace(key, value)
    return token


def execute(
    root: str | Path,
    sha: str | None = None,
    manifest_path: str | Path | None = None,
    artifact_root: str | None = None,
    now: datetime | None = None,
    runner: Any = subprocess.run,
) -> int:
    """Run the manifest command after re-verifying every invariant.

    ``runner`` is injectable purely so tests can assert the exact argv without
    executing the paid module; production always uses ``subprocess.run``.
    """

    root = Path(root)
    provenance = preflight(root, sha=sha, manifest_path=manifest_path, now=now)
    manifest = load_manifest(manifest_path)
    _require_not_expired(manifest, now=now)  # re-check immediately before exec

    launch_commit = provenance["launch_commit"]
    if artifact_root is None:
        artifact_root = os.environ.get("ARTIFACT_ROOT") or f"artifacts/{manifest['action_id']}"
    substitutions = {
        "{artifact_root}": artifact_root,
        "{authorization_file}": manifest["authorization"]["file"],
        "{confirmation}": provenance["expected_confirmation"],
        "{launch_commit}": launch_commit,
    }

    pinned = {entry["path"]: entry["sha256"] for entry in manifest["inputs"]}
    for copy in manifest.get("pre_exec_copies", []):
        source = copy["from"]
        _require(source in pinned, f"pre_exec_copy source must be a pinned input: {source}")
        actual = hashlib.sha256((root / source).read_bytes()).hexdigest()
        _require(actual == pinned[source], f"pre_exec_copy source hash mismatch: {source}")
        destination = Path(_substitute(copy["to"], substitutions))
        if not destination.is_absolute():
            # Anchor under the repo root so behaviour does not depend on the
            # process cwd (the workflow runs the gate with cwd == root; the
            # executed module receives the same relative paths and cwd).
            destination = root / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / source, destination)

    argv = [_substitute(token, substitutions) for token in manifest["command"]["argv"]]
    command = [sys.executable, "-m", manifest["command"]["module"], *argv]
    completed = runner(command, cwd=str(root))
    return int(getattr(completed, "returncode", 0) or 0)


# --------------------------------------------------------------------------- #
# validate-only: manifest shape against the working tree, no git, no provider
# --------------------------------------------------------------------------- #
def validate_only(manifest_path: str | Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    return {
        "status": "validated_unpaid",
        "action_id": manifest["action_id"],
        "module": manifest["command"]["module"],
        "max_new_spend_cents": manifest["caps"]["max_new_spend_cents"],
        "decimal_error_backstop_cents": DECIMAL_ERROR_BACKSTOP_CENTS,
        "provider_calls_authorized": False,
        "spend_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scoped paid-action gate")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    preflight_parser = sub.add_parser("preflight", help="verify invariants; no secret in scope")
    preflight_parser.add_argument("--manifest", required=True)
    preflight_parser.add_argument("--sha", default=None)
    preflight_parser.add_argument("--root", default=".")

    execute_parser = sub.add_parser("execute", help="re-verify then run the manifest command")
    execute_parser.add_argument("--manifest", required=True)
    execute_parser.add_argument("--sha", default=None)
    execute_parser.add_argument("--root", default=".")
    execute_parser.add_argument("--artifact-root", default=None)

    validate_parser = sub.add_parser("validate", help="unpaid manifest shape check (no git state)")
    validate_parser.add_argument("--manifest", required=True)

    args = parser.parse_args(argv)
    try:
        if args.subcommand == "preflight":
            print(json.dumps(
                preflight(args.root, sha=args.sha, manifest_path=args.manifest),
                indent=2, sort_keys=True,
            ))
            return 0
        if args.subcommand == "execute":
            return execute(
                args.root, sha=args.sha, manifest_path=args.manifest,
                artifact_root=args.artifact_root,
            )
        if args.subcommand == "validate":
            print(json.dumps(validate_only(args.manifest), sort_keys=True))
            return 0
    except GateViolation as exc:
        print(f"GATE VIOLATION: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
