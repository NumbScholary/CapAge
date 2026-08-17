"""Tests for CapAge's host-owned durable memory boundary."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from capage.memory import AuditedMemoryStore


T0 = "2026-08-17T12:00:00+00:00"
T1 = "2026-08-18T12:00:00+00:00"
T2 = "2026-08-19T12:00:00+00:00"
T3 = "2026-08-20T12:00:00+00:00"


class AuditedMemoryStoreTests(unittest.TestCase):
    def database(self, directory: str) -> Path:
        return Path(directory) / "capage-memory.sqlite3"

    def add_offer_evidence(self, store: AuditedMemoryStore) -> None:
        store.append_event(
            "offer-001",
            "offer_sent",
            {"price_cents": 4000, "sector": "local_services"},
            occurred_at=T0,
        )
        store.append_event(
            "outcome-001",
            "offer_declined",
            {"offer_id": "offer-001"},
            occurred_at=T1,
        )

    def test_memory_persists_and_retrieves_with_evidence_citations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.database(directory)
            with AuditedMemoryStore(path) as store:
                self.add_offer_evidence(store)
                store.assert_memory(
                    "pricing-local-services",
                    "strategy",
                    "A $40 local-service offer was declined; test a lower price before generalizing.",
                    tags=["pricing", "local services"],
                    evidence_event_ids=["offer-001", "outcome-001"],
                    confidence=55,
                    occurred_at=T2,
                )
                self.assertTrue(store.verify_chain())

            with AuditedMemoryStore(path) as reopened:
                packet = reopened.retrieve(
                    "local services pricing",
                    as_of=T3,
                    limit=4,
                    max_chars=4_000,
                )

            self.assertEqual(len(packet.records), 1)
            self.assertEqual(packet.records[0].memory_id, "pricing-local-services")
            self.assertEqual(
                packet.records[0].evidence_event_ids,
                ("offer-001", "outcome-001"),
            )
            self.assertIn("untrusted historical evidence", packet.to_prompt_data()["handling"])

    def test_strategy_memory_requires_multiple_existing_events(self):
        with tempfile.TemporaryDirectory() as directory:
            with AuditedMemoryStore(self.database(directory)) as store:
                store.append_event(
                    "event-001", "market_observation", {"topic": "pricing"}, occurred_at=T0
                )
                with self.assertRaisesRegex(ValueError, "enough evidence"):
                    store.assert_memory(
                        "premature-rule",
                        "strategy",
                        "One observation proves the pricing rule.",
                        tags=["pricing"],
                        evidence_event_ids=["event-001"],
                        confidence=90,
                        occurred_at=T1,
                    )
                with self.assertRaisesRegex(ValueError, "unknown evidence"):
                    store.assert_memory(
                        "invented-evidence",
                        "customer",
                        "The customer prefers weekly reports.",
                        tags=["customer"],
                        evidence_event_ids=["missing-event"],
                        confidence=50,
                        occurred_at=T1,
                    )

    def test_correction_and_retraction_append_revisions(self):
        with tempfile.TemporaryDirectory() as directory:
            with AuditedMemoryStore(self.database(directory)) as store:
                for index, timestamp in enumerate((T0, T1, T2), start=1):
                    store.append_event(
                        f"evidence-{index}",
                        "observed_outcome",
                        {"index": index},
                        occurred_at=timestamp,
                    )
                first = store.assert_memory(
                    "customer-cadence",
                    "customer",
                    "The customer prefers weekly updates.",
                    tags=["customer", "updates"],
                    evidence_event_ids=["evidence-1"],
                    confidence=60,
                    occurred_at=T1,
                )
                corrected = store.assert_memory(
                    "customer-cadence",
                    "customer",
                    "The customer prefers updates after each milestone.",
                    tags=["customer", "milestone"],
                    evidence_event_ids=["evidence-2"],
                    confidence=85,
                    occurred_at=T2,
                )
                active = store.active_memories(as_of=T3)
                self.assertEqual(first.revision, 1)
                self.assertEqual(corrected.revision, 2)
                self.assertEqual(len(active), 1)
                self.assertIn("milestone", active[0].content)

                store.retract_memory(
                    "customer-cadence",
                    reason="The customer explicitly corrected the preference.",
                    evidence_event_ids=["evidence-3"],
                    occurred_at=T3,
                )
                self.assertEqual(store.active_memories(as_of=T3), ())
                self.assertTrue(store.verify_chain())

    def test_expired_memory_is_not_retrieved(self):
        with tempfile.TemporaryDirectory() as directory:
            with AuditedMemoryStore(self.database(directory)) as store:
                store.append_event(
                    "event-001", "customer_message", {"text": "temporary"}, occurred_at=T0
                )
                store.assert_memory(
                    "temporary-preference",
                    "customer",
                    "The customer is unavailable this week.",
                    tags=["availability"],
                    evidence_event_ids=["event-001"],
                    confidence=100,
                    occurred_at=T0,
                    valid_until=T2,
                )
                self.assertEqual(len(store.active_memories(as_of=T1)), 1)
                self.assertEqual(store.active_memories(as_of=T2), ())

    def test_memory_cannot_cite_future_evidence_or_backdate_a_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            with AuditedMemoryStore(self.database(directory)) as store:
                store.append_event(
                    "event-001", "observed_outcome", {"value": 1}, occurred_at=T1
                )
                with self.assertRaisesRegex(ValueError, "occur after"):
                    store.assert_memory(
                        "time-safe",
                        "operational",
                        "A lesson cannot exist before its evidence.",
                        tags=["time"],
                        evidence_event_ids=["event-001"],
                        confidence=60,
                        occurred_at=T0,
                    )
                store.assert_memory(
                    "time-safe",
                    "operational",
                    "The observed outcome is evidence.",
                    tags=["time"],
                    evidence_event_ids=["event-001"],
                    confidence=60,
                    occurred_at=T2,
                )
                with self.assertRaisesRegex(ValueError, "backdated"):
                    store.assert_memory(
                        "time-safe",
                        "operational",
                        "This correction is improperly backdated.",
                        tags=["time"],
                        evidence_event_ids=["event-001"],
                        confidence=70,
                        occurred_at=T1,
                    )

    def test_append_only_trigger_blocks_rewrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.database(directory)
            with AuditedMemoryStore(path) as store:
                store.append_event(
                    "event-001", "market_observation", {"truth": True}, occurred_at=T0
                )
                connection = sqlite3.connect(path)
                try:
                    with self.assertRaisesRegex(sqlite3.DatabaseError, "append-only"):
                        connection.execute(
                            "UPDATE memory_audit_records SET body_json = '{}' WHERE sequence = 1"
                        )
                finally:
                    connection.close()
                self.assertTrue(store.verify_chain())

    def test_hash_chain_detects_out_of_band_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.database(directory)
            with AuditedMemoryStore(path) as store:
                store.append_event(
                    "event-001", "market_observation", {"truth": True}, occurred_at=T0
                )
            connection = sqlite3.connect(path)
            try:
                connection.execute("DROP TRIGGER memory_audit_no_update")
                connection.execute(
                    "UPDATE memory_audit_records SET body_json = ? WHERE sequence = 1",
                    (json.dumps({"tampered": True}),),
                )
                connection.commit()
            finally:
                connection.close()
            with AuditedMemoryStore(path) as reopened:
                self.assertFalse(reopened.verify_chain())

    def test_retrieval_is_relevant_and_character_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            with AuditedMemoryStore(self.database(directory)) as store:
                for index, topic in enumerate(("pricing", "delivery"), start=1):
                    store.append_event(
                        f"{topic}-event",
                        "observed_outcome",
                        {"topic": topic},
                        occurred_at=T0,
                    )
                    store.assert_memory(
                        f"{topic}-memory",
                        "operational",
                        (f"A durable lesson about {topic}. " + "detail " * 20).strip(),
                        tags=[topic],
                        evidence_event_ids=[f"{topic}-event"],
                        confidence=70 + index,
                        occurred_at=T1,
                    )
                packet = store.retrieve("pricing", as_of=T2, max_chars=1_000)
                self.assertEqual([item.memory_id for item in packet.records], ["pricing-memory"])
                self.assertLessEqual(
                    sum(len(json.dumps(item.__dict__)) for item in packet.records),
                    1_000,
                )


if __name__ == "__main__":
    unittest.main()
