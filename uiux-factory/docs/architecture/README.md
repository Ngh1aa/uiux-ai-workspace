# Architecture Truth Index

Status: **A40–A48.6 MERGED + A49.1 LIFECYCLE CONTRACT RECONCILIATION IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@47c1aa143b14eb07ce68ae8387a51fcb14506025`

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
28. `A49-LIFECYCLE-CONTRACT-RECONCILIATION.md` — executable comparison contract for Factory product lifecycle vs managed checkpoint lifecycle.

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

A48.4 adds `ManagedArtifactCompletionAdapter`, preserving Factory async `complete(...) -> str` while offloading synchronous managed providers through `asyncio.to_thread(...)`. A48.5 adds deterministic provider parity across representative artifacts and registered Nova/Lumen/CENNEXT/LuxRoom profiles.

A48.6 wires the adapter into the Factory manager behind:

```text
UIUX_FACTORY_PROVIDER_LANE=managed_compat
```

The default remains `legacy`; unknown values fail closed and there is no automatic cross-lane fallback. AI-engine runs persist secret-free `provider-lane.json` execution provenance with no evidence/gate/release authority. Provider default migration remains a separate governance decision requiring stronger live-provider evidence.

## Lifecycle reconciliation boundary

A49.1 adds the descriptive executable contract:

```text
core/runtime/lifecycle_reconciliation.py
```

It compares both supported top-level experiences through ten vocabulary phases:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

This vocabulary is **not a new lifecycle runtime**. Factory remains an async product pipeline over `RunContext`; managed execution remains an explicit resumable/checkpoint lifecycle over `ManagedWebsiteRun` and resolved Flow stages.

A49.1 deliberately records non-parity instead of synthesizing false equivalence. In particular, Factory normal completion does not implicitly expose production deployment, while managed finalization/release remain separate `ProductionReleaseController` actions with explicit authority.

The reconciliation contract has:

```text
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity corpora before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. Provider/runtime changes also trigger A13 Nova and A14 golden/canary regression.

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains the default. Any future default migration requires separate live-provider evidence and explicit governance.
2. A49.1 has mapped top-level lifecycle non-parity; a future adapter may project common lifecycle events/status but must not create a third state machine or collapse release authority into completion.
3. A broader declarative Knowledge OS is not implemented as one canonical subsystem; methodology remains correctly owned by `skills_UIUX`.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

After A49.1 is green and merged, combine **A49.2 + A49.3 — Lifecycle Adapter + Parity** if the implementation remains adapter-first: project read-only lifecycle events/status from the two existing state owners, benchmark equivalent transitions, and keep Factory/Managed execution owners unchanged. Do not introduce a third lifecycle state machine.