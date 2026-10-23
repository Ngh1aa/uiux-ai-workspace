# iOS / iPadOS spec sheet

Concrete defaults for designing native iPhone and iPad interfaces. Units are **points (pt)**;
1 pt = 2 px on @2x and 3 px on @3x screens. Values reflect Apple's Human Interface Guidelines as
checked in 2026-10 (Liquid Glass design language introduced in iOS 26 and refined afterwards).
Always prefer **system components and safe-area APIs** over hard-coded sizes: they adapt to device,
OS version and accessibility settings automatically. Re-check
<https://developer.apple.com/design/human-interface-guidelines/> for the deployment target.

## 1. Canvas and safe areas

| Item | Value | Note |
|---|---|---|
| Design canvas | 393 × 852 pt (iPhone 15/16/17 class) | Also check 375 × 667 (SE) and 440 × 956 (Pro Max class) |
| Status bar / Dynamic Island area | ~54–62 pt top inset | Never hard-code; use safe area |
| Home indicator inset | 34 pt bottom on Face ID devices | Content may scroll under it; controls may not |
| Screen margin (layout margins) | 16 pt compact, 20 pt on larger phones | iPad uses readable content width for text |
| Readable text width (iPad) | ~ 672 pt max | Use readable content guide |

## 2. Typography — Dynamic Type (default "Large" size)

Font: **SF Pro** (system). Optical sizes switch automatically; do not set SF Pro Display/Text manually
in code. Use text **styles**, not fixed sizes, so text scales from xSmall to AX5 (≈ 310%).

| Style | Size / Leading (pt) | Weight |
|---|---|---|
| Large Title | 34 / 41 | Regular (Bold for nav large titles) |
| Title 1 | 28 / 34 | Regular |
| Title 2 | 22 / 28 | Regular |
| Title 3 | 20 / 25 | Regular |
| Headline | 17 / 22 | Semibold |
| Body | 17 / 22 | Regular |
| Callout | 16 / 21 | Regular |
| Subheadline | 15 / 20 | Regular |
| Footnote | 13 / 18 | Regular |
| Caption 1 | 12 / 16 | Regular |
| Caption 2 | 11 / 13 | Regular |

Emphasis comes from weight variants of the same style (e.g. Body Semibold), not new sizes.
Design every key screen at **Large** and **AX3** at minimum; at accessibility sizes, horizontal
layouts should stack vertically and truncation should give way to wrapping.

A custom brand typeface is fine; map it to the same styles with `UIFontMetrics` / `relativeTo:` so it
still scales.

## 3. Navigation chrome

| Component | Height | Rules |
|---|---|---|
| Navigation bar (inline title) | 44 pt + status inset | Back button keeps the previous title or "Back"; one primary action on the trailing side |
| Navigation bar (large title) | ~ 96 pt + status inset, collapses to 44 on scroll | Use on top-level screens of content apps; not on modal tasks |
| Tab bar | 49 pt + home indicator inset (system floating style in Liquid Glass) | 3–5 tabs, icon + short label, never hide on push for primary flows, never use for actions |
| Toolbar | 44 pt + home indicator inset | Contextual actions for the current screen |
| Search | System search field in the navigation bar or tab bar search role | Show recent and suggested searches |

Liquid Glass guidance: system bars and controls float in a translucent **control layer** above the
content layer. Let content scroll beneath bars; do **not** paint custom glass, blur or tinted panels
on the content layer to imitate it, and do not stack glass on glass. Respect **Reduce Transparency**
and **Increase Contrast**, which turn glass more opaque.

## 4. Presentation and modality

| Pattern | Use for | Rules |
|---|---|---|
| Push (navigation stack) | Hierarchical drill-down | Edge-swipe back must always work; never block it with a custom gesture |
| Sheet (`.medium` / `.large` detents) | Focused sub-task, quick create, filters | Show grabber when resizable; swipe-down dismiss; if there are unsaved edits, confirm before discarding |
| Full-screen cover | Immersive or multi-step task that must not be dismissed accidentally | Explicit Cancel / Done |
| Popover (iPad) | Contextual options from a control | Becomes a sheet on iPhone |
| Alert | Critical info or a destructive confirmation needing a decision | Max 2–3 buttons; destructive styled red; title states the consequence |
| Action sheet / menu | Choice among actions tied to an element | Cancel always available |
| Context menu (long press) | Secondary actions and preview | Never the only path to an action |

Modal tasks use **Cancel** (leading) and **Done/Save** (trailing, bold). Avoid modals over modals.

## 5. Controls and metrics

| Control | Default | Notes |
|---|---|---|
| Minimum hit target | 44 × 44 pt | Visual glyph may be smaller |
| List row (cell) | 44 pt minimum; 60–76 pt with subtitle or thumbnail | Use system list styles (inset grouped is the settings default) |
| Grouped list corner radius | system (≈ 10–12 pt; larger under Liquid Glass) | Don't override per screen |
| Button (prominent, large) | 50 pt tall full-width common for primary CTA | Use `.borderedProminent`, `.bordered`, `.plain` styles |
| Switch | System toggle | Label left, toggle right; applies immediately (no Save) |
| Segmented control | 2–5 segments, ~32 pt | For switching views of the same content, not navigation |
| Text field | ≥ 44 pt | Correct keyboard type, content type (autofill), return key label |
| Steppers, pickers, date pickers | System | Prefer inline or compact date picker over custom wheels |

## 6. Iconography and imagery

- **SF Symbols** for UI icons; match the symbol weight to adjacent text weight and use the
  same scale (small/medium/large). Use hierarchical or palette rendering for depth, not random colours.
- App icon: 1024 × 1024 master; provide light, dark and tinted appearances (iOS 18+) and layered
  artwork for the Liquid Glass icon treatment (Icon Composer). No text in icons, no screenshots.
- Images: deliver @2x and @3x or vector (PDF/SVG asset catalogue).

## 7. Colour and materials

- Use **semantic system colours** (`label`, `secondaryLabel`, `systemBackground`,
  `secondarySystemBackground`, `separator`, `tint`) or map your tokens to them, so Dark Mode and
  Increase Contrast work.
- One app **tint** (accent) colour for interactive elements. Don't colour non-interactive text with it.
- Destructive actions use system red; success uses system green with an icon.

## 8. Feedback

| Moment | Haptic |
|---|---|
| Selection changes (picker, segmented) | selection |
| Toggle / snap / drop | impact light or medium |
| Task success / warning / failure | notification success / warning / error |

Use haptics sparingly and always together with a visual change. Respect the system haptics setting.

## 9. Gestures — never break these

Edge swipe back · swipe down to dismiss sheet · pull to refresh on lists · swipe actions on rows
(trailing destructive, leading positive) · long press for context menu · pinch/zoom on media and maps.
Custom gestures are only accelerators; there must always be a visible control too.

## 10. Accessibility checklist (design time)

- Every control has a VoiceOver label (what), trait (button, header, selected) and value.
- Logical reading order; group related elements (a card reads as one sentence).
- Dynamic Type at AX sizes reflows; nothing essential truncates.
- Contrast ≥ 4.5:1 (text), ≥ 3:1 (glyphs and controls), in light and dark.
- Reduce Motion: replace slides/zooms with cross-fades. Reduce Transparency: opaque surfaces.
- Don't rely on colour, position or gesture alone.

## 11. Handoff to SwiftUI

Specify: screen → `NavigationStack` / `TabView` structure, sheet detents, text styles, semantic colour
roles, SF Symbol names and rendering mode, spacing tokens, haptics, accessibility labels, and states.
See the [design-system platform mapping](../../../design-system/docs/platform-mapping.md).
