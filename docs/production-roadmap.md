# Production Roadmap

This proof of concept is intentionally small. A production system needs a wider
platform around the same runtime/gateway boundary.

## Phase 1: POC Hardening

- Replace the small JSON Schema subset validator with a complete JSON Schema
  implementation.
- Add `amg check` to validate agents, overlays, profiles, and route eligibility.
- Add `amg explain-route PROFILE` for deterministic routing explanations.
- Expand OpenAI response normalization for refusals, incomplete responses, tool
  calls, and provider error bodies.
- Add structured logging with prompt and secret redaction tests.
- Add request IDs to CLI/API/runtime/gateway responses.

## Phase 2: Service Readiness

- Add API authentication.
- Add workload identity and tenant/team context.
- Add rate limits, request size limits, and quotas.
- Add provider timeouts, retry policy, and circuit breakers.
- Move secrets to AWS Secrets Manager, SSM Parameter Store, or another managed
  secret backend.
- Add metrics for latency, routing decisions, token usage, cost estimates, and
  validation failures.
- Replace demo model metadata with centrally managed model capability and
  pricing data.

## Phase 3: Runtime Maturity

- Add durable run state.
- Add background workers and a queue.
- Add the Tool/MCP Gateway.
- Add human approval gates for write-capable tools.
- Add run cancellation and replay.
- Add evaluation fixtures for agent quality and regression testing.

## Phase 4: Governance and Scale

- Store agents, overlays, profiles, and models in immutable versioned registries.
- Add policy-as-code for model use, data classification, and tool permissions.
- Add a UI or admin API for reviewing route decisions and run history.
- Add multi-provider support beyond OpenAI and fake.
- Add regional deployment, failover, and provider-specific capacity controls.

## Phase 5: Enterprise Operations

- Integrate with organization identity providers.
- Add audit log export.
- Add cost allocation by team, agent, repository, and environment.
- Add SLO dashboards and alerting.
- Add change-management workflows for model/profile updates.
