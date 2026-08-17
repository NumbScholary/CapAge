# CapAge Audited Memory v1

## Purpose

CapAge's durable memory belongs to the host application, not to any particular
language model. A replacement model can therefore inherit verified business
history without inheriting hidden model state or being allowed to rewrite the
past.

## Trust boundary

`AuditedMemoryStore` is never registered as an agent tool. Trusted host code
records observable events and decides whether a proposed lesson satisfies the
memory policy. Retrieved memories are labeled untrusted historical evidence;
they cannot override the current ledger, obligations, policy, or tool results.

## Record model

Events and memory revisions share one append-only SQLite audit stream. Every
record contains the previous record's SHA-256 hash. Database triggers block
updates and deletions, while full-chain verification detects out-of-band
tampering.

Memory assertions include:

- a stable memory identifier and revision number;
- a bounded category, statement, and tag set;
- citations to immutable evidence events;
- host-validated confidence;
- an optional expiration time.

Strategy memories require at least two evidence events. Corrections append a
new assertion under the same identifier. Retractions also append a revision,
so the original statement and the reason it was withdrawn remain auditable.

## Retrieval

Retrieval filters expired and retracted assertions, ranks remaining records by
query relevance, confidence, and sequence, and enforces record-count and
character budgets before data is placed in a model context. Every packet carries
the current audit-chain head hash and the evidence identifiers for each record.

## Explicit non-goals

Memory v1 does not modify model weights, create autonomous memory-write tools,
or yet carry state between sandbox months. The next milestone will connect this
host-owned store to a longitudinal runner and compare matched memory-enabled and
memoryless trajectories.
