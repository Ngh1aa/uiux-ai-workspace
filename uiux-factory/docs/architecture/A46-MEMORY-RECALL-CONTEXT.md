# A46.2 — Post-Routing Memory Recall Context

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A43.1 canonical flow-selection adapter + A46.1 typed Brain memory

## Purpose

A46.2 allows project-scoped historical Brain memory to enrich reasoning **only after** canonical flow selection has already occurred.

Canonical implementation:

```text
core/brain_os/adapters/memory_context.py
```

The adapter requires an existing A43.1 `FlowSelectionDecision`. It has no API to select, replan or widen a flow.

## Ordering contract

Required order:

```text
canonical GoalInterpreter / Task Contract
→ canonical FlowPlanner
→ FlowSelectionDecision
→ attach_memory_after_flow_selection(...)
→ MemoryReasoningContext
```

Historical memory therefore cannot participate in initial change-surface or flow selection.

## MemoryReasoningContext

The context contains:

```text
current_run_id
flow_selection
bounded historical memories
attached_after_flow_selection = true
advisory_only = true
flow_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
```

The embedded `FlowSelectionDecision` is immutable and retained unchanged.

## Historical-only rule

The adapter always calls the A46.1 store with:

```text
exclude_run_id = current_run_id
```

The context validator independently rejects any recalled item whose `source_run_id` equals the current run.

Every `MemoryRecallItem` also requires:

```text
current_run_evidence = false
```

This gives two layers of protection against same-run memory being recycled as historical evidence.

## Allowed recall filters

Callers may request bounded memory by:

```text
kind
tag
source_ref
limit
```

The underlying `BrainMemoryStore` still owns project scope, persistence safety and policy ceilings.

## Authority boundary

The adapter does not import/call:

```text
FlowPlanner(...)
select_canonical_flow(...)
propose_bounded_escalation(...)
ManagedFlowController
ProviderManagedRunner
gate_evidence_errors
run_target_command
release_action
ProductionReleaseController
merge_pull_request
```

It cannot:

- choose or mutate a flow;
- activate JIT skills;
- change task authority;
- validate historical hypotheses;
- select historical decisions;
- satisfy runtime gates;
- promote memory to current-run evidence;
- merge, deploy or release.

## Acceptance criteria

- [x] existing `FlowSelectionDecision` is mandatory input;
- [x] memory attaches after flow selection only;
- [x] flow decision remains unchanged;
- [x] current-run memory is excluded during store recall;
- [x] context independently rejects current-run memory;
- [x] every recalled item remains `current_run_evidence=false`;
- [x] flow/authority/gate/evidence effects remain none;
- [x] empty recall does not imply pass/fail or alter execution;
- [x] adapter has no routing/execution/gate/release owner;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## Handoff

After A46.2 is green and merged, A46.3 should add a deterministic **memory boundary benchmark** that locks project isolation, current-run exclusion, post-routing ordering and no-flow/no-gate/no-evidence effects before wider Brain orchestration consumes memory.
