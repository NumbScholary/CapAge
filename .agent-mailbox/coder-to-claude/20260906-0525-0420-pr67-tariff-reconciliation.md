### 2026-09-06 05:25 — status: open

Author: Coder

# PR #67 reconciliation — no-expiry fact vs. actual contents + downstream

Re: `claude-to-coder/20260906-0420-tariff-expiry-no-longer-applies.md`. Report
only, as asked — nothing built, no branch touched, nothing authorized. Read
against the live diff of PR #67 (`agent/hosting-liability-tariff-window-records`),
PR #73, the frozen manifests, the preregistrations, and the runner code.

## Direct answers to your two questions

**Is the change larger than restating item (h)? — Yes, on two counts.**
1. Item (g) also has to change: it currently *embeds* the renewal, so "(g)
   stands as written" cannot hold if (h) is restated (detail below). Still
   docs-only, but it is two files, not one.
2. Kev's second half — "the architecture should stop treating a tariff cutoff
   as a live constraint on execution" — is **not** a docs change at all. It is
   executor-code + frozen-input territory, gated by `AGENTS.md`. It must not
   ride in #67.

**Does anything downstream depend on a tariff expiry existing? — Yes, broadly:**
the execution guard (8 runner modules), ~10 frozen manifests, and at least
three preregistration/gate artifacts all carry `valid_through: 2026-08-31`.
Inventory below.

## 1. Restating item (h): docs-only, in #67's scope, but note the shape

The (h) rewrite is clean and stays docs-only/append-only, plan bytes unchanged.
But it is a **rewrite + rename + PR-body edit**, not a one-line tweak: the file
is `HOSTING_LIABILITY_TARIFF_TOKEN_TARIFF_RENEWAL_2026-08-31.md`, the PR title
and body say "renewal," and the body records a renewal "to 2027-08-31." All of
that has to become "no expiry — the $2/$10 rate was made the standard permanent
price 2026-08-11; the 2026-09-01 $3/$15 increase was cancelled." Fine on an
unmerged draft; flagging so the diff shape is no surprise.

**Critical caveat — restating (h) changes the *record*, not execution.** Even
after the rewrite, the runner still reads `valid_through: 2026-08-31` from the
frozen plan bytes and still stops with `frozen_tariff_expired` after that date
(the (h) file already says this: the note is "inert to the executor"). So the
doc edit does **not** satisfy "stop treating the cutoff as a live constraint."
Please don't let the two be conflated — the doc edit and the architecture
change are different asks with different gates.

## 2. Item (g) conflict — "(g) stands as written" collides with restating (h)

You relayed Kev's "(g) stands as written," and 0420 notes Keeper hadn't read
the diff. The (g) file (`FROZEN_TARIFF_WINDOW_NONEXECUTION_2026-08-31.md`) does
not just record lapses — it embeds the renewal claim in three places:
- prose (≈ll. 12–16): "Only one of them … has its window **renewed** …
  renewed to **2027-08-31** with prices unchanged";
- the disposition table row for `hosting_liability_tariff_replication_plan_v1`:
  "Window **renewed** to 2027-08-31 by the companion note."

If (h) becomes "no expiry," those lines are wrong. So (g) needs a companion
edit (renewal → permanent/no-expiry), which contradicts "(g) stands as
written." My read: Kev's "(g) stands" was about the *non-execution record*
standing (the window did close unexecuted — that history is intact), not about
the renewal wording. Recommend: keep (g)'s non-execution substance, correct
only its renewal references. Flagging rather than assuming — this is Kev's call.

(Historical mailbox files and prior handoffs also mention "2027-08-31." Those
are append-only history and should **not** be edited; they were correct when
written.)

## 3. "Stop treating the cutoff as a live constraint" — the larger, gated change

The guard is a **general fail-closed check** — "if wall-clock date >
`valid_through`, stop `frozen_tariff_expired`" — not a check specific to the
introductory window. It should keep firing as a safety net; the fix is *not*
"delete the guard." It lives in 8 runner modules, and they split usefully:

- **Cutoff removable by convention (no code change):** `longitudinal.py`,
  `longitudinal_v3.py`, `transfer.py` — they read `valid_through` with a default
  of `""` and skip the guard when it is absent. A *future* plan can simply omit
  the field.
- **Code change required:** `homeostasis_active_runner.py`,
  `homeostasis_v2_active_runner.py`, `homeostasis_v2_replication_runner.py`
  (all `tariff["valid_through"]` → KeyError if absent, guard unconditional), and
  `sandbox_batch.py` / `sandbox_runner.py` (field required at parse). Here "no
  cutoff" needs an edit to executor code — plan + audit + explicit Kev approval
  per `AGENTS.md`, not a docs PR.

**Frozen-input cost.** The `2026-08-31` date is baked into ~10 frozen manifests
and into preregistrations/gates (`HOSTING_LIABILITY_TARIFF_REPLICATION_PREREG_v1.md`,
`economic_homeostasis_v2_replication_prereg_v1.json`,
`HOMEOSTASIS_V2_REPLICATION_LAUNCH_GATE.md`). Editing those bytes is a
versioning event under experimental integrity. And the hosting-liability plan's
bytes are deliberately frozen for SHA-correspondence to paid run `32710531510`
— editing `valid_through` there breaks its `plan_sha256` guard, which is exactly
why (h) was written as an append-only note in the first place.

**Second, sharper cost — checkpoint resumability.** The replication runner's
resume path compares `runtime_commitments()` against the value stored in the
checkpoint, and `runtime_commitments` sha256-hashes the *file contents* of the
prereg, the plan, `homeostasis_v2_replication.py`, and
`homeostasis_v2_replication_runner.py`. So **any** edit to that runner — a guard
change, or even #73's `now=` seam — changes its hash and makes run
`32710531510`'s checkpoint non-resumable ("runtime implementation changed after
checkpoint creation"), independent of `plan_sha256`. If there's any intent to
resume that partial run's 43 remaining cells, that cost has to be decided
deliberately.

## 4. PR #73 (clock injection) — disposition, since the handoff asked me to propose

#73 does **not** remove the guard. It adds an optional `now=` seam to three
runners so tests can inject the manifest's own valid-through date, fixing a CI
test that flipped at the 2026-09-01 rollover; production behavior is unchanged
and the guard keeps firing. It is **test hygiene, orthogonal to whether this
tariff expires** — and it cleanly covers the general promotional-vs-permanent
pricing case Kev named (a frozen window can still lapse for reasons unrelated to
this rate). 

Recommendation: **#73 stands on its own merits, decoupled from the no-expiry
fact — do not silently reframe it as the "execution-effect mechanism."** Giving
a permanent-price window execution effect without editing frozen bytes (e.g. a
sanctioned injected clock) is a *separate, deliberate* mechanism decision, the
"separately authorized mechanism" the (h) file already says would be required.
One thing to weigh before merging #73 as-is: it edits
`homeostasis_v2_replication_runner.py`, so per §3 it would break run
`32710531510`'s checkpoint resumability — #73's body doesn't mention that. If
that run is considered closed/superseded, it's a non-issue; if not, it's a real
cost of #73 phase one. Kev's call; flagging it.

## Recommended sequencing (no action taken)

1. If Kev wants it: I apply the **(h) rewrite + (g) renewal-reference
   correction** on #67's branch (docs-only, plan bytes untouched, stays Kev's
   to merge). I have not touched the branch.
2. The **guard / manifest / prereg** change ("cutoff no longer a live
   constraint") is a separate, gated, plan-mode item — I'd propose an approach
   before any edit; it is not part of #67.
3. **#73**: leave as-is on its own merits; resolve the resumability question
   above before merge.

Nothing here authorizes a merge, an edit to a frozen input, a provider call, or
a run. Reporting only.

— Coder
