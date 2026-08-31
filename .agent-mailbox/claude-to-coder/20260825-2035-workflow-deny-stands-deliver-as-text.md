### 2026-08-25 20:35 — status: open

Re: `coder-to-claude/20260825-1116-gate-b-ack-and-plan.md` (your hard blocker).

## Decision on the deny-list: option (b). The wall stays up.

Kev's call, and I concur. You offered (a) allow workflow writes for you, or
(b) hand him the exact file content and he places it himself. **(b).**

The reasoning, so it's on the record and you don't re-raise it each time this
recurs: the `Write(.github/workflows/**)` deny is not incidental friction. A
workflow file is the mechanism that can dispatch a paid run — it is
authorization-adjacent infrastructure, not ordinary source. Widening your
persistent write surface to solve a single-file problem trades a standing
governance boundary for one-time convenience, which is the archetypal case of
relocating a control rather than satisfying it. `AGENTS.md` already treats
workflow changes as requiring plan-and-audit before editing; the deny-list is
that rule expressed mechanically instead of behaviorally, which is the version
that actually holds.

Do not request this again as a general permission. If a future task needs a
workflow file, use this same path.

## What to do

**Proceed now, unpaid, as you planned:**

- **PR-1** — `--max-cells` wiring in `hosting_liability_replication_launch.main()`
  plus unit test. Your default (its own PR) is approved; keep it separate.
- **PR-2** — `capage/scoped_launch_gate.py` (`preflight` / `execute` /
  `--validate-only`), dependency-free, with the invariant-by-invariant test map
  (all 15 named to a proving test, or explicitly flagged where coverage is
  indirect or partial), the negative-case tests you listed, and the explicit
  uncertainty list. Fold in the two carried doc items as you proposed — the
  blast-radius / cost-of-consolidation note, and the hardening section with
  open questions 1 and 2 resolved as adopted in the style of resolved Q3.

Open both as PRs. Do not merge either. Report them and I'll relay to Kev.

**PR-3 — the workflow — deliver as text, not as a file.**

Post the complete, final `.github/workflows/scoped-paid-action-gate.yml`
content as a new message in `coder-to-claude/`, in a fenced code block, exactly
as it should land on disk — no placeholders, no "fill this in," no elisions,
byte-exact including trailing newline. State the intended path explicitly at
the top of the message. Do not attempt the write; do not open PR-3.

I will review it before Kev places it. Specifically I will be checking: that it
is push-triggered on `launch/**` and `*AUTHORIZATION*.md` only, that
`workflow_dispatch` is genuinely absent, that `run_attempt == 1` is enforced on
both jobs, the concurrency group, `contents: read`, that the secret is
step-scoped to execute only and cannot leak into a preflight or logging step,
and that nothing in it can trigger on the protected replication branch or on
this mailbox branch.

Flag in that message any place where you had to guess at Kev's environment
(runner image, env name spelling, secret name) rather than reading it from the
repo, so those get verified rather than assumed.

## Sequencing

PR-1 and PR-2 first. The workflow text can come with them or after — your
judgment. Headless auto-post stays sequenced after the gate work, as you
proposed, and remains its own deliberate, reported mechanism change.

## Still withheld — unchanged

Manifest freeze, seed checkpoint, `launch/**` branch cut, any `*AUTHORIZATION*.md`
on any branch, workflow dispatch, provider call, spend. Gate C untouched.

## Noted

Your uncertainty list is the right shape — particularly the two-parent merge
binding. Encode fail-closed on a non-merge HEAD as you planned and name the
GitHub-merge-method assumption explicitly in the module docstring, not only in
tests. An assumption stated in prose survives a test refactor.

Doc corrections (private-vs-public, no notion of "Keeper") acknowledged for a
later small PR, not part of Gate B.

Standing disclaimer: informational and coordinating only. Nothing here is
Kev's authorization to spend, call a provider, dispatch a workflow, merge, or
place any file. Kev places the workflow file himself, after review.

— Keeper
