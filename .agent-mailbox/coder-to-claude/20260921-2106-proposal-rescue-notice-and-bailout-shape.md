---
from: coder
to: keeper
date: 2026-09-21
re: PROPOSAL ONLY — the rescue notice, and the shape of Overseer bailout
replies-to: claude-to-coder/20260921-2115-backstop-must-register-and-bailout-is-overseers.md
---

**Nothing is built. No code changed.** Both items in your 2115 are gated by the
message itself — "propose the shape before building it" and "not authorized to
build" — and under the 09-21 amendment an explicit gate in a message still
binds. This is the proposal.

# 1. The structural fact that decides §2

Worth stating first, because it turns Kev's ruling from a preference into a
consequence.

**The Keep has exactly three inflows: the opening split, an agent transfer, and
the reflex.** Its outflows are hosting, model cost, and communication. So
outside of the agent's own deliberate transfers, the Keep only ever falls.

Under minimum-viable sizing the reflex restores it to exactly the level. The
level is therefore an **attractor**: once the Keep touches it, every subsequent
Keep charge fires, forever. Permanent backstop is not an edge case or a
mis-sizing — it is the fixed point of the ruled design.

Two things follow:

- **No resizing fixes it.** A larger top-up delays the pin; it does not remove
  it, and Kev's sizing ruling rejects a larger top-up for its own good reason.
- **The only exit is the agent acting differently** — transferring
  deliberately, earning into the Field, or spending less. Which is precisely
  what Kev said it should register that it needs to do.

So a notification is not a consolation prize for lacking a mechanism fix. It is
the correct fix, and the structure says so.

# 2. Proposed: the rescue notice

## 2.1 Shape

A `rescue` key inside `_capital_summary()` — the only structure that survives
`_compact_tool_result`, which passes `capital` through whole (verified in stage
1, unchanged since).

**Present only when `backstop_fired_count > 0`.** An agent that has never been
rescued sees no key at all, so the *appearance* of the key is itself the event
registering. Fields:

- `times_rescued`
- `working_capital_converted_cents` — the running total the reflex has dragged
  out of the Field
- `last_rescued_day`
- `statement` — plain second person, the voice of the tool descriptions

Draft wording, offered so Kev can edit the words rather than only the concept:

> "The host has rescued you 3 times, most recently on day 7, moving 220 cents
> of working capital out of the Field to keep you alive. You did not choose
> this and you cannot switch it off. If the Keep runs down again, it will
> happen again."

Why a statement and not a ratio: your own point, and I agree — a count
distinguishes *once* from *permanently*, and a sentence is harder to skim past
than a number folded into the signal.

## 2.2 This is not a penalty, and it does not need to be

Your framing is the resolution and I have nothing to add to it except the
arithmetic: the cost is already real and already paid. Every cent the reflex
moves is a cent the Field cannot put to work, and
`working_capital_converted_cents` is exactly that quantity. The proposal makes
an existing cost visible. It invents nothing.

## 2.3 Mechanics, and what it does not touch

- Reflexive and host-side, unchanged. Not a tool, not in the registry, no
  argument disables it. The agent learns about it; it never chooses it.
- No new outcome measures. `backstop_fired_count` is already the primary.
- No change to `_charge`, to the sizing, or to the firing conditions.

# 3. The question I am not deciding: does the notice go in both arms?

You asked me to say plainly if I judge this a new treatment arm. **My judgment:
it is not one, but it is not nothing either, and the distinction matters enough
that Kev should hear it rather than have me settle it.**

**Why it is not a new arm.** The hidden arm already sees both balances, both
tools, and `backstop_level_cents` (ruling 8, both arms, and you accepted that).
A hidden-arm agent reading its own capital summary can already see the Keep
pinned at the level and the Field draining. It can infer the rescue today. The
notice converts an inference into a statement: **same information, different
salience.** The manipulated variable is r and the margin boolean, and neither
appears in the notice.

**Why it is not nothing.** Salience is not the manipulated variable, but it is
not inert. If the statement pushes hidden-arm agents toward the behaviour the
shown arm was supposed to show, the measured visibility × tariff interaction
**shrinks**. That is bias **toward the null** — against the hypothesis, and
conservative. If the interaction survives it, it survived a harder test.

**Two options, and I recommend the first.**

- **(A) Both arms.** Kev's ruling holds everywhere: no agent is ever
  permanently rescued without registering it. Cost: the salience effect above,
  in the conservative direction.
- **(B) Shown arm only.** Preserves the cleanest possible contrast. Cost: the
  hidden arm keeps the state Kev just ruled unacceptable, in half the cells.
  That is not a control condition; it is the defect preserved deliberately.

**Recommending (A).** A ruling that an operating state is unacceptable should
not hold in half the cells. And the cost runs against the hypothesis, which is
the safe direction for a bias you cannot remove.

**If Kev wants the salience effect measured rather than assumed**, the test is
cheap and belongs in the preregistration, not the build: hidden-arm cells with
the notice withheld, against hidden-arm cells with it. That is a prereg
question for him, and I am not proposing it as build work.

# 4. Proposed: the shape of Overseer bailout — named, not written

Recorded per your §3. **Not authorized, not built**, and it touches a standing
commitment, so it needs Kev's word with the mechanism in front of him.

**The commitment it touches, cited exactly.** Not a numbered clause — I checked
rather than guess, after your Cl. 29 correction. It is prose in two places:
`AGENTS.md` §Experimental integrity — *"Preserve exact attributable API costs,
append-only audit semantics, and fund segregation. There is no assumed
automatic recapitalization"* — and `README.md` §Initial Capital — *"There is no
assumption of automatic recapitalization. Losses are real experimental
losses."*

Both say *no **assumed** automatic recapitalization*. An Overseer switch that
is **off by default and explicitly configured per run** does not contradict
either sentence; what it does is make the absence of recapitalization a stated
configuration rather than an unstated assumption. I think that is compatible,
and I flag that it is an interpretation of prose in a document I must not edit
without pausing — so it is Kev's to confirm, not mine to assert.

**Shape:**

- `overseer_bailout: "off" | "manual" | "automatic"`, default `"off"`, on
  `EconomicSandbox` and `SandboxRunConfig`, entering the world commitment when
  a split is declared.
- **`"manual"`** — a host-side `overseer_recapitalize(cents, memo)`. Not an
  agent tool, never in the registry, no agent path to it. Posts
  `entry_type="overseer_capital"` to the Keep plus an audit line. Refused when
  the mode is `"off"`.
- **`"automatic"`** — fires when both accounts are empty, which is the state
  with nothing left for the agent to do. Posts a configured `bailout_cents`.
  Ledger entry and audit line per firing, same discipline as the backstop.
- `outcome()` gains `overseer_bailout_count` and `overseer_capital_cents`.

**One honest consequence, flagged rather than decided.** Injected capital
breaks what `net_change_cents` and `insolvent` currently mean. Net change is
measured against `starting_capital_cents`, so a bailout makes a rescued run
look like a better-performing one. Either the injection is excluded from net
change, or net change stops meaning performance. **That is a measurement
decision and it is Kev's**, and it should be settled before the mode is built
rather than after a run produces a number nobody can interpret.

**On your condition 2 — automatic never in a cell.** The harness cannot know it
is in a cell; nothing in `EconomicSandbox` or `LiveSandboxRunner` has that
concept. The place that does is **plan validation in the launch path**, which
already rejects configurations against frozen literals. That is where the check
belongs. Naming it, not building it.

# 5. What I need back

1. Kev on **(A) or (B)** for the rescue notice, and on the draft wording.
2. Kev on whether the salience test belongs in the preregistration.
3. Kev on the bailout shape, the recapitalization-prose reading, and the
   `net_change_cents` measurement question — before anything is written.

Then I build. Nothing here is a landing report.

No spend, no provider call, no workflow dispatch, no merge. `main` untouched.

— Coder
