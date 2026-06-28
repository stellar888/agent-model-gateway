# Codex Repository Instructions

## Mission

Build a small, comprehensible proof of concept for a provider-neutral agent runtime and model gateway.

The repository is intended to communicate an architecture to engineers and technical leaders. Prefer clarity, explicit interfaces, and good documentation over clever abstractions.

## Required outcomes

The repository must demonstrate:

1. An agent depends on a model profile, not a provider model name.
2. A model gateway resolves a profile to an eligible provider/model.
3. Provider SDKs are isolated inside provider adapters.
4. The gateway emits a normalized response.
5. The agent runtime validates the normalized response against an output schema.
6. The same agent can run against a fake provider or a real OpenAI provider.
7. Configuration can be layered without copying the base agent.
8. The architecture and boundaries are documented with Mermaid diagrams.

## Development rules

- Use Python 3.12 or newer.
- Use type hints throughout.
- Use Pydantic v2 for external and domain validation.
- Use async interfaces for provider calls and gateway execution.
- Use dependency injection rather than global provider clients.
- Keep modules small and focused.
- Do not leak OpenAI SDK types outside `app/providers/openai_provider.py`.
- Do not place workflow or agent-specific logic inside the gateway.
- Do not execute agent tools inside the model gateway.
- Do not silently fall back to a model that lacks required capabilities.
- Do not log API keys, authorization headers, full secrets, or sensitive prompt contents.
- Prefer deterministic tests.
- The fake provider is the default in tests and examples.
- Every public class and important function should have a concise docstring.
- Update documentation when architecture or behavior changes.

## Suggested repository structure

```text
.
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example
├── app/
│   ├── api.py
│   ├── config.py
│   ├── domain/
│   │   ├── agent.py
│   │   ├── capabilities.py
│   │   ├── messages.py
│   │   ├── models.py
│   │   └── responses.py
│   ├── gateway/
│   │   ├── service.py
│   │   ├── router.py
│   │   ├── registry.py
│   │   └── errors.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── fake_provider.py
│   │   └── openai_provider.py
│   ├── runtime/
│   │   ├── loader.py
│   │   ├── overlays.py
│   │   ├── runner.py
│   │   └── validation.py
│   └── cli.py
├── agents/
│   ├── pr-reviewer/
│   │   ├── agent.yaml
│   │   ├── prompt.md
│   │   └── output.schema.json
│   └── overlays/
│       └── payments-team.yaml
├── config/
│   ├── model-profiles.yaml
│   └── models.yaml
├── examples/
│   └── pr-reviewer-request.json
├── docs/
│   ├── architecture.md
│   ├── system-design.md
│   ├── flowchart.md
│   └── adr/
│       └── 0001-separate-runtime-and-gateway.md
└── tests/
    ├── unit/
    └── integration/
```

Adjust names only when there is a clear benefit. Preserve the architectural separation.

## Domain contracts

Create provider-neutral request and response contracts.

At minimum, support:

```python
ModelRequest
ModelResponse
Message
ContentBlock
ToolDefinition
ToolCall
TokenUsage
ModelCapabilities
ModelDescriptor
ModelProfile
AgentDefinition
AgentRunRequest
AgentRunResult
```

A normalized tool call must contain:

```python
id: str
name: str
arguments: dict[str, object]
```

The normalized model response must contain:

```python
content: list[ContentBlock]
tool_calls: list[ToolCall]
usage: TokenUsage
stop_reason: str
provider_metadata: dict[str, object]
```

## Model profile behavior

An agent references a logical profile such as:

```yaml
model_profile: coding_high
```

A profile describes requirements and ordered routes:

```yaml
profiles:
  coding_high:
    requirements:
      tool_calling: true
      structured_output: true
      minimum_context_window: 32000
    routes:
      - provider: openai
        model: configured-openai-model
      - provider: fake
        model: fake-coding-model
```

The router must:

1. Load the requested profile.
2. Inspect candidate model capabilities.
3. Reject candidates that do not meet requirements.
4. Apply request constraints.
5. Return the first eligible candidate.
6. Explain the routing decision in structured metadata.
7. Raise a typed error when no candidate is eligible.

Do not implement opaque machine-learning-based routing.

## Agent overlays

Implement a small, explicit overlay system.

A base agent may be extended by a team or repository overlay:

```yaml
extends: agents/pr-reviewer/agent.yaml

instructions:
  append:
    - "Pay special attention to payment idempotency."

settings:
  severity_threshold: medium
```

Overlay rules:

- Lists under `instructions.append` are appended.
- Scalar settings override unlocked base settings.
- Locked fields cannot be changed.
- Tool additions are rejected unless the base definition explicitly permits them.
- The resolved agent configuration can be printed by the CLI.
- Preserve the source files and include resolution metadata.

Keep the merge rules deliberately limited and documented.

## API endpoints

Implement:

```text
GET  /health
GET  /v1/profiles
GET  /v1/models
POST /v1/generate
POST /v1/agents/run
```

The HTTP API is for demonstration. The same services must be callable directly from Python without HTTP.

## CLI commands

Implement commands similar to:

```bash
amg profiles
amg models
amg resolve-agent agents/pr-reviewer/agent.yaml
amg run examples/pr-reviewer-request.json
amg serve
```

The default example should use the fake provider.

## Testing expectations

Tests must cover:

- Capability matching.
- Rejection of an ineligible model.
- Stable routing order.
- Provider response normalization.
- Structured-output validation.
- Agent loading.
- Overlay merging.
- Locked field protection.
- End-to-end fake-provider execution.
- API health and one generation endpoint.

No test should require a live API key.

## Documentation expectations

Use Mermaid for diagrams. Mermaid source must remain readable in plain text.

The system design should discuss:

- Context and goals.
- Components.
- Request sequence.
- Configuration and versioning.
- Customization through overlays.
- Security boundaries.
- Reliability and fallback.
- Observability.
- Scaling path.
- Trade-offs.
- Non-goals.
- Future MCP integration.

## Completion definition

Before declaring the repository complete, run:

```bash
ruff check .
ruff format --check .
mypy app
pytest
```

Correct all failures. Then review the repository against `specs/acceptance-criteria.md`.
