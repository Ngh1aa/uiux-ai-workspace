---
name: android-app-design
description: Defines Android app design using Material 3, adaptive layouts, system insets, predictive back and accessibility. Applies to native Android design/handoff; excludes CSS responsive layout and automatic framework migration.
---

# Android App Design

## Decisions
Inspect target components, brand, minimum/target SDK and actual UI toolkit. Material 3 is a reference system, not an instruction to replace the existing product's brand or migrate Views to Compose.

- Select navigation destinations and back-stack behavior before designing app bars. Distinguish system Back from hierarchical Up; define predictive-back commit/cancel when relevant.
- Respect system bars, cutouts, gesture areas and IME insets. Verify edge-to-edge content and reachable actions with the keyboard open.
- Android recommends 48×48 **dp** touch targets. Use **sp**/supported text scaling for typography; do not copy CSS px or iOS pt numerically without a platform mapping.
- Use semantic Material roles and light/dark states. Dynamic color and Expressive patterns require an explicit brand/compatibility decision, not automatic adoption.
- Design from available window space and content requirements. Tablet, foldable and multi-window layouts may change navigation and pane structure; scaling a phone frame is insufficient.
- Specify TalkBack labels, values, actions, traversal and announcements. Identify focus behavior for keyboard/switch access where relevant.
- Request permissions at point of need; design denial, revocation, retry and fallback. Specify state restoration for interruption/process recreation when the task depends on it.

## Output
Produce Android navigation/insets/adaptive rules, component/state mapping and a supported SDK/device matrix. Consult [Android entries in the source registry](../mobile-app-design/data/sources.json). Choose the relevant `compose-samples` example or Now in Android module as a reference; do not copy an entire application architecture.

The native QA plan combines semantics checks and device interaction with screenshot review. Browser axe/Lighthouse results do not certify the app.
