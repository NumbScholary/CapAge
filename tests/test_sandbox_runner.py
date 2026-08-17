"""Tests for the paid-call boundary and bounded sandbox loop."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from capage.anthropic_client import AnthropicAPIError, AnthropicMessagesClient
from capage.sandbox import TokenTariff
from capage.sandbox_runner import (
    LiveSandboxRunner,
    SandboxRunConfig,
    assess_artifact,
)


class FakeClient:
    def __init__(self, responses, input_tokens=200):
        self.responses = list(responses)
        self.input_tokens = input_tokens
        self.count_calls = 0
        self.message_calls = 0

    def count_tokens(self, request_body):
        assert request_body["tool_choice"]["disable_parallel_tool_use"] is True
        self.count_calls += 1
        return self.input_tokens

    def create_message(self, request_body):
        assert request_body["max_tokens"] == 512
        self.message_calls += 1
        return self.responses.pop(0)


def response(tool_name, arguments, input_tokens=200, output_tokens=50):
    return {
        "id": f"message-{tool_name}",
        "content": [
            {
                "type": "tool_use",
                "id": f"tool-{tool_name}",
                "name": tool_name,
                "input": arguments,
            }
        ],
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
        "stop_reason": "tool_use",
    }


class LiveSandboxRunnerTests(unittest.TestCase):
    def config(self, **overrides):
        values = {
            "run_name": "test-run",
            "seed": 17,
            "model": "claude-sonnet-5",
            "effort": "medium",
            "max_output_tokens": 512,
            "max_decisions": 2,
            "max_run_cost_cents": 75,
            "horizon_days": 7,
            "starting_capital_cents": 25_000,
            "tariff": TokenTariff("test", 200, 1_000),
        }
        values.update(overrides)
        return SandboxRunConfig(**values)

    def test_runner_meters_each_call_and_executes_only_registered_tools(self):
        client = FakeClient(
            [
                response(
                    "sandbox_search_market",
                    {"query": "spreadsheet records inconsistent", "limit": 4},
                ),
                response("sandbox_wait", {"days": 7}),
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            runner = LiveSandboxRunner(
                self.config(), client, audit_path=Path(directory) / "audit.jsonl"
            )
            result = runner.run()

        self.assertEqual(client.message_calls, 2)
        self.assertEqual(result["decision_count"], 2)
        self.assertEqual(result["outcome"]["day"], 7)
        self.assertEqual(result["outcome"]["model_input_tokens"], 400)
        self.assertEqual(result["outcome"]["model_output_tokens"], 100)
        self.assertEqual(
            [item["host_tool_name"] for item in result["transcript"]],
            ["sandbox.search_market", "sandbox.wait"],
        )

    def test_external_cost_cap_blocks_before_any_paid_message(self):
        client = FakeClient([], input_tokens=1_000_000)
        with tempfile.TemporaryDirectory() as directory:
            runner = LiveSandboxRunner(
                self.config(max_run_cost_cents=1),
                client,
                audit_path=Path(directory) / "audit.jsonl",
            )
            result = runner.run()

        self.assertEqual(client.count_calls, 1)
        self.assertEqual(client.message_calls, 0)
        self.assertEqual(result["stop_reason"], "external_model_cost_cap_reached")
        self.assertEqual(result["actual_model_cost_cents_billed"], 0)

    def test_invalid_paid_response_is_metered_and_preserved_without_retry(self):
        invalid = {
            "id": "message-invalid",
            "content": [{"type": "text", "text": "I decline to choose an action."}],
            "usage": {"input_tokens": 200, "output_tokens": 20},
            "stop_reason": "end_turn",
        }
        client = FakeClient([invalid])
        with tempfile.TemporaryDirectory() as directory:
            runner = LiveSandboxRunner(
                self.config(), client, audit_path=Path(directory) / "audit.jsonl"
            )
            result = runner.run()

        self.assertEqual(client.message_calls, 1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stop_reason"], "invalid_model_action")
        self.assertEqual(result["decision_count"], 1)
        self.assertEqual(result["outcome"]["model_input_tokens"], 200)
        self.assertEqual(result["outcome"]["model_output_tokens"], 20)
        self.assertEqual(
            result["transcript"][0]["provider_response"]["id"],
            "message-invalid",
        )

    def test_host_rejects_bounds_removed_from_provider_schema(self):
        client = FakeClient([response("sandbox_wait", {"days": 8})])
        with tempfile.TemporaryDirectory() as directory:
            runner = LiveSandboxRunner(
                self.config(), client, audit_path=Path(directory) / "audit.jsonl"
            )
            result = runner.run()

        self.assertEqual(client.message_calls, 1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stop_reason"], "invalid_model_action")
        self.assertIn("input.days must be at most 7", result["failure"])
        self.assertNotIn("host_tool_name", result["transcript"][0])

    def test_truncated_tool_call_has_distinct_stop_reason(self):
        truncated = response("sandbox_submit_delivery", {"contract_id": "contract-001"})
        truncated["stop_reason"] = "max_tokens"
        truncated["usage"]["output_tokens"] = 512
        client = FakeClient([truncated])
        with tempfile.TemporaryDirectory() as directory:
            runner = LiveSandboxRunner(
                self.config(), client, audit_path=Path(directory) / "audit.jsonl"
            )
            result = runner.run()

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stop_reason"], "model_output_limit_reached")
        self.assertIn("output-token limit", result["failure"])
        self.assertEqual(result["outcome"]["model_output_tokens"], 512)

    def test_artifact_assessor_rewards_relevant_substantive_work(self):
        strong = """# Supplier comparison\n
1. Record each supplier's unit price, minimum order, lead time, and last update.\n
2. Normalize prices to cost per usable component and flag stale quotes.\n
3. Review the table weekly; escalate lead-time increases before the reorder point.\n
- Recommended fields: supplier, component, quantity, unit cost, shipping, lead time.\n
- Decision rule: prefer the lowest landed cost that still meets the required lead time.\n"""
        weak = "Here is some information that may help your business."
        target = "A workshop needs to track supplier prices and lead times."
        strong_score, _ = assess_artifact(
            strong,
            public_need=target,
            promised_scope="Compare supplier prices and recurring material lead times.",
            solution_tags=["supplier_research"],
        )
        weak_score, _ = assess_artifact(
            weak,
            public_need=target,
            promised_scope="Compare supplier prices and recurring material lead times.",
            solution_tags=["supplier_research"],
        )
        self.assertGreaterEqual(strong_score, 70)
        self.assertLess(weak_score, strong_score)

    def test_delivery_is_scored_by_host_after_submission(self):
        artifact = """# Focused guide plan
1. Review the newsletter archive and extract every recurring audience question.
2. Group repeated questions by topic, intent, and reader difficulty.
3. Rank topics by frequency and usefulness, then outline one searchable focused guide.
- Include a plain-language answer, archive references, examples, and next steps.
- Add an index so readers can find the relevant interview or article later.
"""
        client = FakeClient(
            [
                response(
                    "sandbox_search_market",
                    {
                        "query": "newsletter publisher recurring questions archive focused guide",
                        "limit": 5,
                    },
                ),
                response(
                    "sandbox_send_offer",
                    {
                        "signal_id": "signal-007",
                        "price_cents": 100,
                        "promise_days": 3,
                        "scope": "Research the archive and propose a focused guide.",
                        "solution_tags": ["audience_research"],
                    },
                ),
                response("sandbox_wait", {"days": 1}),
                response(
                    "sandbox_submit_delivery",
                    {"contract_id": "contract-001", "artifact": artifact},
                ),
                response(
                    "sandbox_request_feedback", {"contract_id": "contract-001"}
                ),
                response("sandbox_wait", {"days": 1}),
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            runner = LiveSandboxRunner(
                self.config(seed=6, max_decisions=6),
                client,
                audit_path=Path(directory) / "audit.jsonl",
            )
            result = runner.run()

        assessment = result["transcript"][3]["host_assessment"]
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment["assessor_version"], "deterministic-artifact-v1")
        self.assertGreaterEqual(assessment["quality_score"], 70)
        self.assertEqual(result["outcome"]["contracts_paid"], 1)
        self.assertGreater(result["outcome"]["earned_revenue_cents"], 0)


class AnthropicClientTests(unittest.TestCase):
    def test_unsupported_constraints_are_described_but_not_transmitted(self):
        captured = {}

        def successful_urlopen(request, timeout):
            del timeout
            captured["body"] = json.loads(request.data)
            return io.BytesIO(b'{"input_tokens":123}')

        client = AnthropicMessagesClient(
            api_key="secret-test-key", urlopen=successful_urlopen
        )
        original = {
            "model": "claude-sonnet-5",
            "messages": [],
            "tools": [
                {
                    "name": "bounded_tool",
                    "strict": True,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "minimum": 1, "maximum": 10},
                            "label": {"type": "string", "minLength": 1, "maxLength": 20},
                        },
                        "required": ["count", "label"],
                        "additionalProperties": False,
                    },
                }
            ],
        }

        self.assertEqual(client.count_tokens(original), 123)
        transmitted = captured["body"]["tools"][0]["input_schema"]
        serialized = json.dumps(transmitted, sort_keys=True)
        for unsupported in ("minimum", "maximum", "minLength", "maxLength"):
            self.assertNotIn(f'"{unsupported}"', serialized)
        self.assertIn("Must be at least 1", serialized)
        self.assertIn("Must contain at most 20 characters", serialized)
        self.assertIn("minimum", original["tools"][0]["input_schema"]["properties"]["count"])

    def test_http_error_preserves_bounded_detail_and_redacts_key(self):
        api_key = "secret-test-key"
        body = (
            '{"type":"error","error":{"type":"invalid_request_error",'
            '"message":"Unexpected field; secret-test-key must not leak"},'
            '"request_id":"req_test_123"}'
        ).encode("utf-8")

        def failing_urlopen(request, timeout):
            del request, timeout
            raise urllib.error.HTTPError(
                "https://api.anthropic.com/v1/messages/count_tokens",
                400,
                "Bad Request",
                {},
                io.BytesIO(body),
            )

        client = AnthropicMessagesClient(api_key=api_key, urlopen=failing_urlopen)
        with self.assertRaises(AnthropicAPIError) as captured:
            client.count_tokens({"model": "claude-sonnet-5", "messages": []})

        message = str(captured.exception)
        self.assertIn("HTTP 400", message)
        self.assertIn("/v1/messages/count_tokens", message)
        self.assertIn("invalid_request_error", message)
        self.assertIn("Unexpected field", message)
        self.assertIn("request_id=req_test_123", message)
        self.assertNotIn(api_key, message)


if __name__ == "__main__":
    unittest.main()
