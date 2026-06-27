# Task 7 — Create the Architecture and System Design Documents

Create and fully populate:

- `docs/flowchart.md`
- `docs/architecture.md`
- `docs/system-design.md`
- `docs/adr/0001-separate-runtime-and-gateway.md`

## Flowchart

Include a Mermaid flowchart showing:

1. Engineer or CI submits an agent run.
2. Runtime loads base agent and overlay.
3. Runtime assembles instructions and schema.
4. Gateway loads the profile.
5. Router evaluates candidate models.
6. Eligible provider is selected.
7. Provider response is normalized.
8. Runtime validates structured output.
9. Result and routing metadata are returned.
10. Error paths for no eligible model and invalid output.

## Architecture

Include a Mermaid component diagram covering:

- CLI/API clients.
- Agent runtime.
- Agent registry/files.
- Overlay resolver.
- Model gateway.
- Router.
- Profile and model registries.
- Provider adapters.
- OpenAI.
- Fake provider.
- Future tool/MCP gateway.
- Future observability and policy services.

## System design

Cover:

- Executive summary.
- Problem statement.
- Goals and non-goals.
- Core design principles.
- Component responsibilities.
- Domain contracts.
- End-to-end request sequence.
- Capability-based routing.
- Failure and fallback semantics.
- Agent versioning.
- Overlay customization.
- Security and identity boundaries.
- Observability.
- Testing and evaluation.
- Horizontal scaling path.
- Deployment evolution.
- Trade-offs.
- Future MCP and durable workflow integration.

Clearly distinguish the implemented proof of concept from the proposed production architecture.

## ADR

Explain why the model gateway manages individual model interactions while the runtime manages agent behavior, context, validation, and future tool loops.

Reference actual code paths from the repository.
