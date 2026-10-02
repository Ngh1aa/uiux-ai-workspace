# A52.2 — Lifecycle Event Interoperability Contract

Status: **IMPLEMENTED / VERIFIED**  
Date: **2026-10-02**  
Depends on: A52.1 Lifecycle Mutation Convergence Readiness

## Purpose

A52.2 implements the only lifecycle follow-up authorized by A52.1: a bounded, read-only event/receipt interoperability layer across the two existing lifecycle mutation owners.

It does not unify mutation semantics.

Current owners remain:

```text
Factory -> core.runtime.run_context.RunContext
Managed -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

The interoperability owner is:

```text
core/runtime/lifecycle_event_interop.py
```

## Why receipts instead of a shared event bus

A52.1 proved that the two owners have materially different mutation semantics.

Factory owns an append-only chronology:

```text
RunSessionEvent
seq + timestamp + run_id + native event payload
```

Managed lifecycle persistence is checkpoint-oriented:

```text
ManagedWebsiteRun snapshot
stage_runs
replan_history
approved_gates
flow revision
```

Treating those as equivalent native event streams would fabricate chronology and hide one of the A52.1 blockers.

A52.2 therefore emits observation receipts with an explicit chronology-strength distinction:

```text
Factory -> durable_append_only
Managed -> derived_checkpoint_delta
```

## Receipt contract

Canonical schema marker:

```text
lifecycle-event-receipt.v1
```

Each receipt carries:

```text
surface_id
chronology_strength
kind
run_id
phase
native_type
native_stage
source_seq / source_timestamp
previous_checkpoint_hash / checkpoint_hash
lineage_refs
details
```

Every receipt also declares:

```text
observation_only = true
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

A receipt can be used for observability/regression comparison only. It cannot execute a transition, satisfy a gate, create trusted product evidence, approve release or authorize state-owner convergence.

## Factory projection

`project_factory_event_receipts(...)` consumes existing `RunSessionEvent` values or equivalent mappings.

It preserves native:

```text
seq
timestamp
run_id
stage
data
```

Known events normalize to bounded vocabulary:

```text
run.created      -> run_started
stage.started    -> stage_started
stage.completed  -> stage_completed
run.completed    -> run_completed
run.failed       -> run_failed
session.forked   -> run_forked
```

Unknown/future native events fail safe as:

```text
native_event_observed
```

They are not guessed into a lifecycle phase or authority-bearing meaning.

Factory `run.completed` may project to `FINALIZE` because A49 already established that default Factory completion represents run finalization, not deployment. It never becomes `RELEASE`.

## Managed checkpoint-delta projection

`project_managed_transition_receipts(previous, current)` compares two checkpoint-shaped mappings without writing either checkpoint and without calling `ManagedFlowController` transition methods.

Safely derivable deltas include:

```text
stage_run appended       -> stage_started
completed_stage appended -> stage_completed
approved_gate appended   -> approval_granted
state enters AWAITING_APPROVAL -> approval_required
flow revision/replan count increases -> replan_applied
state enters COMPLETED   -> run_completed
state enters FAILED      -> run_failed
state enters BLOCKED     -> run_blocked
```

An initial checkpoint with no previous snapshot does **not** prove run-start chronology. It emits only:

```text
native_event_observed
```

Managed receipts intentionally have:

```text
source_seq = null
source_timestamp = null
```

and instead carry stable checkpoint hashes. Their deterministic projection order is not native chronology.

Managed `COMPLETED` remains phase-unmapped at the run level because A49/A52.1 established that workspace finalization and production release live outside `ManagedWebsiteRun`.

## Lineage protection

Managed `stage_runs` are treated as append-only lineage for interoperability projection.

If the newer checkpoint shrinks or rewrites an existing stage-run prefix, projection fails closed rather than manufacturing a replacement event history.

## Benchmark

Corpus:

```text
benchmarks/lifecycle-event-interop-v1.json
```

Evaluator:

```text
core/benchmarks/lifecycle_event_interop_regression.py
```

Validator:

```text
scripts/validate_lifecycle_event_interop.py
```

The corpus covers eight bounded cases:

1. Factory native chronology preservation;
2. Factory fork + unknown-event fail-safe behavior;
3. Managed initial checkpoint without fabricated start;
4. Managed stage-run delta;
5. Managed human approval required;
6. Managed human approval granted;
7. Managed replan delta;
8. Managed stage + run completion without release inference.

Every case verifies source inputs remain unchanged and receipts remain non-authoritative.

## A52.1 blockers remain

A52.2 does not clear or downgrade the six A52.1 mutation blockers:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

The interoperability layer makes those differences observable; it does not erase them.

## Non-goals

A52.2 does not:

- modify `RunContext` transitions;
- modify `ManagedFlowController` transitions;
- replace either state owner;
- create a shared mutable lifecycle state;
- create a third lifecycle state machine;
- turn Managed checkpoints into an append-only event log;
- infer native timestamps or event sequence numbers for Managed checkpoints;
- satisfy human approvals;
- create trusted evidence;
- change routing/provider defaults;
- finalize a workspace;
- deploy production;
- open mutation-level convergence governance.

## Verification

Executable verification immediately before the final documentation-only status commit established:

```text
UIUX Factory CI #1649 = SUCCESS
A20 UIUX Factory v1 Release Candidate #186 = SUCCESS
A52.2 interoperability corpus = 8/8 PASS
source_inputs_unchanged = true
authority_boundaries_clear = true
pytest = 631 passed / 50 skipped
```

The final documentation-only head must independently rerun the same mandatory CI/A20 gates before merge. No executable lifecycle or authority code is changed by this status update.

## Acceptance criteria

- [x] one observation receipt schema covers both lifecycle surfaces;
- [x] Factory native seq/timestamp provenance is preserved;
- [x] Managed chronology weakness is explicit and no seq/timestamp is fabricated;
- [x] approval/replan/stage lineage deltas are observable without mutation;
- [x] unknown events fail safe;
- [x] Managed completion does not imply finalize/release;
- [x] stage-run lineage rewrite fails closed;
- [x] deterministic corpus + validator + tests exist;
- [x] active UIUX Factory CI invokes A52.2 validation;
- [x] executable PR head passes UIUX Factory CI;
- [x] executable PR head passes A20 regression/security/dogfood;
- [x] PR is mergeable before final documentation-only verification.

## Handoff

A52.2 is an observability/regression convergence layer only.

After it is green and merged, no direct lifecycle-mutation task should be inferred automatically. Any later attempt to reduce the A52.1 blockers must be separately scoped and governed from executable evidence. Provider-default migration remains independently blocked on A51.1 live receipts; GenAI/NIST remains freshness-held; vector search remains deferred.
