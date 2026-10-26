# Design system

A working, tested design system that the skills in `skills_UIUX/` can point to as a concrete
reference. Tokens follow the [Design Tokens Format Module 2025.10](https://www.designtokens.org/)
(the first stable DTCG spec), components are plain CSS with no framework dependency, and every
rule that can be checked by a machine is checked in CI.

Status: **v0.3.0**, pre-1.0. The token paths and class names may still change; see
[governance](docs/governance.md) for how.

## What is in it

```text
design-system/
├── tokens/                     source of truth (DTCG JSON)
│   ├── primitive/              raw scales: color (OKLCH-derived), space, radius, size, type, motion, shadow
│   ├── semantic/               roles: surface, text, border, action, feedback, dataviz, media, type, spacing, shape, elevation
│   │   ├── color.light.json    one file per mode, identical paths (parity is enforced)
│   │   └── color.dark.json
│   └── component/              per-component decisions that alias semantic roles
├── generated/                  build output, committed for consumers (do not edit)
│   ├── tokens.css              CSS custom properties, light default, dark via media query or data-theme
│   └── tokens.json             fully resolved values per mode (native handoff, Figma plugins)
├── components/
│   ├── components.css          25 components, tokens only, no color literals
│   └── icons.svg               original 24px outline icon sprite
├── patterns/
│   ├── patterns.css            30 composed blocks (hero, data, content, flow, conversion, states), tokens only
│   ├── index.html              gallery of every pattern in both modes
│   └── README.md               contract per pattern: anatomy, when to use, minimum density, misuse
├── fonts/                      Be Vietnam Pro (SIL OFL 1.1), Latin + Vietnamese subsets
├── docs/
│   ├── index.html              generated living style guide: roles, contrast table, type scale, all states
│   ├── component-contracts.md  purpose, anatomy, variants, states, accessibility, misuse per component
│   └── governance.md           versioning, deprecation, contribution, definition of done
├── examples/appointment-app/   three task-led mobile screens built only from the system
├── examples/money-app/         v0.2 finance reference: sheet, progress, skeleton, segmented filter
├── examples/gom-moc/           trial run of the client process: brief, brand.css, landing page, app screens
├── starter/                    starter kit: placeholder brand layer, 8 mobile + 2 web screens, 6 desktop app shells, landing skeleton
├── contrast-pairs.json         79 declared foreground/background pairs, checked in both modes
├── scripts/                    build.py, validate.py, capture-example.cjs (Python stdlib, Node for browser checks)
└── tests/                      pytest regression and negative tests
```

## Architecture

```text
primitive  color.jade.700, space.400, font.size.400        raw values, never used by components
    │
semantic   action.primary.bg, text.secondary, type.body-md  meaning; the only layer that changes per mode
    │
component  button.height.md, field.border, tab-bar.item-active   per-component decisions
    │
CSS        .ds-button--primary { background: var(--ds-action-primary-bg) }
```

Aliases stay aliases in the generated CSS (`--ds-action-primary-bg: var(--ds-color-jade-700)`), so
the dark block overrides only the semantic layer and every component follows.

## Decisions worth knowing

- **Be Vietnam Pro.** Drawn for Vietnamese stacked diacritics. Body line height never drops below
  1.5 and inputs are 52px tall so 17px text with marks like "ể" never clips.
- **Warm neutral + jade.** Neutrals carry a slight warm hue so surfaces read as paper, not
  clinical gray; jade is the single brand hue. Scales are generated in OKLCH for even perceived
  steps, then stored as sRGB per the DTCG color format.
- **Charts get their own roles.** `dataviz.*` gives six categorical hues (each ≥ 3:1 on page and
  card surfaces in both modes), a sequential and a diverging ramp, plus grid, axis, highlight and
  muted. One highlight per chart; everything else muted.
- **Status is never color-only.** Badges and banners always carry icon + text.
- **Placeholder text meets 4.5:1.** Users still have to read it.
- **One primary button per view region,** enforced by contract and review, not by code.

## Use it

```html
<link rel="stylesheet" href="design-system/fonts/fonts.css">
<link rel="stylesheet" href="design-system/generated/tokens.css">
<link rel="stylesheet" href="design-system/components/components.css">
<!-- optional: composed blocks, see patterns/README.md -->
<link rel="stylesheet" href="design-system/patterns/patterns.css">
<body class="ds-root">
  <button class="ds-button ds-button--primary">Đặt lịch</button>
</body>
```

Theme: follows `prefers-color-scheme`; force with `<html data-theme="dark">` or `"light"`.
Figma: Tokens Studio and other DTCG-aware plugins can import `tokens/`; verify the plugin's current
DTCG 2025.10 support before relying on it.

## Change it

```sh
python3 design-system/scripts/build.py              # regenerate generated/ and docs/index.html
python3 design-system/scripts/validate.py --report  # format, layering, mode parity, contrast, CSS lint
python3 -m pytest design-system/tests -q            # regression + negative tests
NODE_PATH=<playwright-and-axe-core> node design-system/scripts/capture-example.cjs artifacts/ds
node --test design-system/tests/browser-gate.test.cjs
```

CI runs the first three on every push and pull request that touches `design-system/`, then runs the
capture script in Chromium, WebKit and Firefox (`.github/workflows/design-system.yml`).

The browser gate requires every requested engine and axe-core. It writes a fresh `RUNNING`
report before checks and `PASS` or `FAIL` afterward, preserving failure diagnostics. For a
deliberately reduced local review, pass an explicit engine list or `--allow-partial`;
missing-engine/axe evidence is labelled `PARTIAL`. CI cannot opt out of the strict gate.
`scripts/check-all.sh` continues all checks and exits nonzero if any check fails.

## What the checks prove, and what they do not

| Claim | Evidence | Status |
|---|---|---|
| Tokens are valid DTCG 2025.10 for the types used | `validate.py` shape checks | VERIFIED |
| Declared text and UI pairs meet WCAG 2.x contrast in both modes | `contrast-pairs.json`, 98 checks | VERIFIED for declared pairs only |
| Components use no hard-coded colors | CSS lint in `validate.py` | VERIFIED |
| Example and docs have no automated axe-core A/AA violations | `examples/appointment-app/review/browser-report.json` | VERIFIED in Chromium only |
| Works in Safari and Firefox | not run | UNKNOWN |
| Full WCAG 2.2 AA conformance | needs manual and assistive-technology testing | UNKNOWN |
| Users prefer it or complete tasks faster | no participant study | UNKNOWN |
