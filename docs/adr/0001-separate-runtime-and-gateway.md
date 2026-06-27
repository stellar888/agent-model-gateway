# ADR 0001: Separate Runtime and Gateway

## Status

Accepted.

## Context

The proof of concept needs to show that agents can depend on logical model
profiles rather than provider model names. It also needs to keep provider SDK
types isolated inside provider adapters and keep workflow logic out of the model
gateway.

The implemented code separates these concerns:

- Runtime: `app/runtime/loader.py`, `app/runtime/overlays.py`,
  `app/runtime/runner.py`, and `app/runtime/validation.py`
- Gateway: `app/gateway/service.py`, `app/gateway/router.py`,
  `app/gateway/registry.py`, and `app/gateway/errors.py`
- Providers: `app/providers/fake_provider.py` and
  `app/providers/openai_provider.py`

## Decision

The model gateway manages one model interaction. It resolves a model profile to
an eligible provider/model, calls the selected provider adapter, and returns a
normalized `ModelResponse` plus routing metadata.

The agent runtime manages agent behavior. It loads agent definitions, applies
overlays, assembles prompts and schemas, calls the gateway, validates structured
output, and will own future tool loops.

## Consequences

This makes routing deterministic and explainable. Provider SDKs stay behind
adapters, and runtime code does not need provider-specific conditionals. The
same runtime can call the fake provider or a real OpenAI adapter through the
gateway.

The split does add some ceremony: domain contracts must be explicit, and tests
must cover the boundary between runtime and gateway. For this repository, that
ceremony is useful because the goal is to communicate architecture clearly.

## Rejected Alternatives

Putting provider selection inside the agent runtime would make each workflow
responsible for provider-specific decisions and would encourage copied routing
logic.

Putting agent tool loops inside the gateway would blur model interaction with
workflow execution. It would also make it harder to add durable workflows, MCP
tool services, or policy checks later.
