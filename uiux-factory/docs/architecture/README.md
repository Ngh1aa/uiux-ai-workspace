# Architecture Truth Index

Status: **A40 GUARDED + A41 MERGED + A42 MERGED + A43 MERGED + A44.1 CORE DESIGN CRITICS IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@178480ad0ba5ec32173f13df7ead16ae196c0b17`

This directory contains the current architecture truth for UIUX Factory / Flow OS / Brain OS evolution.

Read in this order:

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, owners, evidence/memory surfaces and remaining convergence debt.
2. `MIGRATION-BOUNDARIES.md` — active post-A4 architecture contract and Brain OS boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` — A40.1 audit findings, capability/ownership matrix, duplicate-surface classification and roadmap corrections.
4. `A40-ARCHITECTURE-GUARDRAILS.md` — A40.2 executable invariants that protect the reconciled architecture.
5. `A41-BRAIN-CORE-CONTRACTS.md` — strict BrainTaskFrame / Uncertainty / Hypothesis / Decision data/control contracts introduced by A41.1.
6. `A41-CRITIQUE-REPAIR-CONTRACTS.md` — strict CritiqueIssue / RootCause / RepairDirective / RetestRequirement / RepairLink lineage contracts introduced by A41.2.
7. `A42-EVIDENCE-GRAPH-FOUNDATION.md` — adapter-first relationship graph over canonical runtime/provenance/release evidence IDs.
8. `A42-EVIDENCE-INTEGRITY.md` — false-evidence protection, repair-lineage integrity and task-to-evidence lineage validation.
9. `A43-FLOW-SELECTION-ENGINE.md` — Brain-facing adapter over canonical change-surface classification and FlowPlanner selection, with bounded adjacent escalation.
10. `A43-JIT-CONTEXT-LOADER.md` — read-only projection of canonical mandatory/JIT skill routing and runtime context budgets.
11. `A43-ROUTING-BENCHMARK.md` — deterministic regression corpus for Task Contract surface → flow → mandatory/JIT skill routing.
12. `A44-CORE-DESIGN-CRITICS.md` — advisory VisualBrain adapter plus bounded UX/IA, Design System and Accessibility critics.

## Current architecture statement

A4 runtime consolidation is implemented. The shared executable Flow OS owner is:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas and runtime policy. Python modules under `skills_UIUX/runtime/` are compatibility shims, not a second executable Flow OS.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`, while the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS rule

Brain OS may add reasoning, hypothesis/decision contracts, critique orchestration, evidence relationships, richer memory and unified evaluation **above** the canonical runtime.

It must not create a third execution runtime or a competing evidence/authority system.

A40.2 makes these boundaries executable through:

```text
uiux-factory/tests/test_architecture_guardrails_a40.py
```

A41 establishes contract-only reasoning state:

```text
core/brain_os/contracts.py
core/brain_os/critique_contracts.py
```

These contracts contain reasoning/control metadata only. They do not own tools, providers, gates, merge/release authority or trusted-evidence semantics.

A42 adds the evidence relationship + integrity layer:

```text
core/brain_os/reasoning/evidence_graph.py
core/brain_os/adapters/evidence.py
core/brain_os/reasoning/evidence_integrity.py
core/brain_os/reasoning/lineage_integrity.py
```

The graph and integrity validators reference canonical evidence owned by:

```text
core/runtime/flow_os/evidence.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
```

They do not define a new evidence record, trusted-evidence type set, evidence store, release registry or gate evaluator.

Current intended lineage is:

```text
Task
→ Hypothesis
→ Decision
→ CritiqueIssue
→ RootCause
→ RepairDirective
→ RetestRequirement
→ canonical evidence reference
```

A42.2 can validate that this lineage is internally truthful and complete. It cannot prove execution, upgrade trust, mark a runtime gate passed or declare release readiness.

## Flow selection boundary

A43.1 adds a Brain-facing adapter only:

```text
core/brain_os/adapters/flow_selection.py
```

Canonical owners remain:

```text
core/runtime/flow_os/adaptive_surface.py::classify_change_surface
core/runtime/flow_os/flow.py::FlowPlanner
```

Brain may record the selected flow and propose a one-rung escalation:

```text
MICRO → FOCUSED → PAGE → REDESIGN → PRODUCT
```

but it cannot define a second `FlowPlanner`, skip arbitrary surface levels, mutate flow policy or execute the selected flow itself.

## JIT context boundary

A43.2 adds a read-only Brain projection:

```text
core/brain_os/adapters/jit_context.py
```

The source data remains canonical `ResolvedStage` output from `SkillResolver`, plus operator-owned runtime policy.

Brain may observe:

```text
mandatory/default skills
routed JIT pool
JIT provenance
active/available JIT view
count and section budgets
provider document policy ceiling
```

It cannot add non-routed skills, raise budgets, change authority/gates/evidence or claim that a JIT activation actually occurred. Provider/runtime preflight remains authoritative.

## Routing benchmark boundary

A43.3 adds evaluation-only routing coverage:

```text
benchmarks/routing-v1.json
core/benchmarks/routing_regression.py
scripts/validate_routing_benchmark.py
```

The benchmark runs representative natural-language tasks through the production `GoalInterpreter`, canonical `FlowPlanner` and A43 JIT projection, then compares the result with reviewed expectations.

It does not participate in routing, cannot mutate flow policy and records no execution authority. Tests hash `skills_UIUX/flows/*.json` before/after a benchmark run to enforce this read-only boundary.

## Core critic boundary

A44.1 adds advisory design critics under:

```text
core/brain_os/critics/core_design.py
```

The visual critic adapter reuses the actual existing primitive:

```text
core/orchestration/visual_brain.py::VisualBrain
```

and calls `evaluate()` only. It does not apply calibration or mutate source artifacts.

The UX/IA, Design System and Accessibility critics inspect current structured contracts and emit only `CritiqueIssue(status=OBSERVED)`. Critic reports have no `passed` field and explicitly declare:

```text
advisory_only = true
authority_effect = none
gate_effect = none
evidence_effect = none
```

No critic can self-confirm a finding, self-pass a runtime gate or manufacture trusted evidence.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

Historical documents remain useful audit history, but do not override current code.

## Next architecture task

After A44.1 is green and merged, A44.2 should add Product, Runtime and Evidence/Truth critics by reusing A42 integrity and current runtime artifacts. Those critics remain advisory and cannot duplicate evidence/gate authority.
