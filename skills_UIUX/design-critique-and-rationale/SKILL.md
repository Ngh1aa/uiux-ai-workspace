---
name: design-critique-and-rationale
description: Structure critique around goals, evidence, tradeoffs and actionable design decisions instead of taste. Use before major UI changes, during review or when comparing alternatives.
---

# Design Critique & Rationale

## Goal

Make critique change the design for the better, and make decisions explainable later.
A critique that cannot be acted on, or a decision nobody can explain in three months, is waste.

## Workflow

1. Restate user/business goal and constraints.
2. Describe observed issue before proposing solution.
3. Tie critique to evidence, principle or expected outcome.
4. Explore at least one alternative for high-impact decisions.
5. Record tradeoff and why the chosen option wins now.
6. Separate blocker, improvement and preference.
7. Define how uncertain decisions will be validated.

## Critique order (structure before surface)

Review in this order and stop to fix earlier layers before polishing later ones:

1. **Goal fit**: does this screen/flow serve the top task and the user question?
2. **Flow**: can the task be completed, recovered and resumed?
3. **Hierarchy**: is the most important thing seen first; is there one clear primary action?
4. **Content**: are labels and copy in the user's language and accurate?
5. **Interaction**: feedback, states, affordance, reach.
6. **Visual craft**: type, spacing, colour, imagery, motion, consistency.
7. **Accessibility and inclusion** run across all layers, not as a final pass.

Commenting on colour while the flow has a dead end is the most common critique failure.

## Feedback format

```text
I noticed <observation, specific screen/state>
which matters because <goal / evidence / principle>
so I suggest <option> or ask <question>
Type: blocker | improvement | preference
```

Example: "On Review, 'Confirm' and 'Change slot' look the same weight, which matters because parents rushing between meetings may tap the wrong one (H5 error prevention), so I suggest making Change a text button. Type: improvement."

## Running a critique session

- Presenter states the goal, stage (wireframe / visual / build) and what feedback is wanted.
- Reviewers critique the work, not the person; ask before prescribing.
- Time-box; capture in the [design rationale template](../templates/ux/design-rationale.md).
- End with decisions, owners and what is parked.

## Rationale record

Required for consequential decisions (navigation model, primary action, data model visible to users, irreversible patterns). Use the template; include "how we will know we were wrong".

## Quality gate

- Feedback is specific, located and actionable.
- Taste is labelled preference, never presented as fact.
- Structural issues are resolved before visual polish feedback is acted on.
- Rationale can be revisited when evidence changes.
