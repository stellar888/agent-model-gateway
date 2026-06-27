# Target Agent Definition

Codex should use this as the conceptual target and may refine field names while preserving the meaning.

```yaml
api_version: agents.example.io/v1
kind: Agent

metadata:
  name: pr-reviewer
  version: 0.1.0
  owner: developer-platform
  description: Reviews a pull request summary and produces structured findings.

spec:
  model_profile: coding_high

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
    max_cost_usd: 1.00
    writes_allowed: false

  customization:
    append_instructions: allowed
    settings:
      severity_threshold: allowed
    model_profile: locked
    tools_add: locked

  settings:
    severity_threshold: low
```

Sample output schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PullRequestReview",
  "type": "object",
  "additionalProperties": false,
  "required": ["summary", "risk_level", "findings"],
  "properties": {
    "summary": {"type": "string"},
    "risk_level": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["title", "severity", "explanation"],
        "properties": {
          "title": {"type": "string"},
          "severity": {
            "type": "string",
            "enum": ["info", "low", "medium", "high"]
          },
          "explanation": {"type": "string"}
        }
      }
    }
  }
}
```
