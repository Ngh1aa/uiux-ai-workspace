# Design Extraction Schema — Pinned Synthesis

Source reviewed: `billhector/design-skills@afee427d8f1e2d9deb004a96bcaa8391c572c9f5` (MIT), especially `design-extractor` and `design-auditor`.

This schema adapts the useful extraction discipline while removing mandatory Firecrawl/Tailwind assumptions.

## Per-target metadata

```text
Target:
Reference type:
Pages/states or source files inspected:
Captured date:
Tooling/evidence available:
Limitations:
```

## Visual system fields

### Color

For each recurring color:

| Observed value | Inferred role | Usage evidence | Source | Certainty |
|---|---|---|---|---|

Prefer semantic role inference only when usage supports it: primary action, secondary action, accent, text, muted text, background/surface, border, success/warning/error.

### Typography

| Family/stack | Size | Weight | Line-height | Letter spacing | Usage | Source | Certainty |
|---|---:|---:|---:|---:|---|---|---|

Record actual locale/content constraints when visible. Do not assume a font file/license simply from a CSS family name.

### Spacing

Collect repeated `margin/padding/gap` values and contexts. Distinguish:

- raw observed scale;
- inferred rhythm/system;
- outliers/inconsistencies.

Do not automatically normalize raw values in the evidence table.

### Radius / border / elevation

Record values with component/context rather than only a frequency count. One radius used on a modal and one on a badge may have different semantic roles.

### Layout

Capture:

- container/max widths;
- column/grid patterns;
- section padding/rhythm;
- alignment rules;
- sticky/fixed regions;
- page-role-specific composition.

### Responsive behavior

| Breakpoint / pressure point | Observed change | Page/state | Source | Certainty |
|---|---|---|---|---|

Prefer observed transformations over inferred “mobile-first” assumptions.

### Components and states

Inventory component families and visible states:

`default / hover / focus / active / selected / disabled / loading / empty / error / success`

Only list states actually observed or present in code; missing state is a finding, not permission to invent one.

### Theme / dark mode

Look for actual evidence:

- `prefers-color-scheme`;
- `.dark`/theme/data-attribute toggles;
- semantic token mode definitions;
- dark-mode class usage;
- alternate design-system variables.

No evidence → `UNKNOWN/NOT OBSERVED`; do not fabricate an alternate palette.

## Accessibility observations

Automated/analytical checks may cover:

- verified foreground/background contrast pairs;
- missing visible labels;
- focus-style evidence;
- target sizing clues;
- text clipping/overflow risk;
- state conveyed by color alone.

These are audit observations, not formal conformance.

## External-reference transfer table

| Observed pattern | Why it appears to work | Transferable principle | Brand-specific / do not copy | Project adaptation |
|---|---|---|---|---|

The final visual direction must be able to stand without naming the reference.

## Current-project inconsistency table

| System area | Observed variants | Intended owner | Risk | Normalize now? | Verification |
|---|---|---|---|---|---|

Do not “clean up” inconsistencies outside user scope merely because the audit found them.
