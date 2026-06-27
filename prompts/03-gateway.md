# Task 3 — Implement the Model Gateway

Implement:

- Provider protocol.
- Provider registry.
- Model registry.
- Profile registry.
- Deterministic capability-aware router.
- Gateway service.
- Typed gateway and routing errors.
- Fake provider.
- OpenAI provider adapter.

Routing behavior:

1. Resolve the requested profile.
2. Evaluate routes in declared order.
3. Verify that a concrete model exists.
4. Verify that its provider is registered.
5. Verify model capabilities against profile and request requirements.
6. Apply data-classification and cost constraints if supplied.
7. Select the first eligible route.
8. Return structured routing metadata including rejected candidates.
9. Raise `NoEligibleModelError` if none qualify.

Provider rules:

- The fake provider must be deterministic.
- The OpenAI SDK must only be imported in the OpenAI adapter.
- Translate provider responses into the internal `ModelResponse`.
- Do not execute tool calls.
- Do not implement an unrestricted fallback after an execution error.
- Retry only clearly retryable provider failures, with a low fixed limit.

Add tests for capability matching, routing order, rejected candidates, fake normalization, and no-eligible-model behavior.
