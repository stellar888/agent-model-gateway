# Task 5 — Build the CLI and Demonstration

Implement these commands:

```bash
amg profiles
amg models
amg resolve-agent PATH [--overlay PATH]
amg run REQUEST_JSON
amg serve
```

Create `examples/pr-reviewer-request.json`.

The default configuration and example must use the fake provider so the demonstration works without an API key.

The run output should display:

- Agent name and version.
- Resolved profile.
- Selected provider and model.
- Rejected routes, when present.
- Validated structured result.
- Token usage.
- Whether an overlay was applied.

Keep output readable and deterministic. Avoid a heavy terminal UI dependency.
