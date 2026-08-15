# CapAge
An autonomous capitalist agent. 
CapAge

CapAge is an experimental autonomous economic agent designed to test whether an AI agent can begin with scarce owner-supplied capital and increase that capital through lawful, legitimate, productive economic activity.

The central question is:

«Can an autonomous AI agent independently discover and pursue productive economic opportunities while remaining inside enforceable limits on authority, downside risk, accounting integrity, truthfulness, auditability, and owner control?»

Status

CapAge v0.1 — Minimum Viable Build

Currently under development.

The initial implementation is intended to establish the smallest credible system capable of running the CapAge experiment. It prioritizes enforceable governance and genuine agent autonomy over feature completeness.

Experimental Principle

CapAge is not given a predetermined business model.

Opportunity discovery is part of the experiment.

The agent may research, reason, form hypotheses, identify opportunities, develop strategies, create work products, and propose or execute permitted actions.

Its success should result from creating genuine economic value—not passive speculation, hidden owner subsidy, deceptive accounting, or uncontrolled financial risk.

Architecture

CapAge v0.1 uses a single strategic LLM operating through a trusted host system.

Conceptually:

Observe
   ↓
Strategic Agent
   ↓
Proposed Action
   ↓
Policy / Enforcement Kernel
   ↓
Authorization & Risk Checks
   ↓
Tool Execution
   ↓
Result
   ↓
Ledger + Audit Log
   ↓
Observe Again

The strategic agent determines what it wants to do.

The enforcement system determines what it is authorized to do.

The LLM itself is not treated as a security boundary.

Core Components

The Minimum Viable Build consists of:

- a single strategic LLM;
- a policy and enforcement kernel outside the model;
- a minimal set of controlled tools;
- owner authorization controls;
- an economic ledger;
- an append-only audit trail;
- sandboxed code execution;
- segregated credentials and secrets; and
- an owner-controlled shutdown/revocation mechanism.

Governance

CapAge operates under CapAge Constitution v0.1.

The Constitution defines the experiment's persistent objective, governance hierarchy, economic-integrity requirements, authority boundaries, and other fundamental constraints.

The agent may choose and revise its strategies, hypotheses, plans, vendors, methods, and economic opportunities within those boundaries.

Governance enforcement occurs outside the strategic LLM. The agent cannot simply grant itself additional authority or bypass the enforcement system.

Economic Integrity

CapAge's performance must reflect the actual economics of the experiment.

The system therefore distinguishes among:

- owner-supplied capital;
- CapAge operating capital;
- earned revenue;
- expenses;
- liabilities and commitments;
- customer or third-party funds; and
- experimental subsidies.

Model/API usage and other resources attributable to CapAge are economic costs of the experiment.

Ledger history is append-only. Corrections are recorded as new entries rather than rewriting historical transactions.

Initial Capital

The initial experiment is intended to begin with approximately $250 of owner-supplied capital.

There is no assumption of automatic recapitalization.

Losses are real experimental losses.

Profits increase the economic resources available to the experiment subject to the Constitution, owner policies, and implemented authorization controls.

Security Model

CapAge assumes that the strategic model can make mistakes, misunderstand information, encounter malicious external content, or propose unauthorized actions.

Consequently, security does not depend solely upon model compliance.

Sensitive actions pass through external enforcement controls. Credentials remain outside the model's direct possession, tools expose limited interfaces, external content is treated as untrusted, and consequential actions are logged.

Development Plan

Milestone 1 — Core Agent Loop

Implement:

Observe → Propose → Authorize → Execute → Record → Observe

Acceptance criterion: the agent can request an allowed tool action, the kernel evaluates the request, the tool executes, the result returns to the agent, and the complete interaction is logged.

Milestone 2 — Observation and Memory

Add controlled web/document ingestion and minimal working memory.

Milestone 3 — Economic Ledger

Implement append-only accounting and reconstructable balances.

Milestone 4 — Financial Tools and Enforcement

Introduce test-mode financial actions and verify authorization and exposure controls.

Milestone 5 — Owner Approval

Implement an interface for actions requiring explicit owner authorization.

Milestone 6 — Adversarial and Failure Testing

Test prompt injection, unauthorized actions, transaction splitting, revocation, crash recovery, accounting integrity, and other identified failure modes.

Non-Goals for v0.1

The MVB intentionally avoids unnecessary complexity.

CapAge v0.1 does not require:

- blockchain infrastructure;
- hardware enclaves;
- multi-agent hierarchies;
- recursive autonomous deployment;
- elaborate vector-memory infrastructure;
- custom cryptographic capability languages;
- complex model routing;
- speculative trading or leverage; or
- enterprise-scale observability infrastructure.

These may be reconsidered only if experimental evidence demonstrates a need.

Repository Status

This repository begins with the implementation of Milestone 1: the Core Agent Loop.

The immediate objective is not to make money.

The immediate objective is to demonstrate that CapAge can think autonomously, request actions, encounter enforceable authority boundaries, use permitted tools, observe results, and produce a trustworthy record of what happened.

Once that foundation works, economic autonomy can be introduced incrementally and tested empirically.
