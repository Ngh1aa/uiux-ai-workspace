---
name: accessibility-conformance-evaluation
description: Plans and conducts a structured WCAG conformance evaluation and the manual assistive-technology testing it depends on (keyboard, screen readers, zoom/reflow, reduced motion, speech) using defined scope, representative samples, complete processes and explicit reporting limitations. Use for formal accessibility review, release gates, accessibility statements, or verifying critical journeys after significant interaction changes—not routine linting alone.
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

## Assistive technology testing

Owns manual verification of critical journeys with assistive technology. It was previously a
separate skill (`assistive-technology-testing`) and is part of every conformance evaluation; it can
also run on its own after significant interaction changes, labelled `targeted verification`.

1. Define critical journeys and the browser + assistive-technology combinations in scope
   (for example NVDA or JAWS with Firefox/Chrome on Windows, VoiceOver with Safari on macOS and
   iOS, TalkBack with Chrome on Android). Record versions.
2. Keyboard only: reach every control, visible focus, logical order, no traps, focus restored after
   dialogs and sheets close, skip links where needed.
3. Screen reader: names, roles, values and states; reading order; headings and landmarks;
   live-region announcements for async updates and errors; form errors linked to their fields.
4. Zoom and reflow: 200% text resize and 400% zoom (320 CSS px) without loss of content or
   two-dimensional scrolling, except content that needs it (tables, maps).
5. Reduced motion, contrast and colour independence.
6. Speech/voice control where relevant: visible labels match accessible names.
7. Record reproducible defects with the combination used, and retest every fix with the same one.

Rules: automated scans are never the only evidence. A visual state change must have a matching
focus or announcement behaviour. Baseline: WCAG 2.2 AA, with GOV.UK assistive-technology testing
guidance as a practical reference.

## Required artifact
Create/update `docs/accessibility-evaluation.md`.

## Gate
Never say `WCAG conformant`, `fully accessible` or equivalent from a partial audit. Use precise language such as `sampled audit`, `critical-flow review`, or `targeted verification` when that is what occurred.

## Anti-patterns
- Lighthouse/axe score used as conformance proof.
- Testing one page and generalizing to the site.
- Ignoring complete processes and dynamic states.
- Skipping manual/AT evaluation for critical interactions.
- Testing a screen reader only by reading the DOM or an accessibility-tree dump.
- Hiding unresolved failures behind an aggregate score.
