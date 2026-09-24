---
name: visual-regression-and-design-drift
description: Protects UI quality across repeated human/AI changes using baseline screenshots, representative viewports/states, intentional-change review, token/component drift detection and regression triage. Use for mature design systems, multi-page sites or automated coding workflows where visual inconsistency can accumulate.
---

# Visual Regression & Design Drift

## Principle
A site can pass functional tests while its visual system slowly fragments — or while an elementary rendered defect remains completely obvious to a human.

Protect both:
1. **render regressions** — unexpected visual changes;
2. **system drift** — new one-off tokens/components/patterns that weaken the design language;
3. **visual sanity failures** — invisible text/controls, broken interaction-state contrast, shared cascade regressions and invalid focal crops.

## Workflow
### 1. Define coverage
Choose representative:
- templates/routes;
- breakpoints/viewports;
- critical component states;
- themes/locales when relevant;
- data conditions that materially affect layout.

**Coverage override for shared owners:** representative sampling is acceptable for deep aesthetic review, but a changed shared header/footer/nav/theme/button/surface owner must receive elementary sanity coverage on **every affected route/template** where it renders.

### 2. Establish stable baselines
Control fonts, animations, timestamps, random content and asynchronous loading where possible. Baselines are reviewed artifacts, not arbitrary first snapshots.

A baseline with an obvious broken screenshot is invalid even if the capture script exits `0`.

### 3. Run elementary rendered sanity before pixel-diff interpretation
For applicable changed/shared UI, assert/inspect:

- visible important text is not foreground≈background and does not require selection/highlight to read;
- shared light↔dark surface changes retain compatible descendant text/link/icon/divider/control states;
- default/hover/focus/active/selected/disabled labels remain perceptible;
- computed browser styles match the intended component/surface contract; specificity/cascade regressions are blockers;
- human/primary focal subjects survive actual target crops; `object-fit: cover` is not proof.

Automated contrast checks are regression signals, not formal accessibility conformance claims.

### 4. Compare
Use visual diff tooling when available, then triage changes as:
- intended + approved;
- intended but system-breaking;
- unintended regression;
- unstable/flaky capture.

Human visual veto wins: if the rendered image is obviously broken, do not accept it because a numeric diff threshold, DOM assertion, build or CI passed.

### 5. Audit system drift
Flag unjustified:
- raw colors instead of tokens;
- one-off type/spacing/radius/shadow values;
- duplicate components;
- local interaction patterns;
- competing icon/image/motion treatments;
- local background overrides that break a shared surface/foreground contract.

### 6. Update intentionally
Baseline updates require a rationale tied to an approved design change.

Never update a baseline to normalize an unresolved invisible-label, low-contrast, broken-cascade or focal-crop defect.

## Failure-promotion rule

If a user/reviewer catches an obvious defect that existing QA should have caught:

1. fix the owning project code/token/component/media rule;
2. add a project regression/check where feasible;
3. update the owning skill/checklist if the failure is generalizable;
4. add/promote a regression eval case in this library;
5. exercise the new guard before closing the remediation.

A one-off patch without prevention evidence is not a complete reliability fix.

## Required artifact
Create/update `docs/visual-regression-plan.md` and a drift issue list where applicable.

For high-risk/shared visual changes, the plan must distinguish:
- representative deep visual-review routes;
- all-affected-route elementary sanity coverage;
- component state variants;
- media/focal crop pressure points.

## Gate
Critical templates/states should have verified visual coverage before high-risk releases. Do not call a changed screenshot a regression until intent and rendering stability are checked.

`PASS` is forbidden when any DUE-NOW P0/P1 visual sanity failure remains, regardless of build/CI/pixel-diff status.

## Anti-patterns
- Pixel-perfect diff with uncontrolled dynamic content.
- Automatically accepting all new baselines.
- Treating every visual difference as a bug.
- Ignoring declared responsive states.
- Solving drift by adding more one-off CSS.
- Sampling one route after changing a site-wide footer/header/theme owner.
- Auditing only default button screenshots and skipping hover/focus/disabled.
- Accepting `object-fit: cover` without inspecting the actual focal crop.
- Closing a user-caught obvious defect without adding a regression guard.
