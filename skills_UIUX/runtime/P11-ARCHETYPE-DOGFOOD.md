# P1.1 Archetype Real-Task Dogfood

## Purpose

This lane validates the canonical specialist-routing ownership introduced by P1.1 against pinned, real project repositories rather than synthetic fixtures.

It exercises the same production routing chain used by external tasks:

`GoalInterpreter -> target-project truth merge -> FlowPlanner -> SpecialistComposer -> external task manifest`

The lane is intentionally read-only. A PASS is routing evidence, not rendered UX QA, user validation, deployment verification or a release verdict.

## Pinned real targets

| Project | Repository | Pinned SHA | Evidence |
| --- | --- | --- | --- |
| PATH / EdTech | `Ngh1aa/EdTech` | `c33be024e1fb59ceadd5edace0e1a42473618ae2` | `index.html`, `app.js`, `style.css` |
| LuxRoom | `Ngh1aa/LuxRoom` | `37e6a8c4a2aecdb9cefd9fd4291b353252d5356b` | `index.html`, `detail.html`, `cart.html`, `checkout.html` |

## Four task cases

### 1. EdTech — learning-experience

Task:

> Redesign the whole product learning experience for the PATH EdTech course platform: lessons, quizzes, assignments, learning paths and mistake review.

Expected canonical routing:

- domain: `education-edtech`
- archetype: `learning-experience`
- change surface: `PRODUCT`
- flow: `professional-website-redesign`
- specialist evidence includes learning journey/progress UX and implementation recovery states.

### 2. EdTech — learning-operations

Task:

> Build a product for the PATH EdTech LMS admin with an instructor dashboard, course management, grading, student management and learning analytics.

Expected canonical routing:

- domain: `education-edtech`
- archetype: `learning-operations`
- change surface: `PRODUCT`
- flow: `professional-website-redesign`
- specialist evidence includes enterprise tables, dashboard visualization, complex forms and error recovery.

### 3. Ecommerce — catalog-commerce

Task:

> Redesign the whole product catalog discovery experience for the LuxRoom ecommerce website: product listing, category browsing, filters, search and product detail.

Expected canonical routing:

- domain: `commerce-retail`
- archetype: `catalog-commerce`
- change surface: `PRODUCT`
- flow: `professional-website-redesign`
- specialist evidence includes ecommerce intelligence, conversion/content and search/findability.

### 4. Ecommerce — checkout-commerce

Task:

> Improve the LuxRoom ecommerce checkout page, cart, payment and order confirmation flow.

Expected canonical routing:

- domain: `commerce-retail`
- archetype: `checkout-commerce`
- change surface: `PAGE`
- flow: `page-ui-work`
- specialist evidence includes form interaction, trust/transparency, complex forms and error recovery.

## PASS contract

For each pinned checkout the dogfood runner must prove:

1. Target SHA matches the declared real-project pin.
2. Required repository evidence exists.
3. Working tree is clean before and after execution.
4. The external task manifest preserves read-only authority.
5. Target-project truth is probed before flow resolution.
6. Canonical domain, archetype and change surface match the task.
7. Canonical FlowPlanner chooses the expected flow.
8. Required specialist skills appear on the expected stages.
9. All four archetypes are present across the two reports.

## Truth boundary

This lane does **not** claim:

- rendered visual correctness,
- accessibility conformance,
- user-validated outcomes,
- deployment health,
- production readiness,
- or release approval.

Those remain owned by their existing QA, validation and governance lanes.
