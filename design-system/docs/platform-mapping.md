# Platform mapping — CSS, SwiftUI, Jetpack Compose

How the semantic tokens in this system translate to native platforms. The source of truth stays
`tokens/` (DTCG). `generated/tokens.json` holds fully resolved values per mode for native build
scripts and design-tool plugins.

**Principle:** share *meaning* (roles, scale steps, states) across platforms; let each platform keep
its own chrome, text-scaling system and controls. Do not force identical pixels.

## 1. Units

| Source | Web | iOS | Android |
|---|---|---|---|
| `space.*`, `radius.*`, `size.*` (px) | px / rem | pt (same number) | dp (same number) |
| `font.size.*` (rem) | rem | pt via text style mapping (§3) | sp via type role mapping (§3) |
| `duration.*` | ms | seconds (`0.2`) | ms (`200`) |
| `easing.*` cubic-bezier | CSS | `Animation.timingCurve(x1, y1, x2, y2, duration:)` | `CubicBezierEasing(x1, y1, x2, y2)` |

1 CSS px at 1× ≈ 1 pt ≈ 1 dp, so numeric values carry over. Text is the exception: use the
platform's scalable text system, not fixed numbers.

## 2. Colour roles

Export each colour role to **asset-catalogue colour sets** (iOS, light + dark appearances) and a
**Compose `ColorScheme`** plus custom extension (Android). Keep role names identical so design QA can
compare across platforms.

| Token role | SwiftUI | Compose (Material 3) |
|---|---|---|
| `surface.page` | `Color("surface/page")` → background | `colorScheme.background` / `surface` |
| `surface.raised` | `Color("surface/raised")` | `surfaceContainerLow` |
| `surface.sunken` | `Color("surface/sunken")` | `surfaceContainerHighest` |
| `surface.brand-subtle` | `Color("surface/brandSubtle")` | `primaryContainer` |
| `surface.brand-strong` | `Color("surface/brandStrong")` | `primary` |
| `surface.inverse` | `Color("surface/inverse")` | `inverseSurface` |
| `text.primary` | `Color("text/primary")` (or `.primary`) | `onSurface` |
| `text.secondary` | `Color("text/secondary")` (or `.secondary`) | `onSurfaceVariant` |
| `text.brand` | `.tint` | `primary` |
| `text.on-brand-strong` | `Color("text/onBrandStrong")` | `onPrimary` |
| `border.subtle` / `border.control` | `Color("border/…")` / `.separator` | `outlineVariant` / `outline` |
| `border.focus` | system focus ring (keep) | `primary` focus indicator |
| `action.primary.bg` / `.text` | `.tint` + `.borderedProminent` | `primary` / `onPrimary` (Filled button) |
| `action.secondary.*` | `.bordered` | `secondaryContainer` / Tonal button |
| `action.danger.*` | `role: .destructive` | `error` / `onError` |
| `feedback.{success,warning,danger,info}.*` | `Color("feedback/…")` | custom `ExtendedColors` via `CompositionLocal` |

Generate both platforms from `generated/tokens.json` in CI rather than copying hex values by hand.

## 3. Typography roles

Map **roles**, not sizes. Native text then scales with Dynamic Type / font scale.

| Token role | Web size | iOS text style (relativeTo) | Material 3 role |
|---|---|---|---|
| `type.display` | 32 | `.largeTitle` (bold) | Headline Large / Display Small |
| `type.title-lg` | 24 | `.title2` | Headline Small |
| `type.title-md` | 20 | `.title3` | Title Large |
| `type.title-sm` | 17 | `.headline` | Title Medium |
| `type.body-lg` | 17 | `.body` | Body Large |
| `type.body-md` | 15 | `.subheadline` | Body Medium |
| `type.body-sm` | 14 | `.footnote` | Body Small |
| `type.label-lg` | 15 | `.callout` (semibold) | Label Large |
| `type.label-md` | 14 | `.subheadline` (medium) | Label Medium |
| `type.label-sm` | 12 | `.caption` (medium) | Label Small |

Web sizes are the resolved values in `generated/tokens.json`; native sizes follow the platform style at its default text size.

SwiftUI with the brand typeface while keeping Dynamic Type:

```swift
extension Font {
    static let dsTitleLg = Font.custom("BeVietnamPro-Bold", size: 24, relativeTo: .title2)
    static let dsBodyMd  = Font.custom("BeVietnamPro-Regular", size: 15, relativeTo: .subheadline)
}
```

Compose:

```kotlin
val BeVietnam = FontFamily(Font(R.font.be_vietnam_pro_regular), Font(R.font.be_vietnam_pro_bold, FontWeight.Bold))
val DsTypography = Typography(
    headlineSmall = TextStyle(fontFamily = BeVietnam, fontWeight = FontWeight.Bold, fontSize = 24.sp, lineHeight = 30.sp),
    bodyMedium    = TextStyle(fontFamily = BeVietnam, fontSize = 15.sp, lineHeight = 24.sp),
)
```

Be Vietnam Pro is licensed under SIL OFL 1.1 and may be bundled in apps; keep the licence file.

## 4. Shape, elevation, motion

| Token | SwiftUI | Compose |
|---|---|---|
| `shape.control` | `RoundedRectangle(cornerRadius: …, style: .continuous)` | `Shapes.small` / `medium` |
| `shape.card` | continuous corner radius | `Shapes.medium` / `large` |
| `shape.sheet` | system sheet radius (do not override) | `Shapes.extraLarge` (top corners) |
| `elevation.raised` | subtle shadow or material; prefer grouping | `surfaceContainerLow` tone, 1 dp shadow |
| `elevation.overlay` | system sheet/popover | Tonal + shadow level 3 |
| `duration.*` + `easing.*` | `withAnimation(.timingCurve(…))`; springs for gestures | `tween(duration, easing)`; spring specs for gestures |

Always use **continuous** corners on iOS. Always provide a Reduce Motion / animator-scale-0 path.

## 5. Components

| System component | iOS native counterpart | Android native counterpart |
|---|---|---|
| `ds-button--primary/secondary/tertiary/danger` | `Button` + `.borderedProminent` / `.bordered` / `.plain` / destructive role | Filled / Tonal / Text / error-coloured Filled button |
| `ds-field` | `TextField` with `.textContentType` | `OutlinedTextField` / `TextField` |
| `ds-chip` | Custom capsule or `Toggle` with `.button` style | `FilterChip` / `AssistChip` |
| `ds-tab-bar` | `TabView` (system tab bar) | `NavigationBar` |
| `ds-card` | Inset grouped `List` section or custom view | `Card` / `ElevatedCard` |
| `ds-badge` (status) | Label with SF Symbol + text | `AssistChip` / custom with icon + text |
| `ds-banner` | Inline view; avoid alerts for non-blocking info | Inline card or `Snackbar` for transient |

Prefer the native control and apply tokens to it; build custom only when no native control fits.

## 6. Handoff checklist

- Role names identical across CSS, asset catalogue and Compose theme.
- Light and dark values exported from `generated/tokens.json` by script.
- Each text role mapped to a scalable platform style.
- Touch targets meet 44 pt / 48 dp, regardless of visual size.
- States (pressed, disabled, focus, selected, error, loading) specified per component.
- Platform differences documented (navigation, back, sheets, feedback), not hidden.
