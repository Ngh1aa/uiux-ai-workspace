---
name: web-ui-code-review
description: Reviews implemented web UI code for interface-quality, accessibility, interaction, copy/state and performance risks, with conditional React/Next.js specialization. Use for code-level UI review, pre-merge interface audits, React/Next performance review or when rendered QA findings need source-level root-cause checks.
---

# Web UI Code Review

## Boundary

This skill owns **code-level interface review orchestration**. It does not replace:

- `accessibility` / formal accessibility evaluation;
- `web-quality-and-performance` / project performance budgets;
- `ui-craft-and-visual-qa` / rendered pixel inspection;
- `frontend-architecture-and-refactoring` / architecture redesign;
- `testing-strategy` / full verification planning.

It coordinates a concise review and routes material findings to those owners.

## Workflow

1. Read project context, Design Contract and changed files first.
2. Detect actual stack/version from source. Never assume React/Next.js.
3. Review general web-interface concerns before framework-specific optimization.
4. If React/Next is detected and performance is material, apply the prioritized React/Next reference.
5. Classify each finding by severity and owner skill; avoid duplicate reports for the same root cause.
6. Prefer root-owner fixes over CSS/JS patches layered on top.
7. Run source/build/tests appropriate to the finding, then require rendered QA when visual/interaction claims depend on pixels.

## General review categories

Check only categories relevant to changed UI:

- semantic interactive elements and keyboard/focus behavior;
- forms, labels, validation, errors and recovery;
- navigation/state/deep-link behavior;
- touch targets and pointer/hover assumptions;
- typography/text overflow/localization resilience;
- media dimensions, lazy loading, crop and layout stability;
- motion purpose, interruption behavior and reduced motion;
- UI copy/action clarity where strings affect use;
- client/server ownership and hydration risks where applicable;
- asset/icon semantics;
- loading/empty/error/success states;
- avoidable performance cost that changes perceived UI quality.

## React/Next conditional review

When the detected stack is React/Next.js, prioritize:

1. waterfalls and serial async work;
2. unnecessary bundle cost / broad imports / heavy client code;
3. server-side data/serialization/cache ownership;
4. client data-fetch duplication and global listeners;
5. avoidable re-renders and effect-derived state;
6. rendering/hydration/list performance;
7. lower-impact JavaScript hot paths;
8. advanced patterns only after higher-impact findings.

Do not apply a framework recommendation that conflicts with the project's actual major version or architecture. If version fit is uncertain, keep the finding `UNKNOWN`/conditional rather than forcing a refactor.

## Finding format

```text
[SEVERITY] file:line — issue
Evidence:
User/quality impact:
Root owner:
Recommended fix:
Verification:
Source basis: project | local skill | pinned external reference
```

Severity:

- `BLOCKING` — breaks critical interaction/accessibility/system truth or creates major regression risk;
- `IMPORTANT` — meaningful usability/performance/maintainability risk;
- `POLISH` — low-risk refinement after core issues.

## Hard rules

- Do not fetch mutable upstream `main` during a review; use the pinned synthesis in `references/`.
- Do not call automated code review WCAG conformance.
- Do not call performance improved without appropriate measurement.
- Do not report style preference as defect unless tied to Design Contract or user impact.
- Build success is not rendered QA.
- Do not optimize React/Next code that is outside scope merely because a best-practice rule exists.

## Progressive references

- [Web interface review](references/web-interface-review.md)
- [React/Next performance review](references/react-next-performance-review.md)

Source pins are recorded in `vendor/external-uiux/SOURCE-LOCKS.md`.

## Acceptance criteria

- Stack/version is detected or explicitly marked unknown.
- Findings are evidence-backed and deduplicated by root cause.
- React/Next checks only activate when applicable.
- Each material finding has owner + verification.
- Rendered/behavior verification is not substituted by source inspection when the claim requires it.
