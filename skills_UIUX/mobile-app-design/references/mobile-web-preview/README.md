# Mobile Web Preview

> Hướng dẫn con của skill `mobile-app-design` (trước đây là skill `mobile-web-preview`). Dùng khi: Build and hand off an interactive browser prototype of an iOS/Android app for client review by link or QR. Reuse the target renderer, components and states, verify phone/desktop interactions and static hosting paths, and distinguish prepared assets from an authorized verified deployment. Does not build native apps.

## Scope and owners

Use this guide when the requested output is an interactive browser presentation of an app.
Follow `START-HERE.md` and `WORKFLOWS.md` for task sizing and checks. Design-only work stays on
`mobile-app-design`; native application requests need the target's native toolchain and tests.
Keep browser evidence, native evidence and publication authorization separate.

## Design and implementation

Inspect the target before choosing a stack. Reuse its tokens, components, renderer, data fixtures and navigation/state model. Keep preview code in the target app project; this repository provides guidance, not a shared runtime for every client's demo. For Expo with web-compatible components, adapt the existing web export after checking the installed SDK. For SwiftUI/Compose or unsupported native components, implement a browser presentation from the approved design contract and label platform simulations. Do not claim it is shared native code.

Inventory screens, states and transitions first. One screen should render relevant states from shared data, not become many unrelated HTML copies. Make representative states addressable through the project's route/query/hash convention. Preserve browser Back, reload, dismiss, error recovery and an explicit demo reset. Use local labelled fixtures when no real backend exists; no real credential, payment or destructive action should be represented as completed by a mock interaction.

On a phone, show the usable app viewport; on desktop, a centered phone-sized presentation can aid review. Account for safe areas, long content, keyboard/focus behavior, zoom and narrow widths. Keep reviewer controls outside the product flow. Camera, push, biometrics and haptics remain simulated or NOT_RUN until native evidence exists.

## Browser QA and delivery

Reuse existing target tests and browser tooling (Playwright, axe) for state/focus checks. Verify primary tasks and relevant recovery, direct state URLs, reload/Back, small phones, desktop frame, assets and console/network errors. Serve the built output under the intended project subpath, not just `/`; GitHub Pages does not supply arbitrary SPA route rewrites or a backend.

Turn explicit UX thresholds into a criterion/evidence matrix. Separate implemented behavior, automated checks, inspected images, native/assistive-technology checks and real participant outcomes. A route count or green build cannot substitute any missing category. Retain exact failures and retest results. Check browser automation capabilities before claiming offline reload or native permission coverage; an unsupported runner is NOT_RUN, not a successful product check. Measure load/interaction under declared network, CPU and cache conditions; local transition timing is not field INP. Inspect rendered states even when automated accessibility reports no violations.

Keep failing requested performance profiles in the handoff. Isolate network/CPU variables to diagnose them, but do not replace a failed stricter profile with an easier passing one. A reviewable prototype can be delivered with open criteria; it must not be labelled QA-accepted or production-ready while applicable requested budgets fail or required evidence is missing.

Use [browser handoff](templates/client-handoff.md) to record exact source SHA, build output, captures/findings, runtime limits and reset instructions. Use the [hosting guide](references/hosting-and-verification.md) only when selecting/exporting/publishing a preview. The [Pages workflow asset](assets/github-pages.yml) is an opt-in target-project starting point, not an active deployment workflow of this repository.

`branch_write` can prepare code/assets; it cannot publish. Release/publication uses existing explicit authorization and the canonical release owner, not delegated QA/provider authority. Existing authorization in the session applies; do not ask again just because this skill is loaded. When publication is outside scope, hand off PREPARED assets and identify the pending URL. When a client link is requested and authorized, continue through publication and live verification. Do not call a PREPARED package a delivered live demo.

Only record DEPLOYED_VERIFIED after the existing deployment-truth checker agrees with independently retrieved provider deployment SHA/status and a live route probe; also retest the critical interaction on that URL. A URL, green workflow or QR alone proves neither deployment provenance nor behavior. Generate QR from the confirmed URL with the target's available tool; do not add an external QR service by default.

## Completion

Report browser prototype, hosted demo, native app, real backend and user validation separately. Browser PASS cannot satisfy native QA. Source assets and a routing manifest are preparation, not evidence that a client's app has been generated, reviewed or deployed.
