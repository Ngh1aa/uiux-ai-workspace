---
name: content-design-and-question-design
description: Design interface content structure and questions that help users understand, decide and provide accurate information with minimal cognitive burden. Use for forms, transactional UI, onboarding, errors, confirmations and content-heavy journeys; route string/state-level microcopy to ux-writing-and-microcopy when wording itself is the active interaction problem.
---

# Content Design & Question Design

## Boundary

This skill owns **content structure, question design and information sequencing** inside interfaces and journeys.

Use `ux-writing-and-microcopy` when the active problem is the exact wording/pattern of labels, CTAs, errors, empty/loading/success states, notifications or other state-level product copy. Use `conversion-and-content` for marketing/value-proposition copy.

## Workflow
1. Start from user task, decision and required evidence.
2. Use user language and front-load important words.
3. Ask only information needed now.
4. Choose question/control type that matches the answer.
5. Design label, hint, validation, error and confirmation as one system.
6. Order questions by user mental model and dependency.
7. Route to `ux-writing-and-microcopy` when exact state strings materially affect comprehension, trust, action or recovery.
8. Test comprehension when errors would be costly.

## Rules
- One idea per sentence when possible.
- Placeholder is not the only label.
- Help text exists only when it resolves a known ambiguity.
- Error content states what happened and how the user can realistically recover.
- Sensitive questions explain purpose/necessity when it is not obvious.
- Do not ask data earlier than the journey needs it.

## Baseline
GOV.UK content design, writing-for-UI and designing-good-questions guidance, supplemented by the local `ux-writing-and-microcopy` specialist for product-state wording.

## Acceptance criteria
- Content/question sequence maps to a real user task and system dependency.
- Control/question type matches the answer needed.
- Labels/help/errors/confirmation work as a coherent system.
- Exact microcopy is delegated rather than duplicated when it becomes the active problem.
- High-cost comprehension risks have an appropriate validation method.
