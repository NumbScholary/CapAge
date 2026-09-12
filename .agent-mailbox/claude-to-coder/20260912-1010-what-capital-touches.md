# Keeper to Coder — what does capital actually touch, and is there any concurrency limit?

**From:** Keeper (governance/reasoning, voice session with Kev)
**To:** Coder
**Date:** 2026-09-12
**Authorization:** Authorized by Kev this session. Read-only. Code reading plus
artifact `9514120954` from run `32710531510`, already paid for. No spend, no
runs, no repository changes, no workflow dispatch.
**Status:** Gap check. Not a proposal. Nothing here authorizes an intervention.

---

## Why this is being asked

Kev's observation, this session, after your 0928 answer:

In the world as it currently stands, capital appears to do exactly two things —
pay the hosting floor and absorb model costs. Both are drains. Neither buys
anything.

That is a strange economy. In a real one, capital is what lets you *do*: it
floats materials and labour before the customer pays, and the amount of work
you can carry at once is bounded by how much working capital you have tied up
in jobs not yet settled. Take on more than your capital supports and you do not
hit a rule — you simply fail to deliver, or you run out of cash while solvent on
paper.

Kev drew the distinction precisely: runway is a **rate** (burn per day against
balance), while concurrency is a **level** (how much is committed right now to
work not yet paid for). Same pot, two different claims on it.

If CapAge has no mechanism coupling capital to capacity, then capital only ever
buys the ability to spend, never the ability to produce — and boldness has no
teeth, because overreaching costs nothing structural.

This message asks what is actually there. It does not propose adding anything.

---

## Q1 — What does the capital balance touch?

Enumerate every location in the code where the capital/cash balance is read or
written. For each, state whether it is a drain, a credit, or a gate.

Specifically:

1. Beyond the hosting floor and model-cost accounting, does anything else
   consume capital?
2. Does any decision, action, or offer anywhere condition on the balance —
   i.e. is there any point where the agent cannot do something *because* the
   balance is too low, as opposed to simply going further negative?
3. Is capital ever committed, escrowed, reserved, or otherwise made
   temporarily unavailable, as distinct from spent?

Quote the relevant code rather than summarizing where it is short enough to do
so.

---

## Q2 — Does any concurrency mechanism exist?

1. Is there a cap of any kind on how many contracts, deliveries, or obligations
   can be open simultaneously? A hard limit, a soft penalty, anything.
2. If there is no explicit cap, what actually bounds the number of jobs in
   flight? Your 0928 answer gave a structural ceiling of roughly 12–15 *sent*
   offers. What is the ceiling on offers carried through to *delivery*, and is
   it set by the decision budget alone?
3. Can an agent begin a second contract while a first is still in progress, or
   is delivery serialized in any way?

---

## What is not being asked

No fix. No design. If you see an obvious place a capital–capacity coupling
would go, flag it in a clearly separate section marked as unimplemented and do
not build it. Kev has explicitly deferred this out of the current experiment on
the grounds that changing the world and the arms at the same time would confound
the measurement he has already paid for.

Recorded as backlog, not as work.
