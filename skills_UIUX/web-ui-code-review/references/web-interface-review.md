# Web Interface Review — Pinned Synthesis

Sources reviewed:

- Vercel `web-design-guidelines` at `vercel-labs/agent-skills@063bee94c3f4df8453406c830b0a7df0f2860278`.
- Vercel Web Interface Guidelines at `vercel-labs/web-interface-guidelines@e3d624baaf29dc1fc645aff3e38f03e564d2d6b1` (MIT).

This is a local synthesis, not a runtime fetch of upstream `main`.

## High-value checks

### Interaction and semantics

- Use native semantic controls when possible; do not rebuild button/link/input behavior with generic containers.
- Keyboard focus must be visible and not obscured.
- Icon-only controls need an accessible name.
- Hover cannot be the only way to discover essential information/action.
- Disabled controls must not leave the user without an explanation or recovery path.

### Forms and feedback

- Persistent labels beat placeholder-only labeling.
- Put validation/error guidance close to the field; summarize when a long form needs it.
- Error copy should explain recovery, not only failure.
- Loading, empty, success and failure states need appropriate semantic/state feedback.

### Text and layout resilience

- Long labels, URLs, translated strings and user-generated values must not silently clip essential meaning.
- Avoid brittle fixed-width assumptions for text-bearing controls.
- Use readable line lengths and hierarchy; visual truncation needs an accessible full-value path when unavoidable.

### Touch and pointer

- Interactive targets need practical touch size/spacing.
- Do not rely on precision hover behavior for touch-first or mixed-input experiences.
- Pointer feedback should match actual clickability.

### Media and layout stability

- Reserve image/media dimensions to prevent layout shift.
- Choose crop/focal behavior intentionally; do not treat `object-fit: cover` as art direction.
- Defer non-critical media only when it does not hide above-fold meaning.

### Motion

- Motion should explain state, continuity, hierarchy or feedback.
- Respect `prefers-reduced-motion`.
- Avoid universal duration/easing or animating layout properties when cheaper transforms/opacities communicate the same result.
- Interrupted/rapid interactions must end in correct semantic state.

### Copy

- Use specific action labels when consequence matters; avoid vague `Continue`, `Submit`, `OK` when the next result is important.
- Error messages should offer a useful exit/recovery.
- Prefer plain, direct language over cleverness in transactional UI.

## Local reconciliation

When a check is material, route to the existing local owner:

- semantics/focus/AT → `accessibility`;
- forms/state/recovery → `interaction-patterns-and-form-ux` or advanced state specialists;
- copy → `ux-writing-and-microcopy`;
- media/crop → `asset-media-and-art-direction` + media integrity gates;
- responsive breakage → `responsive-and-device-strategy`;
- performance/layout stability → `web-quality-and-performance`;
- rendered fidelity → `ui-craft-and-visual-qa`.

A Vercel guideline is guidance, not evidence that a project fails or passes until the relevant project state is inspected.
