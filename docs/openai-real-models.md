# Using Real OpenAI Models

This proof of concept defaults to the fake provider so tests and demos work
offline. To query a real OpenAI model, enable the OpenAI provider and select an
OpenAI-backed profile.

The OpenAI adapter uses the Responses API. OpenAI documents the Responses API as
the interface for creating model responses with text inputs, JSON outputs,
function calls, and built-in tools. The request supports an `instructions`
system/developer message, `input`, `model`, `text`, and `tools` fields.

## Configure Credentials

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Then set:

```bash
OPENAI_API_KEY=sk-...
APP_ENV=development
```

That is enough for this repository to register the OpenAI provider. If you want
to be explicit, set `AMG_ENABLE_OPENAI=true`; if you want to force the fake-only
path even when a key is present, set `AMG_ENABLE_OPENAI=false`.

The configured model lives in `config/models.yaml` and the OpenAI-only route
lives in `config/model-profiles.yaml`.

## Current Sample Model

The sample configuration includes a small OpenAI profile ladder:

| Profile | Model | Intended use |
| --- | --- | --- |
| `coding_power_openai` | `gpt-5.5` | highest-power coding and review |
| `coding_balanced_openai` | `gpt-5.4` | balanced quality and latency |
| `coding_fast_openai` | `gpt-5.4-mini` | lighter triage and lower-latency work |

The legacy `coding_high_openai` profile is kept as an alias to the high-power
`gpt-5.5` route for existing examples.

OpenAI's model docs list GPT-5.5 and GPT-5.4 variants, and the Structured
Outputs guide recommends starting new projects with `gpt-5.5`. Treat the
`cost_per_1k_tokens_usd` field in `config/models.yaml` as optional routing
metadata. This repository does not encode official OpenAI pricing.

To use another model, update both files:

```yaml
# config/model-profiles.yaml
routes:
  - provider: openai
    model: your-model-id
```

```yaml
# config/models.yaml
- provider: openai
  model: your-model-id
  capabilities:
    tool_calling: true
    structured_output: true
    streaming: true
    max_context_window: 128000
```

Keep the capability metadata honest. The router trusts this file when deciding
whether a model satisfies an agent profile.

## Run the OpenAI-Backed Sample Agent

The fake-provider agent uses `coding_high`; the high-powered real-model sample
uses `coding_power_openai`.

```bash
amg run examples/openai-pr-reviewer-request.json
```

Run the lighter triage agent:

```bash
amg run examples/openai-pr-triage-lite-request.json
```

That request loads:

- `agents/openai-pr-reviewer/agent.yaml`
- `agents/openai-pr-triage-lite/agent.yaml`
- `config/model-profiles.yaml`
- `config/models.yaml`
- `app/providers/openai_provider.py`

The agent runtime still talks only to the provider-neutral gateway. It does not
import or instantiate the OpenAI SDK directly.

## Call the Gateway Directly from Python

```python
import asyncio

from app.config import build_gateway
from app.domain import Message, MessageRole, ModelRequest


async def main() -> None:
    gateway = build_gateway(include_openai=True)
    result = await gateway.generate(
        ModelRequest(
            model_profile="coding_high_openai",
            messages=[
                Message.from_text(
                    MessageRole.USER,
                    "Return one concise sentence about gateway routing.",
                )
            ],
        )
    )
    print(result.routing.model_dump(mode="json"))
    print(result.response.model_dump(mode="json"))


asyncio.run(main())
```

## Run the Gateway as an HTTP API

Start the API:

```bash
amg serve
```

Generate through OpenAI:

```bash
curl -sS http://127.0.0.1:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_profile": "coding_high_openai",
    "messages": [
      {
        "role": "user",
        "content": [{"type": "text", "text": "Summarize this gateway in one sentence."}]
      }
    ]
  }'
```

Run the OpenAI-backed agent through the API:

```bash
curl -sS http://127.0.0.1:8000/v1/agents/run \
  -H "Content-Type: application/json" \
  -d @examples/openai-pr-reviewer-request.json
```

## Build a New Sample Agent

Create a new folder under `agents/`:

```text
agents/my-agent/
├── agent.yaml
├── prompt.md
└── output.schema.json
```

Minimal `agent.yaml`:

```yaml
api_version: agents.example.io/v1
kind: Agent

metadata:
  name: my-agent
  version: 0.1.0
  owner: my-team
  description: Demonstrates a custom OpenAI-backed agent.

spec:
  model_profile: coding_power_openai
  instructions:
    system_file: prompt.md
  capabilities:
    required:
      tool_calling: false
      structured_output: true
      minimum_context_window: 32000
  tools: []
  output:
    schema_file: output.schema.json
  policies:
    max_iterations: 1
    max_cost_usd: 1.0
    writes_allowed: false
  customization:
    append_instructions: allowed
    settings: {}
    model_profile: locked
    tools_add: locked
  settings: {}
```

Then create a request JSON:

```json
{
  "agent_path": "agents/my-agent/agent.yaml",
  "overlay_path": null,
  "input": {
    "task": "Analyze this input."
  }
}
```

Run it:

```bash
amg run examples/my-agent-request.json
```

Your agent does not call OpenAI directly. Your app or CLI calls the runtime,
and the runtime calls the gateway with the agent's logical model profile.
