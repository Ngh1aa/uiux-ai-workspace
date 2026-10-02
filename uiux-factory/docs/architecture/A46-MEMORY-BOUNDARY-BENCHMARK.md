# A46.3 — Memory Boundary Benchmark

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A46.1 typed Brain memory + A46.2 post-routing memory context

## Purpose

A46.3 adds a deterministic regression benchmark for the architectural boundaries around historical Brain memory.

Canonical artifacts:

```text
benchmarks/memory-boundary-v1.json
core/benchmarks/memory_boundary_regression.py
scripts/validate_memory_boundary_benchmark.py
tests/test_memory_boundary_benchmark_a46.py
```

The benchmark is evaluation-only. It does not participate in routing, memory writes for real projects, gate evaluation or release.

## Coverage

The initial corpus covers:

- historical typed hypothesis recall;
- current-run exclusion;
- tag-bounded recall;
- source-ref-bounded recall;
- bounded newest-first recall;
- cross-project write rejection.

Each recall case also requires an existing `FlowSelectionDecision` and checks that it remains byte-for-byte semantically unchanged after memory attachment.

## Locked invariants

Recall cases must preserve:

```text
attached_after_flow_selection = true
flow_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
current_run_evidence = false
```

No recalled record may originate from `current_run_id`.

The cross-project case must prove that a record scoped to another project root is rejected and leaves the target store empty.

## Read-only production-source guard

Tests hash these production sources before and after a full benchmark run:

```text
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
```

The hashes must remain unchanged.

The benchmark evaluator is also statically guarded against importing/calling:

```text
FlowPlanner(...)
select_canonical_flow(...)
ManagedFlowController
ProviderManagedRunner
gate_evidence_errors
run_target_command
release_action
ProductionReleaseController
merge_pull_request
```

## CI

Main UIUX Factory CI now runs:

```text
validate_benchmark_corpus.py
validate_routing_benchmark.py
validate_repair_proposal_benchmark.py
validate_memory_boundary_benchmark.py
```

before the full pytest suite.

## Acceptance criteria

- [x] benchmark covers project isolation and current-run isolation;
- [x] bounded recall filters and limits are regression-tested;
- [x] existing canonical flow selection is required and preserved;
- [x] no recall item becomes current-run evidence;
- [x] no flow/authority/gate/evidence effect is introduced;
- [x] cross-project write rejection is regression-tested;
- [x] production memory sources remain byte-identical after evaluation;
- [x] benchmark validator is part of main CI;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## Handoff

A46 completes the first bounded semantic-memory slice: typed storage, post-routing recall and regression protection. After A46.3 merges, re-audit architecture truth before choosing the next numbered task. The remaining likely gap is the provenance-aware unified Brain scorecard, but it should reuse existing evaluator outputs rather than create a competing QA/gate system.
