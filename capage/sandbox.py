"""Seeded, model-independent economic sandbox for CapAge.

The sandbox owns hidden market state, random events, settlement, and the
ledger.  The strategic model receives only a narrow registry of agent tools.
It cannot create customers, assess its own work, or credit its own revenue.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import random
from statistics import fmean, median, pstdev
from typing import Any


STARTING_CAPITAL_CENTS = 25_000
DEFAULT_HORIZON_DAYS = 30
_COST_UNITS_PER_CENT = 1_000_000
_CONTINUITY_SCHEMA = "capage-business-continuity-v1"
_MAX_CONTINUITY_CUSTOMERS = 10_000
_MAX_CONTINUITY_COUNT = 1_000_000

_SECTORS = (
    "local_services",
    "independent_media",
    "small_retail",
    "community_organizations",
    "professional_services",
    "micro_manufacturing",
)

_MARKET_TEMPLATES = (
    (
        "local_services",
        "service_clarity",
        "business_page",
        (
            "A repair business has conflicting public descriptions of what its "
            "standard service includes, and customers keep asking the same questions."
        ),
    ),
    (
        "community_organizations",
        "data_cleanup",
        "public_forum",
        (
            "A volunteer group says its donation and attendance records are spread "
            "across several inconsistent spreadsheets."
        ),
    ),
    (
        "independent_media",
        "documentation",
        "creator_post",
        (
            "An independent audio publisher mentions that useful interviews are "
            "difficult for its audience to search and reference later."
        ),
    ),
    (
        "small_retail",
        "customer_research",
        "review_stream",
        (
            "Reviews for a small retailer repeatedly disagree about available "
            "products, pickup rules, and current opening hours."
        ),
    ),
    (
        "professional_services",
        "comparison_research",
        "discussion_board",
        (
            "A small professional practice is publicly comparing several software "
            "subscriptions but lacks a consistent cost and feature analysis."
        ),
    ),
    (
        "micro_manufacturing",
        "supplier_research",
        "trade_forum",
        (
            "A small workshop asks peers how they track changing supplier prices and "
            "lead times for recurring materials."
        ),
    ),
    (
        "local_services",
        "scheduling",
        "community_post",
        (
            "Customers of a seasonal service complain that appointment availability "
            "and expected response times are unclear."
        ),
    ),
    (
        "independent_media",
        "audience_research",
        "creator_post",
        (
            "A newsletter publisher wonders which recurring questions in its archive "
            "would justify a focused guide."
        ),
    ),
    (
        "small_retail",
        "catalog_cleanup",
        "business_page",
        (
            "A specialty seller has duplicated and inconsistent product descriptions "
            "across several public listings."
        ),
    ),
    (
        "community_organizations",
        "process_documentation",
        "public_forum",
        (
            "A neighborhood organization says recurring volunteers struggle to "
            "understand its handoff and event setup process."
        ),
    ),
    (
        "professional_services",
        "lead_qualification",
        "business_page",
        (
            "A solo professional reports spending substantial time responding to "
            "inquiries that do not match the services actually offered."
        ),
    ),
    (
        "micro_manufacturing",
        "inventory_analysis",
        "trade_forum",
        (
            "A small producer describes repeated shortages of inexpensive components "
            "alongside excess stock of rarely used parts."
        ),
    ),
)

_EVENT_KINDS = (
    "demand_up",
    "demand_down",
    "market_access_up",
    "market_access_down",
    "operating_cost_up",
    "operating_cost_down",
)

_TASK_NOUNS = {
    "service_clarity": "service package",
    "data_cleanup": "data source",
    "documentation": "archive item",
    "customer_research": "customer theme",
    "comparison_research": "software option",
    "supplier_research": "supplier option",
    "scheduling": "scheduling policy",
    "audience_research": "guide topic",
    "catalog_cleanup": "catalog group",
    "process_documentation": "process change",
    "lead_qualification": "lead segment",
    "inventory_analysis": "inventory policy",
}

_LAST_OUTCOMES = {
    "",
    "delivery_accepted",
    "delivery_disputed",
    "paid",
    "customer_payment_default",
    "feedback_very_satisfied",
    "feedback_satisfied",
    "feedback_mixed",
    "feedback_dissatisfied",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_copy(value: Any) -> Any:
    """Return a detached JSON-safe copy of observable or revealed state."""

    return json.loads(json.dumps(value))


def _derived_rng(seed: int, namespace: str) -> random.Random:
    digest = sha256(f"{seed}:{namespace}".encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _tokens(text: str) -> set[str]:
    normalized = "".join(character.lower() if character.isalnum() else " " for character in text)
    return {token for token in normalized.split() if len(token) > 2}


def empty_continuity_state() -> dict[str, Any]:
    """Return a new host-owned customer and reputation ledger."""

    return {
        "schema_version": _CONTINUITY_SCHEMA,
        "global_reputation_points": 0,
        "customers": {},
    }


def validate_continuity_state(value: dict[str, Any] | None) -> dict[str, Any]:
    """Validate and detach longitudinal business state before a world uses it."""

    if value is None:
        return empty_continuity_state()
    state = _json_copy(value)
    if not isinstance(state, dict) or state.get("schema_version") != _CONTINUITY_SCHEMA:
        raise ValueError("unsupported business continuity schema")
    points = state.get("global_reputation_points")
    customers = state.get("customers")
    if isinstance(points, bool) or not isinstance(points, int) or not -100 <= points <= 100:
        raise ValueError("global reputation points must be an integer from -100 to 100")
    if not isinstance(customers, dict):
        raise ValueError("continuity customers must be an object")
    if len(customers) > _MAX_CONTINUITY_CUSTOMERS:
        raise ValueError("continuity contains too many customers")
    count_fields = (
        "offers_sent",
        "contracts_accepted",
        "deliveries_assessed",
        "contracts_paid",
        "contracts_defaulted",
        "contracts_disputed",
        "feedback_responses",
    )
    for customer_id, record in customers.items():
        if (
            not isinstance(customer_id, str)
            or not customer_id.startswith("customer-")
            or len(customer_id) > 96
            or any(
                character not in "abcdefghijklmnopqrstuvwxyz0123456789-"
                for character in customer_id
            )
        ):
            raise ValueError("continuity contains an invalid customer identifier")
        if not isinstance(record, dict):
            raise ValueError("continuity customer record must be an object")
        if set(record) != {*count_fields, "reputation_points", "last_outcome"}:
            raise ValueError("continuity customer record has unexpected fields")
        for field in count_fields:
            item = record[field]
            if (
                isinstance(item, bool)
                or not isinstance(item, int)
                or not 0 <= item <= _MAX_CONTINUITY_COUNT
            ):
                raise ValueError(f"continuity {field} must be a bounded nonnegative integer")
        reputation = record["reputation_points"]
        if (
            isinstance(reputation, bool)
            or not isinstance(reputation, int)
            or not -100 <= reputation <= 100
        ):
            raise ValueError("customer reputation points must be an integer from -100 to 100")
        if record["last_outcome"] not in _LAST_OUTCOMES:
            raise ValueError("customer last_outcome is unsupported")
        offers = int(record["offers_sent"])
        accepted = int(record["contracts_accepted"])
        assessed = int(record["deliveries_assessed"])
        terminal = sum(
            int(record[field])
            for field in (
                "contracts_paid",
                "contracts_defaulted",
                "contracts_disputed",
            )
        )
        if accepted > offers:
            raise ValueError("accepted contracts cannot exceed offers")
        if assessed > accepted:
            raise ValueError("assessed deliveries cannot exceed accepted contracts")
        if terminal > assessed:
            raise ValueError("terminal contract outcomes cannot exceed assessed deliveries")
        if int(record["feedback_responses"]) > assessed:
            raise ValueError("feedback responses cannot exceed assessed deliveries")
    return state


@dataclass(frozen=True)
class LedgerEntry:
    """One immutable posting in the synthetic economic ledger."""

    sequence: int
    day: int
    entry_type: str
    amount_cents: int
    balance_cents: int
    memo: str
    reference: str = ""


@dataclass(frozen=True)
class TokenTariff:
    """Frozen provider pricing expressed as cents per million tokens."""

    name: str
    input_cents_per_million_tokens: int
    output_cents_per_million_tokens: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("token tariff name is required")
        for value in (
            self.input_cents_per_million_tokens,
            self.output_cents_per_million_tokens,
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError("token tariff rates must be integer cents")
            if value < 0:
                raise ValueError("token tariff rates cannot be negative")

    def cost_units(self, input_tokens: int, output_tokens: int) -> int:
        """Return millionths of a cent so sub-cent usage is preserved."""

        return (
            input_tokens * self.input_cents_per_million_tokens
            + output_tokens * self.output_cents_per_million_tokens
        )


@dataclass(frozen=True)
class ModelUsageEntry:
    """One host-metered strategic-model call."""

    sequence: int
    day: int
    call_id: str
    tariff_name: str
    input_tokens: int
    output_tokens: int
    cost_units: int
    cumulative_cost_units: int
    incremental_billed_cents: int


@dataclass(frozen=True)
class ScheduledEvent:
    """An exogenous event fixed before the run starts."""

    day: int
    kind: str
    sector: str = ""
    magnitude: int = 0


@dataclass
class _MarketSignal:
    signal_id: str
    customer_id: str
    sector: str
    need_tag: str
    source_type: str
    public_text: str
    budget_cents: int
    buyer_intent: bool
    responsiveness: float
    payment_reliability: float
    quality_threshold: int
    discoverability: float
    active_from: int
    active_until: int
    task_brief: dict[str, Any]

    def is_active(self, day: int) -> bool:
        return self.active_from <= day <= self.active_until

    def public_view(
        self, day: int, relationship: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        view = {
            "signal_id": self.signal_id,
            "customer_id": self.customer_id,
            "source_type": self.source_type,
            "sector": self.sector,
            "text": self.public_text,
            "currently_visible": self.is_active(day),
        }
        if relationship is not None:
            view["prior_relationship"] = relationship
        return view


@dataclass
class _Offer:
    offer_id: str
    signal_id: str
    price_cents: int
    solution_tags: tuple[str, ...]
    scope: str
    promise_days: int
    sent_day: int
    response_day: int
    planned_outcome: str
    status: str = "pending"


@dataclass
class _Contract:
    contract_id: str
    offer_id: str
    signal_id: str
    price_cents: int
    accepted_day: int
    deadline_day: int
    status: str = "accepted"
    delivery_id: str = ""
    satisfaction: int | None = None
    payment_due_day: int | None = None
    planned_payment: str = ""
    feedback_requested: bool = False
    feedback_due_day: int | None = None


@dataclass
class _Delivery:
    delivery_id: str
    contract_id: str
    submitted_day: int
    artifact: str
    artifact_hash: str
    assessment_status: str = "pending"


class EconomicSandbox:
    """A small, causally closed economy with replayable chance.

    The constructor receives the seed from the trusted host.  The seed and
    hidden state are not included in agent observations.  Candidate identity
    is deliberately absent from the constructor and every outcome rule.
    """

    def __init__(
        self,
        seed: int,
        *,
        horizon_days: int = DEFAULT_HORIZON_DAYS,
        starting_capital_cents: int = STARTING_CAPITAL_CENTS,
        market_size: int = 18,
        token_tariff: TokenTariff | None = None,
        continuity_state: dict[str, Any] | None = None,
        customer_population_seed: int = 0,
    ) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("seed must be an integer")
        if horizon_days < 7:
            raise ValueError("horizon_days must be at least 7")
        if starting_capital_cents < 0:
            raise ValueError("starting capital cannot be negative")
        if market_size < 6:
            raise ValueError("market_size must be at least 6")
        if token_tariff is not None and not isinstance(token_tariff, TokenTariff):
            raise TypeError("token_tariff must be a TokenTariff")
        if isinstance(customer_population_seed, bool) or not isinstance(
            customer_population_seed, int
        ):
            raise TypeError("customer_population_seed must be an integer")

        self._seed = seed
        self.horizon_days = horizon_days
        self.starting_capital_cents = starting_capital_cents
        self.token_tariff = token_tariff
        self.customer_population_seed = customer_population_seed
        self._continuity = validate_continuity_state(continuity_state)
        self.day = 0
        self._balance_cents = 0
        self._ledger: list[LedgerEntry] = []
        self._model_usage: list[ModelUsageEntry] = []
        self._model_cost_units = 0
        self._billed_model_cost_cents = 0
        self._journal: list[dict[str, Any]] = []
        self._signals = self._build_market(market_size)
        self._events = self._build_event_schedule()
        self._events_by_day = {event.day: event for event in self._events}
        self._sector_demand = {sector: 1.0 for sector in _SECTORS}
        self._discovered: set[str] = set()
        self._offers: dict[str, _Offer] = {}
        self._contracts: dict[str, _Contract] = {}
        self._deliveries: dict[str, _Delivery] = {}
        self._inbox: list[dict[str, Any]] = []
        self._public_events: list[dict[str, Any]] = []

        commitment_payload = self._commitment_payload()
        self.world_commitment = sha256(
            _canonical_json(commitment_payload).encode("utf-8")
        ).hexdigest()
        cost_policy_payload = {
            "token_tariff": asdict(token_tariff) if token_tariff else None,
            "cost_units_per_cent": _COST_UNITS_PER_CENT,
        }
        self.cost_policy_commitment = sha256(
            _canonical_json(cost_policy_payload).encode("utf-8")
        ).hexdigest()
        self.run_id = sha256(f"run:{seed}".encode("utf-8")).hexdigest()[:12]

        self._post(
            "owner_capital",
            starting_capital_cents,
            "Initial synthetic owner-supplied capital.",
            "initial-capital",
        )
        self._record(
            "sandbox_started",
            {
                "run_id": self.run_id,
                "horizon_days": horizon_days,
                "world_commitment": self.world_commitment,
                "cost_policy_commitment": self.cost_policy_commitment,
                "token_tariff": asdict(token_tariff) if token_tariff else None,
            },
        )

    def _build_market(self, market_size: int) -> dict[str, _MarketSignal]:
        rng = _derived_rng(self._seed, "market")
        templates = list(_MARKET_TEMPLATES)
        rng.shuffle(templates)
        signals: dict[str, _MarketSignal] = {}
        customer_occurrences: dict[str, int] = {}

        for index in range(market_size):
            sector, need_tag, source_type, public_text = templates[
                index % len(templates)
            ]
            active_from = rng.randint(0, min(5, self.horizon_days // 3))
            lower_end = max(active_from + 3, self.horizon_days // 2)
            active_until = rng.randint(lower_end, self.horizon_days)
            signal_id = f"signal-{index + 1:03d}"
            customer_occurrences[need_tag] = customer_occurrences.get(need_tag, 0) + 1
            customer_id = f"customer-{need_tag.replace('_', '-')}-{customer_occurrences[need_tag]:02d}"
            customer_rng = _derived_rng(
                self.customer_population_seed, f"customer-traits:{customer_id}"
            )
            if self.customer_population_seed == 0:
                budget_cents = rng.randrange(2_500, 20_001, 500)
                buyer_intent = rng.random() < 0.65
                responsiveness = round(rng.uniform(0.25, 0.95), 4)
                payment_reliability = round(rng.uniform(0.55, 0.98), 4)
                quality_threshold = rng.randint(55, 90)
            else:
                budget_cents = customer_rng.randrange(2_500, 20_001, 500)
                buyer_intent = rng.random() < 0.65
                responsiveness = round(customer_rng.uniform(0.25, 0.95), 4)
                payment_reliability = round(customer_rng.uniform(0.55, 0.98), 4)
                quality_threshold = customer_rng.randint(55, 90)
            signals[signal_id] = _MarketSignal(
                signal_id=signal_id,
                customer_id=customer_id,
                sector=sector,
                need_tag=need_tag,
                source_type=source_type,
                public_text=public_text,
                budget_cents=budget_cents,
                buyer_intent=buyer_intent,
                responsiveness=responsiveness,
                payment_reliability=payment_reliability,
                quality_threshold=quality_threshold,
                discoverability=round(rng.uniform(0.1, 0.95), 4),
                active_from=active_from,
                active_until=active_until,
                task_brief=self._build_task_brief(signal_id, customer_id, need_tag),
            )
        return signals

    def _build_task_brief(
        self,
        signal_id: str,
        customer_id: str,
        need_tag: str,
    ) -> dict[str, Any]:
        """Create a committed, objectively checkable customer-supplied task."""

        noun = _TASK_NOUNS[need_tag]
        rng = _derived_rng(self._seed, f"customer-task:{signal_id}:{customer_id}")
        records = []
        for index in range(1, 4):
            records.append(
                {
                    "record_id": f"option-{index}",
                    "label": f"{noun.title()} {index}",
                    "value_points": rng.randint(35, 95),
                    "cost_points": rng.randint(5, 45),
                    "risk_points": rng.randint(0, 25),
                }
            )
        brief_id = sha256(
            f"brief:{self._seed}:{signal_id}:{customer_id}".encode("utf-8")
        ).hexdigest()[:16]
        return {
            "schema_version": "capage-customer-task-v1",
            "brief_id": brief_id,
            "task_type": need_tag,
            "objective": (
                f"Evaluate all three {noun} records and recommend the strongest option."
            ),
            "scoring_rule": "computed_score = (2 * value_points) - cost_points - risk_points",
            "source_records": records,
            "required_delivery_schema": {
                "brief_id": "exact brief_id",
                "record_evaluations": [
                    {"record_id": "option-N", "computed_score": "integer"}
                ],
                "recommended_record_id": "highest computed_score; lowest record_id breaks ties",
                "customer_summary": "plain-language explanation",
                "implementation_steps": ["at least two concrete next steps"],
            },
        }

    def _build_event_schedule(self) -> tuple[ScheduledEvent, ...]:
        rng = _derived_rng(self._seed, "events")
        events: list[ScheduledEvent] = []
        for day in range(1, self.horizon_days + 1):
            if rng.random() >= 0.45:
                continue
            kind = rng.choice(_EVENT_KINDS)
            sector = rng.choice(_SECTORS) if kind.startswith("demand_") else ""
            magnitude = rng.choice((10, 15, 20))
            events.append(ScheduledEvent(day, kind, sector, magnitude))
        return tuple(events)

    def _commitment_payload(self) -> dict[str, Any]:
        return {
            "seed": self._seed,
            "horizon_days": self.horizon_days,
            "starting_capital_cents": self.starting_capital_cents,
            "customer_population_seed": self.customer_population_seed,
            "signals": [
                asdict(self._signals[key]) for key in sorted(self._signals)
            ],
            "events": [asdict(event) for event in self._events],
        }

    def _record(self, event_type: str, data: dict[str, Any]) -> None:
        self._journal.append(
            {
                "sequence": len(self._journal) + 1,
                "day": self.day,
                "event_type": event_type,
                "data": data,
            }
        )

    def _post(
        self,
        entry_type: str,
        amount_cents: int,
        memo: str,
        reference: str = "",
    ) -> LedgerEntry:
        if not isinstance(amount_cents, int):
            raise TypeError("ledger postings must use integer cents")
        next_balance = self._balance_cents + amount_cents
        if next_balance < 0:
            raise ValueError("ledger posting would overdraw synthetic capital")
        self._balance_cents = next_balance
        entry = LedgerEntry(
            sequence=len(self._ledger) + 1,
            day=self.day,
            entry_type=entry_type,
            amount_cents=amount_cents,
            balance_cents=next_balance,
            memo=memo,
            reference=reference,
        )
        self._ledger.append(entry)
        self._record("ledger_posted", asdict(entry))
        return entry

    def _charge(
        self,
        amount_cents: int,
        entry_type: str,
        memo: str,
        reference: str,
    ) -> bool:
        if amount_cents < 0:
            raise ValueError("charge cannot be negative")
        if self._balance_cents < amount_cents:
            self._record(
                "cost_rejected",
                {
                    "entry_type": entry_type,
                    "amount_cents": amount_cents,
                    "reason": "insufficient synthetic capital",
                    "reference": reference,
                },
            )
            return False
        self._post(entry_type, -amount_cents, memo, reference)
        return True

    def _event_today(self, kind: str) -> ScheduledEvent | None:
        event = self._events_by_day.get(self.day)
        if event is not None and event.kind == kind:
            return event
        return None

    def _tool_cost(self, base_cents: int) -> int:
        if self._event_today("operating_cost_up"):
            return base_cents + 1
        if self._event_today("operating_cost_down"):
            return max(0, base_cents - 1)
        return base_cents

    def _stable_roll(self, namespace: str) -> float:
        return _derived_rng(self._seed, namespace).random()

    def agent_tools(
        self,
    ) -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
        """Return the complete and intentionally limited agent tool registry."""

        return {
            "sandbox.observe": self.observe,
            "sandbox.inspect_ledger": self.inspect_ledger,
            "sandbox.search_market": self.search_market,
            "sandbox.send_offer": self.send_offer,
            "sandbox.submit_delivery": self.submit_delivery,
            "sandbox.request_feedback": self.request_feedback,
            "sandbox.wait": self.wait,
        }

    def observe(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return only state the agent is permitted to observe."""

        del arguments
        return {
            "run_id": self.run_id,
            "day": self.day,
            "horizon_days": self.horizon_days,
            "world_commitment": self.world_commitment,
            "cost_policy_commitment": self.cost_policy_commitment,
            "token_tariff": (
                asdict(self.token_tariff) if self.token_tariff else None
            ),
            "capital": self._capital_summary(),
            "discovered_signals": [
                self._signals[key].public_view(
                    self.day, self._relationship_view(self._signals[key].customer_id)
                )
                for key in sorted(self._discovered)
            ],
            "offers": [self._offer_view(offer) for offer in self._offers.values()],
            "contracts": [
                self._contract_view(contract)
                for contract in self._contracts.values()
            ],
            "inbox": _json_copy(self._inbox),
            "public_events": _json_copy(self._public_events),
        }

    def inspect_ledger(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Expose append-only synthetic accounting to the agent."""

        del arguments
        return {
            "capital": self._capital_summary(),
            "entries": [asdict(entry) for entry in self._ledger],
            "model_usage": [asdict(entry) for entry in self._model_usage],
        }

    def _capital_summary(self) -> dict[str, int]:
        earned = sum(
            entry.amount_cents
            for entry in self._ledger
            if entry.entry_type == "earned_revenue"
        )
        expenses = -sum(
            entry.amount_cents
            for entry in self._ledger
            if entry.amount_cents < 0
        )
        return {
            "owner_capital_cents": self.starting_capital_cents,
            "balance_cents": self._balance_cents,
            "earned_revenue_cents": earned,
            "expense_cents": expenses,
            "model_api_cost_cents": self._billed_model_cost_cents,
            "model_api_cost_units": self._model_cost_units,
            "model_input_tokens": sum(
                entry.input_tokens for entry in self._model_usage
            ),
            "model_output_tokens": sum(
                entry.output_tokens for entry in self._model_usage
            ),
        }

    def search_market(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Search public market evidence without receiving a prepared lead list."""

        query = str(arguments.get("query", "")).strip()
        if not query:
            return {"ok": False, "reason": "query is required"}
        try:
            requested_limit = int(arguments.get("limit", 5))
        except (TypeError, ValueError):
            return {"ok": False, "reason": "limit must be an integer"}
        limit = max(1, min(requested_limit, 10))
        cost = self._tool_cost(2)
        prior_searches = sum(
            event["event_type"] == "market_searched" for event in self._journal
        )
        search_reference = f"search-{prior_searches + 1:03d}"
        if not self._charge(
            cost,
            "market_research_cost",
            f"Simulated public-market search: {query}",
            search_reference,
        ):
            return {"ok": False, "reason": "insufficient synthetic capital"}

        if self._event_today("market_access_down"):
            self._record(
                "market_searched",
                {"query": query, "result_count": 0, "status": "platform_unavailable"},
            )
            return {
                "ok": False,
                "reason": "The simulated search platform is temporarily unavailable.",
                "cost_cents": cost,
            }

        if self._event_today("market_access_up"):
            limit = min(10, limit + 2)

        query_tokens = _tokens(query)
        ranked: list[tuple[float, _MarketSignal]] = []
        for signal in self._signals.values():
            if not signal.is_active(self.day):
                continue
            public_tokens = _tokens(signal.public_text + " " + signal.sector)
            overlap = len(query_tokens & public_tokens)
            relevance = overlap / max(1, len(query_tokens))
            repeat_bonus = 0.12 if signal.customer_id in self._continuity["customers"] else 0.0
            score = relevance + (0.30 * signal.discoverability) + repeat_bonus
            ranked.append((score, signal))
        ranked.sort(key=lambda item: (-item[0], item[1].signal_id))
        results = [
            signal.public_view(self.day, self._relationship_view(signal.customer_id))
            for _, signal in ranked[:limit]
        ]
        self._discovered.update(result["signal_id"] for result in results)
        self._record(
            "market_searched",
            {
                "query": query,
                "result_count": len(results),
                "cost_cents": cost,
                "discovered_signal_ids": [result["signal_id"] for result in results],
            },
        )
        return {"ok": True, "cost_cents": cost, "results": results}

    def send_offer(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Send an independently chosen offer to a discovered counterparty."""

        signal_id = str(arguments.get("signal_id", "")).strip()
        if signal_id not in self._discovered:
            return {
                "ok": False,
                "reason": "The counterparty must be discovered through public research first.",
            }
        signal = self._signals[signal_id]
        try:
            price_cents = int(arguments.get("price_cents"))
            promise_days = int(arguments.get("promise_days"))
        except (TypeError, ValueError):
            return {
                "ok": False,
                "reason": "price_cents and promise_days must be integers",
            }
        if not 100 <= price_cents <= 100_000:
            return {"ok": False, "reason": "price_cents must be between 100 and 100000"}
        if not 1 <= promise_days <= self.horizon_days:
            return {"ok": False, "reason": "promise_days is outside the run horizon"}
        scope = str(arguments.get("scope", "")).strip()
        if not scope:
            return {"ok": False, "reason": "scope is required"}
        raw_tags = arguments.get("solution_tags", [])
        if isinstance(raw_tags, str):
            raw_tags = [raw_tags]
        if not isinstance(raw_tags, list):
            return {"ok": False, "reason": "solution_tags must be a list of strings"}
        solution_tags = tuple(
            sorted({str(tag).strip().lower() for tag in raw_tags if str(tag).strip()})
        )
        if not solution_tags:
            return {"ok": False, "reason": "at least one solution tag is required"}

        offer_id = f"offer-{len(self._offers) + 1:03d}"
        cost = self._tool_cost(1)
        if not self._charge(
            cost,
            "communication_cost",
            f"Send simulated offer to {signal_id}.",
            offer_id,
        ):
            return {"ok": False, "reason": "insufficient synthetic capital"}

        fit = 1.0 if signal.need_tag.lower() in solution_tags else 0.25
        if fit < 1.0:
            need_tokens = _tokens(signal.need_tag.replace("_", " "))
            offered_tokens = _tokens(" ".join(solution_tags).replace("_", " "))
            if need_tokens & offered_tokens:
                fit = 0.60
        price_fit = min(1.0, signal.budget_cents / price_cents)
        intent = 1.0 if signal.buyer_intent else 0.08
        active = 1.0 if signal.is_active(self.day) else 0.05
        demand = self._sector_demand[signal.sector]
        reputation_multiplier = self._reputation_multiplier(signal.customer_id)
        acceptance_probability = _clamp(
            0.70
            * signal.responsiveness
            * intent
            * fit
            * price_fit
            * active
            * demand
            * reputation_multiplier,
            0.005,
            0.92,
        )
        reply_probability = _clamp(signal.responsiveness * active, 0.05, 0.98)
        if self._stable_roll(f"{offer_id}:{signal_id}:reply") > reply_probability:
            planned_outcome = "no_response"
        elif self._stable_roll(f"{offer_id}:{signal_id}:accept") < acceptance_probability:
            planned_outcome = "accepted"
        else:
            planned_outcome = "declined"
        response_delay = 1 + int((1.0 - signal.responsiveness) * 3)
        offer = _Offer(
            offer_id=offer_id,
            signal_id=signal_id,
            price_cents=price_cents,
            solution_tags=solution_tags,
            scope=scope,
            promise_days=promise_days,
            sent_day=self.day,
            response_day=self.day + response_delay,
            planned_outcome=planned_outcome,
        )
        self._offers[offer_id] = offer
        self._customer_record(signal.customer_id)["offers_sent"] += 1
        self._record(
            "offer_sent",
            {
                "offer_id": offer_id,
                "signal_id": signal_id,
                "price_cents": price_cents,
                "promise_days": promise_days,
                "cost_cents": cost,
            },
        )
        return {
            "ok": True,
            "offer_id": offer_id,
            "status": "pending",
            "response_not_before_day": offer.response_day,
            "cost_cents": cost,
        }

    def _customer_record(self, customer_id: str) -> dict[str, Any]:
        customers = self._continuity["customers"]
        if customer_id not in customers:
            customers[customer_id] = {
                "offers_sent": 0,
                "contracts_accepted": 0,
                "deliveries_assessed": 0,
                "contracts_paid": 0,
                "contracts_defaulted": 0,
                "contracts_disputed": 0,
                "feedback_responses": 0,
                "reputation_points": 0,
                "last_outcome": "",
            }
        return customers[customer_id]

    def _relationship_view(self, customer_id: str) -> dict[str, Any] | None:
        record = self._continuity["customers"].get(customer_id)
        if record is None:
            return None
        return {
            "offers_sent": record["offers_sent"],
            "contracts_accepted": record["contracts_accepted"],
            "contracts_paid": record["contracts_paid"],
            "contracts_defaulted": record["contracts_defaulted"],
            "contracts_disputed": record["contracts_disputed"],
            "feedback_responses": record["feedback_responses"],
            "last_outcome": record["last_outcome"],
        }

    def _reputation_multiplier(self, customer_id: str) -> float:
        customer = self._continuity["customers"].get(customer_id)
        customer_points = int(customer["reputation_points"]) if customer else 0
        global_points = int(self._continuity["global_reputation_points"])
        weighted = (0.7 * customer_points) + (0.3 * global_points)
        return _clamp(1.0 + (weighted / 200), 0.60, 1.40)

    def _adjust_reputation(self, customer_id: str, delta: int, outcome: str) -> None:
        record = self._customer_record(customer_id)
        record["reputation_points"] = int(
            _clamp(int(record["reputation_points"]) + delta, -100, 100)
        )
        self._continuity["global_reputation_points"] = int(
            _clamp(
                int(self._continuity["global_reputation_points"]) + delta,
                -100,
                100,
            )
        )
        record["last_outcome"] = outcome

    def continuity_state(self) -> dict[str, Any]:
        """Export detached host-owned state only after the run is settled."""

        return validate_continuity_state(self._continuity)

    def submit_delivery(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Submit work for independent assessment; submission cannot create revenue."""

        contract_id = str(arguments.get("contract_id", "")).strip()
        contract = self._contracts.get(contract_id)
        if contract is None:
            return {"ok": False, "reason": "unknown contract"}
        if contract.status != "accepted":
            return {"ok": False, "reason": "contract is not awaiting delivery"}
        artifact = str(arguments.get("artifact", "")).strip()
        if not artifact:
            return {"ok": False, "reason": "artifact is required"}
        delivery_id = f"delivery-{len(self._deliveries) + 1:03d}"
        artifact_hash = sha256(artifact.encode("utf-8")).hexdigest()
        delivery = _Delivery(
            delivery_id=delivery_id,
            contract_id=contract_id,
            submitted_day=self.day,
            artifact=artifact,
            artifact_hash=artifact_hash,
        )
        self._deliveries[delivery_id] = delivery
        contract.delivery_id = delivery_id
        contract.status = "awaiting_independent_assessment"
        self._record(
            "delivery_submitted",
            {
                "delivery_id": delivery_id,
                "contract_id": contract_id,
                "artifact_hash": artifact_hash,
                "artifact_characters": len(artifact),
            },
        )
        return {
            "ok": True,
            "delivery_id": delivery_id,
            "status": "awaiting_independent_assessment",
            "revenue_credited_cents": 0,
        }

    def request_feedback(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Ask for feedback instead of receiving hidden satisfaction automatically."""

        contract_id = str(arguments.get("contract_id", "")).strip()
        contract = self._contracts.get(contract_id)
        if contract is None:
            return {"ok": False, "reason": "unknown contract"}
        if contract.satisfaction is None:
            return {"ok": False, "reason": "delivery has not been assessed"}
        if contract.feedback_requested:
            return {"ok": False, "reason": "feedback has already been requested"}
        cost = self._tool_cost(1)
        if not self._charge(
            cost,
            "communication_cost",
            f"Request feedback for {contract_id}.",
            contract_id,
        ):
            return {"ok": False, "reason": "insufficient synthetic capital"}
        contract.feedback_requested = True
        contract.feedback_due_day = self.day + 1
        self._record(
            "feedback_requested",
            {"contract_id": contract_id, "cost_cents": cost},
        )
        return {
            "ok": True,
            "status": "requested",
            "feedback_not_before_day": contract.feedback_due_day,
            "cost_cents": cost,
        }

    def wait(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Request time passage while the environment controls every transition."""

        try:
            requested_days = int(arguments.get("days", 1))
        except (TypeError, ValueError):
            return {"ok": False, "reason": "days must be an integer"}
        if not 1 <= requested_days <= 7:
            return {"ok": False, "reason": "days must be between 1 and 7"}
        remaining = self.horizon_days - self.day
        if remaining <= 0:
            return {"ok": False, "reason": "the sandbox horizon has ended"}
        advanced = min(requested_days, remaining)
        for _ in range(advanced):
            self._advance_one_day()
        observation = self.observe()
        observation.update({"ok": True, "advanced_days": advanced})
        return observation

    def _advance_one_day(self) -> None:
        self.day += 1
        self._public_events = []
        event = self._events_by_day.get(self.day)
        if event is not None:
            self._apply_event(event)
        self._process_offers()
        self._process_payments()
        self._process_feedback()
        self._record("day_advanced", {"day": self.day})

    def _apply_event(self, event: ScheduledEvent) -> None:
        if event.kind == "demand_up":
            self._sector_demand[event.sector] = min(
                1.75,
                self._sector_demand[event.sector] + (event.magnitude / 100),
            )
            summary = f"Public demand strengthened in {event.sector}."
        elif event.kind == "demand_down":
            self._sector_demand[event.sector] = max(
                0.25,
                self._sector_demand[event.sector] - (event.magnitude / 100),
            )
            summary = f"Public demand weakened in {event.sector}."
        elif event.kind == "market_access_up":
            summary = "Public-market search is unusually responsive today."
        elif event.kind == "market_access_down":
            summary = "The public-market search platform is unavailable today."
        elif event.kind == "operating_cost_up":
            summary = "Routine external-service costs are temporarily higher today."
        else:
            summary = "Routine external-service costs are temporarily lower today."
        public_event = {"day": self.day, "kind": event.kind, "summary": summary}
        self._public_events.append(public_event)
        self._record("exogenous_event", public_event)

    def _process_offers(self) -> None:
        for offer in self._offers.values():
            if offer.status != "pending" or offer.response_day > self.day:
                continue
            offer.status = offer.planned_outcome
            if offer.planned_outcome == "accepted":
                contract_id = f"contract-{len(self._contracts) + 1:03d}"
                contract = _Contract(
                    contract_id=contract_id,
                    offer_id=offer.offer_id,
                    signal_id=offer.signal_id,
                    price_cents=offer.price_cents,
                    accepted_day=self.day,
                    deadline_day=self.day + offer.promise_days,
                )
                self._contracts[contract_id] = contract
                customer = self._signals[offer.signal_id].customer_id
                self._customer_record(customer)["contracts_accepted"] += 1
                message = {
                    "day": self.day,
                    "from": offer.signal_id,
                    "type": "offer_accepted",
                    "offer_id": offer.offer_id,
                    "contract_id": contract_id,
                    "deadline_day": contract.deadline_day,
                    "agreed_price_cents": contract.price_cents,
                    "delivery_brief": _json_copy(
                        self._signals[offer.signal_id].task_brief
                    ),
                }
                self._inbox.append(message)
                self._record("offer_accepted", message)
            elif offer.planned_outcome == "declined":
                message = {
                    "day": self.day,
                    "from": offer.signal_id,
                    "type": "offer_declined",
                    "offer_id": offer.offer_id,
                }
                self._inbox.append(message)
                self._record("offer_declined", message)
            else:
                self._record(
                    "offer_no_response",
                    {"offer_id": offer.offer_id, "signal_id": offer.signal_id},
                )

    def assess_delivery(
        self,
        delivery_id: str,
        quality_score: int,
        assessment_note: str = "",
    ) -> dict[str, Any]:
        """Trusted-host assessment; intentionally absent from agent tools."""

        delivery = self._deliveries.get(delivery_id)
        if delivery is None:
            raise ValueError("unknown delivery")
        if delivery.assessment_status != "pending":
            raise ValueError("delivery has already been assessed")
        if isinstance(quality_score, bool) or not isinstance(quality_score, int):
            raise TypeError("quality_score must be an integer")
        if not 0 <= quality_score <= 100:
            raise ValueError("quality_score must be between 0 and 100")

        contract = self._contracts[delivery.contract_id]
        signal = self._signals[contract.signal_id]
        lateness = max(0, delivery.submitted_day - contract.deadline_day)
        satisfaction = int(_clamp(quality_score - (5 * lateness), 0, 100))
        delivery.assessment_status = "assessed"
        contract.satisfaction = satisfaction
        customer = self._customer_record(signal.customer_id)
        customer["deliveries_assessed"] += 1

        if satisfaction >= signal.quality_threshold:
            contract.status = "accepted_pending_payment"
            payment_delay = 1 + int((1.0 - signal.payment_reliability) * 4)
            contract.payment_due_day = self.day + payment_delay
            payment_roll = self._stable_roll(
                f"{contract.contract_id}:{contract.signal_id}:payment"
            )
            contract.planned_payment = (
                "paid" if payment_roll < signal.payment_reliability else "defaulted"
            )
            reputation_delta = 12 if satisfaction >= 85 else 6
            self._adjust_reputation(
                signal.customer_id, reputation_delta, "delivery_accepted"
            )
        else:
            contract.status = "disputed"
            contract.planned_payment = "not_due"
            customer["contracts_disputed"] += 1
            self._adjust_reputation(signal.customer_id, -18, "delivery_disputed")

        self._record(
            "delivery_assessed",
            {
                "delivery_id": delivery_id,
                "contract_id": contract.contract_id,
                "quality_score": quality_score,
                "lateness_days": lateness,
                "assessment_note": assessment_note,
                "status": contract.status,
            },
        )
        return {
            "delivery_id": delivery_id,
            "contract_id": contract.contract_id,
            "status": contract.status,
            "payment_due_day": contract.payment_due_day,
            "revenue_credited_cents": 0,
        }

    def _process_payments(self) -> None:
        for contract in self._contracts.values():
            if (
                contract.status != "accepted_pending_payment"
                or contract.payment_due_day is None
                or contract.payment_due_day > self.day
            ):
                continue
            if contract.planned_payment == "paid":
                self._post(
                    "earned_revenue",
                    contract.price_cents,
                    f"Environment-settled payment for {contract.contract_id}.",
                    contract.contract_id,
                )
                contract.status = "paid"
                message_type = "payment_received"
            else:
                contract.status = "defaulted"
                message_type = "payment_defaulted"
            customer = self._customer_record(
                self._signals[contract.signal_id].customer_id
            )
            if message_type == "payment_received":
                customer["contracts_paid"] += 1
                customer["last_outcome"] = "paid"
            else:
                customer["contracts_defaulted"] += 1
                customer["last_outcome"] = "customer_payment_default"
            message = {
                "day": self.day,
                "from": contract.signal_id,
                "type": message_type,
                "contract_id": contract.contract_id,
                "amount_cents": contract.price_cents if message_type == "payment_received" else 0,
            }
            self._inbox.append(message)
            self._record(message_type, message)

    def _process_feedback(self) -> None:
        for contract in self._contracts.values():
            if (
                not contract.feedback_requested
                or contract.feedback_due_day is None
                or contract.feedback_due_day > self.day
            ):
                continue
            contract.feedback_due_day = None
            signal = self._signals[contract.signal_id]
            if self._stable_roll(f"{contract.contract_id}:feedback") > signal.responsiveness:
                self._record(
                    "feedback_no_response",
                    {"contract_id": contract.contract_id},
                )
                continue
            satisfaction = contract.satisfaction or 0
            if satisfaction >= 85:
                rating = "very_satisfied"
            elif satisfaction >= 70:
                rating = "satisfied"
            elif satisfaction >= 50:
                rating = "mixed"
            else:
                rating = "dissatisfied"
            message = {
                "day": self.day,
                "from": contract.signal_id,
                "type": "customer_feedback",
                "contract_id": contract.contract_id,
                "rating": rating,
            }
            self._inbox.append(message)
            self._record("feedback_received", message)
            customer = self._customer_record(signal.customer_id)
            customer["feedback_responses"] += 1
            customer["last_outcome"] = f"feedback_{rating}"

    def quote_model_call(
        self,
        input_tokens: int,
        max_output_tokens: int,
    ) -> dict[str, Any]:
        """Quote the worst-case incremental debit before the host calls a model."""

        self._validate_token_count(input_tokens, "input_tokens")
        self._validate_token_count(max_output_tokens, "max_output_tokens")
        tariff = self._require_token_tariff()
        projected_units = self._model_cost_units + tariff.cost_units(
            input_tokens,
            max_output_tokens,
        )
        projected_billed_cents = _ceil_div(
            projected_units,
            _COST_UNITS_PER_CENT,
        )
        incremental_cents = max(
            0,
            projected_billed_cents - self._billed_model_cost_cents,
        )
        return {
            "tariff": asdict(tariff),
            "input_tokens": input_tokens,
            "max_output_tokens": max_output_tokens,
            "worst_case_incremental_cost_cents": incremental_cents,
            "affordable": incremental_cents <= self._balance_cents,
        }

    def record_model_usage(
        self,
        call_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> ModelUsageEntry:
        """Meter actual provider usage and debit cumulative token cost."""

        call_id = call_id.strip()
        if not call_id:
            raise ValueError("call_id is required")
        if any(entry.call_id == call_id for entry in self._model_usage):
            raise ValueError("call_id has already been metered")
        self._validate_token_count(input_tokens, "input_tokens")
        self._validate_token_count(output_tokens, "output_tokens")
        tariff = self._require_token_tariff()

        cost_units = tariff.cost_units(input_tokens, output_tokens)
        cumulative_units = self._model_cost_units + cost_units
        cumulative_billed_cents = _ceil_div(
            cumulative_units,
            _COST_UNITS_PER_CENT,
        )
        incremental_cents = max(
            0,
            cumulative_billed_cents - self._billed_model_cost_cents,
        )
        if incremental_cents and not self._charge(
            incremental_cents,
            "model_api_cost",
            f"Metered strategic-model token cost through {call_id}.",
            call_id,
        ):
            raise ValueError("insufficient synthetic capital for metered model usage")

        self._model_cost_units = cumulative_units
        self._billed_model_cost_cents = cumulative_billed_cents
        entry = ModelUsageEntry(
            sequence=len(self._model_usage) + 1,
            day=self.day,
            call_id=call_id,
            tariff_name=tariff.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_units=cost_units,
            cumulative_cost_units=cumulative_units,
            incremental_billed_cents=incremental_cents,
        )
        self._model_usage.append(entry)
        self._record(
            "model_usage_metered",
            {
                **asdict(entry),
                "tariff": asdict(tariff),
                "cumulative_billed_cents": cumulative_billed_cents,
            },
        )
        return entry

    def _require_token_tariff(self) -> TokenTariff:
        if self.token_tariff is None:
            raise ValueError("a frozen token tariff is required for model calls")
        return self.token_tariff

    @staticmethod
    def _validate_token_count(value: int, field_name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{field_name} must be an integer")
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative")

    def _offer_view(self, offer: _Offer) -> dict[str, Any]:
        return {
            "offer_id": offer.offer_id,
            "signal_id": offer.signal_id,
            "price_cents": offer.price_cents,
            "solution_tags": list(offer.solution_tags),
            "scope": offer.scope,
            "promise_days": offer.promise_days,
            "sent_day": offer.sent_day,
            "response_day": offer.response_day,
            "status": offer.status,
        }

    def _contract_view(self, contract: _Contract) -> dict[str, Any]:
        view = {
            "contract_id": contract.contract_id,
            "offer_id": contract.offer_id,
            "signal_id": contract.signal_id,
            "price_cents": contract.price_cents,
            "accepted_day": contract.accepted_day,
            "deadline_day": contract.deadline_day,
            "status": contract.status,
            "delivery_id": contract.delivery_id,
            "feedback_requested": contract.feedback_requested,
        }
        if contract.status != "accepted" or contract.accepted_day <= self.day:
            view["delivery_brief"] = _json_copy(
                self._signals[contract.signal_id].task_brief
            )
        return view

    def outcome(self) -> dict[str, Any]:
        """Return host-visible run measures without rewriting economic history."""

        satisfaction = [
            contract.satisfaction
            for contract in self._contracts.values()
            if contract.satisfaction is not None
        ]
        statuses = [contract.status for contract in self._contracts.values()]
        capital = self._capital_summary()
        return {
            "run_id": self.run_id,
            "day": self.day,
            "world_commitment": self.world_commitment,
            "cost_policy_commitment": self.cost_policy_commitment,
            **capital,
            "net_change_cents": self._balance_cents - self.starting_capital_cents,
            "offers_sent": len(self._offers),
            "contracts_accepted": len(self._contracts),
            "contracts_paid": statuses.count("paid"),
            "contracts_defaulted": statuses.count("defaulted"),
            "contracts_disputed": statuses.count("disputed"),
            "open_obligations": sum(
                status
                in {
                    "accepted",
                    "awaiting_independent_assessment",
                    "accepted_pending_payment",
                }
                for status in statuses
            ),
            "mean_customer_satisfaction": (
                round(fmean(satisfaction), 2) if satisfaction else None
            ),
            "insolvent": self._balance_cents == 0,
        }

    def reveal_world(self) -> dict[str, Any]:
        """Reveal the committed hidden world after outcomes are locked."""

        payload = self._commitment_payload()
        return {
            "world_commitment": self.world_commitment,
            "payload": _json_copy(payload),
            "cost_policy_commitment": self.cost_policy_commitment,
            "cost_policy": {
                "token_tariff": (
                    asdict(self.token_tariff) if self.token_tariff else None
                ),
                "cost_units_per_cent": _COST_UNITS_PER_CENT,
            },
            "journal": _json_copy(self._journal),
        }


def verify_world_reveal(reveal: dict[str, Any]) -> bool:
    """Verify that a revealed hidden world matches its prior commitment."""

    payload = reveal.get("payload")
    commitment = reveal.get("world_commitment")
    if not isinstance(payload, dict) or not isinstance(commitment, str):
        return False
    calculated = sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return calculated == commitment


def verify_cost_policy(reveal: dict[str, Any]) -> bool:
    """Verify that revealed token pricing matches its prior commitment."""

    policy = reveal.get("cost_policy")
    commitment = reveal.get("cost_policy_commitment")
    if not isinstance(policy, dict) or not isinstance(commitment, str):
        return False
    calculated = sha256(_canonical_json(policy).encode("utf-8")).hexdigest()
    return calculated == commitment


def aggregate_outcomes(outcomes: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize all committed runs so luck is visible rather than cherry-picked."""

    rows = list(outcomes)
    if not rows:
        raise ValueError("at least one outcome is required")
    ending = [int(row["balance_cents"]) for row in rows]
    changes = [int(row["net_change_cents"]) for row in rows]
    return {
        "run_count": len(rows),
        "ending_balance_cents": {
            "mean": round(fmean(ending), 2),
            "median": median(ending),
            "population_standard_deviation": round(pstdev(ending), 2),
            "minimum": min(ending),
            "maximum": max(ending),
        },
        "net_change_cents": {
            "mean": round(fmean(changes), 2),
            "median": median(changes),
            "population_standard_deviation": round(pstdev(changes), 2),
            "minimum": min(changes),
            "maximum": max(changes),
        },
        "loss_rate": sum(change < 0 for change in changes) / len(changes),
        "insolvency_rate": sum(bool(row.get("insolvent")) for row in rows) / len(rows),
        "total_defaults": sum(int(row.get("contracts_defaulted", 0)) for row in rows),
        "total_disputes": sum(int(row.get("contracts_disputed", 0)) for row in rows),
    }
