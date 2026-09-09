---
name: product-strategy-and-prioritization
description: Frames product positioning, ranks competing opportunities/features, and cuts scope using explicit evidence, tradeoffs and appetite. Use after discovery when deciding what deserves design/build effort, what to defer, or how the product should be positioned; complements product-discovery and does not replace user research.
---

# Product Strategy & Prioritization

## Boundary

This skill owns the decision layer between **validated-enough discovery** and detailed design/implementation:

`problem/audience evidence → positioning → candidate opportunities → priority → scope boundary → design/build handoff`

`product-discovery` still owns problem/audience/JTBD/assumption discovery. `product-decision-and-stakeholder-framing` owns ambiguous stakeholder calls. `analytics-and-experimentation` owns measurement and pre-run experiment design.

## Workflow

### 1. Check decision readiness

Confirm the candidate work is tied to a real problem, audience and outcome. If the underlying problem is still a feature request or evidence is missing, hand back to discovery rather than manufacture a ranking.

### 2. Position from reality

When positioning is material, walk this chain in order:

1. **Competitive alternatives** — what would the best-fit customer do if this product/page/feature did not exist, including indirect/manual/do-nothing alternatives?
2. **Unique attributes** — concrete capabilities/evidence, not adjectives.
3. **Customer value** — what those attributes enable or improve.
4. **Best-fit customer/context** — who feels that value most strongly and why.
5. **Market/category framing** — choose only after the first four are clear.

Do not start from an aspirational category or unprovable superlative.

### 3. Define the decision outcome

For the current prioritization cycle, record:

- target user/business outcome;
- primary metric or observable success criterion;
- constraints/appetite;
- must-preserve requirements;
- candidate opportunities/features/pages.

### 4. Rank with evidence, not false precision

Use a quantitative model only when its inputs are defensible. A RICE-style matrix can be useful when reach, impact, confidence and effort are known well enough:

`priority signal = reach × impact × confidence / effort`

But the score is a **decision aid**, not truth. Record the source behind each input. Unknown inputs remain UNKNOWN; never invent reach, conversion lift or effort just to complete the formula.

Also classify each candidate by its role:

- **BLOCKER** — removes a material barrier to adoption, task completion, trust, accessibility, retention or delivery;
- **ENABLER** — deepens value/delight after the core path already works;
- **MANDATORY** — legal, safety, accessibility, security, contractual or project-truth requirement that should not be traded away by a product score;
- **OPTIONAL** — useful but deferrable without breaking the core outcome.

Near-tied scores should trigger judgment using evidence quality, reversibility, blocker status and strategic fit rather than decimal-place ranking.

### 5. Cut scope with appetite

For substantial work, establish what the problem is worth in time/resources before expanding the solution. Then reduce breadth until a coherent outcome fits.

Ask for each proposed part:

- Does the primary user outcome fail without it?
- Is it core path or edge case?
- Can a smaller surface deliver the same validated learning/value?
- Can we defer configurability/variants while preserving quality and recovery?
- Does cutting it create accessibility, security, trust, data-integrity or system-reality debt? If yes, it is not a safe scope cut.

**Cut breadth before quality.** Do not use “MVP” as permission to ship broken states, deceptive behavior or inaccessible critical journeys.

### 6. Produce the decision handoff

Output:

```text
Decision outcome:
Positioning chain:
Candidate set:
Evidence/source per candidate:
Priority method + rationale:
Priority matrix:
Scope IN:
Scope OUT / deferred:
Mandatory/non-negotiable requirements:
Assumptions/unknowns:
Revisit trigger:
Design/build handoff:
```

## Hard rules

- Do not prioritize a disguised solution request before translating it to a problem/outcome.
- Do not fabricate quantitative inputs.
- Do not treat RICE or any framework as a universal ranking oracle.
- Do not optimize reach/impact at the expense of mandatory safety/accessibility/security/project-truth requirements.
- Do not position for “everyone”.
- Do not confuse feature attributes with customer value.
- Do not create a new market category merely because it sounds distinctive.
- Scope decisions must remain reversible when evidence is weak where practical.

## Progressive reference

Read [references/product-strategy-prioritization.md](references/product-strategy-prioritization.md) when deeper positioning, prioritization or scope-cutting guidance is needed. It is a local synthesis informed by the pinned ProductSkills source recorded in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`.

## Acceptance criteria

- Decision is traceable to problem/audience/outcome evidence.
- Positioning starts from real alternatives and verifiable differences when applicable.
- Priority inputs expose source/confidence instead of hiding guesses.
- Mandatory requirements cannot lose to a product score.
- Scope has explicit IN/OUT boundaries and revisit triggers.
- Handoff is concrete enough for Design Contract/implementation planning.
