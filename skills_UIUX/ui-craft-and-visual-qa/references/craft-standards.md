# Craft standards — expert defaults with numbers

Use these values **when the target project has no design system for the decision at hand**.
A project's own tokens, brand guidelines and platform targets always win. Record each adopted
value as a starting default (source: this file) rather than as project truth, and verify it in
rendered output.

Platform specifics live in the [iOS spec sheet](../../ios-app-design/references/ios-spec-sheet.md),
[Android spec sheet](../../android-app-design/references/android-spec-sheet.md) and
[web app patterns](web-app-patterns.md). Checked against WCAG 2.2, Apple HIG and Material 3
documentation as of 2026-10; re-check when a platform ships a major design update.

---

## 1. Spacing and layout rhythm

**Base unit 4, rhythm unit 8.** Every margin, padding, gap and fixed size is a multiple of 4.

| Token | Value | Typical use |
|---|---|---|
| space-1 | 4 | Icon-to-label gap, tight badge padding |
| space-2 | 8 | Inline gaps, chip padding, related items |
| space-3 | 12 | Inside dense components, list row vertical padding |
| space-4 | 16 | Default component padding, mobile screen margin |
| space-5 | 20 | Card padding on larger phones |
| space-6 | 24 | Between groups inside a section, tablet margin |
| space-8 | 32 | Between sections on mobile |
| space-10 | 40 | |
| space-12 | 48 | Between sections on desktop |
| space-16 | 64 | Major section breaks, marketing pages |
| space-24 | 96 | Hero breathing room on large screens |

Rules that separate expert work from template work:

- **Proximity encodes structure.** Space *inside* a group must be visibly smaller than space
  *between* groups — at least a 1.5× step (e.g. 8 inside, 16 between; 16 inside, 32 between).
  If two adjacent levels use the same gap, the hierarchy is ambiguous: fix it.
- **Use at most 4–5 distinct gap values on one screen.** More reads as noise.
- **Optical alignment beats mathematical alignment** for icons, play glyphs, quotation marks
  and round shapes; nudge 1–2 px and note it.
- **Padding follows radius**: inner radius = outer radius − padding (nested corners stay concentric).
- Container padding on mobile: 16 (compact phones), 20 (large phones), 24 (tablet portrait).

## 2. Typography

### Scale

Pick one modular ratio and stay on it. Defaults:

| Context | Ratio | Body | Why |
|---|---|---|---|
| Product UI / app | 1.125–1.2 | 15–17 | Many levels, small steps, density |
| Marketing / editorial | 1.25–1.333 | 17–20 | Fewer levels, dramatic contrast |

Web product default ramp (px, line-height):

| Role | Size / LH | Weight | Tracking |
|---|---|---|---|
| Display | 48–64 / 1.05–1.1 | 600–700 | −1.5% to −2.5% |
| H1 | 32–40 / 1.15 | 600–700 | −1% to −2% |
| H2 | 24–28 / 1.25 | 600 | −0.5% to −1% |
| H3 | 20 / 1.3 | 600 | 0 |
| Body L | 17–18 / 1.55 | 400 | 0 |
| Body | 15–16 / 1.5 | 400 | 0 |
| Label / UI | 14 / 1.4 | 500 | 0 to +0.5% |
| Caption / meta | 12–13 / 1.4 | 400–500 | +0.5% to +1% |

Mobile native: use the platform text styles (iOS Dynamic Type, Material type scale) instead of
inventing a ramp. See the spec sheets.

### Rules

- **Measure**: body text 45–75 characters per line (aim ~66). Set `max-width: 65ch` on prose.
- **Line height falls as size rises**: 1.5–1.6 for body, 1.2–1.3 for headings, ~1.1 for display.
- **Large text needs negative tracking; small caps/labels need positive tracking.**
- **Two families maximum**, usually one. Hierarchy should come from size, weight and colour
  before a second typeface.
- **Weights**: use 2–3 (e.g. 400, 500/600, 700). Never fake bold.
- **Numbers**: tabular figures (`font-variant-numeric: tabular-nums`) in tables, timers, prices
  that update, and aligned columns.
- **Vietnamese and other stacked-diacritic scripts**: body line height ≥ 1.5, check glyphs such as
  "Ể Ỗ Ặ" at every size; avoid fonts with clipped or detached marks. Test real copy, which is often
  20–35% longer than English.
- **Minimum sizes**: body 16 px on web mobile (prevents iOS input zoom at < 16 px), 11 pt/sp absolute
  minimum anywhere, and only for non-essential meta.
- Avoid pure-weight hierarchy where size is identical and only weight differs between two adjacent
  levels unless colour also differs.

## 3. Colour

### Build the system as roles, not swatches

1. **Neutral ramp** (11–13 steps, e.g. 0, 50, 100…900, 950). Slightly tint neutrals toward the brand
   hue (chroma 0.005–0.02 in OKLCH) so surfaces feel designed, not default gray.
2. **One primary brand hue** with a full ramp; optionally one accent.
3. **Semantic hues**: success, warning, danger, info — each with surface, border, icon and text steps.
4. Generate ramps in **OKLCH** for perceptually even steps; store as sRGB hex (or Display-P3 with sRGB
   fallback).
5. Map to **semantic roles**: `surface/{base, raised, sunken, overlay}`, `text/{primary, secondary,
   tertiary, disabled, inverse, on-accent}`, `border/{subtle, default, strong, focus}`,
   `action/{primary, secondary, ghost, danger}` × `{bg, fg, hover, pressed, disabled}`.

### Proportion

Roughly **70–80% neutral surfaces, 15–25% secondary/structural, 5–10% brand/accent**. Brand colour
earns attention only when it is scarce. One filled primary action per view region.

### Contrast (WCAG 2.2 AA — hard floor)

| Pair | Minimum |
|---|---|
| Body text, < 18.66 px bold / < 24 px regular | 4.5 : 1 |
| Large text | 3 : 1 |
| UI component boundaries, icons that convey meaning, focus indicators | 3 : 1 against adjacent colours |
| Placeholder text that users must read | 4.5 : 1 (treat as text) |
| Disabled controls | Exempt, but keep them recognisable |

Practical targets: primary text ≥ 7:1 on base surface; secondary text ≥ 4.5:1; never put
secondary-grey text on a tinted surface without re-checking.

### Dark mode

- Not an inversion. Base surface around L* 8–12 (e.g. `#111214`–`#1A1B1E`), **not pure black**
  except OLED-specific modes.
- Express elevation with **lighter surfaces** (and optional tonal tint), not heavier shadows.
- Desaturate and lighten brand colours (reduce chroma ~10–20%) so they do not vibrate.
- Primary text ~ 90–95% white, not 100%; secondary ~ 65–70%.
- Re-check every contrast pair in both modes; parity of role names is mandatory.

### Never

- Status communicated by colour alone — always add icon, text or shape.
- Brand colour as large text background without a contrast check.
- More than one saturated hue competing in the same viewport for no role.

## 4. Shape, borders and elevation

**Radius scale**: 0, 4, 8, 12, 16, 24, full. Choose a personality and apply it consistently:

| Personality | Small controls | Cards | Sheets / modals |
|---|---|---|---|
| Precise / pro tools | 4–6 | 8 | 12 |
| Balanced / product | 8 | 12–16 | 16–24 |
| Friendly / consumer | 10–12 | 16–20 | 24–28 |

**Borders**: 1 px hairlines at low contrast (`border/subtle` ~ 1.2–1.5 : 1 against surface) separate
regions; 1.5–2 px for focus and selection. On high-DPI displays a 0.5 pt hairline is acceptable for
native separators.

**Elevation** (light mode), five levels max:

| Level | Use | Shadow (CSS) |
|---|---|---|
| 0 | Flat content | none |
| 1 | Cards, list containers | `0 1px 2px rgb(0 0 0 / .06), 0 1px 1px rgb(0 0 0 / .04)` |
| 2 | Raised / hover, sticky headers | `0 2px 6px rgb(0 0 0 / .08), 0 1px 2px rgb(0 0 0 / .06)` |
| 3 | Popovers, menus, dropdowns | `0 8px 24px rgb(0 0 0 / .12), 0 2px 6px rgb(0 0 0 / .08)` |
| 4 | Modals, sheets | `0 20px 48px rgb(0 0 0 / .18), 0 4px 12px rgb(0 0 0 / .10)` |

Shadows are always **two layers** (a tight contact shadow + a soft ambient one). Pick either border
*or* shadow as the primary separation device for a surface type; doubling both looks heavy.

## 5. Iconography

- One icon family, one stroke weight (1.5 or 2 px at 24 px), one corner style.
- Sizes: 16 (dense/inline), 20 (default UI), 24 (navigation, primary), 32+ (empty states, features).
- Icons align to text **cap height/x-height optically**, not to the line box.
- Pair icon + label in navigation. Icon-only buttons need an accessible name and a tooltip on
  pointer devices.
- Native apps: SF Symbols on iOS, Material Symbols on Android, unless the brand has a full set.

## 6. Grid and breakpoints (web)

| Name | Min width | Columns | Margin | Gutter | Max content |
|---|---|---|---|---|---|
| xs | 0 | 4 | 16 | 16 | — |
| sm | 600 | 8 | 24 | 16 | — |
| md | 840 | 12 | 32 | 24 | — |
| lg | 1200 | 12 | 40 | 24 | 1200–1280 |
| xl | 1600 | 12 | auto | 32 | 1440 |

Base breakpoints on **content**, then snap to this table. Long-form reading containers stay
640–720 px wide whatever the viewport. Use fluid type with `clamp()` between breakpoints for display
sizes only; keep body fixed.

## 7. Touch, pointer and focus

| Rule | Value |
|---|---|
| Minimum target, iOS | 44 × 44 pt |
| Minimum target, Android | 48 × 48 dp |
| Minimum target, web (WCAG 2.5.8 AA) | 24 × 24 CSS px, or spacing that keeps a 24 px circle clear; aim for 44 on touch |
| Spacing between adjacent targets | ≥ 8 |
| Focus indicator | ≥ 2 px, ≥ 3:1 contrast, never removed; not obscured by sticky UI (WCAG 2.4.11) |
| Thumb zone | Primary actions in the bottom half on phones; destructive actions not in the easiest-reach spot |

Visible glyph size and hit area are separate decisions: a 20 px icon can sit in a 44 px target.

## 8. Motion

| Token | Duration | Use |
|---|---|---|
| instant | 0–80 ms | Colour/opacity feedback on press |
| fast | 100–150 ms | Hover, toggles, small state changes |
| base | 200–250 ms | Expanding, dropdowns, tab content |
| slow | 300–400 ms | Sheets, modals, page transitions on mobile |
| deliberate | 400–600 ms | Large spatial moves, onboarding moments (rare) |

Easing:

| Name | Curve | Use |
|---|---|---|
| standard | `cubic-bezier(0.2, 0, 0, 1)` | Most on-screen movement |
| decelerate (enter) | `cubic-bezier(0.05, 0.7, 0.1, 1)` | Elements entering |
| accelerate (exit) | `cubic-bezier(0.3, 0, 0.8, 0.15)` | Elements leaving |
| linear | `linear` | Progress, opacity loops only |

Rules: exits are ~20–30% faster than entries; larger distance → longer duration; animate only
`transform` and `opacity` on the web; springs (native) for gesture-driven motion so velocity is
preserved; every animation has a `prefers-reduced-motion` / Reduce Motion alternative (cross-fade
or none). Motion must explain **where something came from or went**, confirm an action, or direct
attention — otherwise remove it.

## 9. State completeness

Every interactive component specifies:

| State | Visual rule |
|---|---|
| Default | — |
| Hover (pointer only) | Surface shift ~4–8% toward contrast, no layout movement |
| Pressed / active | Darker/lighter by a further step, or scale 0.97–0.98 on touch |
| Focus-visible | Ring per §7; distinct from hover |
| Selected / checked | Shape or icon change, not colour only |
| Disabled | ~40% opacity or dedicated tokens; keep label legible; explain why when possible |
| Loading | Keep size stable; spinner or progress inside; prevent double submit |
| Error | Icon + message adjacent to cause; border change ≥ 3:1 |

Every data-driven screen specifies: **first-use empty, no-results empty, loading (skeleton matching
final layout), partial data, error with recovery action, offline, permission-denied, very long
content, very large numbers, right-to-left or long translations when in scope.**

## 10. Content and data presentation

- Sentence case for UI labels and buttons. Buttons are verbs ("Save changes", "Đặt lịch").
- Truncate with intent: one line + ellipsis for titles in lists, full text on detail; never truncate
  numbers or prices.
- Format numbers for the locale (`1.234.567 ₫`, `$1,234.57`), align decimals in columns, use
  relative time for < 7 days and absolute dates beyond.
- Skeletons over spinners for content that takes > 300 ms; show nothing for < 100 ms to avoid flicker.

## 11. The polish pass (do this last, every time)

1. Squint test: does the eye land on the single most important thing first?
2. Count distinct gaps, font sizes, colours and radii on the screen; remove outliers.
3. Check every text block for widows, orphans and ragged 1-word last lines in headlines.
4. Check alignment edges: every element should share a left (or centre) edge with something.
5. Check optical balance of icons in buttons and circular containers.
6. Test with real, long and localised content; test with largest accessibility text size.
7. Check both themes and both pointer/touch states.
8. Remove one decorative element. If nothing is lost, keep it removed.
