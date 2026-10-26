# Changelog

Semantic versioning on the public surface (token paths, class names, state attributes, contracts).
See [docs/governance.md](docs/governance.md).

## 0.5.0 (2026-10-26)

### Added
- `scripts/export-native.py` and committed output `generated/native/DSTokens.swift` and
  `generated/native/DsTokens.kt`: every semantic colour role in light and dark, spacing, shape,
  motion and type roles mapped to Dynamic Type text styles and Material 3 typography slots, plus a
  Material 3 `ColorScheme` mapping. `--check` runs in CI. Tests in `tests/test_export_native.py`.
- Starter `mobile-ios.html` and `mobile-android.html`: one four-screen flow (list, detail, form,
  destructive confirmation) in iOS and Material 3 chrome, styled by `starter/native.css`.
- Starter icons `app-i-arrow-left`, `app-i-more`, `app-i-trash`.

## 0.4.1 (2026-10-26)

### Added
- `scripts/oklch-scale.py`: generates an 11-step scale (50–950) for any hue in OKLCH, reducing
  chroma per step until it fits sRGB; prints hex or a DTCG colour group. Tests in
  `tests/test_oklch_scale.py`. Guide: `foundations/color-oklch.md`.

## 0.4.0 (2026-10-26)

### Added
- Pattern layer `patterns/`: 30 composed blocks in `patterns.css` (hero cards, KPI and charts,
  media and content cards, timeline, stepper, checklist, agenda, pricing, comparison, proof band,
  empty, block error, progress, image placeholders). Gallery `patterns/index.html`, contracts in
  `patterns/README.md`. Linted like `components.css`; checked by `taste-check` in CI at 320–1440 px.
- Primitive `color.violet` scale (hue 300, OKLCH-derived like the other scales).
- Semantic groups `dataviz` (categorical 1–6, sequential 1–5, diverging, grid, axis, highlight,
  muted) and `media` (placeholder background, pattern, ink; scrim ink), both modes.
- Contrast pairs for every dataviz role on page and raised surfaces, and for placeholder ink.

### Changed
- `validate.py` CSS lint accepts project hook variables used with a fallback
  (`var(--app-font-display, …)`); a hook without a fallback is still an error.

## 0.3.0 (2026-10-24)

### Added
- Web components: checkbox and radio (`.ds-check`, `.ds-fieldset`), tabs, dialog (native
  `<dialog>`), menu, tooltip, table. Contracts in `docs/component-contracts.md`, specimens in the
  generated docs page, regression test `test_v03_web_components_have_contracts_and_docs`.
- Icons `ds-i-check`, `ds-i-chevron-down`, `ds-i-x`.
- Starter `landing.html`: section skeleton for landing pages (structure only, bracketed copy).
- `scripts/check-brand.py`: checks a project's `brand.css` over the system in both modes.

### Changed
- Starter `brand.css` values are placeholders; four contrast pairs fixed.

## 0.2.0 (2026-10-23)

### Added
- App components: segmented control, switch, progress (default, warning, danger), skeleton,
  bottom sheet with scrim, section header. Contracts in `docs/component-contracts.md`, specimens in
  the generated docs page.
- Semantic token `surface.scrim` (dark in both modes) for dimming content behind sheets.
- 12 icons: eye-off, wallet, card, send, receive, plus, chart, bell, target, coffee, bag, bus.
- 7 contrast pairs for the new components and for signed amounts on raised surfaces
  (110 checks across both modes).
- `docs/platform-mapping.md`: how roles, type, shape and motion map to SwiftUI and Jetpack Compose.
- `examples/money-app/`: personal-finance reference with three task-led screens, a sheet,
  progress, skeleton and segmented filtering, reviewed in light and dark.

### Fixed
- Browser review requires all declared engines and axe-core; CI requires all three engines.
- Review reports transition from RUNNING to PASS/FAIL and retain failure diagnostics.
- Explicit reduced local reviews remain PARTIAL when engines or axe are missing.
- Browser gate regressions cover dependency, engine, partial-review and stale-report failures.
- The aggregate local checker continues after failures and exits nonzero, including failed pipelines.

## 0.1.0 (2026-10-22)

### Added
- DTCG 2025.10 token source in three layers: primitive (color, space, radius, border width, size,
  font, duration, easing, shadow), semantic (surface, text, border, action, feedback, type,
  spacing, shape, elevation, motion) and component (button, field, chip, card, tab bar, badge,
  focus ring). 250 tokens per mode, light and dark.
- `build.py`: CSS custom properties with alias-preserving `var()` chains, resolved JSON per mode,
  generated living style guide `docs/index.html`; `--check` for CI.
- `validate.py`: type-specific DTCG shape checks, alias resolution and cycle detection, mode parity,
  layering rules, 49 contrast pairs per mode, component CSS lint.
- Components: button (4 variants, 3 sizes, disabled, busy), icon button, field (input, select,
  hint, error), chip, badge, card, list, avatar, app bar, tab bar, banner, toast, empty state.
- Be Vietnam Pro (OFL 1.1) with Vietnamese unicode-range subset; original icon sprite.
- Component contracts and governance policy.
- Appointment app reference with recorded Chromium + axe-core review.
