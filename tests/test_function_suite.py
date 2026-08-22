"""Run dependency-free function-style tests under standard-library unittest.

The project intentionally has no runtime or test dependency on pytest.  This
bridge keeps the concise function tests while ensuring GitHub's unittest gate
actually executes them instead of silently importing and skipping them.
"""

from __future__ import annotations

import inspect
from pathlib import Path
import tempfile
import unittest

from tests import test_executor, test_sandbox


class _MonkeyPatch:
    def __init__(self) -> None:
        self._undo: list[tuple[dict, str, bool, object]] = []

    def setitem(self, mapping: dict, key: str, value: object) -> None:
        existed = key in mapping
        previous = mapping.get(key)
        mapping[key] = value
        self._undo.append((mapping, key, existed, previous))

    def close(self) -> None:
        for mapping, key, existed, previous in reversed(self._undo):
            if existed:
                mapping[key] = previous
            else:
                mapping.pop(key, None)


def _unittest_case(function):
    def run_case(self) -> None:
        del self
        parameters = list(inspect.signature(function).parameters)
        with tempfile.TemporaryDirectory() as directory:
            patch = _MonkeyPatch()
            arguments = {}
            if "tmp_path" in parameters:
                arguments["tmp_path"] = Path(directory)
            if "monkeypatch" in parameters:
                arguments["monkeypatch"] = patch
            if set(parameters) != set(arguments):
                raise RuntimeError(
                    f"unsupported function-test fixture signature: {parameters}"
                )
            try:
                function(**arguments)
            finally:
                patch.close()

    run_case.__name__ = function.__name__
    run_case.__doc__ = function.__doc__
    return run_case


class FunctionStyleTests(unittest.TestCase):
    """Dynamically populated with every function-style boundary test."""


for _module in (test_executor, test_sandbox):
    for _name, _function in sorted(vars(_module).items()):
        if _name.startswith("test_") and callable(_function):
            setattr(
                FunctionStyleTests,
                f"test_{_module.__name__.rsplit('.', 1)[-1]}__{_name[5:]}",
                _unittest_case(_function),
            )

