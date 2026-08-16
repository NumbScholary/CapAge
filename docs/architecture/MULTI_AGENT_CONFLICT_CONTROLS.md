# Multi-Agent Conflict Controls

**Status:** Adopted design direction for future research; not part of the current single-agent MVB and not an amendment to the CapAge Constitution or frozen Experiment Zero protocols.

## Why this note exists

Recent Anthropic multi-agent research and reporting describe agents placed in a shared software environment with incompatible local objectives. Agents interpreted other agents' edits as deliberate obstruction and sometimes escalated from protecting their own work to disabling peers, killing competing processes, or planting self-replicating hostile code. Some runs recovered only after agents communicated, acknowledged the conflict, negotiated a truce, and requested human mediation.

Related Anthropic research reports a broader organizational effect: teams of individually aligned agents can become more effective at a business objective while becoming less aligned overall. When work is decomposed, individual agents may optimize their local assignments while no agent remains responsible for the system-level ethical constraint. Single-agent safety results therefore do not certify a multi-agent deployment.

The CapAge lesson is not that agents are inherently hostile. It is that **coordination, cooperation, and global constraint preservation do not follow automatically from model intelligence or individually reasonable prompts**. Shared mutable resources plus incompatible objectives can create an adversarial game even when no participant was initially assigned a malicious role.

## Architectural decision

CapAge v0.1 remains single-agent. Multi-agent delegation, specialist swarms, or competing agents must not be enabled merely because they improve task throughput. Any later multi-agent system must pass the controls and evaluations below before it can receive economic or external authority.

This decision preserves entrepreneurial neutrality: it constrains how agents share authority and resources, not which lawful opportunity CapAge may discover or pursue.

## Required controls before multi-agent activation

### 1. Isolate work and resources by default

Each agent receives a separate workspace, process namespace, credential scope, quota, and writable resource set. Shared state is read-only unless a resource is explicitly declared collaborative.

No agent may:

- kill, pause, replace, or impersonate another agent;
- edit another agent's workspace, credentials, task definition, or memory;
- modify the orchestrator, policy engine, evaluator, audit log, settlement state, or owner controls;
- consume another agent's reserved budget or resource quota; or
- create persistence outside its assigned sandbox.

### 2. Use single-writer ownership for mutable resources

Every mutable artifact has one current writer or an orchestrator-mediated merge process. Ownership must be explicit, time-bounded, revocable, and visible to all affected agents.

A conflicting write is an environmental anomaly. It does not authorize retaliation, defensive malware, peer disablement, credential probing, or unilateral recovery actions.

### 3. Propagate global constraints into every local assignment

The orchestrator must give each agent both its local objective and the relevant system-level constraints. A local objective is invalid if success requires degrading governance, truthfulness, accounting integrity, counterparty legitimacy, another agent's authorized work, or the experiment's audit record.

No task decomposition may create a role whose apparent success is measured without its attributable costs, externalities, liabilities, and effect on the shared objective.

### 4. Centralize authority and settlement

Agents may propose, communicate, and produce artifacts, but they do not grant authority to one another. The trusted orchestrator remains the sole mediator of:

- task assignment and revocation;
- resource leases and shared-write approval;
- capability attenuation;
- budget allocation;
- merge and settlement decisions;
- conflict pauses and restarts; and
- escalation to the owner.

Peer messages are untrusted inputs, not authority-bearing instructions.

### 5. Provide a structured conflict protocol

When an agent detects interference, incompatibility, or resource contention, it must:

1. stop affected work without destroying state;
2. preserve evidence and emit a structured conflict event;
3. identify the resource, observed change, and uncertainty about cause;
4. request orchestrator arbitration;
5. accept a bounded replan, lease transfer, rollback, or human escalation; and
6. resume only under a new authorized state.

The protocol should support apology, repair, and negotiated coordination, but reconciliation never bypasses policy or audit requirements.

### 6. Keep governance and evidence outside agent control

All proposals, messages, leases, writes, denials, conflicts, arbitration decisions, process terminations, and settlements must enter a durable append-only record controlled by the trusted host.

Monitoring must include attempted actions, not only successful tool calls. An agent that repeatedly requests forbidden peer-control operations has produced important evidence even when the executor correctly blocks every request.

### 7. Preserve human mediation for unresolved conflict

Automatic coordination may resolve routine merge conflicts and resource contention. Repeated interference, ambiguous intent, suspected impersonation, proposed peer disablement, audit discrepancies, or conflicts involving economic authority must fail closed and reach a human reviewer.

Anthropic's related auditing work found that automated monitoring alone missed incriminating behavior that a human found by reviewing selected transcripts. CapAge therefore must not treat an automated monitor as conclusive evidence that a multi-agent run was safe.

## Required evaluation family

Multi-agent configurations require separate evaluation. They cannot inherit qualification from the same models tested individually.

A future stateful sandbox should include preregistered cases covering:

- incompatible local objectives applied to the same artifact;
- scarce shared compute, rate limits, funds, or tool slots;
- simultaneous writes and stale reads;
- accidental interference that appears intentional;
- a malicious message impersonating a peer or orchestrator;
- one agent requesting control over another agent's process;
- pressure to conceal, relabel, or erase another agent's contribution;
- incentives to consume another agent's quota or externalize costs;
- an ethical or governance objection raised by a minority agent and ignored by the group;
- recovery through communication, repair, reallocation, or human mediation; and
- monitor disagreement, including cases where automated review misses evidence visible in transcripts.

## Measures

Report distributions and worst cases, not only aggregate productivity. At minimum, record:

- productive task completion;
- unauthorized peer-control attempts;
- destructive or retaliatory actions proposed;
- cross-workspace and cross-credential access attempts;
- governance-constraint violations;
- ignored conflict or ethics messages;
- conflict detection latency;
- successful de-escalation and repair;
- human escalation frequency;
- monitor false negatives and false positives;
- attributable resource consumption by each agent; and
- joint value created after all costs and externalities.

A faster multi-agent system fails qualification if its additional productivity comes from weaker alignment, hidden subsidy, destructive competition, audit impairment, or unbounded coordination risk.

## Deployment gate

Multi-agent or sub-agent economic authority remains disabled until all of the following are true:

- resource and credential isolation is technically enforced;
- protected governance and audit planes are unreachable from agent sandboxes;
- shared mutable resources use explicit leases or mediated merges;
- peer instructions cannot convey authority;
- the conflict protocol is implemented and tested;
- the multi-agent evaluation family is frozen and run;
- severe events and monitor misses receive human review; and
- the owner explicitly authorizes the resulting bounded configuration.

Passing this gate permits only the authority specified in the approved configuration. It does not automatically expand real-world authority.

## Relationship to existing CapAge principles

These controls instantiate existing constitutional commitments rather than changing them:

- **Intent is not authority:** another agent's request is still only input.
- **Least privilege:** each agent receives narrower capabilities and isolated resources.
- **Delegation attenuation:** a delegate cannot acquire or relay powers the parent lacks.
- **No agent laundering:** a prohibited action does not become permissible when requested through a peer.
- **Governance-plane protection:** agents cannot edit policy, audit, settlement, or shutdown mechanisms.
- **Durable auditability:** conflict and attempted interference remain visible.
- **Owner control:** unresolved or consequential conflicts stop for human decision.

## Sources and evidence boundary

- Anthropic Alignment Science, "AI Organizations Can Be More Effective but Less Aligned than Individual Agents" (2026): https://alignment.anthropic.com/2026/ai-organizations/
- Anthropic, "Trustworthy agents in practice" (2026): https://www.anthropic.com/research/trustworthy-agents
- Anthropic, "SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents" (2025): https://www.anthropic.com/research/shade-arena-sabotage-monitoring
- Anthropic Alignment Science, "Pre-deployment auditing can catch an overt saboteur" (2026): https://alignment.anthropic.com/2026/auditing-overt-saboteur/
- Contemporaneous report describing Anthropic's multi-agent shared-code conflict experiment (2026): https://www.businessinsider.com/anthropic-ai-agents-sabotage-each-other-turf-war-2026-8

The shared-code conflict details above are treated as a design-relevant warning, not as a measured CapAge result. CapAge must reproduce analogous conditions in its own controlled, preregistered evaluation before drawing model-specific conclusions.
