# Mobile Design Contract

## Project truth
- Source/design revision, baseline and preserved brand/components:
- Problem, audience, context and top task:
- Target platforms, OS/device range and stack (UNKNOWN where absent):
- Requested output, authority, decision owner and excluded work:
- Real/static/mock/simulated data and integration boundaries:

## Screen/state inventory
| Screen ID | Task / entry | Platform | State | Action → destination | Component owner | Verification |
|---|---|---|---|---|---|---|

Link one canonical state/render owner; do not clone every screen. Record loading/content/empty/error and consequential action recovery. Add permissions, offline, session expiry, deep links and interruptions only when relevant.

## Navigation and behavior
- Top-level destinations, detail stacks, sheets and modal ownership:
- Back/Up/dismiss/cancel, unsaved drafts and state restoration:
- Keyboard, safe areas/insets, gestures and reachable CTA:
- Entry via deep link/notification and auth/entity/error conditions:

## Platform/system mapping
| Semantic purpose | Shared brand/state | iOS behavior/control | Android behavior/control | Availability/fallback |
|---|---|---|---|---|

Specify text scaling, light/dark, touch-area units, reduced motion, reading order and assistive-technology semantics. Record actual Figma Variables/styles/component instances separately from imported/static frames when applicable.

## Source-to-decision trace
| Source ID + revision | Observation | Interpretation | ADOPT/ADAPT/REJECT + reason | Screen/state/component | Verification |
|---|---|---|---|---|---|

## Prototype/review
- Task preconditions, actions, expected outcomes and failure/recovery:
- Capture/design revision, conditions and observed findings:
- Actual participant evidence or PLANNED_VALIDATION/UNKNOWN:

## Handoff
- Component/token, content, data/API and asset/license owners:
- Platform differences, constraints, known issues and next owner:
- Design review status; native build/runtime, accessibility, performance and store release remain NOT_RUN/UNKNOWN without their own evidence:
