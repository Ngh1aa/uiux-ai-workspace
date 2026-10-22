---
name: prototype-strategy-and-concept-testing
description: Choose the lowest-fidelity prototype that can answer the current design question and test concepts before expensive implementation. Use in discovery/alpha, major redesigns or uncertain interaction concepts.
---

# Prototype Strategy & Concept Testing

## Workflow

1. State what must be learned and what decision depends on it.
2. Choose fidelity using the table below.
3. Include only interactions needed to test the hypothesis.
4. Mark fake data, simulated behavior and out-of-scope areas.
5. Test comprehension and task behavior.
6. Iterate until key uncertainty is reduced.
7. Promote to production architecture only after learning risk is acceptable.

## Question → fidelity

| Question you need answered | Lowest useful fidelity | AI-assisted option |
|---|---|---|
| Is this the right problem / do they want it? | Concept description, storyboard, fake door | Written concept + 1 static screen |
| Do they understand the offer / content? | Content prototype (real copy, plain layout) | Greyscale page in Claude Design |
| Can they find it? | Tree test / clickable IA | Clickable greyscale nav |
| Can they complete the task? | Clickable wireframe of one flow incl. one failure path | Greyscale clickable flow |
| Does it feel trustworthy / on-brand? | Visual mockup of 2 to 3 key screens | Two contrasting visual directions |
| Does it work with real data, speed, devices? | Coded prototype | Browser prototype (`mobile-web-preview`) |

Rule of thumb: answer structure questions in greyscale. Adding visual polish early makes people comment on colour and hides structural problems.

## Concept test patterns

- **Comprehension**: show for 5 to 10 seconds, ask what it is and who it is for.
- **Desirability**: compare 2 to 3 concepts against the current workaround, ask which and why, watch for "I'd use it if..." conditions.
- **Task**: give a goal, observe completion on the flow.
- **Fake door** (live products): measure interest before building; disclose honestly when clicked.

## AI-generated prototypes

AI tools make high fidelity cheap, which tempts teams to skip structure. Keep the fidelity choice driven by the question above. Mark generated sample data `SAMPLE`, and never present a generated screen as validated just because it looks finished.

## Rules

- Fidelity must match uncertainty, not stakeholder desire for polish.
- Prototype code is disposable unless explicitly engineered for production.
- Avoid backend work that does not improve the current learning objective.
- One prototype, one primary question.

## Quality gate

The prototype answers a named question before additional polish or scope is added; the answer and its evidence class are recorded.
