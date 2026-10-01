# Architecture Truth Index

Status: **A40 GUARDED + A41 MERGED + A42.1 GRAPH + A42.2 INTEGRITY IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@fc2f620fbd1ff4e197bbbfe022d5883b15481178`

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

False-evidence protection includes:

- graph evidence nodes must match canonical adapter projections;
- reasoning/control nodes cannot assign themselves trusted-evidence flags;
- provider claims remain untrusted and cannot terminate a `VERIFIED_BY` chain;
- terminal retest evidence refs must resolve to canonical evidence nodes;
- missing lineage is reported as incomplete rather than inferred.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

Historical documents remain useful audit history, but do not override current code.

## Next architecture task

After A42.2 is green on final-head CI, A43.1 may implement the Flow Selection Engine over the canonical Flow OS: change-surface classification, smallest-flow-first routing and bounded escalation. It must not recreate FlowPlanner or move execution ownership into Brain OS.
