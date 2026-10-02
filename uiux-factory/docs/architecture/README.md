# Architecture Truth Index

Status: **A40–A47 MERGED + A48.1 MERGED + A48.2 PROVIDER CAPABILITY RECONCILIATION IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@6210b9e9b2af7ac82feed8239605a5c0fcffbfae`

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

## Provider capability reconciliation

A48.2 adds a read-only parity/gap contract under:

```text
core/runtime/flow_os/provider_capabilities.py
```

It describes the two current free-tier entry paths without executing either provider:

```text
Factory: async FreeProvider.complete(...) -> raw artifact text
Managed: sync OpenAICompatibleFreeTierProvider.run_stage(...) -> ProviderStageResponse
```

Both support explicitly enabled Groq/Gemini free-tier transport, but direct object substitution is currently unsafe. The Factory lane depends on async raw-artifact completion, optional JSON mode, stage-specific budgets, multi-provider fallback and provider call history. The managed lane owns typed `ProviderStageRequest/ProviderStageResponse`, structured status/actions/evidence and managed replan semantics.

A48.2 therefore records `direct_substitution_safe=false` and `adapter_required=true`. It does not add a third provider runner/transport.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard corpora before the full pytest suite. A20 release-candidate verification continues to run full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood.

## Remaining architecture debt

1. Provider **execution** convergence is not complete. A48.2 proves capability gaps; a later opt-in adapter must preserve Factory call contracts and managed semantics before defaults change.
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

After A48.2 is green and merged, A48.3 may implement an **opt-in bounded compatibility adapter** only after parity tests prove it preserves the Factory `complete(...)` contract, async behavior, provider budget/history needs and managed structured-response semantics. No manager default should change in the same task.
