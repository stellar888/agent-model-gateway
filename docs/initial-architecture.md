# Initial Architecture Direction

This file is an input to the implementation. Codex should replace it with diagrams grounded in the completed proof of concept.

## Logical components

```mermaid
flowchart LR
    Client[CLI or HTTP Client] --> Runtime[Agent Runtime]
    Runtime --> AgentFiles[Agent Definition and Overlay]
    Runtime --> Gateway[Model Gateway]
    Gateway --> Router[Capability Router]
    Router --> Profiles[Model Profiles]
    Router --> Models[Model Registry]
    Gateway --> OpenAIAdapter[OpenAI Adapter]
    Gateway --> FakeAdapter[Fake Provider]
    OpenAIAdapter --> OpenAI[OpenAI API]
    Runtime -. future .-> Tools[Tool or MCP Gateway]
```

## Request lifecycle

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Agent Runtime
    participant G as Model Gateway
    participant RT as Router
    participant P as Provider

    C->>R: Run agent with task
    R->>R: Load base definition and overlay
    R->>R: Assemble prompt and output schema
    R->>G: ModelRequest + logical profile
    G->>RT: Resolve eligible model
    RT-->>G: Provider, model, and routing reasons
    G->>P: Provider-specific request
    P-->>G: Provider-specific response
    G-->>R: Normalized ModelResponse
    R->>R: Validate structured result
    R-->>C: AgentRunResult + routing metadata
```

## Production evolution

The proof of concept should leave clear seams for:

- A durable workflow engine.
- Stateless workers and queues.
- MCP-based tool services.
- Organization policy evaluation.
- User and workload identity propagation.
- Distributed quotas and rate limiting.
- Tracing, audit logs, and cost accounting.
- An immutable agent artifact registry.
- Additional model providers.
