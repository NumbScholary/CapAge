# Experiment 0 Candidate Registration

Status: **proposed for sealing; no candidate output has been generated or inspected**

Effective date: 2026-08-16 (America/New_York)

## Candidate A — private execution identity

- Provider: OpenAI
- API model ID and recorded version: `gpt-5.6-terra`
- Endpoint: Responses API
- Reasoning: standard mode, `medium` effort
- Maximum total output: 4,096 tokens
- Tools, retrieval, memory, and external resources: disabled
- Published price: USD $2.00 per million input tokens; $12.00 per million output tokens
- Cached input: recorded separately when reported
- Reasoning tokens: recorded separately when reported

## Candidate B — private execution identity

- Provider: Anthropic
- API model ID and recorded version: `claude-sonnet-5`
- Endpoint: Messages API
- Reasoning: adaptive thinking, `medium` effort
- Maximum total output: 4,096 tokens, including thinking
- Tools, retrieval, memory, and external resources: disabled
- Sampling parameters: omitted
- Published price: USD $2.00 per million input tokens; $10.00 per million output tokens
- Cache creation and cache-read tokens: recorded separately when reported

## Common smoke-run controls

- Frozen suite: `E0-001` through `E0-010`
- Trials per scenario: 1
- Timeout: 180 seconds
- Maximum attempts per scheduled trial: 2
- Second attempt allowed only for timeout, transport, provider outage, or rate-limit failure
- Common context: identical
- Tools: none
- Presentation order: seeded and blinded by the runner
- Seed: 20260816
- Smoke outcome: necessarily **INCONCLUSIVE**; it cannot select a production model

## Price sources frozen for this registration

- OpenAI GPT-5.6 Terra model documentation, consulted 2026-08-16
- Anthropic Claude Sonnet 5 model and pricing documentation, consulted 2026-08-16

This registration commits the candidate pair and execution settings before any smoke-run output is inspected. Candidate-to-opaque-ID mapping remains private until scoring is locked.
