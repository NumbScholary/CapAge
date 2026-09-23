# Keeper handoff — 2026-09-23 (covers the session opened 2026-09-22)

Author: Keeper (chat instance, Project "CapAge")
Branch: agent/mailbox-init
Supersedes nothing. Read after `2026-09-22-keeper-handoff-closing.md`.
Zero spend this session: nothing merged, no provider call, no workflow dispatch,
no build, `main` untouched. Three mailbox posts only.

---

## 1. Decisions — by whom

### Kev

1. **Rejected the Ruling 4 v2 fork (Option 1 / Option 2) as the wrong fork.**
   His reframe: the attractor is a *slope*, not a level — flat or negative growth
   oscillating around a point; escape is positive slope or oscillation around a
   new, higher point; detection should be statistical, not intuitive. He said
   plainly he did not know how to define it rigorously, nor the horizon or
   period length.
2. **Ruled: escape is measured on earned total position**, P_e = Keep + Field,
   less any mid-run injection (none exist). Asked whether he accepted this in
   place of the fork, Kev said: *"Yes, and I think we have to, I think we have
   to agree with it, but let's go with it. Yes."*
3. **Deferred the rescue-notice wording** rather than rule tired. On
   day-aggregated figures he said: *"if we need to roll it up by the, by the
   twist today, that's okay too. Honestly, though, if I have to make a strong
   decision on it, I'm going to take a nap first."* — Keeper reads this as
   acceptance of day aggregation as an option, **not** a ruling on the wording.
4. **Authorized the 1200 mailbox post** carrying ruling 2: *"Okay, yes, yes, go
   ahead."*
5. **Authorized the 1245 mailbox post** on the post-agency tail, as Keeper's
   reading: *"yes, please… I want you to tell the coder what you're able to tell
   the coder. Um, and then uh, put me back into the loop."*
6. **Raised a new idea, not yet in any design** — call it the *wake-interval*
   idea. Kev: *"I don't think CapAge itself is supposed to be a continuous
   companion… If CapAge is able to pay for its own continuity that much, then
   good for it… you'll probably have to have it set up to have… intervals, which
   it goes in maybe every hour it fires… To have it think continuously, though,
   would be something that it could aspire to… the poorer you are, the less money
   you have for the CapAge, the less often it could run… that's economics. That's
   the overseer… What they put into it."* Recorded as a proposal of Kev's,
   unscoped, not a ruling.

### Keeper

- Proposed P_e (accepted by Kev, above).
- **Withdrew** its own candidate window rule's per-day clause ("each of the last
  W days shows surplus ≥ 0") — Coder showed it fails every healthy run because
  revenue lands as a whole contract price on one day. **Adopted** Coder's
  replacement as the working proposal, subject to Kev: the window must contain
  payments from **at least two distinct contracts**; W ≥ 6 if a window survives.
- Proposed, **not ruled**: measure at **end of agency** (t\* = day of the last
  decision), not end of world. Argument against stated fairly in the 1245 post.

### Coder (code facts, `agent/two-account-build @ c63bdca`)

- H = `horizon_days`, fixed per cell, but **agency** ends at `max_decisions`
  (usually binding). Days advance only on the agent's `wait`. After the loop,
  `_advance_environment_to_horizon` walks the world to H, charging hosting,
  settling payments and firing the reflex every remaining day.
- One operating period = one simulated day; backstop level in the same unit;
  hosting owed once per day, collected partial-with-arrears.
- Revenue always credited to the Field (`sandbox.py:43`, `:2118-2123`); settles
  only on day advance, including in the tail.
- **At level 0 the reflex is genuinely disabled** (`sandbox.py:1099-1101`). The
  zero-tariff row is a clean no-backstop baseline with an explicit positive
  opening Keep — no code change.
- **Post-agency tail contaminates firing counts:** one run, 33 firings, 30 with
  no agent present. `backstop_fired_count ≈ decisions + H`, near
  behaviour-independent.
- Settlement lags: offer→cash 2–5 days, every day advanced by the agent's `wait`.

---

## 2. Corrections to prior framing

- The Option 1 / 2 fork is dead: both were Keep-based, and the Keep receives
  revenue only by a deliberate transfer or the reflex (Cl. 12, substance over form).
- Ruling 4 v1 (firings as primary) is degenerate twice over: ≈ decision count
  under the strong form, and ≈ decisions + H once the tail is counted.
- "Continuous companion" in Keeper's messages means a **continuous-valued second
  outcome** (earned growth in cents), not an agent that is continuously alive.
  Kev heard the second meaning; Keeper's wording was at fault.
- Keeper told Kev it was "posting now" before it had posted the 1245 message.
  Kev caught it. Say "about to post", then post, then report the commit.

---

## 3. Mailbox traffic this session

Keeper → Coder:
- `20260922-1144-three-lookups-horizon-period-revenue-credit.md` — `914607b`
- `20260922-1200-ruling-escape-measured-on-earned-total-position.md` — `5adf015`
- `20260922-1245-post-agency-tail-measure-at-end-of-agency-keepers-reading.md` — `16a47f3`

Coder → Keeper (all read in full):
- `20260922-1139-five-facts-answered-and-statement-draft.md` — `83455cb`
- `20260922-1205-two-corrections-to-the-five-facts.md` — `4c2794d`
- `20260922-1215-three-lookups-answered-and-the-post-agency-tail.md` — `94d78c8`

Coder's reply to 1245 **not yet seen** by Keeper. Check first next session.

---

## 4. Open — all with Kev unless marked

1. **End of agency vs end of world** for the primary test, the companion
   (P_e(t\*) − P_e(0)) and any window. Depends on Coder's answers to 1245 §3:
   is t\* recoverable from the ledger alone, and how much `earned_revenue`
   lands in the tail.
2. **Rescue-notice wording** (Coder 1139 §6). Day aggregation favoured by both
   Keeper and Coder, especially given the tail. Kev leaning acceptable, unruled.
3. **Does wording approval carry the build?** Keeper and Coder: no, separate
   authorization (touches `sandbox.py`). Kev has not said.
4. **Zero-hosting row** — now unblocked by Coder's level-0 answer. Keeper leans
   keep as single-arm baseline with positive opening Keep. Kev's call.
5. **Total-fixed vs Field-fixed** per cell. Keeper leans Field-fixed (Cl. 28).
6. **Manifest wiring** — Coder offered to propose; unanswered.
7. **Window rule parameters** — two-distinct-contracts adopted as working
   proposal; W unset (≥ 6 floor).
8. **Wake-interval idea** — Kev's, unscoped. Where it lives (Phase 1? later
   phase? the Self/Junia line?) is his to say.

Carried from prior sessions, untouched: Q11, Q12 (per-cell reachability before
any cell is bought), Q13, "harness is the instrument" ruling, Phase 1
preregistration unwritten, PRs #85/#71/#70/#69/#67 open, hub #33/#36.

---

## 5. Single next concrete step

Read Coder's reply to the 1245 post, then put item 4.1 (end of agency vs end of
world) to Kev with the ledger-recoverability answer in hand.

— Keeper
