---
name: post-launch-learning-loop
description: Extends production delivery beyond merge/deploy into monitored learning from critical journeys, analytics, support evidence, ongoing user research, experiments, staged rollout and rollback signals. Use for production-learning, live/post-launch work or explicit experimentation/feature-flag requests. Skip ordinary prototypes.
---

# Post-Launch Learning Loop

## Principle

`release → observe → combine signals → diagnose → prioritize → experiment/repair → rollout → measure again`

Production is a learning phase, not the end of design.

## Critical experiences

Name the small set of journeys where failure materially harms user or owner outcomes. For each define:

- success/failure;
- behavioral metric;
- attitudinal/user-research signal;
- technical guardrail;
- support signal;
- owner.

Monitor the experience, not only individual page views.

## Signal mix

Use multiple evidence sources when available:

- product/web analytics;
- service/system logs;
- support tickets/contact reasons;
- user satisfaction or targeted surveys;
- interviews/usability testing;
- accessibility feedback;
- performance/reliability data;
- experiment results.

Analytics tell what happened; qualitative research helps explain why.

## Learning cadence

At each review:

1. inspect trend vs baseline/expected range;
2. review new user/support evidence;
3. identify meaningful regressions/opportunities;
4. locate earliest owner: problem, UX, content, system, implementation, rollout;
5. choose repair, research, experiment or no-change;
6. record the decision and next observation window.

## Experiments

Use experiments when uncertainty is real and the decision can be measured responsibly. Define hypothesis, primary metric, guardrails and decision rule before exposure.

Do not use A/B tests to justify knowingly poor accessibility, deceptive patterns or a baseline that obviously fails the task.

## Staged release / feature flags

For changes with meaningful availability, performance, security or behavior risk, consider staged rollout/feature flags when the target stack supports them.

Define:

- exposure/rollout plan;
- health metrics;
- stop/rollback signals;
- feedback window;
- owner;
- cleanup/removal plan.

A merged feature is not automatically a safely rolled-out feature.

## Feedback to upstream stages

Live evidence must route back to the earliest responsible owner:

- invalid user/problem assumption → research;
- concept/value issue → product/design;
- usability/content issue → UX/content;
- system/reliability issue → architecture/implementation;
- rollout-specific issue → release strategy.

## Output

Create `docs/live-learning.md` or equivalent:

- critical experiences;
- signal sources;
- baseline/health view;
- research/support findings;
- experiments/rollouts;
- decisions and owners;
- next review.

## Quality gate

- Production has defined learning signals, not only technical uptime.
- Critical user journeys have owners and measurable health.
- Ongoing user evidence is possible/planned.
- Experiment/rollout decisions declare guardrails and rollback conditions.
- Live evidence feeds future prioritization and regression coverage.

## Baseline sources

Adapted from:
- GOV.UK Service Manual — continuous user research and analytics/support evidence in live.
- GitLab UX Quality Metrics Framework — live-stage quality monitoring.
- GitLab experimentation guidance — hypothesis + metric-driven product experiments.
- GitLab feature-flag lifecycle — staged rollout and cleanup for risky changes.
