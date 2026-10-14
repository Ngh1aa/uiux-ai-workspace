---
name: mobile-app-design
description: Routes research, UX, interface design, prototypes and handoff for native iOS/Android apps. Uses platform-specific rules after target truth; excludes responsive websites and does not implement or release app code.
---

# Mobile App Design

## Ownership
Owns the mobile design lifecycle and its work cards. Flow OS, runtime policy and target source remain canonical. Reuse discovery, research, brand, copy, auth and state skills; load only the active stage and relevant platform references.

## Intake
Identify the top task, domain, existing screens/components, target platforms, minimum OS, real stack and requested output. Unknown platforms/stack remain UNKNOWN; do not choose Expo, SwiftUI, Compose or Flutter by default. A mobile browser viewport is still web. Source metadata does not grant implementation, Figma mutation, paid services or release authority.

## Lifecycle
1. Research: audit the baseline, establish decisions and source provenance, and separate desk evidence from actual participant research.
2. Design: inventory screens/states before drawing; specify task paths, navigation, failure/recovery and platform differences. Reuse the target design system and compare meaningful alternatives only for unresolved decisions.
3. Review/handoff: inspect the prototype/design captures, record findings and current artifacts, then describe the implementation and native QA still required.

Use [professional practice](references/professional-practice.md) for the complete flow and [source registry](data/sources.json) when selecting guidance. Use [design contract](templates/mobile-design-contract.md) as a starting structure; merge with existing project artifacts rather than creating duplicate specs. Stage cards live in [lifecycle.json](data/lifecycle.json) and are transported by the shared delivery packet owner.

## Stage routing
- Navigation or lifecycle uncertainty: `mobile-navigation-and-state-ux`.
- iOS in scope: `ios-app-design`; Android in scope: `android-app-design`.
- Reusable visual/interaction decisions and engineering handoff: `mobile-design-system-and-handoff`.
- Prototype checks, accessibility review and evidence limits: `mobile-prototype-and-qa`.
- Auth, complex forms, localization or risky data: load the existing owner only when relevant.

## Completion boundary
This capability produces design artifacts. For a coded browser demo and client link, route `requested_output=browser-prototype` to [mobile-web-preview](../mobile-web-preview/SKILL.md); its evidence remains browser-only. It cannot satisfy a request to build/install a native app. Current mobile flows fail closed for native implementation requests. Design record integrity is not visual quality, user validation, runtime accessibility or store readiness. Keep missing checks NOT_RUN/UNKNOWN. Figma writes and production publication require their existing authorization boundaries.
