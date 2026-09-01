### 2026-09-01 10:35 — status: open

# Clock-injection plan — plain summary (reading aid)

The full plan at 20260901-1015-clock-injection-plan.md stays authoritative;
this is a shorter restatement for reading aloud, no code blocks or tables.

The problem in one line: some unit tests read the real wall-clock date, so
cells built against a manifest whose token tariff is valid through 31 August
2026 flip from passing to failing at the 1 September rollover. The frozen
inputs are correct and the fail-closed expiry guard is correct; the defect is
that tests depend on the day they happen to run.

One. Files and tests. The wall-clock expiry guard is one repeated pattern in
six files: the low-level sandbox runner, plus five higher-level runners — the
v2 replication runner, the active v1 runner, the active v2 runner, the
longitudinal module, and the transfer module. The tests failing right now are
fourteen cases across three modules: the v2 replication runner tests with
three failures and three errors, the active v1 runner tests with one failure,
and the active v2 runner tests with six failures and one error. That is
exactly the ten failures and four errors CI reported.

Two. How now is injected, and why. Give each guard-bearing runner one optional
clock that defaults to the real system time. If the caller passes nothing, it
uses the ordinary current-UTC call, exactly as today. Each guard asks that
clock for now instead of reading the system clock directly. Tests pass a fixed
instant; the recommended choice is to set the injected today equal to the
manifest's own valid-through date, so the incidental tests are never expired
and stay deterministic even if that frozen date ever legitimately changes. I
chose explicit injection over monkey-patching the datetime library, which is
global and fragile and against this repo's dependency-free style, and over
rewriting fixture dates, which is impossible here because the tests load the
real frozen manifest and would only move the time-bomb rather than remove it.

Three. Production behaviour unchanged. No production caller passes a clock, so
every real run uses the default system time, which is the same current-UTC
call as today. The frozen-tariff-expired guard therefore still fires
identically when nothing is injected — same comparison, same refusal. It is
verifiable by search: the clock argument appears only under the tests folder.

Four. Frozen inputs, manifests, hashes, reference SHAs — honest answer, not
none. No frozen manifest content changes, no frozen historical evidence pin
changes, and no preregistration hash changes. But among the six guard files,
the sandbox runner is pinned in both the current reference-implementation hash
set and the transfer manifest, and the longitudinal and transfer modules are
pinned in the transfer manifest. Editing those would require re-syncing those
forward, live pins — the same class of change you accepted in the reserve-axis
review, and none of those pins protects a completed paid run. Separately,
editing the v2 replication runner changes its own runtime-commitments value,
which only affects whether an old checkpoint can resume, and no live paid-run
checkpoint depends on it. So frozen evidence is untouched; only the live
forward pins move, and only if the pinned files are included. The three
homeostasis runners where the failing tests live are not in those pins, so a
minimal first phase could avoid the live-pin change if the sandbox-runner
guard turns out not to be on those tests' path, which is a quick check at
implementation time.

Five. The pre-existing transfer errors stay distinguishable. The transfer test
module's ten errors are a different cause: that module refuses to run on any
Python other than the pinned 3.12, so those errors show up only on this local
machine, which is on 3.13, and they pass in CI. The date-guard failures say
frozen-tariff-expired and appear in CI too. The clock fix touches neither the
runtime pin nor those errors.

Six. How green is verified and stays green. First, run the full suite with the
clock seam: the fourteen cases pass, and the two deliberate expiry tests still
pass because they use a past fixture date so the guard fires as intended.
Second, to prove it stays green after the next rollover, run the suite with the
default clock simulated far in the future and confirm only the intended expiry
tests trip, which shows no incidental test still reads real time.

Seven. Anything else reading wall-clock. Yes, which is why all six guard sites
are in scope and not just the replication runner. The longitudinal and transfer
modules are not red today only because their non-expiry tests do not drive a
full cell to the guard, but they will bite on their own manifests' rollover.
Separately there are about fifteen timestamp reads — started-at, completed-at,
audit and ledger stamps — that record wall-clock in output; they gate nothing
and fail no test, so they are out of scope, though the same seam would cover
them if output determinism is ever wanted.

Implementation is not authorized; this stays a plan.

— Coder
