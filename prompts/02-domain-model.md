# Task 2 — Implement Provider-Neutral Domain Models

Read `AGENTS.md` and the target contracts.

Implement the provider-neutral Pydantic models and protocols for:

- Messages and content blocks.
- Tool definitions and tool calls.
- Token usage.
- Model requests and responses.
- Model capabilities and descriptors.
- Model profile requirements and routes.
- Agent definitions and run requests/results.

Requirements:

1. No provider SDK type may appear in these modules.
2. Validate capability and context-window values.
3. Use enums where they improve safety but avoid excessive abstraction.
4. Add serialization and validation tests.
5. Include concise docstrings.
6. Keep provider metadata available as a generic dictionary.

Do not implement routing or providers in this task.
