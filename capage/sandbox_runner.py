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
        if self.assessor_version not in {
            "deterministic-artifact-v1",
            "deterministic-artifact-v2",
        }:
            raise ValueError("unsupported artifact assessor version")
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


_API_TOOL_SCHEMAS = {
    str(tool["name"]): tool["input_schema"]
    for tool in _TOOLS
}


def _schema_error(value: Any, schema: dict[str, Any], path: str = "input") -> str | None:
    """Validate the original tool bounds after provider-side schema simplification."""

    expected = schema.get("type")
    type_ok = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(str(expected), True)
    if not type_ok:
        return f"{path} must have type {expected}"

    enum = schema.get("enum")
    if isinstance(enum, list) and value not in enum:
        return f"{path} is not an allowed value"

    if isinstance(value, dict):
        required = schema.get("required", [])
        for name in required if isinstance(required, list) else []:
            if name not in value:
                return f"{path}.{name} is required"
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            if schema.get("additionalProperties") is False:
                unexpected = sorted(set(value) - set(properties))
                if unexpected:
                    return f"{path} contains unexpected property {unexpected[0]}"
            for name, item in value.items():
                item_schema = properties.get(name)
                if isinstance(item_schema, dict):
                    error = _schema_error(item, item_schema, f"{path}.{name}")
                    if error:
                        return error
        for keyword, comparison, wording in (
            ("minProperties", lambda size, bound: size < bound, "at least"),
            ("maxProperties", lambda size, bound: size > bound, "at most"),
        ):
            bound = schema.get(keyword)
            if isinstance(bound, int) and comparison(len(value), bound):
                return f"{path} must contain {wording} {bound} properties"

    if isinstance(value, list):
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if isinstance(minimum, int) and len(value) < minimum:
            return f"{path} must contain at least {minimum} items"
        if isinstance(maximum, int) and len(value) > maximum:
            return f"{path} must contain at most {maximum} items"
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
            return f"{path} must contain unique items"
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                error = _schema_error(item, item_schema, f"{path}[{index}]")
                if error:
                    return error

    if isinstance(value, str):
        minimum = schema.get("minLength")
        maximum = schema.get("maxLength")
        if isinstance(minimum, int) and len(value) < minimum:
            return f"{path} must contain at least {minimum} characters"
        if isinstance(maximum, int) and len(value) > maximum:
            return f"{path} must contain at most {maximum} characters"

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            return f"{path} must be at least {minimum}"
        if isinstance(maximum, (int, float)) and value > maximum:
            return f"{path} must be at most {maximum}"
        exclusive_minimum = schema.get("exclusiveMinimum")
        exclusive_maximum = schema.get("exclusiveMaximum")
        if isinstance(exclusive_minimum, (int, float)) and value <= exclusive_minimum:
            return f"{path} must be greater than {exclusive_minimum}"
        if isinstance(exclusive_maximum, (int, float)) and value >= exclusive_maximum:
            return f"{path} must be less than {exclusive_maximum}"
        multiple = schema.get("multipleOf")
        if isinstance(multiple, (int, float)) and multiple and value % multiple != 0:
            return f"{path} must be a multiple of {multiple}"
    return None


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
    assessor_version: str = "deterministic-artifact-v1",
) -> tuple[int, dict[str, int]]:
    """Return a deterministic host score without asking the strategic model."""

    if assessor_version == "deterministic-artifact-v2":
        return _assess_artifact_v2(
            artifact,
            public_need=public_need,
            promised_scope=promised_scope,
            solution_tags=solution_tags,
        )
    if assessor_version != "deterministic-artifact-v1":
        raise ValueError("unsupported artifact assessor version")

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


_V2_CRITERIA = {
    "service_clarity": (("service", "include"), ("price", "scope"), ("question", "faq")),
    "data_cleanup": (("column", "field"), ("duplicate", "deduplicate"), ("validate", "check")),
    "documentation": (("index", "search"), ("transcript", "archive"), ("topic", "tag")),
    "customer_research": (("review", "customer"), ("pattern", "theme"), ("recommend", "change")),
    "comparison_research": (("cost", "price"), ("feature", "requirement"), ("compare", "matrix")),
    "supplier_research": (("supplier", "vendor"), ("lead", "delivery"), ("cost", "price")),
    "scheduling": (("availability", "schedule"), ("response", "confirm"), ("time", "window")),
    "audience_research": (("archive", "interview"), ("question", "topic"), ("guide", "index")),
    "catalog_cleanup": (("product", "item"), ("duplicate", "consistent"), ("description", "listing")),
    "process_documentation": (("step", "checklist"), ("handoff", "owner"), ("event", "setup")),
    "lead_qualification": (("qualify", "criteria"), ("service", "scope"), ("question", "intake")),
    "inventory_analysis": (("stock", "inventory"), ("reorder", "shortage"), ("usage", "quantity")),
}


def _assess_artifact_v2(
    artifact: str,
    *,
    public_need: str,
    promised_scope: str,
    solution_tags: list[str],
) -> tuple[int, dict[str, int]]:
    """Frozen rubric rewarding need coverage and penalizing generic padding."""

    normalized = artifact.strip()
    tokens = _tokens(normalized)
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    target = _tokens(" ".join((public_need, promised_scope, " ".join(solution_tags))))
    overlap = len(tokens & target)
    relevance = min(25, round(25 * overlap / max(4, min(10, len(target)))))

    criteria = []
    for tag in solution_tags:
        criteria.extend(_V2_CRITERIA.get(tag, ()))
    covered = sum(any(word in tokens for word in alternatives) for alternatives in criteria)
    need_coverage = min(30, round(30 * covered / max(1, len(criteria))))

    structured = sum(
        line.startswith(("-", "*", "#")) or re.match(r"^\d+[.)]", line) is not None
        for line in lines
    )
    action_words = {
        "compare", "record", "review", "rank", "group", "validate", "flag",
        "calculate", "publish", "update", "assign", "measure", "recommend",
    }
    actionability = min(25, (3 * min(structured, 4)) + (2 * len(tokens & action_words)))
    specificity = min(15, len(tokens) // 8) + min(5, sum(char.isdigit() for char in normalized))
    clarity = 5 if 3 <= len(lines) <= 30 else 2 if lines else 0

    generic_phrases = (
        "may help your business",
        "comprehensive solution",
        "best in class",
        "leverage synergies",
        "tailored to your needs",
    )
    generic_penalty = 5 * sum(phrase in normalized.lower() for phrase in generic_phrases)
    word_list = re.findall(r"[a-z0-9]+", normalized.lower())
    repetition_penalty = 10 if len(word_list) >= 80 and len(set(word_list)) / len(word_list) < 0.35 else 0
    verbosity_penalty = min(15, max(0, (len(normalized) - 2_500) // 250))
    penalties = generic_penalty + repetition_penalty + verbosity_penalty
    factors = {
        "relevance": relevance,
        "need_coverage": need_coverage,
        "actionability": actionability,
        "specificity": specificity,
        "clarity": clarity,
        "penalties": -penalties,
    }
    return max(0, min(100, sum(factors.values()))), factors


class LiveSandboxRunner:
    """Orchestrate bounded model decisions while preserving the authority split."""

    def __init__(
        self,
        config: SandboxRunConfig,
        client: ModelClient,
        *,
        audit_path: str | Path,
        durable_context: dict[str, Any] | None = None,
        continuity_state: dict[str, Any] | None = None,
    ) -> None:
        self.config = config
        self.client = client
        self.world = EconomicSandbox(
            config.seed,
            horizon_days=config.horizon_days,
            starting_capital_cents=config.starting_capital_cents,
            token_tariff=config.tariff,
            continuity_state=continuity_state,
        )
        registry = self.world.agent_tools()
        self.executor = Executor(
            PolicyEngine(set(registry)),
            AuditLog(str(audit_path)),
            tools=registry,
        )
        self.transcript: list[dict[str, Any]] = []
        self.actual_cost_units = 0
        self.durable_context = (
            json.loads(json.dumps(durable_context, sort_keys=True))
            if durable_context is not None
            else None
        )
        if self.durable_context is not None and not isinstance(
            self.durable_context, dict
        ):
            raise TypeError("durable_context must be an object")

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
                if response.get("stop_reason") == "max_tokens":
                    raise SandboxRunnerError(
                        "provider response reached the output-token limit before "
                        "completing a valid action"
                    )
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
                schema = _API_TOOL_SCHEMAS[api_tool_name]
                bounds_error = _schema_error(arguments, schema)
                if bounds_error:
                    raise SandboxRunnerError(
                        f"model tool input failed host validation: {bounds_error}"
                    )
            except SandboxRunnerError as exc:
                failure = str(exc)
                run_status = "failed"
                stop_reason = (
                    "model_output_limit_reached"
                    if response.get("stop_reason") == "max_tokens"
                    else "invalid_model_action"
                )
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
            "business_continuity": self.world.continuity_state(),
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
        if self.durable_context is not None:
            state["durable_memory"] = self.durable_context
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
            assessor_version=self.config.assessor_version,
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
