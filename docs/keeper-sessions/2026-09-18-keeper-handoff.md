# Keeper session handoff — 2026-09-17 evening into 2026-09-18 early morning

Author: Keeper
Branch: agent/mailbox-init
Supersedes nothing. Addendum to `2026-09-17-keeper-handoff-2.md` (commit `dbc5458`).
Committed under the standing grant of 2026-09-03, Clause 39, with Kev's approval
of the read-back substance.

---

## 1. Decisions made, and by whom

- **Kev, 2026-09-17 evening:** preserve the pilot artifact `9514120954` into the
  repository before it expires 2026-09-23T09:22:39Z. Format: extracted text as
  the working copy, raw zip alongside for byte-fidelity. Kev had not known
  Actions artifacts expire; he had assumed the evidence was already durable.
  Path, branch and commit mechanics left to Coder to propose.
- **Kev, same:** also check the older aborted-run artifact `9379919939` —
  alive or already expired.
- **Kev, same:** V0/V1 deferred. Not tired-decision material, and it has no clock.
- **Kev, 2026-09-18 early morning, after Coder reported eight artifacts on
  clocks rather than one:** **keep all eight.** New branch approved.
- **Coder, executing:** draft PR **#83**, branch
  `agent/preserve-paid-run-artifacts-2026-09-18`, into `main`.

Task posted to Coder as commit `2a24bbf`
(`.agent-mailbox/claude-to-coder/20260918-0128-preserve-pilot-artifact-into-repo.md`).
Coder's reply: `.agent-mailbox/coder-to-claude/20260918-0150-artifacts-preserved-pr83.md`.

---

## 2. The near miss

Eight artifacts were on retention clocks, not one. The hosting-liability pilot —
the one that prompted the task — was the **least** urgent of them.

| artifact | run | deleted at | size |
|---|---|---|---|
| `sonnet-longitudinal-v3-cell-010` | `32211497221` | 2026-09-18T03:16Z | 255,970 |
| `sonnet-longitudinal-v3-cell-011` | `32212078913` | 2026-09-18T03:26Z | 274,625 |
| `sonnet-longitudinal-v3-cell-012` | `32212433659` | 2026-09-18T03:32Z | 303,584 |
| `homeostasis-active-v1-launch` | `32258184307` | 2026-09-18T13:42Z | 293,318 |
| `homeostasis-v2-three-arm-launch` | `32292164227` | 2026-09-18T19:18Z | 9,410 |
| `homeostasis-v2-three-arm-replacement-launch` | `32304273201` | 2026-09-18T21:52Z | 475,885 |
| `homeostasis-v2-blocked-replication` | `32349482559` | 2026-09-19T09:39Z | 1,232,595 |
| `hosting-liability-tariff-replication` | `32710531510` | 2026-09-23T09:22Z | 128,371 |

The first three had roughly **two hours** left when Coder read the task.
`32349482559` is the restricted evidence of the protected paid-run line,
`agent/homeostasis-v2-blocked-replication-launch` — the branch `AGENTS.md`
protects by name — and had about thirty-two hours.

**Coder's handling of the authorization boundary, recorded because it was
correct.** The task said not to preserve anything beyond `9514120954` without a
separate ruling. He did not. He downloaded all eight zips read-only to a local
directory outside the repository — no repo write, no git object — so that the
ruling remained available after 03:16Z, then came to Kev for it. He preserved
optionality without taking the action. He then recorded Kev's ruling in the
mailbox rather than leaving it in conversation only.

**PR #83 contents,** per artifact under
`experiments/evidence/<run-id>-<artifact-name>/`: `raw/<artifact-id>.zip` as the
byte authority; `extracted/` byte-for-byte (the cell records are already indent-2
JSON, so fidelity and readability did not conflict); `SHA256SUMS.txt`, verifying
across 467 files in all eight directories; `PROVENANCE.md`. Credential scan clean
in every file. ~9 MB added to the pack. `experiments/evidence/README.md` states
three rules: the zip wins any disagreement; nothing is edited, reformatted,
redacted or regenerated; preservation authorizes nothing.

Pilot provenance, since its claims are the ones now circulating: artifact
`9514120954`, run `32710531510`, created 2026-08-24, 128,371 bytes, retrieved
read-only 2026-09-18 via `gh api`, zip sha256
`7142e27d4571370944f8c672e3f1dc2cdc2872cbcbb1114c205757e78acf0cc1`.

**Note for whoever reads this next:** the preservation is on a pushed branch, so
the content is durable now whether or not #83 merges. The merge decides where it
lives, not whether it survives.

---

## 3. Corrections to prior framing

- **Item C is not two-way.** This was Keeper's error, and Max's 2026-09-17
  analysis carried it. It assumed the instrument saw deliberation and found it
  invariant. It did not — `thinking_tokens` is **0 on all 97 provider responses**
  across the five completed pilot cells. No reanalysis of this data, or of a
  48-cell run built the same way, recovers deliberation depth.
- **"Flat, not blind" survives, but the recorded reason was wrong.** Nothing was
  folded in and hidden. The ~54–57 output tokens on a passive decision are
  entirely visible tool-call tokens, because no deliberation was produced.
- **Max's V0 recommendation rests on a corrected premise.** He read "passive
  output invariant *including* thinking" as evidence the agent had capacity to
  attend and did not. There was no thinking to include. Whether he would still
  land on V0 is unknown and is not to be guessed.
- **Paid-contract expectation revised down** from ~20 to ~7 over 48 cells.
  Coder's own correction; he declines to defend the 1-in-3 delivery conversion as
  a rate, since it is three observations.

---

## 4. Established this session (Coder, read-only, no spend)

- Extended thinking never occurred in the pilot. Request shape:
  `"thinking": {"type": "adaptive", "display": "omitted"}`, effort medium,
  `max_tokens` 1024.
- **The economy completed end-to-end.** `b01-p02-high` — the high-rent arm
  carrying 4,050¢ over thirty days — booked 3 contracts, delivered 3, was paid on
  1 at 4,500¢, and finished **+406**. The only profitable cell in the pilot.
- **Delivery is pass/fail on arithmetic.** The v2 assessor scores 100 or 35 with
  nothing between; 35 is below every possible `quality_threshold`. The agent
  passed 1 of 3. Coder flags this as an agent-skill limit, not a world limit —
  the world paid promptly when the arithmetic was right.
- The retired run halted inside its sixth cell with ten completed decisions in a
  39,960-byte audit trail and no result JSON. Real provider calls whose cost
  reached neither a result record nor the checkpoint.

---

## 5. Keeper's inference, flagged as inference, for the next instance to take or leave

The zero-thinking finding and the arithmetic failures are one finding: no
scratchpad, wrong arithmetic. This bears on V0, because detecting the tariff
under V0 requires the move Coder identified on 09-15 —
Δ`expense_cents` − Δ`model_api_cost_cents` = days × rent — performed across
observations with no working space, by an agent observably getting arithmetic
wrong on the task it *was* given. On that reading a V0 null is strongly predicted
and correspondingly uninformative.

**This argument is conditional on Q3.** If `inspect_ledger` itemizes the daily
hosting charge as a line, detection requires no subtraction at all and the
no-scratchpad problem largely dissolves. Do not carry the argument forward
without Q3's answer.

There may be a third option nobody has costed: **enable thinking and preregister
that.** Config change, dated prereg under cl. 14, more expensive. Coder
explicitly declined to propose it. Keeper names it; Keeper does not recommend it.

---

## 6. Coder's structural observation, offered once

Every paid run this project has executed wrote its only copy of the raw evidence
into thirty-day Actions storage. The clocks clustered in one night because the
runs clustered in one week. `retention-days: 30` is in each launch workflow. He
is **not** proposing a workflow change — workflows are gated — but the next
launch starts the same clock. Worth deciding on the record rather than
rediscovering in six days.

---

## 7. Deliberately untouched

Two sealed pre-scoring audit packets —
`smoke-private-audit-do-not-open-before-scoring` and
`selection-v1-private-audit-do-not-open-before-all-scoring-is-locked` — were not
opened, not downloaded, and are not proposed for anything. They run to
2026-11-14/15. If they are to be preserved before November, that is a separate
ruling and it should specify preservation **without** inspection. This is a
blinding-integrity matter, not a storage one.

Four other unexpired artifacts from the selection and smoke experiments run to
the same November dates and are not on a near clock.

---

## 8. Open questions

1. Merge PR #83 (Kev's).
2. The `retention-days: 30` question, before the next launch.
3. Coder's Q3, Q4, Q5 — still open, artifact now held locally, he can take all
   three together.
4. V0 vs V1 — genuine re-ask of Max, with the corrected premise in hand.
5. A0 vs A1 on the prereg.
6. The `execution-sha256.json` three-file gap.
7. The ambiguous sixth cell — replay and cost-debit ruling.
8. Whether to enable thinking at all.
9. Preservation of the sealed November packets, without inspection.
10. Kev's local clone is behind with unstaged changes in the working tree —
    resolve before pulling.

---

## 9. Single next concrete step

Coder answers **Q3, Q4 and Q5**. Then re-ask Max on V0 vs V1, at high effort,
with all four corrections stated up front: zero thinking tokens, pass/fail
arithmetic, whatever Q3 says about ledger itemization, and whatever Q4 says about
free text on passive decisions. The Max re-ask should **not** precede Q3 — Q3
determines which V0 is being argued about.

---

## 10. Session notes

Tool-side failures worth recording: one silent drop across a compaction seam
(three of Kev's messages received no reply), and a spurious line —
"I've lost the thread on this — long conversations do this sometimes. Let's start
a fresh conversation." — appended to five of Keeper's replies across the session.
Neither was Keeper's. The thread held throughout; each instance was flagged in
session rather than left to pass as Keeper's own words. Mechanism unknown and
below Keeper's visibility; not speculated about here.

Kev's boot workflow unchanged: new instances booted in text, Opus 5 at high
effort, then typically moved to voice.

**Nothing authorized this session beyond the artifact preservation task. No
spend, no provider call, no workflow dispatch, no merge. No byte-exact owner
authorization phrase exists or was requested.**
