---
name: conversion-and-content
description: Designs marketing-page argument, positioning-to-message translation, content hierarchy, proof, objections and CTA strategy for conversion without fabricating outcomes. Use when a page must persuade/convert, when message match or traffic context matters, or when the interface is visually strong but value/decision path is unclear; ux-writing-and-microcopy owns state-level product strings.
---

# Conversion & Content

## Boundary

This skill owns **marketing/content persuasion at page and journey level**:

`audience + entry context + positioning → page job → argument → proof → objections → CTA → testable hypotheses`

`ux-writing-and-microcopy` owns labels/errors/loading/empty/success product strings. `search-demand-and-content-briefing` owns search-demand evidence. `product-strategy-and-prioritization` owns positioning/prioritization when that strategy is unresolved.

## Inputs

- page role and primary business/user goal;
- audience/JTBD/barriers;
- entry/traffic context when known;
- product positioning/differentiation evidence;
- primary conversion and downstream journey;
- brand voice;
- real proof assets/data.

## CRO diagnostic order

When a page is underperforming or being redesigned, inspect in this order before recommending decorative changes:

1. **Value proposition clarity** — can the intended visitor understand what this is, for whom and why it matters quickly?
2. **Message match / entry context** — does the page meet the promise/intent of organic, paid, referral, email, direct or campaign traffic when known?
3. **Primary action and CTA hierarchy** — one dominant next action per decision context; secondary actions should not compete without rationale.
4. **Information/visual hierarchy** — can a scanner grasp the argument and decision path?
5. **Proof/trust** — are claims supported near the decision they affect?
6. **Objection handling** — price, fit, risk, complexity, process, eligibility, credibility or other evidenced concerns.
7. **Friction** — unnecessary form fields, confusing navigation, unclear next step, performance/mobile/state problems.

A diagnostic finding is a **hypothesis** until supported by research/analytics/testing. Do not call a best-practice recommendation a proven conversion cause.

## Message architecture

### 1. Page job

Define what this page must help this audience decide/do. Different page roles should not inherit the same content argument by default.

### 2. Value proposition

Prefer:

`best-fit audience + important outcome + differentiated reason/proof`

Use specific customer value over generic adjectives. If positioning itself is unclear, hand off upstream rather than inventing a tagline.

### 3. Above-the-fold / first-screen contract

Answer, when appropriate:
- what is this?
- who/what situation is it for?
- what valuable outcome/difference matters?
- what credible proof/context is available?
- what is the next action?

Do not force all five into literal copy if the page/brand can communicate them another way.

### 4. Argument sequence

A common but non-universal pattern:

`promise/value → proof → problem/context → benefits/use cases → how/what → objection/risk reduction → CTA`

Reorder based on audience awareness and page role. High-intent pricing/detail pages may lead with comparison/selection; low-awareness pages may require more context.

### 5. Proof strategy

Use verified evidence only:
- named/authorized testimonials;
- real logos/customers;
- case-study outcomes with source/context;
- certifications/standards where applicable;
- demos/screenshots/process evidence;
- transparent limitations and terms.

Never create fake numbers, logos, reviews or “trusted by” claims.

### 6. CTA copy and hierarchy

Prefer consequence/value-aware labels over interaction mechanics when clarity improves:
- `Get the report`
- `See pricing`
- `Book a consultation`
- `Start free trial`

But do not lengthen a button mechanically if context already makes `Continue` or `Save` unambiguous.

## Traffic/awareness adaptation

When traffic source or prior knowledge is known:
- paid/campaign landing → strong message match and focused conversion path;
- organic informational → answer intent first, then relevant next action;
- returning/high-intent → reduce redundant education and expose decision/proof faster;
- referral/brand direct → preserve trust and orientation, not necessarily aggressive persuasion.

Unknown traffic context stays UNKNOWN; do not assume all visitors are cold.

## Experiment handoff

For material CRO changes, express testable hypotheses:

`Observed evidence → suspected friction/message gap → proposed change → expected metric → guardrail → verification method`

Use `analytics-and-experimentation` to design the experiment and `experimentation-interpretation` after results exist.

## Output

```text
Page role / entry context:
Primary audience + decision:
Value proposition / positioning dependency:
Argument hierarchy:
CTA hierarchy:
Claim → proof map:
Objections / friction:
Copy direction / alternatives:
CRO hypotheses (FACT vs HYPOTHESIS):
Measurement/verification handoff:
```

## Hard rules

- Clarity before cleverness.
- Benefits/value before feature dumping.
- Customer language over internal jargon when evidence exists.
- One main idea/decision per section where practical.
- No fake urgency/scarcity/proof.
- No conversion-improvement claim without outcome data.
- Do not use CRO conventions to override accessibility, trust, consent or project truth.
- Marketing persuasion must not mask destructive, paid, privacy or irreversible consequences.

## External knowledge

CRO/copy patterns are informed by the pinned `ai-vita/skills` snapshot in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`; recommendations remain hypotheses until project evidence/measurement supports them.

## Acceptance criteria

- Page argument matches audience, page role and known entry context.
- Primary CTA supports the real decision/next step.
- Material claims have real proof strategy.
- Objections/friction are evidence-backed or labeled hypotheses.
- UX state copy is delegated to the correct owner.
- No unverified conversion claim is presented as fact.
