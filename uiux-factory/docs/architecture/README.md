# Architecture Truth Index

Status: **A40–A47 MERGED + A48.1–A48.5 MERGED + A48.6 CONTROLLED PROVIDER INTEGRATION IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@abc25946ca37d5b9f155056e616de120b093e9ad`

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
26. `A48-PROVIDER-PARITY-DOGFOOD.md` — deterministic provider-contract parity plus project-profile compatibility smoke.
27. `A48-CONTROLLED-PROVIDER-INTEGRATION.md` — explicit manager lane selection, legacy default, rollback and provider-lane provenance.

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas and runtime policy. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS is an implemented bounded reasoning/control layer under `uiux-factory/core/brain_os/`. It adds contracts, adapters, critique, repair proposals, evidence relationships, typed semantic memory and scorecard aggregation above canonical runtime/evidence/evaluation owners. It is not a third execution runtime.

## Evidence / evaluation truth

Canonical evidence truth remains owned by:

```text
core/runtime/flow_os/evidence.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
uiux-factory/qa/
```

Canonical terminal runtime evaluation remains owned by `core/evaluation/run_evaluator.py`. A42/A47 relationship, integrity and scorecard surfaces reference/aggregate these owners without replacing evidence truth or terminal runtime outcome.

## Flow / JIT / critique / repair boundary

A43 reuses canonical `classify_change_surface` and `FlowPlanner`; Brain can record selection and propose only bounded adjacent escalation. JIT context cannot add non-routed skills, raise budgets or claim activation occurred.

A44 critics remain advisory-only. A45 repair synthesis creates only `PROPOSED/PENDING` repair lineage and deliberately stops before execution/verification. No Brain critic/repair surface can manufacture trusted evidence or runtime gate PASS.

## Typed memory / scorecard boundary

A46 typed historical memory is project-scoped, provenance-bearing and attached only after canonical flow selection. It cannot become current-run evidence, select/replan a flow or satisfy gates.

A47 provenance-aware scorecard mirrors canonical `RunEvaluation.outcome` verbatim and keeps critic/integrity channels separate. It has no synthetic PASS, release-readiness or numeric overall score.

## Provider convergence boundary

A48.2 records provider capability gaps and proves direct substitution unsafe. A48.3 adds the bounded optional raw `artifact` carrier to canonical `ProviderStageResponse` without changing evidence/gate truth.

A48.4 adds `ManagedArtifactCompletionAdapter`, preserving Factory async `complete(...) -> str` while offloading synchronous managed providers through `asyncio.to_thread(...)`. The adapter uses a dependency-light shared compatibility contract for context/call/token/timeout limits and lazy-loads the legacy transport only in explicit `from_env()` construction.

A48.5 adds deterministic provider parity under:

```text
benchmarks/provider-parity-v1.json
core/benchmarks/provider_parity_regression.py
scripts/validate_provider_parity_benchmark.py
```

It checks legacy `complete()` shape by AST, representative plain/JSON/frontend artifact contracts, provider preference, transient fallback, malformed/authority-bearing carrier rejection and compatibility smoke for every registered Nova/Lumen/CENNEXT/LuxRoom dogfood profile.

A48.5 output is explicitly scoped as:

```text
offline_contract_parity_not_live_provider_or_product_evidence
```

A48.6 wires the compatibility adapter into the Factory manager behind one explicit migration flag:

```text
UIUX_FACTORY_PROVIDER_LANE=managed_compat
```

The default remains `legacy` when the flag is absent. Allowed values are only `legacy` and `managed_compat`; unknown values fail closed. There is no automatic cross-lane fallback. AI-engine runs persist secret-free `provider-lane.json` execution provenance, but that artifact has no evidence/gate/release authority.

Provider default migration remains a separate governance decision requiring stronger live-provider evidence; A48.6 does not make it.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity corpora before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. Provider/runtime changes also trigger A13 Nova and A14 golden/canary regression.

## Remaining architecture debt

1. Provider convergence now has a controlled opt-in lane, but `legacy` remains the default. Any future default migration requires separate live-provider evidence and an explicit governance decision.
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

After A48.6 is green and merged, move to **A49.1 — Lifecycle Contract Reconciliation**. Map Factory and managed top-level lifecycle phases, inputs/outputs, evidence, authority and side effects before attempting any lifecycle adapter. Do not combine provider default migration with lifecycle convergence.