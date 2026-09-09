---
name: reference-extraction-and-design-audit
description: Extracts source-attributed visual-system evidence from a reference website or an existing project's styles, then audits tokens, components, responsive behavior and inconsistencies. Use when reference research needs deeper design-system extraction or when a project needs a current-state design-system inventory before redesign/refactor.
---

# Reference Extraction & Design Audit

## Boundary

This skill **extracts and documents what exists**. It does not decide that the extracted system should be copied, does not replace `design-reference-research-and-benchmark`, and does not silently migrate a project to Tailwind or another framework.

Use it:

- after a reference candidate is selected and deeper structure/token evidence is useful;
- before redesign/refactor when the existing codebase's real design system is unclear;
- when visual drift suggests hidden token/component inconsistency.

## Two modes

### A. External reference extraction

Target = production/reference URL or supplied rendered artifact.

Capture, when tooling permits:
- rendered screenshot(s);
- page/state inspected;
- HTML/CSS/computed/source evidence;
- design tokens and component patterns.

### B. Existing project design audit

Target = current repository.

Inspect actual style sources such as:
- CSS/custom properties/theme files;
- Tailwind or other framework config;
- component styles/modules;
- templates/components;
- typography/font declarations;
- dark-mode/theme mechanisms;
- breakpoints and layout primitives.

## Extraction schema

Extract only observed/inferable categories relevant to the task:

- visual atmosphere / design grammar;
- colors by semantic role;
- typography families/scale/weights/line-height;
- spacing rhythm;
- radii and borders;
- shadows/elevation;
- containers/grids/layout primitives;
- component families/states;
- imagery/crop behavior;
- breakpoints/responsive transformations;
- theme/dark-mode mechanism;
- accessibility-relevant contrast/state signals.

For every material item record **source + certainty**.

## Evidence labels

- `FACT` — directly observed in source/rendered evidence;
- `EVIDENCE_BACKED_INFERENCE` — role/pattern inferred from repeated usage;
- `UNKNOWN` — insufficient evidence.

For external references also keep the project reference label: `PRODUCTION / CASE_STUDY / CONCEPT / MOOD_REFERENCE / UNKNOWN`.

## Workflow

1. Read project truth and define why extraction is needed.
2. Identify target pages/states/source files; do not scrape/read everything blindly.
3. Capture rendered visual evidence when appearance/crop/hierarchy is material and tooling permits.
4. Extract tokens/patterns in small passes rather than loading giant HTML/style files wholesale.
5. Deduplicate near-values but preserve the raw observed values in evidence; do not silently normalize them.
6. Flag inconsistencies/drift separately from candidate recommendations.
7. Run contrast/accessibility calculations only on verified color pair contexts; automated contrast is not conformance.
8. Produce an extraction/audit artifact.
9. Hand external-reference results to `design-reference-research-and-benchmark` / `visual-design-direction`; hand current-project drift to the relevant design-system/code owner.

## Output

External reference:

`docs/uiux/reference-extractions/<reference-slug>.md`

Current project:

`docs/uiux/Current-Design-System-Audit.md`

Minimum structure:

```text
Target / pages or files inspected
Evidence status
Visual grammar
Token tables with source
Component/state inventory
Responsive behavior
Theme/dark-mode evidence
Inconsistencies / unknowns
Accessibility observations
Transferable principles (external only)
Do-not-copy boundaries (external only)
Handoff / owner
```

## Hard rules

- Do not infer an entire design system from one homepage screenshot.
- Do not copy proprietary brand assets/text/compositions.
- Do not make extracted values canonical merely because they are frequent.
- Do not auto-convert fixed values to fluid scales or Tailwind tokens unless migration is explicitly in scope.
- Do not fabricate a dark palette when no dark-mode evidence exists.
- Do not require Firecrawl or any one scraping tool; use available authorized browser/source tooling.
- If a source cannot be inspected, keep the missing data `UNKNOWN` rather than approximating it.

## Progressive reference

Read [references/extraction-schema.md](references/extraction-schema.md) for the detailed extraction fields and source-provenance pattern. It is adapted from `billhector/design-skills` pinned in `vendor/external-uiux/SOURCE-LOCKS.md`.

## Acceptance criteria

- Target pages/states/files inspected are explicit.
- Material extracted values have source and certainty.
- Observed values are separated from normalization/recommendation.
- External extraction includes transfer/do-not-copy boundaries.
- Current-project audit identifies inconsistencies without silently migrating architecture.
- Rendered claims use rendered evidence when applicable.
