# Architecture Truth Index

Status: **A40 GUARDED + A41 MERGED + A42 MERGED + A43 MERGED + A44 MERGED + A45.1 MERGED + A45.2 REPAIR LINEAGE GRAPH IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@75fb4878e076c9ba556c0bc5472824f95961dce3`

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
13. `A44-PRODUCT-TRUTH-CRITICS.md` — advisory Product, Runtime and Evidence/Truth critics backed by A41/A42/canonical runtime owners.
14. `A45-CRITIQUE-REPAIR-ORCHESTRATOR.md` — proposal-only bridge from unresolved critique issues into existing A41 repair/retest contracts.
15. `A45-REPAIR-LINEAGE-GRAPH.md` — read-only projection of repair proposals into existing A42 EvidenceGraph relations without verification claims.

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

## Core design critic boundary

A44.1 adds advisory design critics under:

```text
core/brain_os/critics/core_design.py
```

The visual critic adapter reuses the actual existing primitive:

```text
core/orchestration/visual_brain.py::VisualBrain
```

and calls `evaluate()` only. It does not apply calibration or mutate source artifacts.

The UX/IA, Design System and Accessibility critics inspect current structured contracts and emit only `CritiqueIssue(status=OBSERVED)`.

## Product / truth critic boundary

A44.2 adds:

```text
core/brain_os/critics/product_truth.py
```

The Product Critic reads A41 task/hypothesis/decision contracts and flags reasoning/governance gaps without selecting decisions or inventing product evidence.

The Runtime Critic delegates current-state retry/supersession semantics to:

```text
core.runtime.flow_os.evidence.effective_evidence
```

It never calls the canonical gate evaluator and cannot turn review expectations into runtime gates.

The Evidence/Truth Critic directly reuses:

```text
validate_evidence_integrity(...)
validate_end_to_end_lineage(...)
```

A42 findings become `OBSERVED` critique issues only. No trust state is recomputed or upgraded.

All A44 reports intentionally have no `passed` field and declare:

```text
advisory_only = true
authority_effect = none
gate_effect = none
evidence_effect = none
```

No critic can self-confirm a finding, self-pass a runtime gate or manufacture trusted evidence.

## Repair proposal boundary

A45.1 adds:

```text
core/brain_os/repair_orchestrator.py
```

For each unresolved critique issue it may create only existing A41 proposal objects:

```text
RootCause(PROPOSED)
RepairDirective(PROPOSED)
RetestRequirement(PENDING)
RepairLink
```

The orchestrator uses deterministic IDs, preserves existing issue evidence refs without inventing new evidence, and can require human approval for P0 directives. It does not execute the repair or retest.

Every `RepairProposalBundle` declares:

```text
advisory_only = true
execution_effect = none
acceptance_effect = none
resolution_effect = none
gate_effect = none
evidence_effect = none
```

A45.1 cannot ACCEPT a directive, PASS a retest, RESOLVE an issue, run target commands, evaluate canonical gates, merge, deploy or release.

## Repair lineage graph boundary

A45.2 adds:

```text
core/brain_os/adapters/repair_lineage.py
```

It projects one A45.1 proposal bundle into the existing A42 relationship model using only:

```text
CRITIQUE_ISSUE --CAUSED_BY--> ROOT_CAUSE
ROOT_CAUSE --REPAIRED_BY--> REPAIR_DIRECTIVE
REPAIR_DIRECTIVE --REQUIRES_RETEST--> RETEST_REQUIREMENT
```

The projection intentionally stops at the pending retest. It never creates `RETESTED_BY` or `VERIFIED_BY`, never creates canonical evidence nodes and never sets a trusted-evidence flag.

`extend_graph_with_repair_proposal(...)` returns a new immutable graph, is idempotent for the same proposal and rejects identity collisions when an existing graph node/edge differs from the deterministic projection.

A42 end-to-end lineage therefore remains incomplete until a later canonical retest actually produces valid evidence and a truthful verification relationship is added by the appropriate evidence path.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

Historical documents remain useful audit history, but do not override current code.

## Next architecture task

After A45.2 is green and merged, A45.3 should add a deterministic repair-proposal benchmark/policy guard covering critic → target stage → retest evidence mapping and graph shape, with explicit regression protection against accidental auto-execution or false verification semantics.
