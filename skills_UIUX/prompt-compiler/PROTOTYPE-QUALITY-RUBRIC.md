# Adaptive Prototype Quality Rubric

This rubric adapts useful ideas from prototype-design checklists into UIUX Factory without turning heuristics into universal hard laws.

## Scope

Use for visual/UI prototypes when applicable. Do **not** treat this file as a production, legal, SEO, analytics, backend, or release checklist.

Every item is one of:
- `DUE_NOW`
- `PENDING_FUTURE_PHASE`
- `N/A_JUSTIFIED`

## 1. Intent before visuals

- Identify audience/reviewer and demo context.
- Define the desired first-impression emotion in one sentence.
- Identify product/site archetype before choosing layout patterns.
- Define 3 art-direction adjectives.
- Decide whether to follow familiar category conventions or deliberately break them.
- Detect generic AI/template defaults and reject interchangeable styling.
- Define the critical demo journey and one signature/hero moment.

## 2. UX heuristics — guidance, not magic numbers

Review applicable principles such as choice complexity, target size, familiarity, grouping, visual emphasis, responsiveness of feedback, progress visibility, and peak/end quality.

Numbers such as `5–7 nav items`, `44px touch targets`, or `<400ms feedback` are useful defaults, not universal truth. Deviate when product evidence or platform conventions justify it, and document the reason.

## 3. Visual system

### Color
- Define semantic roles for color rather than selecting decorative swatches ad hoc.
- Keep accents intentional; multiple accents are allowed when the information architecture requires them.
- Verify text/background contrast programmatically when applicable, not by visual inspection alone.

### Typography
- Typography must support the selected art direction and content language(s).
- Define a coherent type hierarchy and line-length strategy.
- `Two font families` is a useful simplification, not a universal requirement.
- Test real long strings, Vietnamese diacritics when relevant, and extreme content lengths.

### Layout
- Establish grid/alignment/spacing logic.
- Use whitespace and hierarchy intentionally.
- Perform rendered squint/hierarchy review.
- Do not copy a category layout blindly; use conventions only where they help comprehension.

### Media and visual signature
- Media/icon/illustration treatment should be coherent.
- Prefer relevant, attributable media over generic stock.
- Include at least one project-specific visual or interaction signature when the goal calls for distinctiveness.

## 4. Interaction and motion

- Concentrate craft in one or a few signature motion moments rather than animating every section identically.
- Every interactive element must expose an appropriate hover/focus/active response for the target input mode.
- Avoid `outline: none` without a visible focus replacement.
- Scroll animation must be selective and purposeful.
- Custom cursors and heavy pointer effects require explicit art-direction justification.
- Verify interaction by operating the rendered prototype, not by reading code only.

Timing ranges like `150–300ms` are defaults for common micro-interactions, not mandatory for every interaction type.

## 5. Component/state completeness

For states that occur in the declared demo journey, cover applicable:
- default;
- hover;
- focus;
- active/selected;
- disabled;
- loading;
- empty;
- error;
- success.

If a prototype simulates a wait or backend response, label it `SIMULATED`; never present `setTimeout` behavior as a real backend integration.

## 6. Responsive scope

Decide scope before implementation:
- `desktop_only`, or
- `responsive_all`.

For responsive work, representative widths should usually include mobile/tablet/desktop, but exact widths come from the project contract. Check content priority, overflow, crop, readable type, and target sizes.

## 7. Final rendered critique

Before visual approval:
- squint/hierarchy review;
- 5-second comprehension review when useful;
- remove one unnecessary decorative effect;
- compare result to the 3 art-direction adjectives;
- compare against category references for distinctiveness, not imitation;
- operate the complete demo path;
- replace placeholder content;
- obtain human visual veto for substantial visual work.

## 8. Common failure signals

- every section uses the same fade/slide pattern;
- irrelevant stock imagery;
- universal rounded-card + soft-shadow treatment with no project rationale;
- every heading uses the same uppercase eyebrow pattern;
- primary action is not visually distinguishable;
- interaction states feel delayed or absent;
- strong build/test status is mistaken for strong rendered design.

## Rule

This rubric informs Spec Writer and Visual QA. It must not overwrite verified project truth, force irrelevant work, or create blockers outside the declared phase.