# Workflow Gate

Mark each item PASS or FAIL with evidence.

- [ ] State table exists; every state has exactly one owner.
- [ ] Every irreversible transition is marked and has a confirmation pattern matching its consequence.
- [ ] User-facing status labels contain no internal state names.
- [ ] Each work-item view shows current state, owner, blocker and next action.
- [ ] No percentage is shown where progress cannot be measured.
- [ ] Operations expected to exceed about 10 s let the user leave and notify on completion.
- [ ] Create or charge actions use idempotency keys; triggers are disabled while in flight.
- [ ] Unknown-outcome failures reconcile status before offering resubmit.
- [ ] Cancel semantics are stated, and partial completion reports counts and a route to failed items.
- [ ] Optimistic UI is used only where the four conditions in the reference hold.
- [ ] Draft, autosave and resume behavior is defined where interruption has value; storage scope is honest.
- [ ] Returned or rejected items carry a reason and a named owner.
- [ ] Status changes are announced via live regions; determinate bars expose progressbar values.
- [ ] Unhappy paths walked: tab close, double click, network drop, absent approver, expiry.
