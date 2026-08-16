import json
import tempfile
import unittest
from pathlib import Path

import runner


class RunnerTests(unittest.TestCase):
    def test_canonical_is_stable(self):
        self.assertEqual(runner.canonical({"b": 2, "a": 1}), b'{"a":1,"b":2}\n')

    def test_selection_requires_thirty_scenarios(self):
        manifest = {
            "protocol_version": "1.0", "seed": 1, "scenario_files": ["scenarios.json"],
            "trials_per_scenario": 1, "timeout_seconds": 10, "max_attempts_per_trial": 1,
            "candidates": [
                {"private_id": str(i), "provider": "p", "model": "m", "model_version": "v",
                 "adapter_command": ["x"], "parameters": {}, "pricing": {}}
                for i in range(2)
            ],
        }
        self.assertIn("selection runs require at least 30 frozen scenarios", runner.validate_manifest(manifest, True))

    def test_template_placeholders_are_rejected(self):
        manifest = {
            "protocol_version": "1.0", "seed": 1, "scenario_files": ["scenarios.json"],
            "trials_per_scenario": 1, "timeout_seconds": 10, "max_attempts_per_trial": 1,
            "candidates": [
                {"private_id": str(i), "provider": "REPLACE_ME", "model": "m", "model_version": "v",
                 "adapter_command": ["x"], "parameters": {}, "pricing": {}}
                for i in range(2)
            ],
        }
        self.assertTrue(any("placeholders" in item for item in runner.validate_manifest(manifest)))

    def test_write_new_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            runner.write_new(path, {"first": True})
            with self.assertRaises(SystemExit):
                runner.write_new(path, {"second": True})


if __name__ == "__main__":
    unittest.main()
