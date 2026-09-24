---
name: continuous-learning-and-improvement
description: Converts production analytics, support issues, user feedback, research and regressions into prioritized hypotheses, experiments, fixes and new eval coverage. Use after launch or for long-lived services so learning feeds back into design and agent quality instead of stopping at release.
---

# Continuous Learning & Improvement

## Principle
Release is the start of the next evidence cycle.

`observe → diagnose → hypothesize → change → verify → measure → institutionalize learning`

## Signal sources
Combine when relevant:
- service/journey metrics;
- analytics/search behavior;
- support tickets/call-centre/CRM;
- user feedback and satisfaction;
- usability/research findings;
- accessibility issues;
- performance/security incidents;
- design-system/visual regressions;
- agent eval failures.

## Workflow
### 1. Maintain a learning backlog
Each item records signal, affected audience/journey, severity, confidence, evidence link and proposed next step.

### 2. Diagnose before changing
A drop-off or complaint is a signal, not automatically the root cause. Pair quantitative patterns with qualitative investigation where needed.

### 3. Choose the smallest learning action
Research, instrumentation, content fix, UI change, experiment, rollback, accessibility remediation or technical work.

### 4. Verify and measure
Record expected outcome before implementation, then compare after an appropriate observation window.

### 5. Institutionalize recurring failures
Turn important production bugs/regressions into tests, checklists or eval tasks so the same failure becomes harder to reintroduce.

## Required artifact
Create/update `docs/learning-log.md`:
`signal → evidence → hypothesis → action → expected outcome → result → follow-up → regression coverage`.

## Gate
A post-launch improvement should link to an observed signal or explicit strategic hypothesis—not change merely because a new design trend appeared.

## Anti-patterns
- Dashboard watching with no decision rule.
- Treating every support ticket as universal.
- A/B testing without a meaningful hypothesis/outcome.
- Shipping a fix without checking whether the problem improved.
- Repeated production failures never added to regression coverage.
