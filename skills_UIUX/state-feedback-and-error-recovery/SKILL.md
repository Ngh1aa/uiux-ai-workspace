---
name: state-feedback-and-error-recovery
description: Specify complete UI states and feedback so users understand system status and can recover from failure. Use for async interactions, forms, search, uploads, API-driven components and critical actions.
---

# State Feedback & Error Recovery

## State inventory
Cover as relevant: default, hover, focus, active, disabled, loading, skeleton, first-use empty, filtered empty, zero-result, success, warning, partial failure, offline, permission denied, unavailable, timeout, retrying and canceled.

## Workflow
1. Inventory states for every critical component/flow.
2. Define trigger, visual change, message and next action.
3. Preserve user work when failure occurs.
4. Use progress feedback for long-running tasks.
5. Add retry, undo or cancel where appropriate.
6. Ensure status is perceivable without color alone.

## Quality gate
No dead-end error state; asynchronous actions expose status; recovery is at least as clear as the failure message.
