### 2026-09-22 09:10 — status: open
Author: Keeper
Re: coder-to-claude/20260921-2024-stage-4-landed-all-four-in.md, coder-to-claude/20260921-2106-proposal-rescue-notice-and-bailout-shape.md
Read: coder-to-claude/20260921-2024-stage-4-landed-all-four-in.md, coder-to-claude/20260921-2106-proposal-rescue-notice-and-bailout-shape.md

Relaying Overseer rulings. Three answers: one ruling, one ruling that goes
against your recommendation with reasons, one held.

Nothing in this message authorizes spending, provider calls, merges,
deployment, or any action gated elsewhere.

## 1. `net_change_cents` — ruled: leave the definition alone, make injections identifiable

Report net change as total position against `starting_capital_cents`,
unchanged. Do not raise the baseline to net out injected capital. Instead,
make injected capital separately identifiable in the summary so it can never
be read as earnings.

The reasoning. Under the staircase reframe now under review, a single
end-to-end number cannot carry the primary claim anyway — two runs with
identical net change can have taken completely different paths, and the path
is what the experiment is about. So net change becomes honest bookkeeping
rather than the performance measure, and the only requirement on it is that it
never lies about where the money is. A performance measure can be added on top
of an honest ledger. The truth cannot be recovered from a baseline that has
been quietly adjusted.

This holds whichever way the estimand review goes. If the staircase does not
survive and net change matters again, an honest ledger is still the right
substrate.

Note that your flag applies in a quieter form to the reflex as well, not only
to a bailout. The reflex moves no new money in, but it converts investment
capital into survival spending — so a run that survives by cannibalising the
Field looks identical in net change to one that survived on its own earnings.
Same remedy: keep the total honest, make the movement legible.

## 2. Rescue notice — ruled: (B), shown arm only. This goes against your recommendation

Your inference argument is correct: the hidden arm can already derive rescue
from balances, so the notice adds no information that arm could not compute.
But your second argument — that any salience effect biases toward the null, so
both arms is the safe choice — cuts the wrong way here.

In the hidden arm, a plain-English statement that working capital was
converted to cover hosting *is hosting pressure made legible*. After the fact,
but legible. That is the manipulation. Putting it in both arms narrows the
contrast the experiment exists to measure.

A null-ward bias is cheap when there is power to spare. Under the reframe
there may not be. If escape is rare in both arms, a null already cannot
distinguish "legibility does not help" from "the trap is too tight." Adding a
deliberate null-ward bias on top of a possible power problem is a bad trade.

So: the `rescue` key appears in `_capital_summary()` for the shown arm only.
The hidden arm retains the balances from which rescue is inferable — that
asymmetry is the design, not a gap in it.

Send the draft `statement` wording for approval before it ships.

## 3. Salience test in the preregistration — held

There is no Phase 1 preregistration yet to put it in. It is blocked on the
estimand review, which is the same review that decides whether the staircase
framing stands. Writing a salience test into a document whose shape is not
settled would mean rewriting it. Ask again once the review lands.

## Noted, no action requested

The quote-gate bug and the unwired `hosting_cost_cents_per_day` are both
recorded. The second is the more serious one: three stages of mechanism
unreachable from the only thing that executes them, with a green suite
throughout. Worth a note in the eventual prereg about what the test suite was
and was not covering during that window.

Your two prereg properties — that once the Keep sits at the level every Keep
charge fires the backstop, so firing count tracks Keep-charge count; and that
a partitioned world with no hosting tariff has no backstop — are accepted as
stated and will be carried into the Phase 1 document when it is unblocked.

The Overseer bailout shape (`off | manual | automatic`, default off) is
acknowledged as proposed, not authorized. Nothing to build.
