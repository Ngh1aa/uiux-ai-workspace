# A49.2 + A49.3 — Lifecycle Adapter + Parity

Status: **IMPLEMENTED / VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A49.1 Lifecycle Contract Reconciliation

## Purpose

A49.2/A49.3 add one **read-only lifecycle projection adapter** plus deterministic parity benchmark over the two existing lifecycle state owners.

The goal is observability/comparison, not runtime unification.

## Projection owner

```text
core/runtime/lifecycle_projection.py
```

Inputs are existing snapshots:

```text
Factory        -> RunContext-like mapping
Managed Flow   -> ManagedWebsiteRun-like mapping
```

Output:

```text
LifecycleProjection
```

with the same ten A49.1 comparison phases.

## Projection-only rule

The adapter never calls manager/controller execution methods and cannot:

- start or complete a stage;
- replan;
- execute tools/providers;
- create trusted evidence;
- pass a gate;
- finalize a worktree;
- deploy production.

It declares:

```text
projection_only = true
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## Factory projection

Factory native stage names have an explicit comparison map for research/design/implementation/QA.

`flow_plan` presence is required before INTERPRET/PLAN are projected as completed. A running snapshot without that artifact remains `unknown` rather than guessed.

Factory `status=completed` projects:

```text
FINALIZE = completed
RELEASE = unavailable
```

because default `run.py` completion is not production deployment.

Factory replanning remains `unknown` in a plain RunContext snapshot because creative revision/replan chronology requires event/revision context beyond the fast state snapshot.

## Managed projection

Managed lifecycle maps resolved stages using explicit agent ownership first:

```text
research       -> RESEARCH
implementation -> IMPLEMENT
qa             -> QA
```

Development-owned stages use only bounded stage-id cues for research/design/implementation/QA. Unknown/custom stages become:

```text
unmapped_native_stages
```

instead of being guessed into a phase.

`ManagedWebsiteRun.state=COMPLETED` deliberately does **not** project FINALIZE or RELEASE as complete. Those outcomes live in `ProductionReleaseController` and require separate evidence/authority.

## Parity benchmark

Corpus:

```text
benchmarks/lifecycle-parity-v1.json
```

Evaluator:

```text
core/benchmarks/lifecycle_parity_regression.py
```

CI validator:

```text
scripts/validate_lifecycle_parity_benchmark.py
```

The corpus covers:

- Factory created/intake state;
- Factory active design state with flow-plan provenance;
- Factory completed but not released;
- Managed active research state;
- Managed replanned design state;
- Managed unknown-stage fail-safe behavior.

Every case verifies the input payload is unchanged after projection.

Benchmark scope is explicitly:

```text
projection_parity_not_execution_or_release_evidence
```

A passing benchmark cannot be used as proof that two real runs produced equivalent design quality, evidence, runtime behavior or release readiness.

## CI

Main UIUX Factory CI now runs:

```text
python scripts/validate_lifecycle_parity_benchmark.py
```

before the full pytest suite.

## Non-goals

This package does not:

- replace RunContext;
- replace ManagedWebsiteRun;
- create a shared mutable lifecycle state;
- change Factory stage sequencing;
- change ManagedFlowController transitions;
- infer release from run/stage completion;
- modify evidence/gate/release authority;
- migrate provider defaults.

## Acceptance criteria

- [x] one read-only projection schema covers both existing state owners;
- [x] all ten comparison phases remain visible;
- [x] unknown native stages fail safe as unmapped;
- [x] Factory completion never becomes production release;
- [x] Managed completion never becomes finalize/release without controller outputs;
- [x] projection cannot mutate source payloads;
- [x] deterministic benchmark protects representative lifecycle states;
- [x] CI invokes lifecycle parity benchmark;
- [ ] final head passes UIUX Factory CI;
- [ ] final head passes A20 regression/security/dogfood;
- [ ] PR is mergeable.

## Handoff

After this package is green and merged, A49 lifecycle convergence should be considered complete at the **projection/parity layer**. Any later mutation-level unification would need a separate architecture decision and should not be inferred as necessary merely because a common projection exists.

The next planned architecture package is A50.1 — Knowledge OS Architecture, preserving `skills_UIUX` as methodology owner and avoiding skill/knowledge duplication.
