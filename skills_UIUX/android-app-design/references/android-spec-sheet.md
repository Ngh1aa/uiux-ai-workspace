# Android / Material 3 spec sheet

Concrete defaults for native Android interfaces. Units: **dp** for layout, **sp** for text
(sp scales with the user's font setting). Values reflect Material Design 3 and Android developer
guidance as checked in 2026-10, including the **Material 3 Expressive** update (2025). Prefer
Material components in Jetpack Compose (`androidx.compose.material3`) over hand-built look-alikes.
Re-check <https://m3.material.io> and <https://developer.android.com/design/ui> for the target SDK.

## 1. Window size classes and layout

| Width class | Range (dp) | Typical device | Navigation | Margins | Panes |
|---|---|---|---|---|---|
| Compact | < 600 | Phone portrait | Navigation bar (bottom) | 16 | 1 |
| Medium | 600–839 | Foldable, small tablet portrait | Navigation rail | 24 | 1 (2 optional) |
| Expanded | 840–1199 | Tablet landscape, desktop window | Navigation rail or drawer | 24 | 2 (list–detail) |
| Large | 1200–1599 | Large tablet, desktop | Rail or permanent drawer | 24 | 2 |
| Extra-large | ≥ 1600 | Desktop, external display | Permanent drawer | 24 | 2–3 |

Design for **window size class, not device type** — apps run in split screen, freeform windows and
on foldables. Use canonical layouts: **list–detail**, **supporting pane**, **feed**.

Phone canvas for mockups: 412 × 917 dp (typical); also check 360 × 800 dp.

**Edge-to-edge is mandatory** for apps targeting SDK 35 (Android 15) and later: draw behind the status
and navigation bars, then pad content with window insets. Design the scrim/contrast for system bar
icons; never leave a solid coloured bar as a default.

## 2. Typography — Material 3 type scale

Default family: Roboto / Roboto Flex (or Google Sans Flex in Expressive). Map a brand family to the
same roles.

| Role | Size / Line height (sp) | Weight | Tracking (sp) |
|---|---|---|---|
| Display Large | 57 / 64 | 400 | −0.25 |
| Display Medium | 45 / 52 | 400 | 0 |
| Display Small | 36 / 44 | 400 | 0 |
| Headline Large | 32 / 40 | 400 | 0 |
| Headline Medium | 28 / 36 | 400 | 0 |
| Headline Small | 24 / 32 | 400 | 0 |
| Title Large | 22 / 28 | 400 | 0 |
| Title Medium | 16 / 24 | 500 | 0.15 |
| Title Small | 14 / 20 | 500 | 0.1 |
| Body Large | 16 / 24 | 400 | 0.5 |
| Body Medium | 14 / 20 | 400 | 0.25 |
| Body Small | 12 / 16 | 400 | 0.4 |
| Label Large | 14 / 20 | 500 | 0.1 |
| Label Medium | 12 / 16 | 500 | 0.5 |
| Label Small | 11 / 16 | 500 | 0.5 |

Expressive adds **emphasized** variants (heavier weight) for key moments; use them for hierarchy
peaks, not everywhere. Test at 200% font scale (Android 14+ uses non-linear scaling so large text
grows less than small text).

## 3. Colour — roles and dynamic colour

Material colour roles (generate from one seed with the Material theme builder):
`primary / onPrimary / primaryContainer / onPrimaryContainer`, same for `secondary`, `tertiary`,
`error`; surfaces `surface`, `surfaceDim`, `surfaceBright`, `surfaceContainerLowest … Highest`;
`onSurface`, `onSurfaceVariant`, `outline`, `outlineVariant`, `inverseSurface`.

- Support **dynamic colour** (wallpaper-based, Android 12+) where brand allows; otherwise ship a fixed
  brand scheme and keep the same roles.
- Elevation is expressed mostly by **surface container tone**, with shadows only on floating elements.
- Provide light, dark and (Android 14+) contrast-level variants.

## 4. Components and metrics

| Component | Size | Notes |
|---|---|---|
| Minimum touch target | 48 × 48 dp | Even if the icon is 24 dp |
| Top app bar — small / center | 64 dp | Medium flexible ~112 dp, large ~152 dp, collapse on scroll |
| Navigation bar (bottom) | 80 dp baseline; shorter "flexible" bar in Expressive (~64 dp) | 3–5 destinations, active indicator pill, labels shown |
| Navigation rail | 80–96 dp wide | Medium+ widths; optional FAB at top |
| Navigation drawer | up to 360 dp | Expanded+; modal on compact |
| FAB | 56 dp (small 40, large 96); Expressive adds medium 80 | One per screen, the primary constructive action |
| Extended FAB | 56 dp tall | Icon + verb label |
| Buttons | 40 dp height default (Expressive sizes XS 32 – XL 136) | Filled, tonal, elevated, outlined, text — one filled per region |
| Button groups / split buttons | Expressive | Replace ad-hoc segmented rows |
| Text field | 56 dp | Filled or outlined; label animates to top; supporting text below |
| List item | 56 (1 line), 72 (2 lines), 88 (3 lines) dp | 16 dp side padding |
| Chips | 32 dp | Assist, filter, input, suggestion |
| Bottom sheet | Drag handle 32 × 4 dp | Standard or modal; never hide primary actions behind a collapsed sheet |
| Snackbar | 48 dp min | Brief feedback with one optional action; above nav bar and FAB |
| Dialog | 280–560 dp wide, 28 dp radius | Title, supporting text, max two actions |

## 5. Shape scale

| Token | Radius (dp) | Example |
|---|---|---|
| None | 0 | Full-bleed media |
| Extra small | 4 | Snackbar, small menus |
| Small | 8 | Chips, text-field top corners |
| Medium | 12 | Cards |
| Large | 16 | Navigation drawer, FAB (large 28) |
| Large increased | 20 | Expressive |
| Extra large | 28 | Dialogs, bottom sheets (top corners) |
| Extra large increased / extra-extra large | 32 / 48 | Expressive hero surfaces |
| Full | 50% | Buttons, badges, active indicators |

Expressive introduces **shape morphing** (e.g. a pressed button shifts from round to squarer).
Use it on a few key interactions, not on every control.

## 6. Motion

Material 3 Expressive uses a **spring-based motion scheme** with spatial springs (position, size)
and effects springs (colour, opacity) in fast / default / slow speeds. Classic M3 easing for
non-spring cases:

| Token | Curve | Duration |
|---|---|---|
| Emphasized | `cubic-bezier(0.2, 0, 0, 1)` | 500 ms |
| Emphasized decelerate | `cubic-bezier(0.05, 0.7, 0.1, 1)` | 400 ms |
| Emphasized accelerate | `cubic-bezier(0.3, 0, 0.8, 0.15)` | 200 ms |
| Standard | `cubic-bezier(0.2, 0, 0, 1)` | 300 ms |
| Short (micro) | — | 50–200 ms |

Use container transform for list → detail, shared axis for sibling navigation, fade through for
unrelated destinations. Honour "Remove animations" (animator duration scale 0).

## 7. System behaviour

- **Predictive back**: system back gesture shows a preview of the destination. Support it (it is on
  by default for apps targeting recent SDKs); custom back handling must use the back callback APIs,
  never intercept the gesture visually.
- **Back vs Up**: system back follows history; the top app bar arrow goes up the hierarchy.
- **Permissions**: request in context, after explaining value; design the "Don't allow" and
  "Only this time" paths. Photo picker replaces broad storage access.
- **Notifications**: runtime permission (Android 13+); channels per category; every notification
  deep-links to the exact content.
- **Large screens and foldables**: hinge-aware layouts, no stretched phone UI on tablets.

## 8. Iconography

Material Symbols (outlined or rounded, consistently), 24 dp default, weight 400, optical size matched
to display size. Adaptive app icon 108 × 108 dp with a 72 dp safe zone; provide a monochrome layer
for themed icons.

## 9. Accessibility checklist (design time)

- TalkBack content descriptions for every meaningful icon; decorative ones marked as such.
- Logical focus order; merge row content into one focusable node with a clear label.
- Touch targets ≥ 48 dp; contrast per WCAG AA in light, dark and high-contrast schemes.
- Layouts survive 200% font scale and display size "largest".
- Don't depend on colour alone; provide text for state.

## 10. Handoff to Jetpack Compose

Specify: `MaterialTheme` colour roles and typography mapping, shapes, window-size-class behaviour,
navigation component per class, inset handling, state hoisting for each screen, semantics
(`contentDescription`, `stateDescription`, `heading`), and motion tokens. See the
[design-system platform mapping](../../../design-system/docs/platform-mapping.md).
