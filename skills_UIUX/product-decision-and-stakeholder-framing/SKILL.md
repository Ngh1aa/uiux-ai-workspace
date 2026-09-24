---
name: product-decision-and-stakeholder-framing
description: Clarifies ambiguous or conflicting product/stakeholder asks by translating solution requests into underlying problems, stress-testing evidence and impact, then helping the user choose what matters. Use for hard product calls, stakeholder-driven feature/UI requests, or competing priorities; the user remains the decision-maker.
---

# Product Decision & Stakeholder Framing

## Boundary

This skill owns **hard decision clarification**, especially when the incoming ask is already phrased as a solution:

`stakeholder asks → underlying problems → evidence/blind spots/impact → priority lenses → decision snapshot`

It does not own user research execution, generic stakeholder communication, detailed backlog scoring, or implementation planning. Handoff to `product-discovery`, `product-strategy-and-prioritization`, Design Contract or implementation owners as appropriate.

## Default behavior

Use project evidence before asking the user to repeat information already available. In interactive ambiguity, ask one focused question at a time. In an autonomous project phase with sufficient evidence, perform the same reasoning against the documented sources and mark gaps `UNKNOWN` instead of fabricating answers.

## Stage 1 — Translate asks into problems

For every material ask, record:

```text
Stakeholder/source:
Requested solution/change:
Underlying problem/outcome:
Evidence currently available:
```

Push until the underlying problem can be stated **without the requested feature/UI solution**.

Examples:
- “Make the hero bigger” may map to weak brand prominence, unclear first-screen value or a stakeholder preference. Those are different problems.
- “Add a chatbot” may map to support discoverability, lead qualification or a desire to appear innovative. Do not treat them as equivalent.

Before advancing, account for the main distinct voices/asks and give the user/project evidence a chance to surface missing context.

## Stage 2 — Stress-test every candidate problem

Run three lenses in order for each surviving problem:

### Evidence
How do we know this is the actual problem?

Distinguish direct user/behavioral evidence, analytics/support/sales evidence, stakeholder assertion and hypothesis. Hearsay stays hearsay.

### Blind spots
What else could explain the observed signal/request?

Require at least one plausible alternate framing when the decision is material. Contradictory evidence is logged, not deleted.

### Impact
If this problem were solved well, what changes for the user/business/system?

Tie the impact to an observable journey, metric, risk, trust outcome or strategic obligation. If little changes, explicitly consider removing it from the decision set.

## Stage 3 — Pick what matters

For the problems that survive, consider:

- **Leverage** — solving which problem makes other problems easier or removes an upstream constraint?
- **Cost of being wrong / reversibility** — which mistake is hardest to recover from?
- **Strategic ground** — which problem best connects to the current business/user outcome, trust obligation or product direction?

These are lenses, not weights imposed by the skill. The final call belongs to the user/authorized decision owner.

When the decision needs quantitative prioritization or scope shaping, hand the survivors to `product-strategy-and-prioritization` rather than extending this skill into a backlog framework.

## Decision snapshot

```text
Decision:
Original asks/voices:
Underlying candidate problems:
Evidence + confidence per problem:
Alternatives/blind spots considered:
Problems removed + why:
Problems surviving:
Chosen problem / current priority:
Reasoning (leverage / reversibility / strategic ground):
What remains UNKNOWN:
Next evidence or handoff:
```

## Hard rules

- Do not make a stakeholder preference look like user research.
- Do not preserve a feature request inside the problem statement.
- Do not make the final business call for the user when authority belongs to them.
- Do not turn the exercise into a product-management lecture.
- Do not ask for information that project truth already contains.
- Do not hide contradictory evidence because it weakens the preferred answer.
- High-consequence unknowns remain UNKNOWN and may block the owning phase.

## Progressive reference

Read [references/product-decision-framing.md](references/product-decision-framing.md) for deeper prompts and exit checks adapted from Mind the Product's pinned `make-the-call` practice recorded in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`.

## Acceptance criteria

- Solution requests are translated to solution-independent problems.
- Each material problem is tested against evidence, alternatives and impact.
- The final rationale exposes leverage/reversibility/strategic considerations.
- Decision ownership stays explicit.
- UNKNOWN/conflict is preserved and handed to the correct next owner.
