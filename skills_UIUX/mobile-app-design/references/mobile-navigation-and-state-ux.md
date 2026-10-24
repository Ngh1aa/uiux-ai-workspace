# Mobile Navigation and State UX

> Hướng dẫn con của skill `mobile-app-design` (trước đây là skill `mobile-navigation-and-state-ux`). Dùng khi: Specifies mobile app navigation, screen/state inventory, interruptions, permissions, offline recovery and deep-link behavior. Applies when these native journeys affect design; reuses existing account, form and error-state owners.

## Inventory first
Build one inventory from existing screen/state/render owners. Record screen ID, task, entry, platform, state, actions, next destination and verification. Do not make disconnected screen copies for each state.

## Navigation contract
- Define top-level destinations and stacks; preserve tab/task context on return.
- Specify push, modal, sheet, system back, cancel and dismiss semantics. Confirm destructive exits only when unsaved or consequential work warrants it.
- Treat deep links and notification entry as alternate task starts: auth-required, entity-missing, expired and app-already-open paths need explicit handling.
- Keep navigation history separate from data state. A dismissed view does not necessarily discard a draft.

## State matrix
For data-backed tasks cover loading, content, empty, error and retry; add pending save, failure and conflict when data is editable. Offline, session expiry, permission denial/revocation, background/resume and process restoration are conditional on actual features, not mandatory screens for every app.

Decide which data is local, cached, remote, queued or simulated. State what happens when connectivity returns and how duplicate actions/conflicts are prevented. Reuse `state-feedback-and-error-recovery`, `authentication-account-and-recovery-ux` and form skills for their own decisions.

Presentation fallbacks must not invent a domain fact. For example, a pending appointment must not inherit a named doctor from a decorative default; an unpaid receipt must not become paid because its card looks complete. Put synthetic named facts in labelled fixtures, read facts from the canonical state, and render unknown/unassigned values explicitly. Test the same fact in list, detail, confirmation and notification entry.

## Output and verification
Deliver a navigation graph, transition/state table and critical task scenarios with preconditions, action, expected outcome and evidence owner. Test one recovery path for each consequential action. Generic success toasts and empty handlers do not implement the task.

Use [design contract](../templates/mobile-design-contract.md) and [platform source entries](../data/sources.json). Mark synthetic scenarios explicitly; they are not participants or observed user preference.
