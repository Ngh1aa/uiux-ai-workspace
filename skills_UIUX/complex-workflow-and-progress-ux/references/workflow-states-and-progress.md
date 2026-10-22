# Workflow States and Progress Reference

Read this when writing the state table, choosing a progress pattern for a specific operation, specifying retry and cancel behavior, or when you need a worked example.

## Progress pattern picker

| Expected wait | Can progress be measured? | Pattern | User can leave? |
|---|---|---|---|
| Near instant | n/a | No indicator; show result | n/a |
| Around 1 s | n/a | Inline busy state on the trigger (button label change, disabled) after a short delay to avoid flicker | No need |
| Several seconds | No | Indeterminate indicator with a status label ("Checking availability") | Optional |
| Several seconds | Yes | Determinate bar or "12 of 40 files" | Optional |
| Beyond about 10 s | No | Stage list with current stage, elapsed time, "We will notify you" | Yes, required |
| Beyond about 10 s | Yes | Determinate with remaining count, plus background mode | Yes, required |
| Minutes to days (human steps) | Steps known | Stage tracker with owner per stage and expected timing if the business commits to one | Yes, it is a workflow |

Notes:
- The thresholds are Nielsen's response-time limits. Exact delays before showing a spinner and minimum display time are product decisions; agree them with engineering.
- Use `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax` for determinate bars; omit `aria-valuenow` for indeterminate. Announce stage changes through a polite live region, not every percent tick.

## Stage list anatomy
- Each stage: name in user language, status (done, in progress, waiting on someone, failed, skipped), owner if human, timestamp when done.
- Current stage visually distinct and stated in text, not only by color.
- Failed stage shows reason and the one action that fixes it.
- Upcoming stages visible so users know how much is left.

## Retry and failure taxonomy

| Failure type | Example | Auto retry? | User sees |
|---|---|---|---|
| Transient | Timeout, rate limit, brief outage | Yes, with backoff, limited attempts | Nothing at first; after limit, "Still trying" then manual Retry |
| User fixable | Validation, expired card, missing permission | No | Specific reason plus fix action, input preserved |
| System permanent | Unsupported file, upstream rejection | No | Reason, alternative path, contact or support route |
| Unknown outcome | Connection dropped after submit | No blind resubmit | "Checking whether your order went through" then reconcile via idempotency key |

Idempotency rules:
- Client generates an idempotency key per intended action, reused on retries of that action.
- Server returns the original result for a repeated key; UI treats it as success, not as a duplicate error.
- After an unknown outcome, the UI checks status before offering resubmit.

## Cancellation semantics
- Before side effects: cancel fully, nothing happened; say so.
- During batch: stop remaining items; report "18 of 40 processed before cancel. These remain changed." with a link to the processed set and, where possible, an undo.
- After commit: cancel is not offered; offer a reversal action (refund, unpublish) with its own consequences.

## Optimistic UI decision check
Use optimistic UI only if all are true:
1. Success is the overwhelmingly common outcome for this action.
2. Rollback is cheap and visible.
3. No external party is notified or charged.
4. A later failure can be shown in context, with the user's input kept.

## Draft and resume details
- Autosave on field blur or at intervals, plus on step change; show "Saved 2 min ago" and a failure state "Not saved, retrying".
- Resume link in the dashboard or list of in-progress items, ordered by last activity.
- When others changed the item meanwhile, show a change summary before the user continues.
- Expiry: warn ahead of time with the deadline and what is lost; let users extend if policy allows.

## Worked example: Vendor onboarding approval

### Before
- Status column values: "PENDING", "IN_REVIEW", "ERR".
- After submit, a spinner for up to several minutes while documents are scanned; closing the tab lost the submission.
- Finance rejected items silently; requester saw "PENDING" for days.

### After: state table excerpt

| State (user label) | Internal state | Owner | Entry trigger | Allowed transitions (actor) | Reversible? | User-visible status and next action | Notification |
|---|---|---|---|---|---|---|---|
| Draft | DRAFT | Requester | Create | Submit (Requester), Delete (Requester) | Yes | "Draft, saved 10:42. Continue" | None |
| Checking documents | SCAN | System | Submit | Pass, Fail (System) | No | Stage list: Upload done, Checking documents in progress, "You can leave this page, we will email you" | Email on finish |
| Waiting for finance approval | L2_REVIEW | Finance approver role | Scan passed | Approve, Return with reason (Finance) | Return is reversible | "Waiting for finance approval. Usually reviewed within the team's committed time" | Approver notified |
| Returned for changes | RETURNED | Requester | Return (Finance) | Resubmit (Requester) | Yes | "Finance needs: updated tax form. Fix and resubmit" | Requester notified with reason |
| Approved | ACTIVE | System | Approve | Deactivate (Admin) | Yes, via deactivate | "Approved by A. Tran on 12 Oct" | Requester notified |

Progress spec for "Checking documents": duration unknown, so indeterminate with stage name and elapsed time; background mode after submit; idempotency key on submit so a double click creates one vendor.

## Sources
- Jakob Nielsen, response-time limits.
- IBM Carbon progress indicator and loading guidance; Material Design progress indicators; Atlassian progress tracker.
- WAI-ARIA APG and ARIA spec: progressbar role, live regions; WCAG 4.1.3 Status Messages.
- Public payment API documentation on idempotency keys; verify current guidance.
