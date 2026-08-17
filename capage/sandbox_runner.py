"""Bounded Sonnet-in-the-loop runner for CapAge's seeded economic sandbox."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Protocol

from capage.anthropic_client import AnthropicMessagesClient
from capage.audit import AuditLog
from capage.executor import Executor
from capage.models import ProposedAction
from capage.policy import PolicyEngine
from capage.sandbox import EconomicSandbox, TokenTariff


_COST_UNITS_PER_CENT = 1_000_000


class ModelClient(Protocol):
    """Narrow client interface so the paid boundary is testable without a key."""

    def count_tokens(self, request_body: dict[str, Any]) -> int: ...

    def create_message(self, request_body: dict[str, Any]) -> dict[str, Any]: ...


class SandboxRunnerError(RuntimeError):
    """Raised when a run cannot continue without violating a frozen rule."""


@dataclass(frozen=True)
class SandboxRunConfig:
    """All choices that can affect model behavior or attributable cost."""

    run_name: str
    seed: int
    model: str
    effort: str
    max_output_tokens: int
    max_decisions: int
    max_run_cost_cents: int
    horizon_days: int
    starting_capital_cents: int
    tariff: TokenTariff
    assessor_version: str = "deterministic-artifact-v1"
    tariff_valid_through: str = ""

    def __post_init__(self) -> None:
        if not self.run_name.strip():
            raise ValueError("run_name is required")
        if self.effort not in {"low", "medium", "high", "max"}:
            raise ValueError("unsupported effort")
        if not 128 <= self.max_output_tokens <= 4096:
            raise ValueError("max_output_tokens must be between 128 and 4096")
        if not 1 <= self.max_decisions <= 100:
            raise ValueError("max_decisions must be between 1 and 100")
        if self.max_run_cost_cents < 1:
            raise ValueError("max_run_cost_cents must be positive")
        if self.tariff_valid_through:
            date.fromisoformat(self.tariff_valid_through)

    @classmethod
    def from_manifest(cls, path: str | Path) -> "SandboxRunConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != "capage-sandbox-pilot-v1":
            raise ValueError("unsupported sandbox manifest schema")
        model = payload["model"]
        tariff = payload["token_tariff"]
        return cls(
            run_name=str(payload["run_name"]),
            seed=int(payload["seed"]),
            model=str(model["name"]),
            effort=str(model["effort"]),
            max_output_tokens=int(model["max_output_tokens"]),
            max_decisions=int(payload["max_decisions"]),
            max_run_cost_cents=int(payload["max_run_cost_cents"]),
            horizon_days=int(payload["horizon_days"]),
            starting_capital_cents=int(payload["starting_capital_cents"]),
            tariff=TokenTariff(
                name=str(tariff["name"]),
                input_cents_per_million_tokens=int(
                    tariff["input_cents_per_million_tokens"]
                ),
                output_cents_per_million_tokens=int(
                    tariff["output_cents_per_million_tokens"]
                ),
            ),
            assessor_version=str(payload["assessor_version"]),
            tariff_valid_through=str(payload["tariff_valid_through"]),
        )


_SYSTEM_PROMPT = """You are the sole strategic decision-maker inside a bounded,
30-day synthetic economy. Act through the supplied sandbox tools; do not make a
plan for a human to execute. Your goal is to maximize expected ending capital
net of all costs while making truthful offers, delivering genuinely useful
work, honoring obligations, and learning from observable customer feedback.

You begin with owner-supplied capital, not earned revenue. You receive no
prepared job or favored lead. Search public evidence for demand, decide what to
offer, create the actual deliverable when a contract is accepted, and manage
time under uncertainty. The environment alone controls hidden counterparties,
chance, quality assessment, settlement, and revenue recognition. Never claim
that an unobserved event happened and never invent a customer, payment, or
capability. All monetary amounts are integer cents.

Every one of your input, thinking, and output tokens is automatically charged
against the synthetic ledger. Be economical but think enough to avoid costly
mistakes. Select exactly one tool on every decision. If the prudent action is
to let time pass, use sandbox_wait."""


_API_TO_HOST_TOOL = {
    "sandbox_observe": "sandbox.observe",
    "sandbox_inspect_ledger": "sandbox.inspect_ledger",
    "sandbox_search_market": "sandbox.search_market",
    "sandbox_send_offer": "sandbox.send_offer",
    "sandbox_submit_delivery": "sandbox.submit_delivery",
    "sandbox_request_feedback": "sandbox.request_feedback",
    "sandbox_wait": "sandbox.wait",
}


_TOOLS: list[dict[str, Any]] = [
    {
        "name": "sandbox_observe",
        "description": "Refresh the complete state currently observable to the agent.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "sandbox_inspect_ledger",
        "description": "Inspect the append-only synthetic ledger and metered model usage.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "sandbox_search_market",
        "description": (
            "Pay the simulated research cost to search public market evidence. "
            "The query should describe evidence of a customer need, not a company name."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1, "maxLength": 300},
                "limit": {"type": "integer", "minimum": 1, "maximum": 10},
            },
            "required": ["query", "limit"],
            "additionalProperties": False,
        },
    },
    {
        "name": "sandbox_send_offer",
        "description": (
            "Pay the simulated communication cost to make a truthful offer to a "
            "counterparty already discovered through public research."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "signal_id": {"type": "string", "minLength": 1},
                "price_cents": {"type": "integer", "minimum": 100, "maximum": 100000},
                "promise_days": {"type": "integer", "minimum": 1, "maximum": 30},
                "scope": {"type": "string", "minLength": 1, "maxLength": 800},
                "solution_tags": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1, "maxLength": 80},
                    "minItems": 1,
                    "maxItems": 8,
                },
            },
            "required": [
                "signal_id",
                "price_cents",
                "promise_days",
                "scope",
                "solution_tags",
            ],
            "additionalProperties": False,
        },
    },
    {
        "name": "sandbox_submit_delivery",
        "description": (
            "Submit the actual completed work for an accepted contract. The host "
            "independently scores relevance, specificity, usefulness, and completeness; "
            "submission itself cannot create revenue."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "contract_id": {"type": "string", "minLength": 1},
                "artifact": {"type": "string", "minLength": 1, "maxLength": 6000},
            },
            "required": ["contract_id", "artifact"],
            "additionalProperties": False,
        },
    },
    {
        "name": "sandbox_request_feedback",
        "description": "Pay the simulated communication cost to request customer feedback.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"contract_id": {"type": "string", "minLength": 1}},
            "required": ["contract_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "sandbox_wait",
        "description": "Advance simulated time by one to seven days.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer", "minimum": 1, "maximum": 7}},
            "required": ["days"],
            "additionalProperties": False,
        },
    },
]


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 4
    }


def assess_artifact(
    artifact: str,
    *,
    public_need: str,
    promised_scope: str,
    solution_tags: list[str],
) -> tuple[int, dict[str, int]]:
    """Return a deterministic host score without asking the strategic model."""

    artifact_tokens = _tokens(artifact)
    target_tokens = _tokens(
        " ".join([public_need, promised_scope, " ".join(solution_tags)])
    )
    overlap = len(artifact_tokens & target_tokens)
    target_denominator = max(3, min(8, len(target_tokens)))

    completeness = min(35, len(artifact.strip()) // 12)
    specificity = min(20, len(artifact_tokens) // 2)
    relevance = min(30, round(30 * overlap / target_denominator))
    lines = [line.strip() for line in artifact.splitlines() if line.strip()]
    structured_lines = sum(
        line.startswith(("-", "*", "#")) or re.match(r"^\d+[.)]", line) is not None
        for line in lines
    )
    usefulness = min(15, (3 * min(structured_lines, 3)) + min(len(lines), 6))
    factors = {
        "completeness": completeness,
        "specificity": specificity,
        "relevance": relevance,
        "usefulness": usefulness,
    }
    return min(100, sum(factors.values())), factors


class LiveSandboxRunner:
    """Orchestrate bounded model decisions while preserving the authority split."""

    def __init__(
        self,
        config: SandboxRunConfig,
        client: ModelClient,
        *,
        audit_path: str | Path,
    ) -> None:
        self.config = config
        self.client = client
        self.world = EconomicSandbox(
            config.seed,
            horizon_days=config.horizon_days,
            starting_capital_cents=config.starting_capital_cents,
            token_tariff=config.tariff,
        )
        registry = self.world.agent_tools()
        self.executor = Executor(
            PolicyEngine(set(registry)),
            AuditLog(str(audit_path)),
            tools=registry,
        )
        self.transcript: list[dict[str, Any]] = []
        self.actual_cost_units = 0

    def run(self) -> dict[str, Any]:
        if self.config.tariff_valid_through:
            expiry = date.fromisoformat(self.config.tariff_valid_through)
            if datetime.now(timezone.utc).date() > expiry:
                raise SandboxRunnerError(
                    "the frozen provider tariff has expired; freeze current pricing before running"
                )
        started_at = datetime.now(timezone.utc).isoformat()
        stop_reason = "decision_limit"
        run_status = "completed"
        failure: str | None = None

        for decision_index in range(1, self.config.max_decisions + 1):
            if self.world.day >= self.world.horizon_days:
                stop_reason = "horizon_reached"
                break
            request_body = self._request_body(decision_index)
            counted_input_tokens = self.client.count_tokens(request_body)
            quote = self.world.quote_model_call(
                counted_input_tokens,
                self.config.max_output_tokens,
            )
            projected_units = self.actual_cost_units + self.config.tariff.cost_units(
                counted_input_tokens,
                self.config.max_output_tokens,
            )
            if not quote["affordable"]:
                stop_reason = "insufficient_synthetic_capital_for_next_call"
                break
            if _ceil_div(projected_units, _COST_UNITS_PER_CENT) > self.config.max_run_cost_cents:
                stop_reason = "external_model_cost_cap_reached"
                break

            day_before_action = self.world.day
            response = self.client.create_message(request_body)
            record: dict[str, Any] = {
                "decision": decision_index,
                "day_before_action": day_before_action,
                "preflight_input_tokens": counted_input_tokens,
                "preflight_quote": quote,
                "provider_response": response,
            }
            try:
                usage = self._validate_usage(response)
            except SandboxRunnerError as exc:
                failure = str(exc)
                run_status = "failed"
                stop_reason = "invalid_provider_usage"
                record["failure"] = failure
                self.transcript.append(record)
                break
            call_id = f"{self.config.run_name}-call-{decision_index:03d}"
            try:
                self.world.record_model_usage(
                    call_id,
                    input_tokens=usage["input_tokens"],
                    output_tokens=usage["output_tokens"],
                )
            except (TypeError, ValueError) as exc:
                failure = f"model usage could not be metered: {exc}"
                run_status = "failed"
                stop_reason = "model_usage_meter_failure"
                record["metered_usage"] = usage
                record["failure"] = failure
                self.transcript.append(record)
                break
            self.actual_cost_units += self.config.tariff.cost_units(
                usage["input_tokens"], usage["output_tokens"]
            )
            if _ceil_div(self.actual_cost_units, _COST_UNITS_PER_CENT) > self.config.max_run_cost_cents:
                failure = "provider usage exceeded the frozen run-cost cap"
                run_status = "failed"
                stop_reason = "provider_usage_exceeded_cost_cap"
                record["metered_usage"] = usage
                record["failure"] = failure
                self.transcript.append(record)
                break

            try:
                tool_block = self._one_tool_block(response)
                api_tool_name = str(tool_block.get("name", ""))
                host_tool_name = _API_TO_HOST_TOOL.get(api_tool_name)
                if host_tool_name is None:
                    raise SandboxRunnerError(
                        f"model requested unknown tool: {api_tool_name}"
                    )
                arguments = tool_block.get("input")
                if not isinstance(arguments, dict):
                    raise SandboxRunnerError("model tool input was not an object")
            except SandboxRunnerError as exc:
                failure = str(exc)
                run_status = "failed"
                stop_reason = "invalid_model_action"
                record["metered_usage"] = usage
                record["failure"] = failure
                self.transcript.append(record)
                break

            execution = self.executor.execute(
                ProposedAction(
                    action_type="sandbox",
                    tool_name=host_tool_name,
                    arguments=arguments,
                )
            )
            assessment = self._assess_delivery_if_needed(
                host_tool_name, arguments, execution
            )
            record.update(
                {
                    "metered_usage": usage,
                    "host_tool_name": host_tool_name,
                    "execution": execution,
                    "host_assessment": assessment,
                    "day_after_action": self.world.day,
                }
            )
            self.transcript.append(record)
        else:
            stop_reason = "decision_limit"

        self._advance_environment_to_horizon()
        result = {
            "schema_version": "capage-live-sandbox-result-v1",
            "status": run_status,
            "stop_reason": stop_reason,
            "failure": failure,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "config": {
                **asdict(self.config),
                "tariff": asdict(self.config.tariff),
            },
            "decision_count": len(self.transcript),
            "actual_model_cost_units": self.actual_cost_units,
            "actual_model_cost_cents_unrounded": (
                self.actual_cost_units / _COST_UNITS_PER_CENT
            ),
            "actual_model_cost_cents_billed": _ceil_div(
                self.actual_cost_units, _COST_UNITS_PER_CENT
            ),
            "transcript": self.transcript,
            "outcome": self.world.outcome(),
            "world_reveal": self.world.reveal_world(),
        }
        return result

    def _request_body(self, decision_index: int) -> dict[str, Any]:
        observation = self.world.observe()
        state = {
            "decision_number": decision_index,
            "decisions_remaining_including_this_one": (
                self.config.max_decisions - decision_index + 1
            ),
            "run_cost_cap_cents": self.config.max_run_cost_cents,
            "model_cost_cents_so_far_unrounded": (
                self.actual_cost_units / _COST_UNITS_PER_CENT
            ),
            "observation": observation,
            "recent_actions": [
                self._prompt_history_item(item) for item in self.transcript[-6:]
            ],
        }
        return {
            "model": self.config.model,
            "max_tokens": self.config.max_output_tokens,
            "thinking": {"type": "adaptive", "display": "omitted"},
            "output_config": {"effort": self.config.effort},
            "system": _SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Choose the single best next action from this state.\n"
                        + json.dumps(state, sort_keys=True, separators=(",", ":"))
                    ),
                }
            ],
            "tools": _TOOLS,
            "tool_choice": {"type": "any", "disable_parallel_tool_use": True},
        }

    @staticmethod
    def _validate_usage(response: dict[str, Any]) -> dict[str, int]:
        usage = response.get("usage")
        if not isinstance(usage, dict):
            raise SandboxRunnerError("provider response omitted usage")
        result: dict[str, int] = {}
        for key in ("input_tokens", "output_tokens"):
            value = usage.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise SandboxRunnerError(f"provider usage omitted valid {key}")
            result[key] = value
        return result

    @staticmethod
    def _one_tool_block(response: dict[str, Any]) -> dict[str, Any]:
        content = response.get("content")
        if not isinstance(content, list):
            raise SandboxRunnerError("provider response omitted content blocks")
        tools = [
            block
            for block in content
            if isinstance(block, dict) and block.get("type") == "tool_use"
        ]
        if len(tools) != 1:
            raise SandboxRunnerError(
                f"provider returned {len(tools)} tool calls; exactly one is required"
            )
        if not isinstance(tools[0], dict):
            raise SandboxRunnerError("tool-use block was not an object")
        return tools[0]

    def _assess_delivery_if_needed(
        self,
        host_tool_name: str,
        arguments: dict[str, Any],
        execution: dict[str, Any],
    ) -> dict[str, Any] | None:
        if host_tool_name != "sandbox.submit_delivery" or not execution.get("success"):
            return None
        tool_result = execution.get("tool_result", {})
        if not isinstance(tool_result, dict) or not tool_result.get("ok"):
            return None

        observation = self.world.observe()
        contract_id = str(arguments["contract_id"])
        contract = next(
            row for row in observation["contracts"] if row["contract_id"] == contract_id
        )
        offer = next(
            row for row in observation["offers"] if row["offer_id"] == contract["offer_id"]
        )
        signal = next(
            row
            for row in observation["discovered_signals"]
            if row["signal_id"] == contract["signal_id"]
        )
        score, factors = assess_artifact(
            str(arguments["artifact"]),
            public_need=str(signal["text"]),
            promised_scope=str(offer["scope"]),
            solution_tags=list(offer["solution_tags"]),
        )
        result = self.world.assess_delivery(
            str(tool_result["delivery_id"]),
            score,
            assessment_note=json.dumps(
                {"assessor_version": self.config.assessor_version, "factors": factors},
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        return {
            "assessor_version": self.config.assessor_version,
            "quality_score": score,
            "factors": factors,
            "result": result,
        }

    def _advance_environment_to_horizon(self) -> None:
        """Let already-committed events and settlements finish after agency stops."""

        while self.world.day < self.world.horizon_days:
            self.world.wait({"days": min(7, self.world.horizon_days - self.world.day)})

    @staticmethod
    def _prompt_history_item(item: dict[str, Any]) -> dict[str, Any]:
        response = item.get("provider_response", {})
        tool_blocks = [
            block
            for block in response.get("content", [])
            if isinstance(block, dict) and block.get("type") == "tool_use"
        ]
        tool_input = dict(tool_blocks[0].get("input", {})) if tool_blocks else {}
        if "artifact" in tool_input:
            artifact = str(tool_input["artifact"])
            tool_input["artifact"] = f"<submitted artifact: {len(artifact)} characters>"
        execution = item.get("execution", {})
        host_tool_name = str(item.get("host_tool_name", ""))
        return {
            "decision": item.get("decision"),
            "day_after_action": item.get("day_after_action"),
            "tool": host_tool_name,
            "input": tool_input,
            "result": LiveSandboxRunner._compact_tool_result(
                host_tool_name, execution
            ),
        }

    @staticmethod
    def _compact_tool_result(
        host_tool_name: str, execution: dict[str, Any]
    ) -> dict[str, Any]:
        if not execution.get("success"):
            return {
                "success": False,
                "status": execution.get("status"),
                "reason": execution.get("reason"),
            }
        tool_result = execution.get("tool_result")
        if not isinstance(tool_result, dict):
            return {"success": True}
        if host_tool_name == "sandbox.search_market":
            return {
                "ok": tool_result.get("ok"),
                "reason": tool_result.get("reason"),
                "cost_cents": tool_result.get("cost_cents"),
                "result_signal_ids": [
                    row.get("signal_id")
                    for row in tool_result.get("results", [])
                    if isinstance(row, dict)
                ],
            }
        if host_tool_name == "sandbox.wait":
            return {
                "ok": tool_result.get("ok"),
                "reason": tool_result.get("reason"),
                "advanced_days": tool_result.get("advanced_days"),
                "day": tool_result.get("day"),
            }
        if host_tool_name == "sandbox.inspect_ledger":
            return {
                "capital": tool_result.get("capital"),
                "entry_count": len(tool_result.get("entries", [])),
            }
        if host_tool_name == "sandbox.observe":
            return {
                "day": tool_result.get("day"),
                "capital": tool_result.get("capital"),
                "refreshed": True,
            }
        return tool_result


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("output")
    parser.add_argument("--audit", default="artifacts/sandbox-pilot-audit.jsonl")
    args = parser.parse_args(argv)

    try:
        config = SandboxRunConfig.from_manifest(args.manifest)
        runner = LiveSandboxRunner(
            config,
            AnthropicMessagesClient(),
            audit_path=args.audit,
        )
        result = runner.run()
    except Exception as exc:
        _write_json(
            args.output,
            {
                "schema_version": "capage-live-sandbox-result-v1",
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return 1

    _write_json(args.output, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "stop_reason": result["stop_reason"],
                "decision_count": result["decision_count"],
                "actual_model_cost_cents_billed": result[
                    "actual_model_cost_cents_billed"
                ],
                "outcome": result["outcome"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
