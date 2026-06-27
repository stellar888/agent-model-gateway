# Task 4 — Implement the Agent Runtime

Implement:

- YAML agent loader.
- Prompt and JSON Schema file loading.
- Limited overlay resolution.
- Locked-field enforcement.
- Agent runner.
- Structured-output validation.
- Clear runtime errors.

The runtime must:

1. Load the base agent.
2. Optionally apply one overlay.
3. Construct a provider-neutral `ModelRequest`.
4. Request the agent's logical model profile.
5. Call the model gateway service.
6. Extract the model's structured JSON response.
7. Validate it against the configured JSON Schema.
8. Return an `AgentRunResult` with routing and resolution metadata.

Do not add a multi-step tool loop yet. Document where it would belong.

Create:

- `agents/pr-reviewer/agent.yaml`
- `agents/pr-reviewer/prompt.md`
- `agents/pr-reviewer/output.schema.json`
- `agents/overlays/payments-team.yaml`

Add tests for loading, overlays, locked fields, validation success, and validation failure.
