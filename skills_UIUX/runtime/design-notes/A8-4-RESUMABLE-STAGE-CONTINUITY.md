# A8.4 — Resumable Stage Continuity & Flow-Revision Binding

A8.4 closes a managed-resume gap left after A8–A8.3.

Before A8.4, resuming a managed run with `--managed-run-id` restored the manager checkpoint, but the next provider cycle called `start_stage()` and created a new specialist `RunState`. Any same-stage runtime state already persisted in the previous specialist checkpoint — including activated JIT skills, provider observations, current-run evidence, completed tool actions, artifacts and workspace metadata — was therefore left behind.

A8.4 makes one in-progress specialist stage resumable while binding reuse to the exact current Flow execution epoch.

## Resume contract

`ManagedFlowController.start_stage()` is now idempotent for an in-progress stage when all of the following still match:

```text
manager_run_id
flow_id
flow_revision
stage_id
agent / active_role
effective stage authority
stage gates
explicit source context, when the caller explicitly supplies it
```

and the specialist checkpoint state is:

```text
READY | RUNNING
```

When those invariants hold, the existing specialist `RunState` is returned instead of creating another stage run.

The managed run remains `RUNNING`, and the existing run id is not appended to `stage_runs` a second time.

## What continuity preserves

Because the exact specialist checkpoint is reused, same-stage runtime state remains available after a process/CLI restart, including:

- `jit_active_skills`;
- `provider_observations`;
- trusted current-run `evidence_records`;
- provider metadata/usage attached to that stage checkpoint;
- completed actions;
- artifacts;
- isolated workspace metadata;
- loaded explicit sources.

A8.4 does not copy these fields into a new checkpoint. It resumes the checkpoint that already owns them.

## Flow revision is the routing epoch

A specialist checkpoint may be reused only when its `flow_revision` equals the managed Flow revision.

```text
checkpoint revision < managed revision
    -> stale specialist state; do not resume; start a fresh stage run

checkpoint revision == managed revision
    -> validate full checkpoint identity; resume only if still in progress

checkpoint revision > managed revision
    -> impossible/future state; fail closed
```

A legacy checkpoint with no `flow_revision` is retained as historical state but is not trusted for live specialist continuation. A fresh stage run is created instead.

## REPLANNED is always a fresh specialist epoch

`managed.state == REPLANNED` explicitly prevents specialist checkpoint reuse, even for compatibility callers that did not increment the Flow revision themselves.

This keeps old lifecycle/test callers safe and ensures a replan never silently carries prior JIT activation, quality/provider context or current-run specialist observations into the new execution attempt.

Canonical declarative replanning already increments `flow.revision`; the explicit `REPLANNED` boundary adds defense-in-depth and compatibility for older callers.

## Fail-closed checkpoint validation

A same-revision checkpoint is rejected when its execution identity no longer matches the current stage. The runtime fails closed for:

- manager id mismatch;
- flow id mismatch;
- stage id mismatch;
- agent/active-role mismatch;
- authority mismatch;
- gate mismatch;
- malformed/non-integer revision;
- checkpoint revision ahead of the managed Flow.

These cases are treated as checkpoint integrity problems, not as reasons to silently discard state and start another run.

## Terminal stages are not implicit retries

A same-revision specialist checkpoint in a terminal state such as `FAILED`, `BLOCKED` or `COMPLETED` is not automatically reopened by `start_stage()`.

The caller must advance, replan or otherwise resolve the lifecycle boundary explicitly. This prevents a simple process restart from becoming an unrecorded retry.

## Explicit source continuity

When a caller explicitly supplies `explicit_sources` while resuming an in-progress stage, they must exactly match the checkpoint's existing `loaded_sources`.

A caller cannot mutate source-of-truth context underneath an already-running specialist checkpoint. To use a different explicit source set, the current stage must finish or a new Flow/replan epoch must begin.

Provider-driven managed resume normally supplies no new explicit source list, so the checkpoint's existing source set continues unchanged.

## A8 compatibility

A8.4 does not change:

- Flow selection or skill routing;
- A8/A8.2 JIT pool and provenance semantics;
- A8.3 context-budget/preflight semantics;
- authority ceilings;
- gate definitions or gate evidence requirements;
- trusted evidence types;
- provider routing/budget ownership;
- merge, deploy or release authorization.

It only makes the active specialist checkpoint durable across managed restarts and binds that durability to the correct Flow execution epoch.

## Regression coverage

`uiux-factory/tests/test_stage_resume_continuity_a8_4.py` covers:

- same-revision `start_stage()` idempotence;
- managed restart preserving activated JIT skill context and provider observations;
- new Flow revision invalidating prior specialist state;
- `REPLANNED` forcing a fresh specialist epoch even without a revision increment;
- tampered checkpoint identity failing closed;
- future revision failing closed;
- terminal same-revision specialist state not being implicitly retried;
- explicit source context being immutable during same-stage resume.
