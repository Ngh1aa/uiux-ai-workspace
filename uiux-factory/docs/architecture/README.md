# Architecture Truth Index

Status: **A40–A47 MERGED + A48.1–A48.3 MERGED + A48.4 COMPATIBILITY ADAPTER IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@244ec6ff8c2fe74d5103f83cebaa6cdab00d8eeb`

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
23. `A48-PROVIDER-CAPABILITY-RECONCILIATION.md` — executable parity/gap map for Factory and managed free-tier provider entry paths.
24. `A48-PROVIDER-ARTIFACT-BRIDGE.md` — bounded optional raw-artifact field on the canonical managed provider response.
25. `A48-MANAGED-PROVIDER-COMPAT-ADAPTER.md` — opt-in async Factory-completion adapter over existing managed providers.

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas and runtime policy. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS is an implemented bounded reasoning/control layer under:

```text
uiux-factory/core/brain_os/
```

It adds contracts, adapters, critique, repair proposals, evidence relationships, typed semantic memory and scorecard aggregation above canonical runtime/evidence/evaluation owners. It is not a third execution runtime.

## Evidence / evaluation truth

Canonical evidence truth remains owned by:

```text
core/runtime/flow_os/evidence.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
uiux-factory/qa/
```

Canonical terminal runtime evaluation remains owned by:

```text
core/evaluation/run_evaluator.py
```

A42/A47 relationship, integrity and scorecard surfaces reference/aggregate these owners without replacing evidence truth or terminal runtime outcome.

## Flow / JIT / critique / repair boundary

A43 reuses canonical `classify_change_surface` and `FlowPlanner`; Brain can record selection and propose only bounded adjacent escalation. JIT context cannot add non-routed skills, raise budgets or claim activation occurred.

A44 critics remain advisory-only. A45 repair synthesis creates only `PROPOSED/PENDING` repair lineage and deliberately stops before execution/verification. No Brain critic/repair surface can manufacture trusted evidence or runtime gate PASS.

## Typed memory boundary

A46 typed historical memory lives under:

```text
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
```

It is project-scoped, provenance-bearing and attached only after canonical flow selection. Historical memory cannot become current-run evidence, select/replan a flow or satisfy gates.

## Scorecard boundary

A47 provenance-aware aggregation lives under:

```text
core/brain_os/scorecard.py
```

It mirrors canonical `RunEvaluation.outcome` verbatim and keeps critic/integrity channels separate. It has no synthetic PASS, release-readiness or numeric overall score.

## Provider convergence boundary

A48.2 records the current provider capability gaps and proves direct substitution is unsafe. A48.3 adds the missing bounded optional raw `artifact` carrier to canonical `ProviderStageResponse` without changing evidence/gate truth.

A48.4 adds the opt-in migration bridge:

```text
core/runtime/flow_os/factory_provider_adapter.py
::ManagedArtifactCompletionAdapter
```

The adapter preserves the Factory async `complete(...) -> str` caller shape while delegating synchronous `run_stage(...)` work through `asyncio.to_thread(...)`. It reuses Factory context/call budgets, provider ordering, bounded retry/fallback and history semantics.

Compatibility responses are strictly local neutral carriers:

```text
status = CONTINUE
actions = []
evidence = []
replan_signal = null
artifact = raw output
```

The carrier status never reaches `ManagedFlowController` as a lifecycle decision. Any PASS/FAIL/BLOCKED, tool action, evidence or replan signal in compatibility mode fails closed.

A48.4 is **not wired into `core/manager/` by default**. The current Factory manager still constructs `FreeProvider.from_env(...)`; therefore current default production behavior remains unchanged.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard corpora before the full pytest suite. A20 release-candidate verification continues to run full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. Provider/runtime changes also trigger A13 Nova and A14 golden/canary regression where path filters apply.

## Remaining architecture debt

1. Provider execution convergence is still opt-in only. A48.5 must prove parity/dogfood across representative Factory completion contracts before manager/default integration is considered.
2. Factory product execution (`run.py` + `core/manager/`) and managed CLI execution share routing/runtime owners but still expose distinct top-level lifecycle APIs.
3. A broader declarative Knowledge OS is not implemented as one canonical subsystem; methodology remains correctly owned by `skills_UIUX`.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

After A48.4 is green and merged, A48.5 should run **provider parity + opt-in dogfood** across plain text, JSON artifacts, frontend bundle contracts, invalid output, transient failures and call-budget/history behavior. No manager/default migration should occur until that evidence is green.