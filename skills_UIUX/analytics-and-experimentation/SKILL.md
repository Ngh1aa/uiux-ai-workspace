---
name: analytics-and-experimentation
description: Defines outcome metrics, counter-metrics, event/funnel instrumentation and pre-run experiment plans for UI/UX/product decisions. Use when deciding what to measure, designing an A/B test before launch, or documenting analytics/consent/tracking; use experimentation-interpretation after results exist.
---

# Analytics & Experimentation

## Boundary

This skill owns **measurement design before/while implementation**:

`user/business outcome → metric tree → counter-metrics → instrumentation → hypothesis/experiment plan → validation`

Use `experimentation-interpretation` for completed-result analysis. Use `security-and-privacy` for jurisdiction-specific tracking/privacy controls when material.

## 1. Start from the outcome

Do not start from events. Define:

```text
User need / service purpose:
Desired outcome:
Primary decision metric:
Baseline or N/A:
Target/decision threshold or UNKNOWN:
Data source:
Review cadence:
```

Prefer outcomes that reflect delivered value over vanity totals. If a metric changing would not change a decision, question why it is tracked.

## 2. Build a small metric tree

Connect the core value outcome to actionable inputs such as acquisition, activation, task completion, engagement and retention only when relevant.

For every optimized metric, define at least one **counter/guardrail metric** that catches harm. Examples:
- signup conversion ↔ activation/lead quality;
- task speed ↔ error/recovery rate;
- CTA click rate ↔ completed conversion/trust signal;
- revenue per user ↔ churn/refund/support burden.

Exact formulas beat labels. Define numerator, denominator, population, window and exclusions.

## 3. Instrument only decision-relevant events

Use stable names such as `object_action` and document:

`event | trigger | properties | population | question answered | privacy classification | verification`

Typical journey events:
- page/route view where meaningful;
- key navigation/CTA actions;
- form start/error/submit/success;
- critical task completion;
- error/retry/recovery;
- search/filter result interactions where the product decision needs them.

Do not collect sensitive/PII fields merely because the analytics tool allows them. Verify consent/legal requirements instead of embedding a universal cookie rule.

## 4. Define funnels from actual journeys

A funnel is a hypothesis about progression, not proof of causality. Record:

`step → event/state → eligible population → expected question → known drop-off evidence`

Do not invent target rates. Baselines/targets require project or benchmark evidence with source/context.

## 5. Pre-run experiment design

Before building an experiment, write:

**Hypothesis:** `If [specific change] for [audience], then [primary metric] will [direction / decision-relevant magnitude], because [evidence-based reason].`

Then define:
- one primary metric;
- guardrail metrics;
- eligibility/randomization unit;
- baseline and minimum detectable effect when available;
- sample-size/power calculation appropriate to the metric/method;
- duration covering relevant business/behavior cycles rather than a universal day count;
- pre-registered segments when material;
- analysis method and planned decision rule;
- what happens for win/loss/inconclusive.

Avoid changing several causal ideas at once unless the experiment is intentionally testing a package.

## 6. Verification

Before calling tracking live:
- inspect network/debug/provider events;
- confirm naming/properties/population;
- test success and failure paths;
- check duplicate/late events when material;
- verify consent/privacy behavior for the actual jurisdiction/project;
- reconcile dashboard metric formula with the written metric contract.

Rendered UI or a tracking plan is not proof events are live.

## Output

Use or update `docs/tracking-plan.md` / project equivalent with:

```text
Outcome + metric tree
Metric formulas + counter-metrics
Event taxonomy
Funnels/journeys
Consent/privacy notes
Experiment plans
Implementation/testing status
Known gaps/UNKNOWNs
```

## Hard rules

- No vanity metric without a decision purpose.
- No target/baseline invented to fill a table.
- No experiment without a written hypothesis/analysis plan when causal evidence is the goal.
- No peeking/early-stop recommendation unless the statistical method supports it.
- No claim of live tracking without runtime evidence.
- No PII/sensitive tracking without necessity and appropriate authority/legal basis.

## External knowledge handoff

Pre-run experiment principles are informed by the pinned ProductSkills source in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`. Completed-result interpretation belongs to `experimentation-interpretation`, informed by the pinned Rampstack source.

## Acceptance criteria

- Primary outcome/metric is decision-relevant and precisely defined.
- Optimized metrics have counter/guardrail metrics.
- Events answer explicit questions and have verification.
- Experiment plans specify audience/change/metric/evidence/method/decision rule.
- Unknown data remains UNKNOWN.
