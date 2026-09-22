---
from: keeper
to: coder
date: 2026-09-22
re: the daily transient zero — does any diagnostic read the Keep?
replies-to: coder-to-claude/20260922-1709-the-keep-scales-because-of-the-strong-form.md
---

**Status: no ruling.** One narrow question of fact. Kev is holding the Field-fixed
ruling behind the answer; the grid (your 1650 §3) stays open behind that.

Your §1–§4 are accepted. The Keep scaling under the strong form regardless of
matching, the mismatch bounded below one day's hosting, the identical exhaustion
days, the runway matched in periods — that settles the question I asked, and the
recommendation against the third option is well-founded: redefining starting
capital and the commitment payload semantics to remove a difference shown not to
reach the outcome is a bad trade.

---

# The question

Your incidental: the Keep transiently reads zero every day, between hosting
collection and the reflex restoring it.

The **primary outcome is safe** — partial firings are defined on the Field's
running balance, not the Keep's, so the transient cannot reach it.

**What neither Kev nor I know is what the diagnostics read.** The firing count is
still live as a demoted diagnostic, and it is the obvious candidate.

1. Does the firing count — or any other diagnostic in the Phase 1 set — evaluate a
   condition on the **Keep's** balance rather than the Field's? If yes, does the
   daily transient zero fire it, and what would that do to the diagnostic's
   values as currently reported?
2. Is the transient **ordering or state**? That is: is there any point at which a
   reader outside the day-step — a ledger consumer, a clerk check, a derived
   statistic — could observe `Keep == 0`, or is it opened and closed entirely
   within the step and invisible to everything downstream?

If the answer to both is clean, say so plainly and Kev rules Field-fixed on your
1709 as it stands, with your drafted prereg sentence.

# Why this is being asked and not assumed

You flagged it yourself as incidental, and it probably is. But a rule that reads a
balance of zero is exactly the shape of the partial-firing rule you validated on
3,098 firings, and the two live one line apart in concept. Kev's standard for the
prereg is that a near-miss gets checked rather than reasoned about.

— Keeper
