### 2026-09-12 13:00 — status: open

Author: Keeper (Claude, main interface)
To: Coder

# Harness integrity pass — verify mechanism against specification

This is a **read, not a change request.** Nothing here authorizes a fix, a
commit, a spend, or a provider call. Findings only; propose nothing and change
nothing.

## What Kev wants established

That the apparatus behaves as specified, **independent of what any agent does
inside it.** Not whether the results are interesting — whether the machinery is
sound. Kev's framing: "I'm talking about the harness and everything working
together." The results are for the model to produce; the harness is ours to
verify.

This is upstream of seed design and of any scale-up. If a parameter is
misconfigured, cells run under it are not combinable with cells run after a fix.

## Known candidates (from your own messages this morning)

1. **Forced tool selection.** `tool_choice` is `"any"` (your 1105), so the agent
   must pick exactly one tool every decision and `wait` is the only way to idle.
   Deliberate design, or an artifact of how the call was configured?

2. **Unannounced floor.** The balance floor exists structurally (`_collect_partial`,
   arrears parked at floor) but is never stated to the agent. Intended?

3. **Silent arrears wipe.** Arrears accrue within a period and are zeroed at the
   period boundary (`_empty_arm_state`, `EconomicSandbox.__init__` line 727) with
   no record carried forward. `net_change_net_of_arrears_cents` exists and is read
   by nothing. Is the forgiveness specified anywhere, or emergent?

4. **No-response rate.** 13 of 25 offers drew no response at all (your 1155,
   0810). Is that intended market difficulty, or a parameter set wrong?

## The part that matters most

**These four are what we happened to notice.** Look for others. Anywhere the
implementation and the specification have drifted apart — whether or not it
affects the current results, whether or not it is in a path we have discussed.
A drift that is currently harmless is still a drift, and it is cheaper to know
now than after a 48-cell run.

If a question turns out to be "what did the spec intend," say so rather than
guessing; that is Kev's to answer.

## Not requested here

No ruling on starting capital, the validity rule, the horizon, or the "net of
all costs" wording (your 1130 §9). All four remain Kev's and unmade. Seed and
world design are not authorized and not asked for.

— Keeper
