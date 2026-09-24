---
name: outcome-metrics-and-instrumentation
description: Connects user outcomes and product decisions to measurable behavioral/attitudinal signals, baselines, instrumentation and experiment contracts. Use for production-learning work, explicit KPI/analytics requests, critical journeys and experiments. Do not invent baselines, targets, uplift or analytics that do not exist.
---

# Outcome Metrics & Instrumentation

## Principle

`purpose → user outcome → owner/business outcome → critical experience → metric → data source → instrumentation → baseline → decision rule → learn`

A dashboard is not a measurement strategy. A metric without a decision it informs is usually noise.

## Metric layers

Keep separate:

1. **User outcome** — did the user achieve the meaningful goal?
2. **UX quality** — completion, errors, efficiency, discoverability, learnability, satisfaction/confidence.
3. **Owner/business outcome** — legitimate product/business result connected to the journey.
4. **Technical guardrail** — reliability, performance, accessibility, security or data-quality constraints.

Do not let revenue/conversion alone stand in for user outcome.

## Stage-aware measurement

### Concept
Primarily attitudinal/evidence-fit: value-fit, workflow-fit, understandability, desirability when relevant.

### Design/prototype
Behavioral + attitudinal: task completion, first-click/route correctness, errors/recovery, time/effort where meaningful, perceived ease/confidence.

### Live
Behavioral + attitudinal over time: adoption, completion/abandonment, errors, time-to-value, satisfaction, discoverability, learnability and domain-specific outcome signals.

Treat any published threshold as a reference point, not a universal pass mark. Calibrate against project context and baseline.

## Instrumentation contract

Before release, define for every critical metric:

| Metric | Decision | Event/source | Definition | Segment | Owner | Verification |
|---|---|---|---|---|---|---|

Event definitions should include when relevant:

- event name;
- trigger condition;
- required properties;
- success/failure distinction;
- dedupe/idempotency concern;
- user/session/entity scope;
- privacy/consent/data-retention constraints.

Do not claim instrumentation is working until emitted/received evidence exists.

## Baseline and target

- Prefer a real baseline from current/legacy experience.
- If none exists, mark **UNKNOWN** and establish one.
- Targets require rationale; never fabricate uplift.
- Compare trends over time, not isolated screenshots of data.

## Experiments

For A/B or controlled experiments define:

`problem → hypothesis → primary metric → guardrails → population → exposure → duration/stopping logic → analysis owner → rollout decision`

Do not experiment on an obviously broken baseline merely to produce a number. Use normal product repair first when the improvement is already clear and user risk is high.

## Output

Create `docs/outcome-measurement.md` or equivalent with:

- outcome/metric tree;
- baseline/target state;
- instrumentation map;
- dashboard/report needs;
- experiment candidates;
- limitations/UNKNOWNs.

## Quality gate

- Every primary metric maps to a user/product decision.
- Behavioral and attitudinal evidence are not confused.
- Instrumentation is planned during implementation, not bolted on after launch.
- Privacy/consent and segmentation are explicit where relevant.
- No fabricated analytics, baselines, statistical significance or ROI.

## Baseline sources

Adapted from:
- GitLab UX Quality Metrics Framework — Concepts, Designs, Live; behavioral + attitudinal measurement.
- GitLab Critical Experiences — monitor make-or-break journeys in production.
- GOV.UK Service Manual — define success, measure from the start, combine performance data with user research.
