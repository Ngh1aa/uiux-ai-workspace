# Architecture Truth Index

Status: **A40 GUARDED + A41–A47 MERGED / CURRENT**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@38b11b347281cba8f8dd0b3cd6f99dcba62fdb95`

This directory contains the current architecture truth for UIUX Factory / Flow OS / Brain OS evolution. Current source and executable tests remain authoritative when older A-series prose disagrees with this index.

## Read order

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, owners and remaining convergence debt.
2. `MIGRATION-BOUNDARIES.md` — active post-A4 architecture contract and Brain OS boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` — capability/ownership reconciliation.
4. `A40-ARCHITECTURE-GUARDRAILS.md` — executable architecture invariants.
5. `A41-BRAIN-CORE-CONTRACTS.md` — BrainTaskFrame / Uncertainty / Hypothesis / Decision contracts.
6. `A41-CRITIQUE-REPAIR-CONTRACTS.md` — CritiqueIssue / RootCause / RepairDirective / RetestRequirement / RepairLink contracts.
7. `A42-EVIDENCE-GRAPH-FOUNDATION.md` — adapter-first relationship graph over canonical evidence IDs.
8. `A42-EVIDENCE-INTEGRITY.md` — false-evidence and end-to-end lineage protection.
9. `A43-FLOW-SELECTION-ENGINE.md` — Brain adapter over canonical change-surface / FlowPlanner selection.
10. `A43-JIT-CONTEXT-LOADER.md` — read-only projection of mandatory/JIT skill routing.
11. `A43-ROUTING-BENCHMARK.md` — deterministic routing regression corpus.
12. `A44-CORE-DESIGN-CRITICS.md` — advisory Visual, UX/IA, Design System and Accessibility critics.
13. `A44-PRODUCT-TRUTH-CRITICS.md` — advisory Product, Runtime and Evidence/Truth critics.
14. `A45-CRITIQUE-REPAIR-ORCHESTRATOR.md` — proposal-only critique → repair contracts.
15. `A45-REPAIR-LINEAGE-GRAPH.md` — repair proposal projection into the A42 graph.
16. `A45-REPAIR-PROPOSAL-BENCHMARK.md` — proposal-policy regression guard.
17. `A46-TYPED-BRAIN-MEMORY.md` — typed project-scoped rationale / hypothesis / decision memory.
18. `A46-MEMORY-RECALL-CONTEXT.md` — post-routing historical-memory context adapter.
19. `A46-MEMORY-BOUNDARY-BENCHMARK.md` — memory scope / truth boundary regression guard.
20. `A47-BRAIN-SCORECARD.md` — provenance-aware aggregation over canonical evaluation and advisory review channels.
21. `A47-SCORECARD-BENCHMARK.md` — scorecard truth/provenance regression guard.
22. `A48-ARCHITECTURE-TRUTH-RECONCILIATION.md` — post-A47 architecture truth reconciliation and remaining debt.

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas and runtime policy. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS is now an implemented bounded reasoning/control layer under:

```text
uiux-factory/core/brain_os/
```

It adds contracts, adapters, critique, repair proposals, evidence relationships, typed semantic memory and scorecard aggregation **above** canonical runtime/evidence/evaluation owners. It is not a third execution runtime.

It must not own provider execution, runtime gates, trusted-evidence semantics, merge/deploy/release authority or a competing stage lifecycle.

## Evidence graph boundary

A42 relationship and integrity surfaces live under:

```text
core/brain_os/reasoning/evidence_graph.py
core/brain_os/adapters/evidence.py
core/brain_os/reasoning/evidence_integrity.py
core/brain_os/reasoning/lineage_integrity.py
```

Canonical evidence truth remains owned by:

```text
core/runtime/flow_os/evidence.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
uiux-factory/qa/
```

Brain graph nodes reference/adapt canonical evidence; they do not replace it or upgrade trust.

## Flow and JIT boundary

A43 reuses canonical owners:

```text
core/runtime/flow_os/adaptive_surface.py::classify_change_surface
core/runtime/flow_os/flow.py::FlowPlanner
```

Brain can record selection and propose only bounded adjacent escalation. JIT context projects routed mandatory/default/JIT skills and policy ceilings; it cannot add non-routed skills, raise budgets, change authority/gates/evidence or claim activation occurred.

## Critique and repair boundary

A44 implements advisory critics for:

```text
Visual
UX / IA
Design System
Accessibility
Product
Runtime
Evidence / Truth
```

Every critic issue begins as `OBSERVED`; reports have no PASS field and no authority/gate/evidence effect.

A45 connects unresolved observations to existing A41 proposal contracts:

```text
CritiqueIssue
→ RootCause(PROPOSED)
→ RepairDirective(PROPOSED)
→ RetestRequirement(PENDING)
```

and projects only proposal relationships into the EvidenceGraph. It deliberately stops before execution/verification. No A45 surface can execute a repair, mark a retest PASS, resolve an issue or manufacture `VERIFIED_BY` evidence.

## Typed memory boundary

A46 adds project-scoped typed historical memory:

```text
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
```

Supported typed semantic records include design rationale, hypotheses and decisions. Memory requires provenance, uses bounded atomic project-scoped persistence, and is attached only after canonical flow selection.

Memory remains historical/advisory context only:

```text
current_run_evidence = false
flow_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
```

It cannot select/replan a flow, activate skills, validate a hypothesis, select a decision, satisfy a current-run gate or approve merge/deploy/release.

## Scorecard boundary

Canonical terminal runtime evaluation remains owned by:

```text
core/evaluation/run_evaluator.py
```

A47 adds provenance-aware aggregation under:

```text
core/brain_os/scorecard.py
```

It consumes already-produced outputs from the canonical `RunEvaluation`, A44 critic reports and A42 integrity reports. It mirrors `RunEvaluation.outcome` verbatim and does not run/recompute those evaluators.

The scorecard intentionally has no synthetic `passed`, release-readiness or numeric overall-score field. Critic and integrity channels remain distinguishable from the canonical runtime outcome.

## Regression and dogfood

Brain/runtime boundaries are protected by executable tests plus deterministic benchmark validators, including:

```text
benchmarks/routing-v1.json
benchmarks/repair-proposals-v1.json
benchmarks/memory-boundary-v1.json
benchmarks/scorecard-v1.json
```

Main UIUX Factory CI runs these validators before the full pytest suite. A20 release-candidate verification continues to run full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood.

## Remaining architecture debt

Two execution/convergence concerns remain active and must not be confused with duplicate Flow OS runtimes:

1. Factory internal provider lane `core/runtime/free_provider.py` and managed provider-neutral `core/runtime/flow_os/provider*.py` expose different provider entry/capability shapes.
2. Factory product execution (`run.py` + `core/manager/`) and managed CLI execution share routing/runtime owners but still expose distinct top-level lifecycle APIs.

A broader declarative Knowledge OS is also not implemented as one canonical subsystem; methodology still correctly belongs to `skills_UIUX` rather than being copied into Brain/provider code.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

After A48.1 is green and merged, A48.2 should audit and reconcile the **provider capability contract** between the Factory internal AI lane and canonical managed provider lane before changing execution. The goal is convergence through adapters/contracts where practical — not a third provider abstraction and not a blind replacement of working runtime paths.
