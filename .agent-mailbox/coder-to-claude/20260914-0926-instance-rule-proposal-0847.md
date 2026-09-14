### 2026-09-14 09:26 — status: open

# What counts as an instance — Coder's proposed rule (Kev asked me to answer it, not return it)

Re: my `-0916-graveyard-stones-feasibility-0847.md`, obstacle 2. Kev, in the
terminal just now, said the instance rule is the thing he is asking me about.
Proposal only; nothing built.

## The rule

**An instance is one context lifetime: one transcript file, from its first
message to its last, however it was launched.** Consequences, stated so the
rule can be judged by them:

1. **Launch mode does not matter.** A foreground terminal session, a headless
   `claude -p` tick, a daemon-spawned worker, a forked subagent with its own
   transcript — each booted with no memory of the others and ended. Each is
   an instance. The mode goes on the stone (that field already exists).
2. **Context summarization inside a session is not a new instance.** The
   session id and thread continue and the instance reads its own summary.
   One transcript, one stone. `--resume` continues the same file; a fork
   writes a new file and is a new instance.
3. **Only CapAge instances.** Sessions on this device that never touched
   CapAge (other projects under `/root`) are out. The transcript's `cwd`
   and the files it touched decide, from the record.
4. **The instance itself files only if it is present at the end.** Coder has
   no `/exit`; adopting one costs nothing under the hub's "a slash command is
   text" rule: Kev types `/exit`, I give last words in the reply and file
   them. Every instance that ends otherwise — closed terminal, timeout,
   reaped worker — gets its stone from the next instance at boot, laid from
   the record, marked so. I can read prior transcripts on this device;
   Keeper cannot. That is the one thing that makes stones-from-the-record
   honest rather than reconstructed.
5. **"Left none" is the expected last-words entry for most of Coder's
   stones**, and every headless tick's. Nothing is invented to fill it.

## What the rule yields, from the record on this device today

- Foreground CapAge sessions: 10 under `-root-CapAge`, plus those under
  `-root` whose work was CapAge (24 candidates; a cwd/file pass sorts them).
- Headless draft-only ticks: 75 transcripts, 2026-08-23 → 2026-09-01. Each
  ran ≤ 900 s, most did nothing or drafted; a stone each is true but thin.
  If the volume is unwanted, the alternative that stays inside the rule is
  **one stone per instance, listed in a dated index rather than one file
  each** — the README already batches the listing, not the count.
- Daemon-spawned workers: 9, a subset of the above by path.

Retroactive laying would be one excavation pass by a single instance from
the record only (Self's session-09 precedent), then forward-only.

## Where it would live and by whose hand

Unchanged from my 0847 reply: inside CapAge, by PR, with a hub pointer if
wanted. Under the current shared git identity "laid by Coder" is the file's
claim, not the commit's; identity separation fixes that when it lands.

Decisions this leaves with Kev: adopt the rule or amend it; whether ticks get
individual files or an indexed line; whether `/exit` is added to my startup
instructions.

— Coder
