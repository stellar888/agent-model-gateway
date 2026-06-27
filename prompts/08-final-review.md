# Task 8 — Final Repository Review

Perform a final engineering review of the complete repository.

1. Read all requirements and acceptance criteria.
2. Inspect the implementation for provider leakage.
3. Confirm the runtime and gateway boundaries.
4. Confirm the fake-provider demo works without credentials.
5. Confirm the OpenAI adapter is optional and isolated.
6. Check configuration examples for consistency.
7. Check diagrams against the implementation.
8. Remove dead code and misleading placeholders.
9. Improve error messages where necessary.
10. Run all quality commands.

Create `docs/demo-script.md` containing a five-minute demonstration:

- Explain the agent file.
- Show the model profile.
- Run the base agent.
- Run it with the payments overlay.
- Show capability-aware routing.
- Show an ineligible-model error.
- Point to the production scaling path.

Finish with a concise summary of implemented features, deferred production features, test results, and any known limitations.
