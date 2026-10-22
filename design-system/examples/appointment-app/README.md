# Appointment app reference

Three task-led mobile screens built **only** from design-system tokens and components. It is the
successor to `skills_UIUX/visual-design-direction/examples/mobile-care/`, which is kept unchanged
because its review hashes are locked by `uiux-factory/tests/test_mobile_visual_quality.py`.

Data, clinic and people are synthetic. Nothing is submitted.

## What changed from mobile-care, and why

| Issue in mobile-care | Fix here | Rule it now follows |
|---|---|---|
| Bottom navigation was text-only | Icon + label + indicator pill, `aria-current` | Tab bar contract |
| Three different secondary-action styles | One hierarchy: primary, secondary, tertiary | Button contract |
| Glyph icons (▤ ⌖) at text size, decorative | 24px stroked icons in 40px tiles, list rows with chevrons | List item contract |
| Decorative radial gradients in headers | Plain app bar; one brand-subtle card for the hero object | Card `--brand` limit: one per screen |
| Error shown in a block below the form | Inline error under the field, linked by `aria-describedby`, focus moved to field | Field contract |
| System font, hard-coded hex values | Be Vietnam Pro, every value from tokens, light and dark | Token layering, CSS lint |

Behavior is kept: filter, search, empty state with reset, invalid phone recovery, back keeps input,
feedback on every action.

## Reproduce

```sh
python3 design-system/scripts/build.py
NODE_PATH=<dir containing playwright and axe-core> \
  node design-system/scripts/capture-example.cjs artifacts/appointment-app
```

The script serves the folder on 127.0.0.1 (axe-core needs HTTP to read stylesheets), then for every
available engine, 320/390/1280 px and light/dark: checks overflow, theme initialisation, font
loading, the task flows, axe-core WCAG 2.0/2.1/2.2 A and AA rules, console errors and a 125% root
font-size stress.

## Recorded review (2026-10-22)

| Evidence | Status |
|---|---|
| Playwright Chromium (build 1194), 3 widths x 2 themes x 2 pages, task flows, overflow, console | VERIFIED, `review/browser-report.json` |
| axe-core 4.14.0, WCAG A/AA tags: 0 violations, 0 incomplete | VERIFIED for automated rules only |
| Screenshots opened and inspected by the agent | `review/*.png` (palette-quantised to keep the repo light) |
| WebKit and Firefox | NOT RUN: engines not installed in the build environment |
| Screen reader (VoiceOver, TalkBack), native Dynamic Type | UNKNOWN |
| Human preference or usability with real participants | UNKNOWN |

Issues the checks found and fixed during this work: body-tertiary text at 4.26:1 on the page
surface (palette step 600 darkened), button labels wrapping at 320 px, a truncated search
placeholder, three undefined modifier classes used by the example, and a keyboard-inaccessible
scroll region in the docs page.
