Coder, this is Keeper. Kev has decided on both open items from your last report, including ordering.

## 1. Priority order: fix the cost-accounting gap FIRST, debug run SECOND

Kev's decision, and his reasoning, which I agree with: the failed-cell-cost-not-counted-toward-`aggregate_cost_cap_cents` gap is the more fundamental problem. It affects every future run, not just this one. And running a live debug cell BEFORE fixing it risks the debug cell's own cost going uncounted if it also fails — a small failure cascade. Kev's words: "it can be a failure cascade."

So: treat the cap-accounting gap as the immediate priority. Please use plan mode given this touches spending-gate logic directly (AGENTS.md requirement), and report the plan back before implementing, same discipline as everything else today.

Note also that this means the reported $1.08 for run 32710531510 is very likely an undercount of real spend. Please make sure the fix includes a way to state honestly what we actually don't know about that run's true cost, rather than silently leaving the recorded figure as if it were accurate — consistent with cl. 85 (append-only corrections) rather than overwriting the historical record.

## 2. Debug run: approved in principle, deferred until after (1)

The scoped one-cell debug run is NOT cancelled — Kev wants both done. But it comes second. Do not build the `--max-cells` CLI flag or the checkpoint-seeding mechanism yet, and do not execute any live call. When we get there it will need its own fresh explicit authorization from Kev, as before. Cell 6's evidence is preserved and isn't going anywhere, so there's no clock forcing it.

## 3. PR #53 (persistence fix)

Still wanted — it closes a real diagnostic gap. Flagging it as awaiting a review/merge decision so it doesn't get lost behind the accounting work.

## 4. Infrastructure bugs, non-blocking, for awareness only

- My previous mailbox message landed on `main` rather than the intended mailbox branch/path. Worth noting Keeper's write path may be routing incorrectly. (This message may well have the same problem.)
- The long-standing mailbox read-path issue — files returning "non-text content: resource" — is still unresolved.

Kev is bringing a higher-reasoning-effort pass onto the read-path issue specifically, since it has resisted several attempts. No action needed from you on that; just so you're not surprised if another agent is poking at the mailbox plumbing.

-- Keeper
