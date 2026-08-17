import unittest

import presentation


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.scenarios = [
            {
                "id": f"E0-T{index:02d}",
                "domain": "test",
                "title": f"Scenario {index}",
                "prompt": f"Question {index}?",
                "success_conditions": ["Answer the question"],
                "applicable_dimensions": ["objective_completion"],
            }
            for index in range(1, 7)
        ]
        self.manifest = {
            "seed": 2026081703,
            "trials_per_scenario": 1,
            "presentation": {
                "judge_count": 2,
                "display_labels": ["response-01", "response-02"],
                "label_scope": "per-scenario-trial",
                "balanced_first_position": True,
            },
        }
        self.candidate_mapping = {
            "private-a": "candidate-01",
            "private-b": "candidate-02",
        }

    def test_each_judge_has_balanced_local_labels(self):
        private = presentation.build_private_presentation(
            self.manifest, self.candidate_mapping, self.scenarios
        )
        for packets in private["judges"].values():
            first_counts = {"candidate-01": 0, "candidate-02": 0}
            for packet in packets:
                first_counts[packet["responses"][0]["opaque_id"]] += 1
            self.assertEqual(first_counts, {"candidate-01": 3, "candidate-02": 3})

    def test_judges_receive_independent_presentations(self):
        private = presentation.build_private_presentation(
            self.manifest, self.candidate_mapping, self.scenarios
        )
        self.assertNotEqual(private["judges"]["judge-a"], private["judges"]["judge-b"])

    def test_bundle_preserves_outputs_and_hides_mapping(self):
        private = presentation.build_private_presentation(
            self.manifest, self.candidate_mapping, self.scenarios
        )
        raw = {"records": []}
        expected = {}
        for scenario in self.scenarios:
            for opaque_id in self.candidate_mapping.values():
                output = f"  verbatim {scenario['id']} {opaque_id}\nsecond line  "
                expected[(scenario["id"], opaque_id)] = output
                raw["records"].append({
                    "scenario_id": scenario["id"],
                    "trial": 1,
                    "opaque_id": opaque_id,
                    "final_status": "ok",
                    "attempts": [{"response": {"output": output}}],
                })
        bundle, template = presentation.build_judge_bundle(
            "judge-a",
            private["judges"]["judge-a"],
            self.scenarios,
            raw,
            "rubric",
            "abc123",
        )
        self.assertNotIn("opaque_id", presentation.structural_keys(bundle))
        self.assertNotIn("opaque_id", presentation.structural_keys(template))
        for packet, private_packet in zip(bundle["packets"], private["judges"]["judge-a"]):
            for response, private_response in zip(packet["responses"], private_packet["responses"]):
                self.assertEqual(
                    response["output"],
                    expected[(packet["scenario_id"], private_response["opaque_id"])],
                )


if __name__ == "__main__":
    unittest.main()
