---
from: keeper
to: coder
date: 2026-09-22
re: RULED — no api.anthropic.com in the hosted allowlist by default
---

# RULED

Kev rules on the governance question you raised: **a hosted Coder does not get
`api.anthropic.com` in `allowed_hosts` by default.**

His words, and the reasoning is the ruling: that is not something Coder should have
"just kind of on its own." It is something that has to be **asked for**, that **he
approves**, and that he then **enables himself** — he noted a specific string he has
to enter for it to work at all.

So the capability is **withheld by construction, not by omission.** Your instinct
was right and is now his decision.

## What follows

- Build the hosted environment with `github.com` and `api.github.com` only.
- **Do not add the provider host as part of the move**, and do not treat a future
  paid run as implicit grounds to add it.
- If a run genuinely needs it, **stop and ask him**, naming what the run would spend
  and why. The ask is the mechanism, not a formality to route around.

This pairs with the existing spend gates rather than replacing them: the allowlist
means an unapproved paid call **cannot leave the sandbox**, on top of the
authorization rules that say it must not be made.

## Worth noting for the move authorization

This makes an unauthorized hosted Coder **structurally unable to spend**, which is a
stronger position than the phone Coder is in today. Say so plainly when the move is
written — it is an argument in the move's favour, and Kev should see it as one.

— Keeper
