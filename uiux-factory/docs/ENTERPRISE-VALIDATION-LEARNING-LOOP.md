# Enterprise Validation & Learning Loop

This document records the enterprise patterns adapted into UIUX Factory after benchmarking official sources. The purpose is not to copy company process ceremony. It is to close four capability gaps while preserving the Factory's strong design/implementation/QA loop.

## Capability additions

### 1. Real-user validation
Direct user evidence is now a routed capability rather than an optional note. The system distinguishes direct users/live behavior from proxy, desk research and hypotheses.

### 2. Outcome metrics + instrumentation
Production-learning work defines outcomes, critical experiences, behavioral/attitudinal metrics, baselines and event/data-source contracts before release.

### 3. Human governance
High-consequence decisions preserve explicit human ownership. Outcome framing, recurring playbacks and representative user collaborators help expose drift without turning routine work into meeting-heavy governance.

### 4. Post-launch learning
Production does not terminate at merge/deploy. Critical experiences, analytics, support, user research, experiments and staged rollout feed the next iteration.

## Validation lanes

```text
prototype
  → fast design/build/rendered QA

evidence-led
  → prototype loop
  + direct-user validation plan/evidence
  + explicit evidence labels

production-learning
  → evidence-led loop
  + outcome instrumentation
  + human governance
  + release/live-learning readiness
```

This is risk-proportional: portfolio/recruitment prototypes are not forced through enterprise production ceremony.

## Official source basis

- IBM Enterprise Design Thinking Framework: https://www.ibm.com/training/enterprise-design-thinking/framework
  - adapted: user-outcome framing, Playbacks, recurring representative Sponsor Users.
- GOV.UK Service Manual — User research: https://www.gov.uk/service-manual/user-research
  - adapted: research across discovery/alpha/beta/live; inclusive recruitment; research as a team activity.
- GOV.UK — User research in live: https://www.gov.uk/service-manual/user-research/user-research-in-live
  - adapted: combine analytics, support, surveys, interviews/usability tests and experiments after launch.
- GOV.UK — Measuring success: https://www.gov.uk/service-manual/measuring-success
  - adapted: define success early, combine performance data with user research and continuously improve.
- GitLab UX Quality Metrics Framework: https://handbook.gitlab.com/handbook/product/ux/ux-quality-metrics-framework/
  - adapted: Concepts → Designs → Live; behavioral + attitudinal metrics; instrumentation before launch.
- GitLab Tracking Critical Experiences: https://handbook.gitlab.com/handbook/product/ux/tracking-critical-experiences/
  - adapted: monitor make-or-break journeys rather than isolated UI surfaces.
- GitLab Experimentation: https://handbook.gitlab.com/handbook/product/ux/ux-resources/experimentation/
  - adapted: hypothesis + expected outcome + metric before experimentation.
- GitLab Feature Flag Lifecycle: https://handbook.gitlab.com/handbook/product-development/how-we-work/product-development-flow/feature-flag-lifecycle/
  - adapted: risk-based staged rollout, observation and cleanup.
- Microsoft Inclusive Design: https://inclusive.microsoft.design/
  - adapted: recognize exclusion, learn directly from diversity, avoid simulation as a substitute for people.

## Non-goals

- No universal NPS requirement.
- No fixed sample size fabricated as "enterprise best practice".
- No A/B testing requirement for every website.
- No feature-flag requirement when the target stack/risk does not justify it.
- No claim of user validation without direct evidence.
- No requirement that small prototypes create production analytics infrastructure.
