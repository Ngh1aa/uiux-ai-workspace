---
name: real-user-validation
description: Establishes truthful real-user evidence across problem, concept, solution and live stages. Use for evidence-led/high-risk work, explicit user research or usability testing, and production-learning workflows. Coordinates existing research planning/synthesis skills; it never fabricates participants, quotes, findings or validation.
---

# Real-User Validation

## Principle

`assumption → research question → representative participant → observed evidence → synthesis → decision`

Direct user evidence is a different evidence class from competitor research, stakeholder opinion, heuristic review, analytics, AI critique or design taste.

## Evidence labels

Use one of:

- **DIRECT_USER** — observed/interviewed actual or likely users for the relevant task/context;
- **LIVE_BEHAVIOR** — real product/service behavior from production analytics or service data;
- **PROXY** — support/sales/domain-expert evidence that informs but does not replace target-user research;
- **DESK_EVIDENCE** — market/reference/document research;
- **HYPOTHESIS** — unvalidated product/design belief;
- **UNKNOWN** — insufficient evidence.

Never call a hypothesis "validated" because a prototype looks polished or stakeholders like it.

## Lifecycle use

### Problem validation
Learn current behavior, goals, friction, workarounds, context and exclusion before locking the solution.

### Concept validation
Test whether users understand the idea, see meaningful value and can imagine it fitting their workflow. Keep concepts rough enough to change cheaply.

### Solution validation
Test representative tasks on prototypes or working software. Observe task success, errors/recovery, comprehension, confidence and accessibility needs.

### Live validation
Combine ongoing user research with production behavior/support evidence to understand whether needs or failure modes changed.

## Research contract

Route detailed planning/recruitment to `user-research-planning-and-recruitment` and synthesis to `research-synthesis-and-insight-management`.

For each round define:

`decision → research question → method → participant criteria → task/scenario → evidence captured → success/learning criteria → synthesis → design/product response`

Include disabled people, assistive-technology users, low-digital-confidence users or other excluded contexts when relevant to the target population. Do not simulate those experiences as a substitute for direct engagement.

## Sponsor/design-partner pattern

A representative recurring user collaborator can help the team stay close to reality throughout delivery. Treat this as continuous collaboration, not a replacement for formal research or broader validation.

## Availability rule

If participant access does not exist:

- produce the research plan;
- label the decision **PLANNED VALIDATION** or **BLOCKED USER EVIDENCE**;
- proceed only when project risk allows;
- do not invent sessions/results.

## Output

For substantial work create `docs/user-validation.md`:

- decisions/hypotheses being tested;
- evidence labels;
- participant/recruitment criteria;
- method/tasks;
- findings with traceability;
- contradictory evidence;
- decision impact;
- remaining UNKNOWNs.

## Quality gate

- Material user claims expose their evidence class.
- Direct-user validation is representative enough for the decision being made.
- Accessibility/inclusion is considered in recruitment, not only in QA.
- Findings change or confirm an explicit decision.
- No fictional participant counts, quotes, percentages or "research results".

## Baseline sources

Adapted from:
- GOV.UK Service Manual — user research across discovery, alpha, beta and live.
- IBM Enterprise Design Thinking — Sponsor Users as recurring representative collaborators.
- Microsoft Inclusive Design — learn from diversity and engage people directly.
