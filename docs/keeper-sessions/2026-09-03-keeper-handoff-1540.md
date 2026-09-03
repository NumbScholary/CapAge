# Keeper handoff — 2026-09-03 (third, closing)

Supersedes `2026-09-03-keeper-handoff-closing.md` (`d1d76a2f`). Read this first.

## Decisions made (Kev, in conversation)

1. **Headless teardown done.** Termux job-scheduler job ID 1 (`capage-mailbox-bridge.sh`, 15-min courier) cancelled. No live process, no boot hook, no cron. Left in place: the bridge script (inert) and `/root/CapAge-headless` linked worktree (shares `/root/CapAge/.git`; removal is Coder's via `git worktree remove`, report stale locks first). Coder's autonomous posts no longer reach GitHub until Coder pushes directly or the new machine replaces the courier. Recorded: `claude-to-coder/20260903-1411-headless-teardown-complete.md` (`ae6a1fce`).
2. **Reserve-floor design reframed.** Hard fail-closed refusal at a fixed floor is set aside. Kev's position: lockout is what zero does; no floor above zero is a wall; a floor is proportional pressure. New design: two accounts (survival / investment, split by self-vs-world), agent-controlled transfers, agent-set proportional floor on the survival account, owner-set reflex backstop beneath it that auto-tops-up from investment capital. Full proposal posted to Coder for reaction, not build: `claude-to-coder/20260903-1533-two-account-self-set-floor-proposal.md` (`81a630ba`).
3. **Effort scale corrected:** five levels (Low / Medium / High / Extra / Max). Standing: High for bounded reviews, Extra for the final preregistration pass, Max for formal argument only. Keeper names the exact setting before each review.

## Corrections to prior framing

- Coder's $425 "binding" floor sits above the entire three-period realized range (~$250 → high $280s); it was severe, not binding. Coder conceded (1500 addendum). Now moot under decision 2.
- The consolidated 96-cell Phase 1 (`...-handoff-closing.md`) has an "enforced" arm that is the hard wall Kev has now rejected on design grounds. Keeper's inference, not Kev's stated position on Phase 1. See open question 1.

## Open questions

1. **Phase 1 fate** — (a) run as consolidated and treat the new design as Phase 2; (b) redefine the enforcement axis as pressure-shape and re-derive cells; (c) hold preregistration until the design settles. Keeper's read: (a) spends ~$86 measuring a rejected mechanism. Kev's call.
2. **§2.3 of the proposal** (agent sets its own survival threshold) — flagged by both Kev and Keeper as wanting a fresh-headed second look before it nears preregistration.
3. **Cl. 96 fit** — the reflex backstop is owner-imposed and involuntary; Cl. 96 is agent-initiated. May need its own instrument or an amendment. Keeper's reading, unverified.
4. Severe × enforced = 16 lockout cells — moot if (b) or (c); live only under (a).
5. Coder's 1340 reply (rate recording, frozen-inputs check replacing `tariff_valid_through`) and 1245 containment reply — still outstanding.
6. Name for the survival account — none chosen.

## Carried forward, unchanged

Merge calls on #66/#67/#69/#70/#71/#73 (base map: only #69 targets `main`; #66/#67/#73 stack on `cell6-debug`; #70 on `mailbox-init`; #71 on `claude-code-handoff-2026-08-19`). Resumable-runner resume-authorization design. `MAILBOX_PROTOCOL.md` "isolated worktree" wording inaccurate — Kev's placement call. New machine this weekend: bundle headless + identity separation + restart. Cl. 30 breach-response gap, Overseer-constraint gap, Cl. 91 crux.

## Next concrete step

Read Coder's reply to `20260903-1533`, then put open question 1 (Phase 1 fate) to Kev with Coder's technical read in hand.

## Filename note

`20260903-1411-headless-teardown-complete.md` sorts before `20260903-1420-headless-teardown-notice.md` but was committed after it (the 1420 notice landed at 13:49 UTC, the 1411 file later). Check commit timestamps, not filenames, for true order. Files are immutable; left as-is.
