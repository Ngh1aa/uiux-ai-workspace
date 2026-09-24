---
name: evidence-provenance-and-research-ops
description: Makes UX/research claims traceable to sources, dates, audiences, contexts, confidence and affected decisions. Use when research, analytics, stakeholder evidence or prior findings influence product/design decisions, especially across long-lived or multi-agent projects.
---

# Evidence Provenance & ResearchOps

## Principle
A finding is useful only if the team can tell **where it came from, what it applies to, how current it is and what decision it supports**.

`claim → evidence → context/date → confidence/limitations → decision → outcome`

## Workflow
### 1. Register material claims
Track claims that affect IA, journey, content, prioritization, conversion, accessibility or brand decisions.

### 2. Classify evidence
Examples:
- direct observed user behavior;
- interview/usability finding;
- analytics/search/CRM/support data;
- service/sales/admissions evidence;
- credible external research;
- stakeholder assertion;
- hypothesis/assumption.

Never relabel a lower-confidence source as direct user evidence.

### 3. Store provenance
For each material claim record:
- claim ID and wording;
- source type and source pointer;
- collection/publication date;
- audience/context/sample;
- confidence and limitations;
- contradictory or supporting evidence;
- decisions affected;
- review/expiry trigger.

### 4. Handle conflict and staleness
Do not silently delete contradictory evidence. Mark unresolved conflict and choose whether to research, segment or make a reversible decision.

### 5. Close the loop
After implementation, append validation/outcome evidence rather than overwriting the original rationale.

## Required artifact
Create/update `docs/evidence-register.md`.

Suggested row:
`ID | Claim | Evidence type | Source | Date | Audience/context | Confidence | Limitations/conflicts | Decision | Outcome/status`

## Gate
Before citing "research shows", the agent must be able to point to the registered source and context.

## Anti-patterns
- Invented personas/findings.
- Undated evidence treated as current.
- One participant generalized to all users without caveat.
- Stakeholder preference described as a user need.
- Deleting evidence that contradicts the chosen design.
- Using a confidence percentage with no defensible method.
