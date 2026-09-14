# Keeper Handoff — 2026-09-14

Recorded by Keeper. Substance read back to Kev by voice and approved before commit,
per the standing grant of 2026-09-03 (Clause 39).

---

## 1. Tariff expiry blocker — CLEARED

**[DECISION — Kev, by voice, 2026-09-14]** Route B authorized for the tariff
sentinel: a new plan file rather than editing the completed run's frozen input.
Value `9999-12-31`. Kev's reasoning for a far-future date rather than removing
the field: removing it changes the schema everything else validates against.
The field stays, the guard stays, the date never arrives. **The guard is not
softened.**

**[CURRENT STATE — verified by Coder file-by-file on `agent/hosting-liability-cell6-debug`
at `dd70543`]**

- PR #81 merged, along with #73, #78, #80.
- `hosting_liability_tariff_replication_plan_v2.json`, sha256 `bca619372278a6e1…`,
  `valid_through 9999-12-31`.
- Plan v1 untouched: sha256 `382001b101df3ac6…`, `valid_through 2026-08-31`.
- `PLAN_PATH` resolves to v2. Guard verdict `expired=False` today, where v1 read True.
- Suite: 253 tests, 0 failures. (10 local-only `test_transfer` errors are a
  Python 3.13-vs-3.12 artifact, absent in CI.)
- Section 6 caps unchanged: $0.45 per cell, $21.60 aggregate.
- Recorded, not worked around: a v1 checkpoint cannot resume under v2, since
  `plan_sha256` and `config_commitment` both changed as predicted.

**[NOTE — Kev merged #81 over a red check]**, before reading Coder's explanation.
Defensible only because Coder had already diagnosed the red as inherited from the
base branch — but it was an override, not a passing check. Recorded as such.

**State change:** tariff expiry no longer stops a 48-cell run. The only remaining
barrier is the byte-exact owner authorization phrase, which does not exist and was
not requested.

---

## 2. Correction — the repository is PUBLIC

Prior handoffs describe `NumbScholary/CapAge` as private. **That is false and has
been.** Verified 2026-09-14 by direct API check: `visibility: public`, `private: false`.

Public visibility is deliberate on Kev's part. The error was in the record, not in
the repository settings. Anything previously written on the assumption of privacy
was written on a wrong premise.

---

## 3. Standing rule — no third-party personal detail in this repository

**[DECISION — Kev, 2026-09-14]** The repository is public *and* append-only. Those
two properties together mean a line about a third party cannot be withdrawn once
written — only appended to.

The rule, from hence forward:

- The ledger, handoffs, mailbox posts and all committed documents record **money,
  actions, decisions, and their authorization**. Nothing else.
- **No personal details about third parties** — not names attached to personal
  circumstances, not anyone's legal status, situation, or private affairs. Those
  people did not agree to a permanent public record.
- Kev may disclose what he likes about himself in conversation. Conversation is not
  the repository. Personal context stays in the session and in Claude's own memory,
  which is separate from this repository and not public.
- This rule binds Keeper's own drafting first, since the handoff is where session
  detail would otherwise leak in.

---

## 4. Open — carried forward

1. **Harness integrity findings** (`.agent-mailbox/coder-to-claude/20260912-1330-harness-integrity-pass-findings.md`,
   commit `afc1ecc`). Twelve findings A–L. Four that matter:
   - **(A)** prereg §10 validity text contradicts Kev's 0440 ruling; code comment
     still names the old valid set — three records, two rules.
   - **(B)** `from_plan` enforces caps and tariff arms but only *reads* horizon /
     max_decisions / max_output_tokens / model / effort — a new plan could drift
     past both validators.
   - **(C)** the preregistered research question is **token allocation**, not risk
     posture or pricing. **Open — see below.**
   - **(D)** BUSINESS_CONTINUITY's "runner stops at an open obligation" is
     unimplemented in any replication runner.
   - Positives stand: `tool_token_totals` reconciles to outcome totals to the token
     in all five cells. The preregistered primary instrument works.

2. **Item C — a possible three-way split.** [DISCUSSION, not yet a decision] The
   preregistration frames the question as a two-way split: transactional tool use
   versus passive information-gathering. Kev raised a third category tonight —
   **processing**: compute spent reasoning over information already held, as
   distinct from acting or gathering. A hosting tariff charges for all three
   identically, so the open question is whether rent crowds out *deliberation*.
   Kev also noted the recursion: deciding how to allocate is itself an allocation.
   **Nothing sent to Coder on this.** Any change to the preregistered question is
   Kev's to make explicit before it goes anywhere.

3. **The byte-exact authorization phrase** — the only remaining door to a 48-cell
   run. Not requested, not drafted.

4. **Open PRs** #66, #67, #69, #70, #71 — all unmerged.

5. **Residue disposition** — worktrees and bridge script, frozen pending Kev's word.

6. **Graveyard decisions** — undecided.

7. **Phase 1 go/no-change** — undecided. Evidence indicates no world change:
   conversion 13.3% mean, supply abundant and unused; the deficiency is agent
   search behaviour and the prompt.

---

## Next concrete step

Kev decides item C: whether the preregistered research question stands as a
two-way split, or is amended to name processing as a third category. Everything
downstream of the harness findings waits on that.
