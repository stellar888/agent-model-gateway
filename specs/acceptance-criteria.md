# Proof-of-Concept Acceptance Criteria

## Functional

- [ ] A valid agent YAML file can be loaded.
- [ ] The agent refers to a logical model profile.
- [ ] Model profiles and concrete models are loaded from configuration.
- [ ] The router checks capabilities before selecting a model.
- [ ] An ineligible candidate is skipped with a recorded reason.
- [ ] A typed error is raised when no route is eligible.
- [ ] The fake provider returns a normalized response.
- [ ] The OpenAI provider returns the same normalized response type.
- [ ] Structured output is validated against the agent schema.
- [ ] A team overlay can append instructions and override allowed settings.
- [ ] Locked fields cannot be overridden.
- [ ] The CLI can resolve and print the final agent definition.
- [ ] The CLI can execute the sample agent with the fake provider.
- [ ] The API exposes health, profiles, models, generation, and agent-run endpoints.

## Architecture

- [ ] Provider SDK types do not escape provider adapter modules.
- [ ] The model gateway does not execute tools.
- [ ] The agent runtime does not contain provider-specific conditionals.
- [ ] Routing is deterministic and explainable.
- [ ] Domain contracts are provider-neutral.
- [ ] Configuration is separated from application code.

## Documentation

- [ ] `docs/flowchart.md` contains a Mermaid flowchart.
- [ ] `docs/architecture.md` contains a Mermaid component diagram.
- [ ] `docs/system-design.md` explains the complete design.
- [ ] An ADR explains why runtime and gateway are separate.
- [ ] The README contains setup and demo instructions.
- [ ] Future work describes MCP, durable workflows, distributed workers, and policy services.

## Quality

- [ ] Ruff passes.
- [ ] Mypy passes.
- [ ] Pytest passes.
- [ ] No live credential is required for tests.
- [ ] `.env.example` contains placeholders only.
- [ ] Errors are typed and understandable.
- [ ] Important interfaces have docstrings.
