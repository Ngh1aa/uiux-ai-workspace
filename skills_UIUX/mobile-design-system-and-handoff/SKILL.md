---
name: mobile-design-system-and-handoff
description: Maps an existing brand/design system into mobile semantic tokens, platform component variants and implementation handoff. Applies to iOS/Android app design; does not install component libraries or generate native code automatically.
---

# Mobile Design System and Handoff

## Reuse and map
Audit existing tokens/components before creating new foundations. Share semantic intent across platforms; document platform-specific typography, elevation/materials, hit areas, navigation and controls. Do not require identical chrome or blindly equate pt, dp, sp and CSS px.

Use the existing `design-system-and-components` owner for common foundations. When using Figma, record actual Variables/styles/components/instances and prototype links separately from screenshots or imported HTML. Preserve original work. Any design-tool write follows the calling task's authority.

## Component contract
For each changed component record purpose, anatomy, variants, content limits, states, accessibility semantics, interactions and platform mapping. Cover selected, pressed, disabled, loading and error when applicable; hover is conditional on pointer support.

## Token mapping
Map semantic tokens to SwiftUI, Compose and CSS with the
[design-system platform mapping](../../design-system/docs/platform-mapping.md).

## Stack-specific handoff
- SwiftUI: map to native controls, semantic text/colors, state ownership and availability/fallback notes; consult Apple APIs plus the pinned community reference.
- Compose: map to MaterialTheme roles, composables, hoisted state, semantics and window/insets behavior.
- Expo/RN: inspect SDK/dependency compatibility; consult pinned Expo references for Router, native UI, data and animation. Restyle/Paper are candidates only when they fit the target.
- Flutter: follow target architecture and adapt Material/Cupertino behavior intentionally. Official samples have per-asset license exceptions.

Sources, pins and license limitations are in [the registry](../mobile-app-design/data/sources.json). These are reference adapters; no upstream skill is automatically installed or granted command authority.

## Delivery
Use [handoff checklist](../mobile-app-design/checklists/design-handoff.md). Provide screen/state coverage, component/token owner, API/data reality, assets/license inventory, OS constraints, prototype entry tasks, known gaps and native verification plan. Token format or file coverage is not proof of visual quality. Store submission and paid/cloud services remain separate tasks.
