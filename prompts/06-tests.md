# Task 6 — Complete the Test Suite

Review `specs/acceptance-criteria.md`.

Add or improve tests so the repository covers:

- Model and profile configuration loading.
- Capability matching.
- Routing precedence.
- Ineligible route rejection.
- No eligible model.
- Fake provider normalization.
- OpenAI adapter mapping using mocks only.
- Agent definition loading.
- Overlay merging.
- Locked configuration.
- JSON Schema validation.
- End-to-end agent execution with the fake provider.
- Health, model, profile, generation, and agent-run API endpoints.
- CLI smoke tests.

Tests must not call a real model API.

Run:

```bash
ruff check .
ruff format --check .
mypy app
pytest
```

Fix all failures rather than weakening checks without justification.
