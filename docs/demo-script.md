# Five-Minute Demo Script

## 1. Show the Agent File

Open `agents/pr-reviewer/agent.yaml`.

Point out:

- `spec.model_profile: coding_high`
- The agent does not name a provider model.
- The output schema is referenced by file.
- `customization` allows appended instructions and one setting override, while
  locking `model_profile` and tool additions.

## 2. Show the Model Profile

Open `config/model-profiles.yaml`.

Explain that `coding_high` declares required capabilities and ordered routes.
The fake provider is first so local demos and tests do not need credentials. The
OpenAI route is configured as a real-provider option but is not registered in
the default offline path.

## 3. Run the Base Agent

```bash
amg run examples/pr-reviewer-request.json
```

Expected talking points:

- The selected route is `fake/fake-coding-model`.
- The result is structured JSON.
- Token usage and routing metadata are displayed.
- No API key is required.

## 4. Run with the Payments Overlay

```bash
amg resolve-agent agents/pr-reviewer/agent.yaml --overlay agents/overlays/payments-team.yaml
```

Point out:

- Payment-specific instructions were appended.
- `severity_threshold` changed from `low` to `medium`.
- The base agent file was not copied.
- Locked fields remain protected.

## 5. Show Capability-Aware Routing

```bash
amg profiles
amg models
```

Explain:

- Profiles express requirements.
- Concrete models express capabilities.
- The router evaluates routes in order and records rejected candidates.

## 6. Show an Ineligible-Model Error

Use the API generation endpoint with the intentionally impossible
`coding_tiny` profile:

```bash
python - <<'PY'
import asyncio

from app.domain import Message, MessageRole, ModelRequest
from app.config import build_gateway
from app.gateway.errors import NoEligibleModelError

async def main():
    request = ModelRequest(
        model_profile="coding_tiny",
        messages=[Message.from_text(MessageRole.USER, "hello")],
    )
    try:
        await build_gateway().generate(request)
    except NoEligibleModelError as exc:
        print(exc)
        print(exc.rejected_candidates)

asyncio.run(main())
PY
```

Expected talking points:

- The router raises a typed error.
- The rejection includes structured reasons.
- There is no silent fallback to a model that lacks required capabilities.
- If you see this error for `coding_fast_openai`, OpenAI is not registered for
  the current process. Set `OPENAI_API_KEY` in `.env` or call
  `build_gateway(include_openai=True)` in direct Python scripts.

## 7. Point to the Production Scaling Path

Open `docs/system-design.md`.

Highlight:

- Durable workflow engine for multi-step agents.
- MCP or tool gateway owned by the runtime layer.
- Distributed workers and queues.
- Policy, observability, audit, quotas, and cost services.
- Immutable agent and model configuration registries.

## Optional: Show Real OpenAI Profile Tiers

Open `config/model-profiles.yaml`.

Show:

- `coding_power_openai` routes to `gpt-5.5`.
- `coding_balanced_openai` routes to `gpt-5.4`.
- `coding_fast_openai` routes to `gpt-5.4-mini`.

Then compare:

```bash
amg resolve-agent agents/openai-pr-reviewer/agent.yaml
amg resolve-agent agents/openai-pr-triage-lite/agent.yaml
```
