---
name: mobile-app-design
description: Routes research, UX, interface design, prototypes and handoff for native iOS/Android apps. Uses platform-specific rules after target truth; excludes responsive websites and does not implement or release app code.
---

# Mobile App Design

## Ownership
Owns mobile design guidance. `START-HERE.md` and `WORKFLOWS.md` route the work; the target project's brief, source and design system govern implementation. Load only the active stage and relevant platform references.

## Intake
Identify the top task, domain, existing screens/components, target platforms, minimum OS, real stack and requested output. Unknown platforms/stack remain UNKNOWN; do not choose Expo, SwiftUI, Compose or Flutter by default. A mobile browser viewport is still web. Source metadata does not grant implementation, Figma mutation, paid services or release authority.

## Lifecycle
1. Research: audit the baseline, establish decisions and source provenance, and separate desk evidence from actual participant research.
2. Design: inventory screens/states before drawing; specify task paths, navigation, failure/recovery and platform differences. Reuse the target design system and compare meaningful alternatives only for unresolved decisions.
3. Review/handoff: inspect the prototype/design captures, record findings and current artifacts, then describe the implementation and native QA still required.

Use [professional practice](references/professional-practice.md) for the complete flow and [source registry](data/sources.json) when selecting guidance. Use [design contract](templates/mobile-design-contract.md) and [QA matrix](templates/mobile-qa-matrix.md) as starting structures; merge with existing project artifacts rather than creating duplicate specs.

## Pattern defaults
Use the [mobile patterns playbook](references/mobile-patterns-playbook.md) for structure, onboarding,
auth, permissions, lists, search, forms, feedback, empty states, notifications, settings and
platform divergence. Platform metrics: [iOS](../ios-app-design/references/ios-spec-sheet.md),
[Android](../android-app-design/references/android-spec-sheet.md).

## Stage routing
- UX before visual styling: use [mobile UX-first practice](../visual-design-direction/references/mobile-ux-first.md). Walk through representative tasks and recovery before selecting composition, typography or imagery.
- Visual direction and reference gaps: `visual-design-direction` + `design-reference-research-and-benchmark`; use app-specific page roles when website overview/conversion roles do not fit.
- Rendered visual acceptance: `ui-craft-and-visual-qa`; technical checks and design artifact existence never establish beauty.
- Navigation or lifecycle uncertainty: [`mobile-navigation-and-state-ux`](references/mobile-navigation-and-state-ux.md).
- iOS in scope: `ios-app-design`; Android in scope: `android-app-design`.
- Reusable visual/interaction decisions and engineering handoff: [`mobile-design-system-and-handoff`](references/mobile-design-system-and-handoff.md).
- Prototype checks, accessibility review and evidence limits: [`mobile-prototype-and-qa`](references/mobile-prototype-and-qa.md).
- Auth, complex forms, localization or risky data: load the existing owner only when relevant.

## Completion boundary
This skill produces design artifacts. For a coded browser demo, follow [mobile-web-preview](references/mobile-web-preview/README.md); its evidence remains browser-only. Building/installing a native app requires the target's actual toolchain and native checks. Design record integrity is not visual quality, user validation, runtime accessibility or store readiness. Keep missing checks NOT_RUN/UNKNOWN. Figma writes and production publication require authorization.

## Hướng dẫn con

Các skill trước đây tách riêng, nay gộp vào đây. Chỉ mở hướng dẫn con khi việc đang làm khớp cột bên phải.

| Hướng dẫn | Mở khi |
|---|---|
| [`mobile-navigation-and-state-ux`](references/mobile-navigation-and-state-ux.md) | Specifies mobile app navigation, screen/state inventory, interruptions, permissions, offline recovery and deep-link behavior. Applies when these native journeys affect design; reuses existing account, form and… |
| [`mobile-design-system-and-handoff`](references/mobile-design-system-and-handoff.md) | Maps an existing brand/design system into mobile semantic tokens, platform component variants and implementation handoff. Applies to iOS/Android app design; does not install component libraries or generate native… |
| [`mobile-prototype-and-qa`](references/mobile-prototype-and-qa.md) | Reviews mobile design/prototypes, accessibility annotations and native QA plans with explicit evidence limits. Applies before app design handoff or native verification planning; browser captures and mock prototypes… |
| [`mobile-web-preview`](references/mobile-web-preview/README.md) | Build and hand off an interactive browser prototype of an iOS/Android app for client review by link or QR. Reuse the target renderer, components and states, verify phone/desktop interactions and static hosting paths,… |
