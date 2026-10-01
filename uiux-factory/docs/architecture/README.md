# Architecture Truth Index

Status: **A40 GUARDED + A41.1 MERGED + A41.2 IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@f6157fa339908ecce58062820a407e035353a8c7`

This directory contains the current architecture truth for UIUX Factory / Flow OS / Brain OS evolution.

Read in this order:

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, owners, evidence/memory surfaces and remaining convergence debt.
2. `MIGRATION-BOUNDARIES.md` — active post-A4 architecture contract and Brain OS boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` — A40.1 audit findings, capability/ownership matrix, duplicate-surface classification and roadmap corrections.
4. `A40-ARCHITECTURE-GUARDRAILS.md` — A40.2 executable invariants that protect the reconciled architecture.
5. `A41-BRAIN-CORE-CONTRACTS.md` — strict BrainTaskFrame / Uncertainty / Hypothesis / Decision data/control contracts introduced by A41.1.
6. `A41-CRITIQUE-REPAIR-CONTRACTS.md` — strict CritiqueIssue / RootCause / RepairDirective / RetestRequirement / RepairLink lineage contracts introduced by A41.2.

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

A41 now establishes contract-only reasoning state:

```text
core/brain_os/contracts.py
core/brain_os/critique_contracts.py
```

These contracts contain reasoning/control metadata only. They do not own tools, providers, gates, merge/release authority or trusted-evidence semantics.

The critique/repair lineage is:

```text
CritiqueIssue → RootCause → RepairDirective → RetestRequirement
                         \→ RepairLink records the relationship graph
```

A `RepairDirective` is an instruction, not proof of execution. A `PASSED` retest or `RESOLVED` critique requires evidence references; runtime/provenance layers remain the authority for whether those references are trusted.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

Historical documents remain useful audit history, but do not override current code.

## Next architecture task

After A41.2 is green on CI, A42 should begin Evidence Graph Foundation by adapting existing runtime/provenance evidence primitives. It must not create a second independent evidence authority/store.
