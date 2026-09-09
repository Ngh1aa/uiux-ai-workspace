---
name: accessibility-conformance-evaluation
description: Plans and conducts a structured WCAG conformance evaluation using defined scope, representative samples, complete processes, appropriate manual/automated/assistive-technology checks, and explicit reporting limitations. Use for formal accessibility review, release gates or accessibility statements—not routine linting alone.
---

# Accessibility Conformance Evaluation

## Principle
Automated scans and spot checks are useful evidence, but they do not by themselves justify a conformance claim.

Use the current W3C/WAI WCAG-EM methodology appropriate to the project and verify its current status before a formal external claim.

## Evaluation workflow
### 1. Define scope
Record:
- product/site scope;
- target WCAG version/level;
- environments/technologies relied upon;
- exclusions and additional requirements;
- evaluator/date.

### 2. Explore the target
Inventory page/view types, shared components, dynamic states, technologies and critical processes.

### 3. Select representative samples
Include:
- common templates/components;
- structurally/functionally distinct pages;
- important states;
- complete critical processes, including relevant branch paths;
- a reasonable additional sample where appropriate.

### 4. Evaluate
Combine suitable:
- automated tooling;
- keyboard/manual checks;
- zoom/reflow/color/motion checks;
- screen reader/assistive technology testing;
- code inspection;
- user evaluation with disabled people where useful.

### 5. Report
Record failures, affected samples/processes, severity, evidence, remediation and retest status. State exactly what was and was not evaluated.

## Required artifact
Create/update `docs/accessibility-evaluation.md`.

## Gate
Never say `WCAG conformant`, `fully accessible` or equivalent from a partial audit. Use precise language such as `sampled audit`, `critical-flow review`, or `targeted verification` when that is what occurred.

## Anti-patterns
- Lighthouse/axe score used as conformance proof.
- Testing one page and generalizing to the site.
- Ignoring complete processes and dynamic states.
- Skipping manual/AT evaluation for critical interactions.
- Hiding unresolved failures behind an aggregate score.
