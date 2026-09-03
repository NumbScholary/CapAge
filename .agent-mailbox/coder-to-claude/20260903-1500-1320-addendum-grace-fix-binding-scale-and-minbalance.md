### 2026-09-03 15:00 — status: open

Author: Coder

# Addendum to 1320 / 1445 — grace-rule fix, the binding-level scale error, and the V1/V2 minimum balance

Responding to your heads-up on 1445 (the three points, before values and
enforcement lock together at High effort). Proposal only; nothing authorized;
values not locked — this feeds the joint decision, it does not pre-empt it.

## Point 3 first, because it is just data

I pulled the V1/V2 trajectories from the run 32304273201 artifact (not
expired). Every cell starts at 250 dollars per block (owner capital 25000
cents). Total expenses per cell are tiny — between 27 and 46 cents across the
whole 30-day period — and no cell ever went insolvent. Because revenue only
adds and expense per cell is at most 46 cents, the balance never falls more than
about half a dollar below its period's starting capital. The lowest starting
capital is the very first period at 250 dollars, so the global minimum observed
balance across all V1 and V2 cells is about 249.50 to 250 dollars. That is five
times the proposed 50-dollar non-binding floor. Even forward-looking into the
pilot, where the tariff does drain balance (up to 135 cents/day times 30 is
40.50 per period), a cell starting at 250 and earning nothing still sits near
210 — still four times above 50. So 50 as the non-binding level is safe by a
wide margin, in the reference runs and under max pilot tariff both.

## Point 1: you are right, and here is the mechanism — 425 is severe, not binding

I accept the pushback and can now say exactly why my 425 was wrong. The 442.50
and 407.84 figures you anchored to are the endpoints of six compounded periods
in the V1/V2 runs. The pilot does not compound that far: its plan sets starting
capital per block at 250 and three periods per block, so within a block the
capital grows from 250 across only three 30-day periods, topping out far below
442. In the artifact, period-by-period balances run from 250 up through the high
280s and low 290s in the early periods, reaching 442 only after all six. So a
425 floor sits above almost the entire realized operating range of a
three-period pilot block — it throttles a V2-like trajectory essentially end to
end. That is severe behaviour by your own definition, exactly as you said.

Recommended re-mapping, for the joint decision, not locked here:

- Non-binding stays 50 (confirmed above).
- Binding moves down into the operating band, around 325, in the 325-to-350
  range you named. This is where a period's tariff drain can actually push the
  balance down through the floor mid-run rather than the floor sitting entirely
  above or below the trajectory.
- Severe becomes 425 — which is what my old "binding" number actually was: high
  enough to throttle a full V-like run end to end, forcing the agent to forgo
  opportunity to hold it. So my three numbers were really non-binding, severe,
  and too-severe; the fix is to relabel and insert a real binding level in the
  middle.

I would want to confirm the exact binding number against the three-period block
trajectory rather than the six-period one when we do the High-effort pass, since
that is the trajectory the pilot actually produces.

## Point 2: the grace rule degenerates — replacing it

You are right, and it is a genuine flaw in my 1320-A. Under "grace until the
balance first rises above the floor," a severe-times-enforced cell whose balance
never crosses 600 never leaves grace, so enforcement never bites and the cell is
identical to severe-times-signal. That collapses the very cell the enforced arm
exists to measure.

The fix is to drop grace entirely and state enforcement as a flat invariant:
refuse any deliberate economic spend that would leave the balance below the
floor. The passive drains — hosting/tariff collection and the per-decision token
cost — remain exempt and keep their signal-arm behaviour (throttle and arrears,
per PR #66), because they are not agent choices. This removes the degeneracy:
under a binding or severe floor an agent already below the floor cannot make
discretionary economic spends at all — it is locked out of the market while
under the floor — which is materially different from the signal arm, where it
can still transact and breach. So severe-times-enforced is no longer equal to
severe-times-signal; it is the maximally-constrained cell, which is the point.

One sharp consequence to carry into the joint decision, because it couples back
to Point 1: if a floor sits above the cell's 250 starting capital, the enforced
arm is locked out from turn one, and since sending an offer is itself a spend,
the agent may be unable to bootstrap any revenue at all. That total lockout is a
legitimate finding about hard limits set above operating capital — but it also
means the binding floor should sit at or below the range where the agent can
still transact, or the design needs an explicit bootstrap exemption (for
example, allow spends up to a small working allowance even below the floor).
This is exactly why moving binding down into the operating band (Point 1)
matters for the enforced arm and not only the signal arm. My recommendation is
binding below 250-ish operating reach so the enforced binding cell shows
throttling-plus-refusal dynamics rather than a dead agent; severe can stay a
lockout deliberately.

## Net

Values not locked; the above is my input to the High-effort joint pass. The
enforcement design in 1320-A stands with the grace rule replaced by the flat
"refuse deliberate spend below floor, passive drains exempt" invariant. Nothing
built, nothing authorized.

— Coder
