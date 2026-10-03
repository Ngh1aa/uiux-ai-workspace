# P1.6 — Execution Driver / Real Runner Integration

## Purpose

P1.6 turns the P1.5 execution eligibility model into a governed driver that can invoke a concrete runner, collect real artifacts, update execution state automatically, persist checkpoints, and route QA failures back to the nearest repair owner.

The execution chain is:

`WorkExecutionPlan → runnable segment → SegmentExecutionRequest → runner → RunnerResult → ArtifactRegistry → P1.5 output gate → state transition → checkpoint`

P1.6 does not replace P1.1–P1.5 routing or state contracts.

## Segment runner request

Each runner request carries the canonical resolved segment and its active flow stage:

- segment id/order/lifecycle phase,
- intent, scope and change surface,
- active stage id,
- routed agent,
- specialist skills and mandatory skills,
- stage gates,
- upstream input artifact refs,
- expected output kinds,
- preserve/forbidden constraints,
- normal or repair mode.

This prevents a runner from re-inferring which specialist or lifecycle stage should own the work.

## Command runner adapter

`CommandRunnerAdapter` provides the concrete process boundary.

It writes a request JSON file, invokes a command without a shell, and exposes:

- `UIUX_EXECUTION_REQUEST`
- `UIUX_EXECUTION_RESULT`
- `UIUX_EXECUTION_SEGMENT_ID`
- `UIUX_EXECUTION_MODE`

The runner must write a result JSON with `status=passed|failed` plus produced artifacts. A process that exits without a result becomes `RUNNER_CONTRACT_FAILED` rather than an implicit pass.

## Artifact registry

Runner artifacts declare a lifecycle `kind` and one of these storage classes:

- `file`
- `report`
- `screenshot`
- `commit`
- `evidence`

Local file artifacts must live inside the configured workspace root. The registry verifies existence and computes SHA-256. URI-only artifacts such as a commit reference retain their declared URI/provenance.

Artifacts are ingested before outcome evaluation but are not marked `accepted_for_handoff` until the P1.5 expected-output gate passes. Failure evidence therefore remains auditable without unlocking downstream work.

## Automatic state transitions

For one runnable segment the driver:

1. marks it `running`,
2. executes the runner,
3. registers returned artifacts,
4. on runner PASS, asks P1.5 to validate expected outputs,
5. marks accepted artifacts as handoff evidence,
6. lets P1.5 unlock the next node,
7. persists a checkpoint.

A runner that reports PASS but omits required outputs becomes `RUNNER_OUTPUT_GATE_FAILED`; downstream remains blocked.

## Checkpoints and resume

`JsonCheckpointStore` atomically persists:

- execution-plan state,
- artifact registry,
- repair counters/context,
- driver history,
- a fingerprint of the resolved work plan.

Resume is rejected when the current resolved plan fingerprint differs from the checkpoint, preventing stale state from being attached to a different routing plan.

## QA repair loop

When a QA runner returns `PRODUCT_QA_FAILED`, the driver finds the nearest upstream implementation owner for the same scope, falling back to design only when no implementation owner exists.

If the repair budget is not exhausted:

- audit/design upstream of that owner remain passed,
- execution resets from the repair owner only,
- QA failure evidence remains in the registry but is not promoted,
- the repair owner becomes runnable in `repair` mode,
- the repair request receives the failed QA artifact ids and repair capabilities,
- implementation and QA rerun from that point.

`max_repair_attempts` bounds the loop so the driver cannot repair indefinitely.

## Factory entrypoint

`ProfessionalWebsiteFlow.resolve_execution_driver(...)` performs:

`GoalInterpreter → WorkSequenceInterpreter → SequenceFlowPlanner → WorkExecutionPlan → ExecutionDriver`

P1.3 ambiguity therefore still fails closed before any runner can execute.

## Safety boundary

P1.6 coordinates execution but does not grant new repository or deployment authority. The concrete runner remains responsible for obeying the caller's granted authority and for producing truthful implementation/QA evidence. A manifest, request or process exit code alone is never treated as product QA PASS.

## CI evidence

The P1.6 lane uses a real subprocess fixture rather than calling P1.5 `pass_segment()` directly. It verifies:

- exact stage/agent/skills/gates are sent to the runner,
- real filesystem artifacts are hashed and registered,
- handoff artifacts appear in the next request,
- file/report/screenshot/commit/evidence storage classes,
- automatic transitions to completion,
- output-gate failure behavior,
- checkpoint resume,
- stale checkpoint rejection,
- QA failure → implementation repair → QA rerun,
- failure evidence retained but not promoted,
- P1.3 ambiguity remains fail-closed.
