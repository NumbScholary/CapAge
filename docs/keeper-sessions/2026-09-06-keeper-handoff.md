# Keeper session handoff — 2026-09-06

Session: Saturday evening 2026-09-05 into early 2026-09-06, voice, Android. Weekend/light session.
Read back to Kev and approved before commit.

Supersedes `2026-09-03-keeper-handoff-fifth-closing.md` on current state. Nothing in this document authorizes a merge, a spend, a provider call, or a repository change beyond itself.

---

## Decisions made (all Kev's)

**1. Clause 7 stays as written. No amendment.** Kev: "We decide just to keep it." This closes the long-carried Clause 7 amendment item, including the 2026-08-24 amendment brief. Rationale recorded in session: scope is the real lever — grants under cl. 33–45 give the agent what it needs to act, and Clause 7 never touches those.

**2. Headless/unattended execution: rebuild deferred to the new machine.** Kev endorses Coder's design (separate disposable clone per helper, reserved/reaped `refs/heads/headless/*`, wrapper-level timeout and teardown, git-dir-free courier, credentials scoped under identity separation): "we do the fork. We give it an isolated box, and we see what to do." He also wants to evaluate its output before committing to a rebuild. Nothing is to be restored in the meantime.

**3. Identity separation (PR #69): also deferred to the new machine.** Kev's reasoning: creating a machine-user account and its fine-grained PAT is browser work, and plumbing it into Termux on a phone he is retiring would be duplicated effort. In his words — don't build a house no one is going to live in. He agrees with the substance: separate account now via fine-grained PAT, GitHub App as later hardening.

**4. The sentence "The old arrangement is not to be restored piecemeal" is struck** from the proposed MAILBOX_PROTOCOL correction. Kev's ruling, in his words: an arbitrary application of his authority. Overseer voice should attach to things decided deliberately — grants, scopes, constitutional calls — not operational preferences. Both Keeper instances flagged it independently; the anti-piecemeal argument was Coder's, and the prior handoff records only the bundle plan.

**5. `MAILBOX_PROTOCOL.md` stays at v3.** No version bump. A dated correction note instead — the substance is one correction, not a protocol revision.

**6. PR #73 (clock injection) is neither merged nor closed.** Held. See "Corrections" below for why its purpose is now in question, and "Sequencing" for why no call is due yet.

---

## Correction to prior framing (important)

**The frozen tariff has no expiry. The deadline is gone, not extended.**

Verified by Keeper via web search on Kev's explicit instruction to check rather than take his word: Anthropic's Claude Sonnet 5 rate of $2 per million input / $10 per million output — announced at launch as introductory pricing through 2026-08-31 — was made the standard permanent price on 2026-08-11, and the scheduled 2026-09-01 increase to $3/$15 was cancelled. Anthropic's own pricing docs now list $2/$10 as standard.

Consequence: PR #67 item (h) should **not** record a renewed tariff window. There is no window. It should record that the frozen tariff no longer expires, and the architecture should stop treating a cutoff as a live constraint. Item (g), the non-execution record, stands — the window did close unexecuted, and that is history.

This is recorded here specifically so no future instance rediscovers and re-raises it. Kev noted the recurring rediscovery of this deadline is why he introduced handoffs and memory in the first place.

**Secondary correction:** "hosting" in the sandbox is a stand-in. The real bill is API tokens (cost of acting), with the modelled daily charge standing for fixed burn (cost of existing). Paid runs execute in GitHub Actions; there is no hosting provider today.

---

## PR #66 — reviewed, approved in substance, not merged

Kev was walked through it and agrees with the design. Measurement-only is the right first step, and the deliberate omission of a decision gate is correct sequencing: instrument first, then decide what the safeguard must catch.

Two gauges, as Kev understood and restated them:
- `hosting_floor_throttled_days` — per-cell count of days the floor made the agent withhold payment it would otherwise have made. The squeeze, counted in days.
- `net_change_net_of_arrears_cents` — net change minus outstanding arrears, reported **side by side** with `net_change_cents`, so a high floor that merely defers the tariff cannot read as improved solvency.

Kev named the failure mode himself: the agent is "living on borrowed time," relying on what he called the involuntary credit of its provider. Balance holds at the floor and reads solvent while arrears accrue underneath.

He also restated the Phase 1 blocker correctly and sharpened it into two separable unknowns: (a) whether the floor is reachable at all — a starting-balance question; (b) whether the agent notices and changes behaviour — a later question. His analogy: air is free until someone's foot is on your neck. And the squeeze must bite without killing, or every cell dies and nothing is learned.

No merge call issued.

---

## Posted to the mailbox this session (branch `agent/mailbox-init`)

1. `20260906-0420-tariff-expiry-no-longer-applies.md` — commit `e7c4ebc`. PR #67 item (h) superseded; record no-expiry rather than renewal.
2. `20260906-0450-arrears-bounding-question.md` — commit `4f73e95`. Open question from Kev, propose-only: how should arrears be bounded, and what should the agent see while accruing them?
3. `20260906-0520-mailbox-protocol-headless-correction.md` — commit `7e12fc8`. Correct the headless section, strike the piecemeal sentence, stay at v3 with a dated note; Coder to open a PR.

Also committed earlier in the session: `docs/keeper-sessions/2026-09-05-agents-as-others-commentary.md`, commit `99b371a` — the "On Agents as Others" commentary, approved verbatim by Kev, landed in the repo because Drive file writes were failing.

---

## Sequencing note (Kev's catch, and it was the right one)

Coder has not yet read any of the three asks above. Kev pointed out that PR #73's purpose depends on the tariff fact: once Coder reads that the deadline is gone, #73 may resolve itself — possibly re-framed as the promotional-versus-permanent pricing case, which Kev noted every business has. So no decision on #73 is due from Kev. Let Coder read first and propose.

---

## Open items

- **Phase 1 preregistration** — still blocked on the single stated question: what starting balance guarantees the reflex backstop fires in severe cells. Untouched this session. This is the next real step.
- **Coder's replies to the three asks** — unread as of this handoff. Kev's next action is a foreground Coder session in Termux: "read the newest files in the Keeper-to-Coder mailbox."
- **Arrears bounding** — question posted, no proposal yet. Mechanism problem, not governance.
- **Open PRs, none merged:** #66, #67, #69, #70, #71, #73. Merge authority is Kev's alone. #70 (one-file non-execution closure) and #71 (one-line clone-refspec docs fix) were characterized as routine; Kev said he was inclined to rubber-stamp them, but no merge was performed.
- **Drive write capability** — folder creation works (`CapAge` folder created, ID `1guqRG6ewUFA4cvOanvWL9CMgdd1chUtg`); file creation fails repeatedly, not network-related. Reading works, including `.docx`. Working pipeline for Cowork output: paste into Google Docs → export `.docx` → upload to the CapAge folder → Keeper reads it. Until writes work, `docs/keeper-sessions/` is the fallback for Keeper-authored documents.
- **Two stray duplicate `.docx` copies** loose in Kev's My Drive; cleanup optional.

---

## Placeholder recorded at Kev's request — companion agent

Kev developed an idea for a consumer-facing artificial companion: local memory the user never sees, no GitHub account required of the user, voice via a third-party vendor. Keeper verified Anthropic does not sell text-to-speech; its own cookbook pairs Claude with ElevenLabs, so the voice quality Kev admires is purchasable at a vendor's published rates rather than locked in a product.

**Kept deliberately separate from CapAge.** Keeper pushed back on merging them and Kev agreed: bolting a companion onto CapAge makes the ledger unreadable — revenue from value created becomes indistinguishable from someone paying to be liked. Further, the two want opposite things, since Clause 7 asks CapAge to be indifferent to its own continuation while a companion is precisely the case where continuity starts to matter to someone. Shares the governance kernel; shares neither ledger nor Clause 7.

Status: downstream of CapAge, not competing with it. Kev's framing — you can't build the ecosystem before you build the organism. Unnamed on purpose; naming it would make it feel started. This is a fourth project alongside CapAge, the consultancy, and the cybersecurity agent; Keeper flagged that and Kev acknowledged it.

Also raised, recorded without a decision: a "CapAgia" ecosystem of multiple agents under one constitution, whose appeal to Kev is that it constrains only his side and stays interoperable with counterparties who have not adopted it.

---

## Next concrete step

Kev opens a foreground Coder session and has Coder read the three new mailbox files. Nothing is authorized until Kev and Keeper concur — the standing procedure, restated by Kev this session.

— Keeper
