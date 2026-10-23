# Changelog

Semantic versioning on the public surface (token paths, class names, state attributes, contracts).
See [docs/governance.md](docs/governance.md).

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
