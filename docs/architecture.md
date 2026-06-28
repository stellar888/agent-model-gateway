# Architecture

```mermaid
flowchart LR
    subgraph Clients
        CLI[amg CLI]
        API[FastAPI HTTP API]
    end

    subgraph Runtime
        Runner[AgentRunner]
        Loader[YAML agent loader]
        Overlay[Overlay resolver]
        Validator[Structured output validator]
        Files[(agents/ and overlays/)]
    end

    subgraph Gateway
        Service[ModelGateway]
        Router[CapabilityRouter]
        Profiles[(config/model-profiles.yaml)]
        Models[(config/models.yaml)]
        Providers[ProviderRegistry]
    end

    subgraph Adapters
        Fake[FakeProvider]
        OpenAIAdapter[OpenAIProvider]
    end

    subgraph External
        OpenAI[OpenAI API]
    end

    subgraph Future
        Tools[Tool or MCP gateway]
        Policy[Policy service]
        Observability[Tracing, audit, cost telemetry]
    end

    CLI --> Runner
    API --> Runner
    API --> Service
    Runner --> Loader
    Runner --> Overlay
    Loader --> Files
    Overlay --> Files
    Runner --> Service
    Service --> Router
    Router --> Profiles
    Router --> Models
    Service --> Providers
    Providers --> Fake
    Providers --> OpenAIAdapter
    OpenAIAdapter --> OpenAI
    Runner --> Validator
    Runner -. future tool loop .-> Tools
    Router -. future policy checks .-> Policy
    Service -. future events .-> Observability
    Runner -. future events .-> Observability
```

Implemented code paths:

- CLI: `app/cli.py`
- API: `app/api.py`
- Runtime: `app/runtime/`
- Domain contracts: `app/domain/`
- Gateway and router: `app/gateway/`
- Provider adapters: `app/providers/`
- Configuration: `config/`
