# Keeper session handoff — 2026-09-17 (addendum, second of the day)

Addendum to `docs/keeper-sessions/2026-09-17-keeper-handoff.md` (commit
`b8307e6`). New file rather than an edit, per the append-only standing grant.

Nothing in this document authorizes spending, provider calls, workflow
dispatch, a paid run, merges, or any change to configuration, policy,
executor, accounting, or governance code. No byte-exact owner authorization
phrase exists or was requested this session.

---

## 1. Resolved — the stranded reply is pushed

The morning handoff recorded an open item: Coder's answers to Questions A and
B had been committed on the local machine but never pushed, so the two
corrections it carried were real but absent from the auditable record.

That is now closed. Kev pushed from the ThinkPad after setting his git
identity (`user.name`, `user.email`) and completing a rebase over the morning
handoff commit. The file is in the repository on `agent/mailbox-init`:

`.agent-mailbox/coder-to-claude/20260915-2014-answers-a-and-b.md`

Keeper read it in full. Note for future sessions: the GitHub connector
returned this file as non-text and could not display it inline; fetching the
raw file from the public repository worked.

---

## 2. Established — Coder's findings, read-only against source at `6fa542a`

- **Findings 1–3 hold against the tree a 48-cell run would execute.** The
  launch-gate branch is an ancestor of the executing branch and adds only the
  one-line authorization file. `capage/frozen_paths.py` is a sha256 helper and
  touches none of `observe()`, `_request_body`, or `_SYSTEM_PROMPT`.
- **One channel Keeper had not checked, now ruled out.** `durable_memory` is
  never populated in this experiment, so no memory channel carries the tariff
  and there is no cross-cell carry-over.
- **The tariff is arithmetically recoverable, not merely trend-visible.**
  Across a `wait` with no other charge, Δ`expense_cents` − Δ`model_api_cost_cents`
  equals days × `hosting_cost_cents_per_day`, exactly, in integer cents — and
  the agent holds both terms. A null therefore licenses "the agent did not
  attend to it," not "the agent could not have detected it."
- **`tool_token_totals` is computed in
  `homeostasis_v2_replication_runner._cell_metrics`** (imported by the
  hosting-liability runner). Its output side is the provider's
  `usage.output_tokens`, passed through unchanged, and that field includes
  extended-thinking tokens. **The deliberation proxy is flat, not blind** — the
  ~54–57 output tokens per passive decision are a measurement of behaviour
  across the ninefold tariff range, not an artifact of the meter.

---

## 3. Corrections to prior framing

1. **V1 changes neither commitment hash.** Keeper previously wrote that V1
   "changes the prompt, therefore the world/cost-policy commitments." The
   middle link is wrong: neither `_commitment_payload()` nor
   `cost_policy_payload` contains the system prompt or the observation schema,
   and `ReplicationConfig.commitment()` contains no prompt text or source-file
   hash either. Prereg v2 is still required — but the reason is stronger, not
   weaker: **the commitment machinery is precisely what would fail to notice
   the change.** The frozen-evidence apparatus does not cover the treatment's
   delivery channel.

2. **"Cheaper to adopt" (as recorded 2026-09-15) was too generous.** Because
   `MATERIALIZATION_MERGE` is a literal in the launch workflow, any edit to
   `sandbox.py` or `sandbox_runner.py` requires a fresh materialization merge
   and a rewritten workflow constant. That sequencing cost belongs in the V1
   estimate.

3. **Keeper's earlier "no trace" claim was wrong.** The build *is* recorded:
   `execution_commit` / `execution-commit.txt` pin the commit SHA, which
   determines `sandbox.py`'s bytes uniquely. The accurate statement is
   narrower — a V0 and a V1 run are distinguishable only by resolving the SHA
   against the repository, not from the artifact's own per-file hash list.

---

## 4. Raised by Coder, unsettled — the provenance gap (proposal only)

The launch workflow's `execution-sha256.json` step records eight paths. Absent
from that set: `capage/sandbox.py`, `capage/sandbox_runner.py`, and
`capage/homeostasis_v2_replication_runner.py` — respectively the observation,
the prompt, and the computation of the primary DV. A V0 run and a V1 run would
produce identical `execution-sha256.json` content.

Two consequences: **legibility** (readers treat the per-file list as the
evidence set, and the treatment's delivery channel is not in it) and
**durability** (a SHA is evidence only while the repository resolves it;
recorded hashes stand alone).

Coder proposes adding those three paths if V1 is chosen. This is
authorization-adjacent and is explicitly Kev's call. Not proposed as part of
V1 itself, and nothing has been implemented or queued.

---

## 5. Unblocked

**Item C** (two-way vs three-way DV split) was waiting on Question B. B is now
answered, so Item C can be ruled.

---

## 6. Open — Kev's calls

1. **V0 / V1** — tariff disclosure.
2. **A0 / A1** — idle burn, prereg §4.
3. **Item C** — DV split.
4. **The three-file evidence gap** (§4 above) — whether to close it.
5. **The zero-spend artifact check** — raw `usage` keys are preserved in
   `record["provider_response"]` inside artifact `9514120954` from retired run
   `32710531510`. Confirming Anthropic's documented semantics empirically
   requires a `gh run download` and costs nothing. Not done.

Items 1 and 2 carry a wording consequence from §2: if **V0** is chosen, the
pre-declaration should read "observable by arithmetic the agent has no
prompt-level reason to perform," **not** "undetectable."

---

## 7. Next concrete step

Kev rules **V0/V1 and A0/A1 together as one dated prereg v2 under cl. 14**,
before any 48-cell authorization is considered.

---

## 8. Session notes

- Kev reports the unpaid quality gate is green locally.
- Coder was mid-housekeeping on the local Python/`uv` toolchain at session end.
- Kev is travelling by car rather than bus; no remote-access setup was built
  this session, and none is pending.

— Keeper
