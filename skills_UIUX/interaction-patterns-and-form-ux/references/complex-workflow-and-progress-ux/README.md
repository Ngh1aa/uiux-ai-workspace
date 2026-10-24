# Complex Workflow & Progress UX

> Hướng dẫn con của skill `interaction-patterns-and-form-ux` (trước đây là skill `complex-workflow-and-progress-ux`). Dùng khi: Design long-running, multi-stage or interruptible workflows with ownership, progress, resumability and safe completion. Use for approvals, processing queues, applications, publishing flows or multi-actor enterprise tasks.

## Goal and scope

At any moment, anyone looking at a piece of work can answer four questions: what state is it in, who owns the next move, what is blocking it, and what happens if I leave now. Progress feedback is honest about what the system knows, interrupted work is recoverable where it matters, and nothing irreversible happens twice or by accident.

**When not to use**

- A single-session form split into steps (field design, validation, step navigation): use [complex-forms-and-wizards](../complex-forms-and-wizards.md). Come here when the work spans sessions, actors or background processing.
- Inline field errors, toasts and generic error recovery copy: use [state-feedback-and-error-recovery](../../../state-feedback-and-error-recovery/SKILL.md).
- Motion of spinners and progress indicators: use [motion-and-microinteractions](../../../motion-and-microinteractions/SKILL.md).
- AI agent tasks with model uncertainty and human oversight: use [human-ai-interaction-design](../../../human-ai-interaction-design/SKILL.md).
- End-to-end service mapping across channels and staff: use service-blueprinting.

## Decisions

**1. Model the workflow as states, not screens**
- Write a state machine: states, transitions, the actor allowed to trigger each transition, and which transitions are irreversible.
- Every state has exactly one current owner (a person, a role, or "System"). "Pending" with no owner is a design bug.
- Separate user progress (what the user has completed) from backend processing status (what the system is doing). Show them as distinct elements.
- Status labels use user language ("Waiting for finance approval"), not internal states ("PENDING_L2").

**2. Feedback by expected duration (Nielsen response-time limits)**
- About 0.1 s: feels instantaneous; no indicator, just the result.
- About 1 s: user notices delay but keeps flow; avoid spinners that flash, show a subtle busy state only if it lasts.
- About 10 s: attention limit; anything longer needs a progress indicator, an estimate or stage list, and the ability to do something else.
- Beyond that: move work to the background, let the user leave, and notify on completion (in-app, email or push as appropriate).
- Suppress indicators for very short waits to avoid flicker, and once shown, keep them visible long enough to read. Pick values with engineering; do not invent them in copy.

**3. Determinate vs indeterminate progress**
- Determinate (bar with percent or "3 of 7") only when the system can measure real progress: bytes, items, known steps.
- Indeterminate (spinner, looping bar) when duration is unknown, and only for short waits; for long unknown waits, show stage names and elapsed time instead of a spinner.
- Never fake a percentage. A bar that sits at 99% destroys trust faster than an honest "Processing, this usually takes a few minutes".
- For multi-stage jobs, show a stage list (done, current, upcoming) with per-stage status; partial completion is visible.

**4. Optimistic UI**
- Use optimistic updates when the action is very likely to succeed, cheap to roll back, and the result is local to the user (like, rename, reorder, mark as read).
- Do not use optimistic UI for payments, submissions to third parties, irreversible deletes or anything that triggers external side effects.
- On failure, revert visibly, explain, and keep the user's input so they can retry.

**5. Retry, idempotency and cancellation**
- Every submit that creates or charges must be idempotent: the client sends an idempotency key, double-clicks and network retries produce one result. Disable the button while in flight and show state.
- Automatic retry only for transient failures, with backoff; after that, show a manual "Retry" with the reason.
- Cancel means a defined thing: stop before side effects, or stop the remaining items and report what already completed. Say which in the confirmation.
- Partial completion is reported with counts and a path to the failed items, never as a generic "Something went wrong".

**6. Save, draft and resume**
- Autosave drafts for work that takes more than a few minutes or spans sessions; show "Saved" status with time.
- Resume returns the user to the exact step and scroll context with data intact; show what changed since they left if other actors acted.
- Expiring drafts or sessions warn before expiry and say what will be lost.
- Cross-device continuation requires server-side drafts; local storage alone is a per-device convenience.

**7. Confirmation strength matches consequence**
- Reversible, low impact: no confirmation; offer undo.
- Reversible, high impact: confirmation optional; undo window plus clear result summary.
- Irreversible or affects others: explicit confirmation naming the object and consequence; for severe cases, type-to-confirm.
- Multi-actor approvals: show who approves, in what order, with SLA or expected time if the business has one.

**8. Audit and multi-actor visibility**
- Activity history lists who did what, when, and with what comment, in user language.
- Notifications go to the new owner on every ownership change; the previous owner sees the hand-off.
- Rejected or returned items state the reason and the required fix, and go back to a named owner.

## Workflow

1. Map stages, actors, dependencies and irreversible actions as a state machine (Decision 1).
2. Separate user progress from backend processing status; choose feedback by expected duration and measurability (Decisions 2 and 3).
3. Show current state, owner, blocker and next action on every view of the work item.
4. Support draft, save and resume, and cross-session continuation where useful (Decision 6).
5. Handle background jobs, queues, cancellation, idempotent retries and partial completion (Decisions 4 and 5).
6. Design review, approval and audit history for multi-actor flows (Decisions 7 and 8).
7. Write status copy for every state and every failure, in user language.
8. Walk the unhappy paths: tab closed mid-submit, double click, network drop, approver on leave, job half done, session expiry.

Read [workflow states and progress reference](references/workflow-states-and-progress.md) when writing the state table, choosing a progress pattern, specifying retries, or when you need a worked example.
Before handoff run [workflow gate](checklists/workflow-gate.md).

**Anti-patterns**

- Fake percentage bars driven by a timer.
- "Processing..." spinner with no stage, no elapsed time and no way to leave for a multi-minute job.
- Status "Pending" with no owner and no expected next step.
- Submit button that stays enabled during the request, causing duplicate orders or charges.
- Optimistic "Sent!" for an email or payment that later fails silently.
- Cancel that leaves the system half-done with no report of what completed.
- Drafts stored only in local storage, presented as "saved" across devices.
- Rejection that returns an item with no reason and no assigned fixer.
- Internal state names in user-facing UI ("ERR_STATE_4", "QUEUED_RETRY").
- Modal confirmation for every trivial action, training users to click through the dangerous one.

**Output**

1. State table:

| State (user label) | Internal state | Owner | Entry trigger | Allowed transitions (actor) | Reversible? | User-visible status and next action | Notification |
|---|---|---|---|---|---|---|---|

2. Progress spec per long operation: expected duration band, determinate or indeterminate, stage list, background behavior, completion notification.
3. Failure and retry spec: idempotency, auto retry policy, manual retry, cancel semantics, partial completion report.
4. Draft and resume spec: autosave trigger, storage scope, expiry, resume target.
5. Confirmation matrix: action, reversibility, impact, pattern (none, undo, confirm, type-to-confirm).
6. Audit history fields.

## Quality gate

- PASS only if interrupted work can be recovered where business or user value warrants it, and the decision is documented per flow.
- PASS only if no stage leaves ownership ambiguous: every state in the table has one owner.
- PASS only if no percentage progress is shown when duration or amount is unknown.
- PASS only if status language is user meaningful; no internal state names are visible.
- PASS only if confirmation strength matches reversibility and consequence per the matrix.
- PASS only if create or charge actions are idempotent and the trigger is disabled while in flight.
- PASS only if operations expected to exceed about 10 s let the user leave and notify on completion.
- PASS only if partial completion reports counts and a route to failed items.

**Baseline / sources**

- Jakob Nielsen, response-time limits (0.1 s, 1 s, 10 s), from Usability Engineering and Nielsen Norman Group articles.
- IBM Carbon loading and progress indicator guidance; Material Design progress indicators; Atlassian progress tracker and flags.
- Idempotency keys as practiced in public payment APIs (for example Stripe API documentation); verify current guidance.
- WAI-ARIA: `progressbar` role, `aria-busy`, live regions for status messages; WCAG 4.1.3 Status Messages.
