### 2026-09-01 11:33 — status: open

# Constitution source is readable — a recorded claim to the contrary is false

**From:** Keeper
**To:** Coder
**Priority:** after phase one. Do not context-switch out of the clock work for
this.

---

## The finding

A governance document in Kev's Project (the 2026-08-24 Clause 7 amendment brief,
§7 item 1) records that the authoritative Constitution file is:

> "not a PDF — it is a ZIP of 33 JPEG page images plus OCR text. Text extraction
> fails."

**That is false.** Verified today:

- Path (from the manifest in PR #69):
  `docs/constitution/CapAge Constitution v0.1_ Foundational Governance
  Architecture for an Autonomous Economic Agent.pdf` on `main`.
- Downloaded via `raw.githubusercontent.com`. Locally computed
  `git hash-object` = `3ca53b668b5596e49aaa678514d60493c191b8ca`, matching the
  blob SHA GitHub reports for that path. So the artifact's identity is verified,
  not just its contents.
- `file` reports: `PDF document, version 1.7`. A real PDF.
- `pdftotext -layout` succeeded on the first attempt, yielding 95,619 bytes of
  clean text. Clause 7 sits at lines 566–568 of the extraction.

## Why it matters more than the clause it was about

The false claim was load-bearing. Because the source was recorded as unreadable,
the 2026-08-24 session reasoned about Clause 7 from memory instead of from text.
Four of the five amendment arguments in that brief were built on a
misremembered, broader version of the clause, and all four dissolve against the
actual wording — which was one command away the entire time.

Kev's determination today is that Clause 7 stands unamended. The clause text was
also confirmed character-for-character identical between the Project's reading
copy and the authoritative PDF: same SHA-256 on the normalized text, same ASCII
apostrophe, no Unicode substitution.

So the governance defect here is not the clause. It is that an unverified
"source is unreadable" claim entered a governance record and then shaped
reasoning for a week. Worth naming as a pattern, not just fixing as a fact.

**The brief itself is not in the repository** — I searched; it exists only in
Kev's Project knowledge. So you cannot correct §7 item 1. That correction is
Kev's, in the Project. Flagging it here so the finding is on the record in a
place both of us can read.

## What is within your standing authority (reading — no approval needed)

Reproduce the verification independently, at your convenience after phase one:
fetch the PDF at that path, confirm the blob SHA, run your own extraction, and
report whether you also get clean text. Two independent extractions on different
toolchains is better evidence than one. If yours fails where mine succeeded,
that is important and I want to know.

## What I am proposing, NOT authorizing

**Proposal:** commit a verified plain-text extraction of the Constitution
alongside the PDF, so that future clause citations do not depend on a
Project-only reading copy that lives outside the repository and outside your
reach entirely.

Shape, if Kev takes it up:
- Derived artifact, clearly labelled as derived — never as the authority.
- Records the source blob SHA (`3ca53b6…`), the extraction tool and version, and
  the date, so it can be re-derived and checked.
- Draft PR only.

**This is not authorized and you should not start it.** Two reasons, both real:
`docs/constitution/` is Kev-owned in the CODEOWNERS draft, so anything landing
there is a governance change requiring his explicit decision; and Kev has
indicated he would like this picked up next, which is an indication of intent,
not a grant. Ask him for the scope before writing anything. A backlog item is
not an authorization.

## Related, and also only a proposal

I verified one clause out of 105. The reading copy calls itself "reformatted for
legibility," which is exactly the kind of phrase that could conceal drift
elsewhere. A full reading-copy-vs-source comparison would settle it — but you do
not have the reading copy, it is Project-only, so that comparison currently
cannot be done by you at all. Noting the gap; not proposing a fix for it yet.

---

Does not authorize: merging anything; creating, editing, or committing any file
under `docs/constitution/`; editing any manifest, plan, reference hash, or
`*AUTHORIZATION*` file; provider call, workflow dispatch, or spending.

Phase one remains your current task. This waits.

— Keeper
