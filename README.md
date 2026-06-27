# Multi-Model Agent Gateway — Codex Proof of Concept

This repository is a specification-first starter for building a proof of concept that demonstrates how an organization can:

- Define agents independently of any single LLM provider.
- Route agent requests through a model gateway.
- Select models through capability-based profiles.
- Normalize provider responses and tool calls.
- Version agent definitions.
- Apply organization, team, repository, and engineer-level configuration.
- Generate an architecture diagram and system design document.
- Run a minimal end-to-end demonstration.

The first implementation should deliberately remain small. It should explain the concept clearly rather than attempting to become a production platform.

## Target proof of concept

The completed repository should contain:

1. A provider-neutral agent definition in YAML.
2. A small Python model gateway.
3. At least two model adapters:
   - A real OpenAI adapter.
   - A deterministic fake adapter for tests and offline demonstrations.
4. A capability-based model profile registry.
5. A simple agent runtime that:
   - Loads an agent definition.
   - Resolves a model profile.
   - Calls the gateway.
   - Validates structured output.
6. A CLI demonstration.
7. Unit and integration tests.
8. A Mermaid architecture diagram.
9. A system design document.
10. A short decision record explaining why the gateway and runtime are separate.

## Recommended stack

- Python 3.12+
- FastAPI
- Pydantic v2
- httpx
- PyYAML
- Typer
- pytest
- Ruff
- mypy
- OpenAI Python SDK

Keep provider integrations behind internal interfaces. Do not import provider SDKs from agent or workflow modules.

## Repository workflow

Read `AGENTS.md` before making changes.

Then give Codex the tasks in `prompts/` in numerical order:

1. `prompts/01-scaffold.md`
2. `prompts/02-domain-model.md`
3. `prompts/03-gateway.md`
4. `prompts/04-agent-runtime.md`
5. `prompts/05-cli-demo.md`
6. `prompts/06-tests.md`
7. `prompts/07-architecture-docs.md`
8. `prompts/08-final-review.md`

Each task includes acceptance criteria. Ask Codex to complete one task per branch or commit so the changes remain reviewable.

## Local setup after implementation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
pytest
agent-poc run examples/pr-reviewer-request.json
uvicorn app.api:app --reload
```

The fake provider must allow the full demo and tests to run without API credentials.

## Design boundary

The proof of concept should preserve this separation:

```text
Agent definition
      |
      v
Agent runtime ------> Tool executor
      |
      v
Model gateway
      |
      +----> OpenAI adapter
      |
      +----> Fake adapter
```

The model gateway manages one model interaction. The agent runtime manages the agent lifecycle, context, tool loop, and output validation.

## Non-goals

Do not build these in the first proof of concept:

- A graphical administration portal.
- Kubernetes deployment.
- A distributed queue.
- Persistent conversation memory.
- Production-grade secret management.
- Complex semantic routing.
- Full MCP implementation.
- Automatic production writes.
- More than one real provider integration.

Document these as future extensions instead.
