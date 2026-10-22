---
name: state-feedback-and-error-recovery
description: Specify complete UI states and feedback so users understand system status and can recover from failure. Use for async interactions, forms, search, uploads, API-driven components and critical actions.
---

# State Feedback & Error Recovery

## Goal

At every moment the user can answer three questions: **what is happening, did my action work,
and what can I do now?** No state is a dead end; failure never costs the user their work.

## State inventory

Cover as relevant: default, hover, focus, active, disabled, loading, skeleton, first-use empty,
filtered empty, zero-result, success, warning, partial failure, offline, permission denied,
unavailable, timeout, retrying and canceled.

Start from the screen inventory produced by `ux-structure-and-flow-design` (U3) when it exists;
do not create a parallel list.

## Workflow

1. Inventory states for every critical component/flow.
2. For each state define: **trigger → visual change → message → next action**.
3. Preserve user work when failure occurs (form input, selections, drafts, scroll position).
4. Use progress feedback for long-running tasks.
5. Add retry, undo or cancel where appropriate.
6. Ensure status is perceivable without color alone (icon + text, announced to assistive tech).

## Feedback timing

| Wait | Pattern |
|---|---|
| < ~0.1 s | Immediate visual response on the control (pressed state) |
| ~0.1 to 1 s | Inline indicator on the control that was used; avoid full-screen blockers |
| ~1 to 10 s | Skeleton or progress with what is happening ("Checking available slots") |
| > ~10 s | Determinate progress when possible, allow leaving, notify on completion |

These are long-standing response-time heuristics, not hard thresholds; verify against the product's performance budget.

## Empty states (three kinds, three jobs)

| Kind | Job | Must include |
|---|---|---|
| First use | Explain value and get started | What will appear here + one primary action to create/add |
| No results (search/filter) | Help the query succeed | Echo the query/filters + one-tap clear + nearest alternatives |
| Cleared / done | Confirm a good outcome | Positive status + what happens next |

Never show a bare "No data".

## Error message anatomy

```text
What happened (plain words) + why, if known + what to do now + keep their input
"Payment didn't go through. Your card was declined by the bank. Your booking is held for 10 minutes. [Try another method]"
```

| Avoid | Prefer |
|---|---|
| "Error 500" / "Something went wrong" | Specific cause and next step |
| Blaming the user ("Invalid input") | Describe the fix ("Enter a phone number with 10 digits") |
| Clearing the form | Keep values, focus first error |
| Toast that disappears for a critical failure | Persistent inline message near the action |

## Choosing recovery

| Action type | Recovery pattern |
|---|---|
| Reversible, low stakes (archive, hide) | Do it immediately + Undo for several seconds |
| Irreversible or costly (delete account, pay) | Confirm with consequence stated, name the object |
| Network failure | Keep state, auto-retry with backoff where safe, manual retry visible |
| Conflict (slot taken, item sold out) | Explain, keep context, offer nearest alternative |
| Permission / auth expired | Re-auth and return to the same place with input intact |

Prefer undo over confirmation dialogs for frequent reversible actions; confirmation fatigue trains users to click through.

## Optimistic UI

Use only when success is very likely and rollback is clear. On failure, revert visibly and say why. Never optimistic for payments, submissions with legal effect or anything the user cannot easily verify.

## Accessibility

- Status changes announced (live region or platform equivalent), not only shown.
- Focus moves to the error summary or first invalid field after submit.
- Loading controls keep their label; spinners have accessible names.

## Quality gate

- No dead-end error or empty state.
- Asynchronous actions expose status within the timing table above.
- Recovery is at least as clear as the failure message.
- User input survives every failure path in the flow.
- Each error message states cause (if known) and next action.
