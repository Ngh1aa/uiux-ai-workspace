---
name: prototype-strategy-and-concept-testing
description: Choose the lowest-fidelity prototype that can answer the current design question and test concepts before expensive implementation. Use in discovery/alpha, major redesigns or uncertain interaction concepts.
---

# Prototype Strategy & Concept Testing

## Workflow
1. State what must be learned and what decision depends on it.
2. Choose fidelity: sketch, content prototype, clickable prototype or coded prototype.
3. Include only interactions needed to test the hypothesis.
4. Mark fake data, simulated behavior and out-of-scope areas.
5. Test comprehension and task behavior.
6. Iterate until key uncertainty is reduced.
7. Promote to production architecture only after learning risk is acceptable.

## Rules
- Fidelity must match uncertainty, not stakeholder desire for polish.
- Prototype code is disposable unless explicitly engineered for production.
- Avoid backend work that does not improve the current learning objective.

## Quality gate
The prototype answers a named question before additional polish or scope is added.
