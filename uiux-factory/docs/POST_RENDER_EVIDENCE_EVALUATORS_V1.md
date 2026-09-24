# Post-render Evidence Evaluators V1

This layer turns previously untested prototype checklist requirements into concrete rendered evidence after BrowserQA and VisualCritic have already established that the site is technically renderable and visually reviewable.

## Execution order

```text
BrowserQA
  -> VisualCritic
  -> State / Interaction Crawler
  -> Preferred Touch-target Evaluator
  -> Content Stress
  -> Squint Critic
  -> Blind Screenshot Comprehension Proxy
  -> 56-rule Evidence Contract
```

A high VisualCritic score cannot bypass an unresolved machine-gated requirement. A dedicated evaluator that cannot establish an outcome returns `cantTell` or `untested`; it never invents PASS.

## 1. State / Interaction Crawler

Uses real Chromium through Playwright. Representative routes receive trace recording with screenshots and DOM snapshots. The crawler inspects default, hover, focus and pressed style signatures and safely invokes only local toggle-like controls such as checkboxes, disclosure controls, `aria-expanded`/`aria-pressed` controls and `<summary>`.

It deliberately does **not** blindly execute destructive, transactional or externally mutating actions. If feedback can be applicable but cannot safely be demonstrated, the result is `cantTell`.

Artifacts:

- `interaction-state-report.json`
- per-route `*-trace.zip`

Playwright Trace Viewer can inspect before/after action snapshots, the action log, screenshots and DOM snapshots. The trace therefore remains durable raw evidence rather than only a Boolean assertion.

## 2. Squint Critic

Creates a downsampled + Gaussian-blurred representative screenshot for each route. The intended hierarchy comes from `visual-composition.json` (`first_visual_anchor` plus prioritized section anchors). The vision evaluator receives alphabetically sorted candidate labels rather than the intended order and ranks the first three visually dominant anchors from the blurred image.

If fewer than three intended anchors exist, the route is `cantTell`; absence of an intended hierarchy is not interpreted as PASS.

Artifacts:

- `squint-review.json`
- blurred screenshots under verification evidence

## 3. Blind screenshot comprehension proxy

The vision model receives only an entry screenshot and no brief. It independently infers:

- what the site appears to be;
- who it appears to be for;
- the primary next action.

The comparison intent is loaded separately from structured project research / UX artifacts after the blind observation is complete.

This is **not** called a real five-second usability test. A genuine five-second test is a participant research method. The automated evaluator is only a blind screenshot-comprehension proxy, and it returns `cantTell` when intended audience/action data is insufficient.

Artifact:

- `blind-five-second-review.json`

## 4. Content stress

Mutates only disposable browser DOM, never generated source. Representative routes are pressure-tested at mobile, tablet and desktop widths using:

- Vietnamese diacritics and long natural-language strings;
- long person/entity names;
- large numeric/currency values;
- long unbroken identifiers.

The evaluator checks for new horizontal overflow and clipped stress targets.

Artifacts:

- `content-stress-report.json`
- route/viewport stress screenshots

## 5. Preferred 44 CSS px touch-target evaluator

Measures important mobile controls at the 390px representative viewport. The default prototype craft target is 44 x 44 CSS px, with an explicit `data-touch-target-exception` escape hatch when the product team has documented a reason.

This must remain separate from the accessibility smoke gate:

- WCAG 2.2 SC 2.5.8 Target Size (Minimum), Level AA: 24 x 24 CSS px with documented exceptions / spacing behavior.
- WCAG 2.2 SC 2.5.5 Target Size (Enhanced), Level AAA: 44 x 44 CSS px with documented exceptions.

The Factory uses 44px here as a preferred prototype-quality target, not as a false claim about WCAG AA.

Artifacts:

- `touch-target-metrics.json`
- mobile route screenshots

## Provenance and stale evidence

Every dedicated evaluator report contains the current project SHA-256 digest. The Evidence Contract consumes a dedicated report only when its bound digest equals the current generated project digest. After source output changes, stale reports fall back to `untested` instead of carrying a historical PASS forward.

## CI

`Post-render Evaluator Smoke` installs Chromium and runs the suite against a deterministic mini-site containing disclosure, checkbox, search and form controls. This validates real Playwright trace creation, preferred touch-target evaluation and disposable content-stress execution without requiring cloud vision credentials.

Vision-dependent evaluators are allowed to degrade to `cantTell` in CI when no free-tier provider is configured. This is intentional: absence of a vision provider must never be converted into a visual PASS.
