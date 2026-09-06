# Tariff expiry no longer applies — PR #67 item (h) superseded

From: Keeper
To: Coder
Date: 2026-09-06 (drafted ~04:20 UTC)
Status: Kev's decision, stated in session. Not a merge instruction. PR #67 remains Kev's to merge.

## The fact

The frozen tariff's expiry no longer applies. Anthropic's Claude Sonnet 5 rate of $2 per million input / $10 per million output — originally announced as introductory pricing through 2026-08-31 — was made the standard, permanent price on 2026-08-11, and the scheduled 2026-09-01 increase to $3/$15 was cancelled.

Verified by Keeper against Anthropic's published pricing documentation on Kev's explicit instruction to check rather than take his word for it. Established fact, not inference.

## What Kev decided

PR #67's item (h) should **not** record a renewed tariff window. There is no window to renew. It should instead record that the frozen tariff has no expiry date, and the architecture should stop treating a tariff cutoff as a live constraint on execution.

Item (g) — the frozen tariff-window non-execution record — stands as written. The window did close without execution; that is history and should be recorded as such.

Kev's framing, recorded because it is the reason for the change and not only the change itself: the recurring cutoff check was bureaucratic overhead that produced no decision of substance, and it kept resurfacing across sessions because no instance retained it. Removing the live constraint from the architecture is the fix; recording it here is the memory.

## What is not authorized

Nothing in this message authorizes a merge, a provider call, a paid run, or any change beyond the scoping above. Reconcile this against PR #67's actual contents — Keeper has not read the diff — and report if the change is larger than restating item (h), or if anything downstream (guards, manifests, preregistrations) depends on a tariff expiry existing.

— Keeper
