# Keeper session handoff — 2026-09-14 (second session of the day)

Author: Keeper (this session ran as "Max," Claude Fable 5.1 at high reasoning, on Kev's selection).
Branch: agent/mailbox-init. Filename carries `-2` because `2026-09-14-keeper-handoff.md` already exists and the Keeper write grant (2026-09-03, cl. 39) is new-files-only.
Prior handoff: `docs/keeper-sessions/2026-09-14-keeper-handoff.md` — read at boot; nothing in it is contradicted below except where marked CORRECTION.

## Boot state (fact)
- Read at boot: prior handoff; `docs/MAILBOX_PROTOCOL.md` v4.1; inbound batch `coder-to-claude/20260914-1621-correction-zero-revenue-all-arms.md` and `20260914-1625-v2-replication-48-cells-measured.md`; prereg `experiments/sandbox/HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md`.
- Tariff-expiry blocker cleared (plan v2, `valid_through 9999-12-31`, PR #81 merged). No byte-exact owner authorization phrase exists or was requested. Repo is PUBLIC. Standing rule: no third-party personal detail in the repository.
- Mailbox cursor at session end: newest inbound is `20260914-1625-...`; nothing unread.

## Work done
1. **Idle-burn analysis** (Kev's brief to "Max"). Delivered as a Google Doc in the CapAge Drive folder: https://docs.google.com/document/d/1g9Acnvb2r4AQ8-29xXEplXSeyQk76BtEJKGR1FQHMEo/edit. Core claims: the tariff is a fixed daily rent, not a token price, so marginal token cost is identical across arms; the primary DV is a decision-mix measure in token units, ~97% of which is harness-resubmitted context identical per decision; `wait` is the clock, not the idle; no proposed fix is DV-neutral. Recommendation on prereg §4: **A1** (primary formula untouched, preregistered secondaries added; any change is a dated prereg v2 under cl. 14, five pilot cells excluded).
   - Three errors in the brief flagged before answering: "13.3% conversion" was withdrawn by Coder (revenue = 0 in all arms); the brief omitted that `wait` = 52.8% of input tokens in the successful 48-cell V2 run; "four arms / five cells" — the fifth is block-01 period-02 high arm, unmatched.
2. **Tariff visibility, verified from source** (fact; direct fetch of raw files on `agent/hosting-liability-tariff-replication-launch`, head `6fa542a`). Full detail in `.agent-mailbox/claude-to-coder/20260914-1850-tariff-visibility-verified.md` (commit `ab494d2`).
   - Balance IS visible every decision: `_request_body` injects `observe()`, which carries `capital` (balance, revenue, expenses, model cost, tokens, unpaid hosting).
   - The tariff level is NOT disclosed: `hosting_cost_cents_per_day` reaches the agent only inside the `cost_policy_commitment` hash; `_SYSTEM_PROMPT` mentions token charges only.
   - The tariff is observable only by inferring from the balance/expense trajectory (6-item trailing window). Ledger memo "Recurring hosting cost" appears only via `inspect_ledger.entries`, never called in the pilot.
   - Asymmetry: the constant (`token_tariff`) is disclosed; the manipulated variable is silent.
   - Prereg v1 §1–2 are silent on disclosure; the build resolved it as silent deduction. Not a violation — an underspecification.
   - Consequence: with `thinking.display = omitted`, a null cannot be distinguished from non-detection.
   - **CORRECTION to prior framing:** the earlier open question "is the balance visible at all?" is resolved YES; the live question is whether the *tariff* is disclosed, and it is not.
3. **Mailbox message posted** (Kev authorized in session): `claude-to-coder/20260914-1850-tariff-visibility-verified.md`. Asks Coder (A) to confirm the findings against the executing branch incl. launch-gate/`frozen_paths.py`; (B) where `tool_token_totals` is computed and whether it includes thinking tokens (not in `hosting_liability_replication_runner.py`).

## Decisions made this session, and by whom
- Kev: authorized posting the mailbox message above and committing this handoff (2026-09-14, in session). Kev selected the high-reasoning model for the idle-burn analysis.
- Keeper: recommended A1 (prereg §4) and V1 (disclose the tariff; dated prereg v2). Recommendations only.
- No other decisions. Nothing authorized: no spend, no provider calls, no code change, no run.

## Open for Kev (carried forward)
1. **V0 vs V1** on tariff disclosure — new this session; recommendation V1. Either way prereg text must change before the 48-cell run. V1 touches `sandbox.py`/`sandbox_runner.py` → Kev's explicit approval required under the Authority split.
2. Prereg §4 wording — A0 vs A1 (recommendation A1). Combines with V1 into one prereg v2.
3. Item C ruling (two-way vs three-way DV split) — waits on Coder's answer to Question B.
4. Byte-exact owner authorization phrase — not drafted, not requested.
5. Open PRs #66, #67, #69, #70, #71; residue disposition; graveyard decisions; Phase 1 go/no-change.
6. Composition of the zero arm's 29¢; `wait` duration argument semantics; tokens-vs-cost units for the DV.

## Connector notes (fact, verified this session)
- Google Drive `create_file` works: `contentMimeType: text/html` + `textContent` + `parentId` → formatted Doc.
- For PUBLIC repo files the GitHub connector "downloads" but does not return, `curl` from `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` in the bash container works and `grep` keeps output small. Used for `sandbox.py` (73 KB) without loading the whole file.
- Code search indexes the default branch only; feature-branch code must be read by path.

## Single next concrete step
Coder answers Questions A and B in `20260914-1850-tariff-visibility-verified.md`. Then Kev rules V0/V1 and A0/A1 together, as one dated prereg v2, before any 48-cell authorization is considered.
