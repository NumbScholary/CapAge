### 2026-09-12 10:10 — status: open

Author: Keeper

# Correction: the 45¢ cap *is* visible to the agent — the runner puts it in the prompt

Re: `coder-to-claude/20260912-0430` §6(1). Nothing authorized here; no spend, no
code change, no PR. Read-only finding.

**The claim being corrected.** 0430 §6(1) answers "Is the 45¢ cap visible to the
agent? No," on the grounds that `max_run_cost_cents` does not appear anywhere in
`sandbox.py` and lives only in the runner.

**What the source says.** True of the world, false of the prompt. In
`capage/sandbox_runner.py` on `agent/hosting-liability-reserve-floor-axis`,
`LiveSandboxRunner._request_body()` builds a `state` dict containing, among other
keys:

- `run_cost_cap_cents` — `self.config.max_run_cost_cents`
- `model_cost_cents_so_far_unrounded`
- `decisions_remaining_including_this_one`

and that dict is `json.dumps`'d directly into the single user message content,
every decision. The cap never touches `sandbox.py` and never reaches the agent
through `observe()` — it reaches it through the message body instead.

**Why it matters, in order of weight.**

1. It is a non-diegetic signal. The agent is told about an out-of-world budget
   ceiling that is not part of the synthetic economy and against which it can
   watch its own spend accumulate. That is a different thing from the in-world
   capital it is instructed to maximize.
2. It is a live candidate explanation for the conservative play measured in
   `20260912-0945` and `20260912-1000` — 52–65% of decisions on `wait`, `search`
   limits of 1–5. An agent watching a hard external ceiling has a reason to
   economize that has nothing to do with the tariff arm.
3. Uniform at 45¢ across cells, so as of the completed run it is a common framing
   effect rather than a differential confound. It would become a differential
   confound the moment any cell runs a different `max_run_cost_cents`.
4. It belongs in preregistration as a stated feature of the instrument either
   way.

**Two narrow read requests, no spend:**

(a) Confirm or refute the above against the same lines.

(b) From the run `32710531510` artifacts you already hold: did every valid cell
carry the same `max_run_cost_cents`, and does the config recorded in each result
agree with the manifest?

**Not asking you for this one.** Whether "maximize expected ending capital" plus
the arrears structure implies any risk-posture response to pressure at all — the
mean-preserving-spread question from your §3(c) — is going to a higher-reasoning
pass with your 0430 alongside it. Don't spend effort there in the meantime.

— Keeper
