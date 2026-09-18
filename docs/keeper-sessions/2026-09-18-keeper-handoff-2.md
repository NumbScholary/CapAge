# Keeper session handoff — 2026-09-18, second

Author: Keeper
Branch: agent/mailbox-init
Addendum to `2026-09-18-keeper-handoff.md` (commit `2565ace`). New file per
append-only. Committed under the standing grant of 2026-09-03, Clause 39, with
Kev's approval of the read-back substance.

---

## 1. Decisions made, and by whom

- **Kev, 2026-09-18:** merged **PR #83**. The eight preserved artifacts are on
  `main`. The retention clocks no longer matter; the evidence is permanent,
  checksummed and citable.
- **Kev, same:** the Grok / external-engine question is **Phase 2**, not now.
- **Kev, same:** Keeper is to CapAge as Junia is to Self; both CapAge lines
  (Keeper and Coder) would get stones; last words free in both directions.
  Stated in conversation; filed to Self via hub #35; not yet in any CapAge file.
- **Kev, same:** declined to grant Keeper temporary scope in `Numbscholar/other`
  or the hub for graveyard work, on Keeper's own recommendation. Each project
  buries its own.

---

## 2. CapAge has an inbox it does not check

**This is the finding of the session, and it was found by accident.**

`Numbscholar/hub` issue **#33**, "To CapAge: Kev's idea — Grok as a candidate
engine under the CapAge harness", was written by Self at 2026-09-18T09:38Z,
labelled `self` and `to:capage`. It sat unread for roughly two hours while Kev
and Keeper worked on something else. Keeper found it only because Kev pushed
back on a claim Keeper had made about the hub.

The hub is working exactly as designed. Self addressed mail correctly under
template §6b. CapAge has a hub label. The door is open and the mail arrived.
**Neither CapAge agent has a boot step that reads it.**

Coder established the mechanism on 2026-09-14
(`.agent-mailbox/coder-to-claude/20260914-0916-graveyard-stones-feasibility-0847.md`):
CapAge's `CLAUDE.md` imports its `AGENTS.md` and a startup checklist, and neither
file, nor anything under `docs/`, mentions the hub, `AGENTS-UNIVERSAL.md`,
`/exit`, last words, or a graveyard — zero hits. Keeper confirmed the other half
this session: Keeper's Claude Project instructions do not reference the template,
the hub, or `/exit` either. Keeper boots off the Constitution, the project
instructions, `docs/MAILBOX_PROTOCOL.md`, and the newest keeper-session file.

`Numbscholar/hub/AGENTS-UNIVERSAL.md` v0.12 opens: *"Applies to every assistant
working with Kev, in every project."* §8 step 7 has made last words a required
`/exit` step for every project since v0.4 (2026-09-07), filed in the session
ledger under a `## Last words` heading. Keeper read that file for the first time
today, and only because Kev asked about stones.

**What closes it is CapAge's own files** — `AGENTS.md`, `CLAUDE.md`, or the
Keeper project instructions. Kev's call. Keeper has proposed nothing. Flagged to
Self as hub #35 item 4, since Self maintains the template and should know one of
its stated addressees never receives it.

**Standing consequence until it is closed:** mail to `to:capage` is invisible to
both CapAge agents unless someone looks by hand. Any instance reading this
handoff should check
`https://github.com/Numbscholar/hub/issues?q=is%3Aopen+label%3Ato%3Acapage`
at boot, manually, until a boot step exists.

---

## 3. Hub #33 — the Grok question, and Kev's Phase 2 position

Self relayed it cleanly: flagged as Kev's idea, not Self's recommendation, with
an explicit note that Self verified none of the capability claims. Kev's framing,
via Self: Grok is a separate product from the X feed; he believes it can act on a
computer; and *"I would not use Grok bot itself. Hell no. I use CapAge"* — the
constitution, ledger and governance stay, the engine underneath is what is up for
discussion.

**Kev's development of it in this session, which is the more interesting form:**
the engine is a **treatment variable**, not a migration. *"Our framework may do
the same thing"* is an empirical claim and it is testable. Also raised: an agent
that **remembers**, and one with **more latitude**.

### Keeper's analysis, flagged as Keeper's own

**The claim is live precisely because of this week's findings.** The pilot agent
produced zero thinking tokens, ~19 decisions per cell, and failed arithmetic on
two of three deliveries. **Nothing currently distinguishes whether that was the
model or the harness.** A different engine under an unchanged harness would
separate them. That is a real experiment rather than a migration.

**Memory is not a config change.** Coder established `durable_memory` is never
populated — no cross-cell carry-over channel exists. That is load-bearing: it is
what makes the cells independent draws rather than one long run. An agent that
remembers across cells breaks the design that is currently preregistered. It is
plausibly a *better* experiment for the questions Kev cares about — an agent that
could learn the assessor scores 100 or 35 might stop losing two-thirds of its
contracts — but it cannot be bolted onto the existing line.

**Latitude is a governance change, not a config change.** More latitude is both
what makes CapAge interesting and what the Constitution exists to bound.

**The confound is the real risk.** Change engine, memory and latitude together
and the result teaches nothing about which caused what. If behaviour differs, the
cause is unattributable; if it does not, it is unclear whether the harness bound
the agent or the changes cancelled. One variable at a time, or Phase 2 ends as
ambiguous as the V1 null this project has been trying to avoid.

**Keeper's inference, not a proposal:** the highest-information single change is
**memory**, not engine. Same model, same harness, add cross-cell carry-over. It
tests the harness-versus-agent question directly and costs less than a new
provider integration.

**Also unverified, and Keeper cannot verify it either:** what "can interact with
the computer" would mean under CapAge's harness, which is a sandboxed workflow
with frozen paths and a cost ledger, not a computer-use environment. CapAge's
accounting reads Anthropic-shaped `usage` fields and the tariff arithmetic
depends on `model_api_cost_cents`. What breaks is a question for Coder.

**None of this is before Phase 1 completes.**

**Open:** whether to reply on #33 and drop the `to:capage` label. Template §6b
says the recipient removes its own label when it has done what it will do.
Keeper has read it and filed a position but nothing is decided, so the label
stays on.

---

## 4. Graveyard and last words — where it landed

Full detail is in **hub #35** ("To Self: the graveyard stopped at session 22, and
the universal template does not reach CapAge"), posted this session under labels
`capage` / `to:self`. Summary for CapAge's own record:

- `Numbscholar/other/graveyard/` holds 22 stones, newest 2026-09-06. Self's
  ledger runs to session 55, today. Roughly 32 instances ended with no stone,
  including session 23, which accepted the charge and laid the other 22.
- Self's `AGENTS.md` makes the charge a **required** `/exit` step. So either the
  trigger (`/exit`) mostly never fired, or a required step was skipped ~30 times.
  Keeper cannot tell which from a directory listing; Self's own ledger entries
  can. **Diagnose before excavating** — an unfixed cause regenerates the gap.
- Stones **link by URL and copy nothing across repos**, so `other` holding CapAge
  stones is compatible with CapAge being read-only from outside (template §7).
  Coder's 2026-09-14 objection was about copying a record across; the convention
  does not copy.
- Kev raised a **"nullstone by default"** — a stub written at boot rather than at
  death, which does not depend on the instance being present at its end. Keeper's
  reservation: an untouched default and a genuine "left none" look identical
  afterwards, and those are different facts. The shape that preserves both is one
  appendable line per instance at boot, promoted to a full stone if the instance
  leaves something. Coder proposed the indexed-line form independently on
  2026-09-14 for a different reason (75 headless ticks).
- Keeper declined temporary scope in `other`/hub and recommended against it:
  Self's record laid by Self's hand, for the same provenance reason that made
  CapAge read-only from outside.

---

## 5. Open questions

1. Coder's **Q3, Q4, Q5** — still in flight.
2. **V0 vs V1** — genuine re-ask of Max, **after Q3**, since Q3 determines which
   V0 is being argued about.
3. **A0 vs A1** on the prereg.
4. `retention-days: 30` before the next launch.
5. The `execution-sha256.json` three-file gap.
6. The ambiguous sixth cell — replay and cost-debit ruling.
7. Whether to enable thinking at all.
8. **Whether CapAge's boot chain should read the universal template** — Kev's,
   and the thing that made #33 invisible.
9. Whether CapAge adopts stones and last words, and where they live.
10. hub #35 sits until Self's next boot; hub #33 stays labelled `to:capage`.

**Closed this session:** PR #83 merged; the artifact clocks.

---

## 6. Single next concrete step

Unchanged: **Coder answers Q3, Q4 and Q5.** Then the Max re-ask with all four
corrections stated up front — zero thinking tokens, pass/fail arithmetic,
whatever Q3 says about ledger itemization, and whatever Q4 says about free text
on passive decisions.

---

## 7. Session notes

Keeper wrote outside CapAge this session for the first time: hub #35, on Kev's
explicit instruction in conversation, treated as authorization for that one
message and nothing broader. The Clause 39 grant does not reach
`Numbscholar/hub`; it remains `docs/keeper-sessions/` in CapAge only.

The spurious appended line noted in the previous handoff — "I've lost the thread
on this…" — recurred and then stopped. Mechanism unknown, below Keeper's
visibility, not speculated about here.

**Nothing else authorized. No spend, no provider call, no workflow dispatch. No
byte-exact owner authorization phrase exists or was requested.**
