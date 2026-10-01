# A40.1 — Architecture Reconciliation Report

Status: **COMPLETED AUDIT / IMPLEMENTED DOCUMENTATION UPDATE**  
Audit date: **2026-10-02**  
Audited branch: `main`  
Audited commit: `304baefb6999e552708150a20e5c01491aa3663e`  
Historical comparison baseline: `0d564b184ab54017caedb85e9074822ff74a1c17`

## 1. Purpose

A40.1 reconciles the Brain OS target architecture with the repository that actually exists after A4–A39.

This task does **not** implement Brain OS. It establishes what already exists, which subsystem owns each capability, which overlaps are intentional, and which future Brain OS proposals must adapt rather than duplicate.

## 2. Key finding

The A1 architecture documents were stale in one material way: they described A4 runtime consolidation as future work.

Current source/tests show that A4 consolidation has happened:

```text
uiux-factory/core/runtime/flow_os/
```

is the single executable shared Flow OS owner, while Python modules under:

```text
skills_UIUX/runtime/
```

are compatibility shims and declarative/runtime documentation inputs.

The repository therefore no longer has two independent Flow OS implementations.

## 3. Current architecture in one view

```text
User / external collaborator
          |
          v
Task / goal intake
          |
          v
canonical GoalInterpreter / Task Contract
uiux-factory/core/runtime/flow_os/task_context.py
          |
          v
canonical FlowPlanner
uiux-factory/core/runtime/flow_os/flow.py
          |
          +-------------------------------+
          | declarative inputs            |
          | skills_UIUX/flows/*.json      |
          | skills_UIUX/*/SKILL.md        |
          | runtime-policy.json           |
          +-------------------------------+
          |
          v
+----------------------+     +----------------------------+
| Factory product path |     | Managed CLI path           |
| core/manager/        |     | ManagedFlowController      |
| detailed stages      |     | provider/tool/checkpoints  |
+----------+-----------+     +-------------+--------------+
           \                           /
            \                         /
             +---- canonical Flow OS -+
                        |
                        v
            tools / sandbox / browser
                        |
                        v
              typed runtime evidence
                        |
        +---------------+----------------+
        |                                |
        v                                v
 provenance / lineage             QA / rendered truth
        |                                |
        +---------------+----------------+
                        |
                        v
                 run evaluation
                        |
                        v
             bounded advisory memory
```

## 4. Capability / ownership matrix

| Capability | Canonical owner today | Reconciliation status | Brain OS implication |
|---|---|---|---|
| Natural-language interpretation | `core/runtime/flow_os/task_context.py` | KEEP | Brain frames above it; do not replace it casually |
| Change-surface classification | `core/runtime/flow_os/task_context.py` + adaptive surface runtime | KEEP | Reuse in Brain TaskFrame |
| Declarative flow definitions | `skills_UIUX/flows/*.json` | KEEP | Brain calls planner; user should not select flows manually |
| Flow planning / skill resolution | `core/runtime/flow_os/flow.py` | KEEP | Brain cannot invent competing stage order |
| Specialist knowledge | `skills_UIUX/<skill>/SKILL.md` | KEEP | Future Knowledge OS complements, not copies blindly |
| Runtime policy / authority | `skills_UIUX/runtime/runtime-policy.json` | KEEP | Brain cannot elevate authority |
| Full Factory lifecycle | `core/manager/` | KEEP | Product execution substrate |
| Managed CLI lifecycle | `core/runtime/flow_os/managed.py` | KEEP / ADAPT | Controller, not second Development Manager |
| Factory detailed-stage adapter | `core/orchestration/intelligent_flow.py` | KEEP / ADAPT | Continue mapping canonical stages to specialist stages |
| Legacy runtime imports | `skills_UIUX/runtime/*.py` | DEPRECATE LATER | Compatibility only; no new logic |
| Factory internal AI provider | `core/runtime/free_provider.py` | ADAPT / CONVERGE | Avoid third provider surface |
| Provider-neutral runtime | `core/runtime/flow_os/provider*.py` | KEEP | Future adapters should target common capability contract |
| Runtime evidence records | `core/runtime/flow_os/evidence.py` | KEEP | Existing trusted-evidence backbone |
| Browser evidence | Flow OS browser adapters + `uiux-factory/qa/` | KEEP | Brain observes through evidence, not model claims |
| Fine-grained provenance | `core/provenance/evidence_lineage.py` | KEEP / EXTEND | Future Evidence Graph must adapter/extend this |
| Release evidence registry | `core/provenance/release_evidence_registry.py` | KEEP | Preserve release truth semantics |
| Run evaluation | `core/evaluation/run_evaluator.py` | KEEP / EXTEND | Brain scorecard aggregates; does not replace terminal truth |
| Evaluation/quality memory | `core/memory/evaluation_memory.py` | KEEP / EXTEND | Add typed rationale/decision memory later without weakening boundary |
| Visual critic | `core/agents/visual_critic.py` | ADAPT | First critic in future Critique Orchestrator |
| Domain/product benchmark corpus | `core/benchmarks/`, `benchmarks/corpus/` | KEEP | Unified benchmark references versioned corpus |
| Provider-neutral reliability eval | `skills_UIUX/scripts/eval-harness.py` | KEEP | Aggregate into Brain scorecard later |
| GitHub external control plane | external-agent workflows/scripts | KEEP | Transport/control only; not LLM execution evidence |
| Brain reasoning/control plane | none | NEW | May be added only above canonical runtime |
| Semantic Knowledge OS | no single canonical subsystem | NEW | Must have explicit schema/retrieval owner |
| Unified multi-critic orchestration | none | NEW | Adapt current VisualCritic |
| Hypothesis/decision ledger | no canonical general ledger | NEW | May reference current evidence/provenance IDs |
| Unified Brain benchmark scorecard | none | NEW | Aggregate existing evaluations instead of replacing them |

## 5. Duplicate/overlap classification

### 5.1 Resolved duplicate

**Old concern:** `uiux-factory` and `skills_UIUX/runtime` both implement Flow OS behavior.

**Current truth:** resolved by A4. Legacy runtime Python names re-export canonical Factory classes and are covered by class-identity tests.

Decision: **do not revisit this consolidation in Brain OS.**

### 5.2 Intentional adapter overlap

#### Factory DevelopmentManager vs ManagedFlowController

These are not equivalent owners:

- Factory DevelopmentManager owns the detailed product lifecycle and specialist sequence;
- ManagedFlowController owns managed checkpoint/stage lifecycle for the provider-neutral CLI.

Decision: **KEEP**, but Brain OS must not add another top-level manager.

#### Flow OS browser evidence vs `uiux-factory/qa/`

These differ in integration depth:

- Flow OS consumes/emits bounded runtime evidence records;
- QA harness performs broader browser/render/state/deployment checks.

Decision: **KEEP both**, normalize via evidence adapters rather than merging code mechanically.

### 5.3 Remaining convergence concern

#### Provider paths

Current paths:

```text
core/runtime/free_provider.py
core/runtime/flow_os/provider*.py
```

They serve different current product/managed lanes but represent a future convergence opportunity.

Decision: **ADAPT / CONVERGE later**. Do not add a third Brain-specific provider abstraction.

### 5.4 Distributed-but-complementary evidence surfaces

Current evidence truth is distributed across:

```text
core/runtime/flow_os/evidence.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
uiux-factory/qa/
```

This distribution is not permission to create a new independent Evidence Graph store.

Decision: future Brain Evidence Graph = **logical relationship/adaptor layer over current evidence**.

## 6. Brain OS target fit after reconciliation

The target Brain OS remains viable if it is interpreted as:

```text
Control / reasoning layer
+ typed hypothesis / decision contracts
+ evidence relationship graph
+ memory orchestration
+ critique routing/synthesis
+ unified evaluation reporting
```

placed **above** current execution owners.

It must not become:

```text
BrainRuntime
→ BrainFlowPlanner
→ BrainProvider
→ BrainEvidence
→ BrainGates
```

running beside Factory/Flow OS.

## 7. Roadmap corrections caused by A40.1

### A41 — Brain Contracts

Still valid. No current canonical general-purpose `BrainTaskFrame`, hypothesis, decision, uncertainty or repair-link contract was identified.

### A42 — Evidence Graph

**Change required:** do not build from zero.

A42 should:

1. inventory `EvidenceRecord`, provenance schemas, evidence lineage and release registry;
2. define adapters/relationship edges between existing IDs;
3. add only missing Brain relationships such as hypothesis → decision → critique → repair → retest;
4. preserve trusted/untrusted semantics from existing evidence code.

### A43 — Brain → Flow OS Adapter

Still valid, but it should wrap the already-canonical `GoalInterpreter`/`FlowPlanner`, not duplicate `change_surface` or flow selection logic.

### A44 — Critique Orchestrator

Still valid. Current `VisualCritic` becomes an adapter/first critic.

### A45 — Reasoning Planner

Still valid. Planner actions must route into existing execution/controller APIs.

### A46 — Persistent Memory

**Change required:** extend current `EvaluationMemoryStore` or add a typed sibling store with shared safety invariants. Do not silently replace the working evaluation-memory contract.

### A47 — Knowledge OS

Still new. Keep methodology/declarative ownership separate from runtime Python.

### A51 — Unified Evaluation

**Change required:** aggregate current benchmark corpus, runtime evaluator, dogfood workflows and eval harness. Do not create a scorecard that erases provenance or changes existing PASS semantics.

## 8. Risks discovered

### R1 — Architecture docs can lag executable truth

A1 docs remained labelled current even after A4 consolidation. Mitigation: A40.2 should add architecture regression tests/checks for canonical ownership assertions.

### R2 — Brain OS could duplicate existing evidence/provenance

The target architecture's proposed Evidence Graph overlaps partly with real existing primitives. Mitigation: adapter-first A42.

### R3 — Provider convergence can be confused with runtime consolidation

Two provider paths remain, but the Flow OS runtime itself is consolidated. Mitigation: document them separately and forbid a third provider policy surface.

### R4 — Detailed Factory stages can look like a second flow definition

`DevelopmentManager.FLOW` and `ProfessionalWebsiteFlow` expose detailed stage vocabulary while canonical high-level flow selection is declarative. Mitigation: preserve the adapter boundary; later convergence should be explicit and regression-tested.

### R5 — Brain memory could weaken current evidence boundaries

Existing memory is intentionally advisory and post-flow-selection. Mitigation: any new semantic/decision memory inherits the same no-gate/no-authority invariants by default.

## 9. A40.1 acceptance checklist

- [x] Current `main` SHA recorded.
- [x] Historical A1 baseline retained as history, not current truth.
- [x] A4 canonical runtime consolidation reflected in architecture docs.
- [x] Product manager, Flow OS, skills, policy, evidence, provenance, QA, evaluation and memory owners identified.
- [x] Compatibility shims distinguished from executable runtime.
- [x] Remaining provider/lifecycle overlaps classified rather than hand-waved.
- [x] Existing evidence/provenance primitives identified so A42 will not duplicate them.
- [x] Existing VisualCritic identified so A44 will adapt it.
- [x] Existing evaluation memory identified so A46 will extend rather than overwrite it.
- [x] Existing benchmark/eval surfaces identified so A51 will aggregate them.
- [x] Brain OS constrained to an intelligence/control layer above canonical execution.

## 10. Handoff to A40.2

A40.2 should add executable architecture guardrails for the invariants documented here, especially:

```text
single executable Flow OS owner
compatibility-only legacy runtime wrappers
Brain cannot own gate/authority/release
memory cannot satisfy current evidence
provider claims cannot become trusted evidence
Brain Evidence Graph must reference current evidence primitives
no third runtime/provider policy surface
```

A41 must not begin until those guardrails pass CI.
