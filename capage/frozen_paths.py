"""Shared primitive for hashing a frozen set of implementation files.

This module owns no path lists itself. Which files matter is inherently
per-experiment (a longitudinal checkpoint freezes a different set than a
transfer holdout), so each caller keeps its own frozen path tuple exactly as
it already exists today. Only the "read these files, sha256 each one,
relative to a root, return a mapping" mechanism is shared, so that
mechanism exists in one place instead of being independently reimplemented
by every caller.

Deliberately excludes capage/homeostasis_v2_replication.py's reference-
implementation constants: that module pins exact hash *values* as permanent
evidence for a specific completed, paid replication run, which is a
materially different (and more sensitive) commitment than the plain
"hash whatever these files currently are" pattern this module supports. See
that module's own module-level comment for why it is handled separately.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Iterable


def repository_root() -> Path:
    """Return the repository root, two levels up from this file."""

    return Path(__file__).resolve().parents[1]


def file_sha256(path: str | Path) -> str:
    """Return the sha256 hex digest of one file, read in fixed-size chunks."""

    digest = sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def path_commitments(
    paths: Iterable[str], *, root: str | Path | None = None
) -> dict[str, str]:
    """Return ``{path: sha256 hex digest}`` for every path, relative to root.

    ``root`` defaults to the repository root, matching every existing call
    site that computed it as ``Path(__file__).resolve().parents[1]``.
    Callers that need an explicit root (as
    ``homeostasis_v2_replication_runner.py`` already does, so it can be
    exercised against a temporary directory in tests) can still pass one.
    """

    root_path = Path(root) if root is not None else repository_root()
    return {path: file_sha256(root_path / path) for path in paths}
