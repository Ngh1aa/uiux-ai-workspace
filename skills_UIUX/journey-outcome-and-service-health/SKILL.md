---
name: journey-outcome-and-service-health
description: Defines measurable success for user journeys and services across online/offline channels, connects leading signals to real outcomes, and creates a service-health measurement loop. Use before major release, after journey redesign, or when the team needs to prove UX improvement.
---

# Journey Outcome & Service Health

## Principle
A click or form submission is not automatically the service outcome.

`user need → service purpose → journey outcome → metric → data source → decision`

## Workflow
### 1. Define the journey boundary
State where the meaningful user journey starts and where success actually ends. Include offline/human steps when relevant.

### 2. Define outcome hierarchy
Separate:
- **user outcome** — what progress/success means to the user;
- **service/business outcome** — what healthy delivery means to the organization;
- **experience signals** — task success, errors, time, satisfaction, support demand;
- **funnel signals** — reach/start/progress/completion/handoff.

### 3. Specify metric contracts
For every important metric document:
- exact definition;
- numerator/denominator where applicable;
- data source;
- channel/segment;
- baseline and target/range if justified;
- review cadence;
- known blind spots.

### 4. Combine quantitative + qualitative evidence
Performance data identifies **where** a problem may exist; research helps explain **why**.

### 5. Design decision thresholds
State what change in a metric or user-research signal should trigger investigation, rollback or follow-up research.

## Required artifact
Create/update `docs/service-health.md` with a journey measurement map and metric dictionary.

## Gate
Do not claim "improved UX" from visual preference or CTA clicks alone. State which user/service outcome improved and the evidence window.

## Anti-patterns
- Vanity metrics as primary success criteria.
- Measuring only the website when service success happens later offline.
- Targets with no baseline or rationale.
- Metrics with ambiguous denominators.
- Treating correlation as causal proof.
