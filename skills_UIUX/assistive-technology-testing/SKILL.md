---
name: assistive-technology-testing
description: Verify critical journeys with keyboard, screen readers, zoom/reflow and other assistive technologies in addition to automated checks. Use before release and after significant interaction changes.
---

# Assistive Technology Testing

## Workflow
1. Define critical journeys and target browser/AT combinations.
2. Run keyboard-only navigation, focus visibility/order and trap checks.
3. Test screen-reader names, roles, states, order, live updates and error announcements.
4. Test zoom/reflow and text resizing.
5. Check reduced motion, contrast and color independence.
6. Test speech/voice interaction where relevant.
7. Record reproducible defects and re-test fixes.

## Rules
Automated accessibility scans are never the only evidence.

## Quality gate
Critical journeys have manual evidence, and visual state changes are matched by meaningful focus/announcement behavior.

## Baseline
GOV.UK accessibility and assistive-technology testing guidance; WCAG 2.2 AA remains the minimum conformance baseline.
