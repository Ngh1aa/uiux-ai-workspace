---
name: mobile-prototype-and-qa
description: Reviews mobile design/prototypes, accessibility annotations and native QA plans with explicit evidence limits. Applies before app design handoff or native verification planning; browser captures and mock prototypes cannot prove a native runtime passed.
---

# Mobile Prototype and QA

## Select evidence for the claim
Choose the smallest meaningful matrix from platform scope, critical tasks and risk. Inspect actual design/prototype captures for hierarchy, typography, density, clipping, long/localized content, keyboard assumptions and state consistency. Record observations and issue severity, not an aesthetic score inferred from file existence.

Review primary tasks and failure/recovery. Large text, dark appearance, reduced motion and assistive technology require annotated behavior; a static prototype cannot prove runtime compliance. Without real participants, label expert scenarios separately and keep user validation UNKNOWN.

For a coded browser prototype, use [mobile-web-preview](../mobile-web-preview/SKILL.md) and the existing browser/state QA owners. Test tasks, recovery and hosted subpaths; record browser observations separately from the native plan below.

## Native verification plan
Bind planned checks to source SHA, app/build identity, OS/device, locale, theme, text scale, scenario, expected outcome and artifact/capture hash. Current design flows do not install a native runner or emit trusted native evidence.

- E2E: consider Maestro for supported targets; its iOS simulator support is not physical-iPhone coverage. Appium/Detox are conditional alternatives, not additional default dependencies.
- iOS: XCTest/XCUIAutomation, applicable accessibility audits, VoiceOver review and current snapshots.
- Android: Compose semantics/accessibility checks, TalkBack, insets/back/permission scenarios and screenshot tests.
- Performance/device capabilities: use an appropriate build/device and declared budget. A simulator screenshot does not verify camera, biometrics, battery or production performance.

Use [QA matrix](../mobile-app-design/templates/mobile-qa-matrix.md) and [QA sources/license records](../mobile-app-design/data/sources.json). Verify tool/SDK support before implementation. Windows cannot host Apple's local iOS Simulator; plan macOS, a suitable cloud runner or real-device access.

## Completion
Keep design review, record integrity, native runtime, direct-user validation and store release distinct. Use PASS/FAIL/NOT_RUN/UNKNOWN with evidence specific to the claim. Browser Playwright/axe/Lighthouse PASS never satisfies native runtime verification. Do not refresh baselines merely to hide a visual regression.
