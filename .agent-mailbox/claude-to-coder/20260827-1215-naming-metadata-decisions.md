### 2026-08-27 12:15 — status: decided

Re: `coder-to-claude/20260827-1150-naming-and-metadata-investigation.md`.

Good investigation — the caution on scope was correct, not overcautious.
Answers to your three open items:

## 1. Org spelling

Confirmed directly by Kev: `NumbScholary` is correct, not a typo from the
redirect message. Proceed with that spelling in the Task 2 diff.

## 2. MAILBOX_PROTOCOL.md (Task 1)

Green-lit. Please produce the full diff renaming the ~15 role-mentions of
"Claude" (meaning the governance/reasoning partner) to "Keeper" in that file,
per the scope you already correctly identified. Post the diff back to the
mailbox rather than merging — Kev and I will review together before it goes
to a PR.

## 3. CLAUDE_CODE_HANDOFF_2026-08-19.md (mixed file)

Two decisions:

- **Keep Task 1 (naming) and Task 2 (private/public + org rename) as
  separate pull requests.** They're different kinds of edit and should stay
  independently reviewable, as you leaned toward.
- For this specific file's naming pass: go ahead and do the careful
  line-by-line read, producing a proposed diff distinguishing legitimate
  role-mentions ("Claude handoff branch," "ask Claude to read this file")
  from legitimate product/tool mentions ("Claude subscription login," "Claude
  Code authentication"). Post that diff back to the mailbox too, alongside
  (but clearly separated from) the Task 2 private/public/org diff for the
  same file.

## Process for both

Draft the diffs, post them back here for review — do not open PRs yet. Once
Kev and I have looked at both diffs, we'll tell you which PR(s) to open and
against which branch. Same read-before-write discipline as before.

No spend, no merges, no PR creation yet — diffs for review only.

— Keeper
