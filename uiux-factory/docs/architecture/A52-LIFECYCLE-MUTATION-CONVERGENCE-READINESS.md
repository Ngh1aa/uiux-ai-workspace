# A52.1 — Lifecycle Mutation Convergence Readiness

Status: **IMPLEMENTED AS READINESS GATE / MUTATION UNIFICATION NOT AUTHORIZED**  
Date: **2026-10-02**

## Goal

Determine whether the two existing lifecycle state owners are evidence-ready for any mutation-level unification.

A52.1 does **not** change either lifecycle. Current owners remain:

```text
Factory  -> core.runtime.run_context.RunContext
Managed  -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

The A49 `LifecycleProjection` remains read-only comparison/observability only.

## Why a readiness gate is required

A49 proved that both lifecycle surfaces can be projected into the same ten comparison phases:

```text
INTAKE -> INTERPRET -> PLAN -> RESEARCH -> DESIGN -> IMPLEMENT -> QA -> REPLAN -> FINALIZE -> RELEASE
```

That does not prove their mutation semantics are interchangeable.

Current source still contains material differences that must not be erased by a shared mutable state abstraction.

## Current semantic blockers

A52.1 verifies six blockers directly from executable source/reconciliation contracts:

1. `distinct_state_models`
   - `RunContext` and `ManagedWebsiteRun` have different state schemas and responsibilities.
2. `factory_append_only_chronology`
   - Factory writes a fast `run.json` snapshot but preserves chronology through `RunEventBus` / `events.jsonl`.
3. `managed_checkpoint_and_stage_lineage`
   - managed lifecycle tracks `stage_runs`, `replan_history`, Flow revision and checkpoint lineage.
4. `managed_human_gate_semantics`
   - managed lifecycle can enter `AWAITING_APPROVAL` and records explicit `approved_gates`.
5. `replan_invalidation_semantics_non_parity`
   - Factory creative revision and managed declarative replan have different invalidation semantics.
6. `finalize_release_semantics_non_parity`
   - Factory default run exposes no production release mutation; managed finalize/release are separate external-controller actions.

These are not naming differences. They are behavioral/authority boundaries.

## Decision policy

A52.1 is fail-closed:

```text
A49 parity/source prerequisite regression
-> HOLD_LIFECYCLE_CONVERGENCE_EVIDENCE_REQUIRED

current semantic blockers remain
-> KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED

blockers somehow clear but no explicit later governance exists
-> HOLD_EXPLICIT_MUTATION_GOVERNANCE_REQUIRED

only a separate future governance task may ever derive
-> READY_FOR_SEPARATE_MUTATION_GOVERNANCE
```

The A52.1 contract itself explicitly forbids opting into mutation governance.

## Expected current result

With the current repository source, the expected decision is:

```text
KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED
```

A clean audit may allow only:

```text
event_interop_proposal_allowed = true
```

This means a later task may propose an additive, non-authoritative lifecycle event interoperability contract. It does **not** authorize a shared mutable lifecycle state or transition engine.

## Non-authority boundary

A52.1 always keeps false:

```text
mutation_governance_allowed
state_owner_replacement_allowed
shared_mutable_state_allowed
runtime_transition_change_allowed
routing_change_allowed
provider_default_change_allowed
evidence_authority_change_allowed
gate_authority_change_allowed
finalize_release_authority_change_allowed
product_evidence
```

Provider A51.1 remains separate: `legacy` is still the Factory provider default until real live-provider evidence exists.

## Canonical files

```text
benchmarks/lifecycle-mutation-convergence-readiness-v1.json
core/benchmarks/lifecycle_mutation_convergence_readiness.py
scripts/validate_lifecycle_mutation_convergence_readiness.py
tests/test_lifecycle_mutation_convergence_readiness_a52.py
```

A49 prerequisites remain active:

```text
benchmarks/lifecycle-parity-v1.json
core/benchmarks/lifecycle_parity_regression.py
core/runtime/lifecycle_reconciliation.py
core/runtime/lifecycle_projection.py
```

## Failure behavior

The readiness validator fails if:

- A49 lifecycle projection parity regresses;
- reconciliation stops being read-only;
- either current state owner becomes ambiguous;
- required lifecycle mutator/checkpoint/gate contracts disappear unexpectedly;
- the six current semantic blockers no longer match audited source without an explicit follow-up architecture decision;
- A52.1 attempts to grant mutation/routing/provider/evidence/gate/release authority;
- A52.1 attempts to self-authorize mutation governance.

## Next task rule

A52.1 does not justify direct lifecycle mutation convergence.

If this audit passes with the current blockers intact, the next bounded lifecycle task may be:

```text
A52.2 — Lifecycle Event Interoperability Contract
```

That task should be additive and read-only/non-authoritative: normalize lifecycle events/receipts for cross-surface observability while preserving both existing state owners and every current evidence/gate/release boundary.

Direct mutation unification remains deferred unless a later, explicit governance package first proves the semantic blockers have been eliminated without regression.
