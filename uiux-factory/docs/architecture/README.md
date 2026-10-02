# Architecture Truth Index

Status: **A40–A49.1 MERGED + A49.2/A49.3 LIFECYCLE ADAPTER + PARITY IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@05b71b52d182db9c8b3a31d56622af17eee08e50`

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
29. `A49-LIFECYCLE-ADAPTER-PARITY.md` — read-only lifecycle projection plus deterministic parity regression.

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is `uiux-factory/core/runtime/flow_os/`. `skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas and runtime policy. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS is an implemented bounded reasoning/control layer under `uiux-factory/core/brain_os/`. It adds contracts, adapters, critique, repair proposals, evidence relationships, typed semantic memory and scorecard aggregation above canonical runtime/evidence/evaluation owners. It is not a third execution runtime.

## Evidence / evaluation truth

Canonical evidence truth remains owned by `core/runtime/flow_os/evidence.py`, `core/provenance/`, and `uiux-factory/qa/`. Canonical terminal runtime evaluation remains owned by `core/evaluation/run_evaluator.py`. Brain relationship/integrity/scorecard surfaces reference or aggregate those owners without replacing truth.

## Provider convergence boundary

A48.2–A48.6 establish a controlled provider convergence path. `ManagedArtifactCompletionAdapter` preserves Factory async `complete(...) -> str`; provider parity is benchmarked offline; the Factory manager exposes `UIUX_FACTORY_PROVIDER_LANE=managed_compat` as an explicit opt-in while `legacy` remains default. There is no automatic cross-lane fallback, and provider-lane provenance has no evidence/gate/release authority.

Provider default migration remains a separate governance decision requiring stronger live-provider evidence.

## Lifecycle reconciliation and projection boundary

A49.1 defines the ten comparison phases:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

This remains a comparison vocabulary, not a third lifecycle runtime.

A49.2 adds read-only projection under:

```text
core/runtime/lifecycle_projection.py
```

Factory `RunContext`-like and Managed `ManagedWebsiteRun`-like snapshots can be projected into `LifecycleProjection` for observability/comparison only. The projection never executes, advances, replans, finalizes or releases either lifecycle.

Unknown managed stages fail safe into `unmapped_native_stages` rather than being guessed. Factory completion never implies production release. Managed `state=COMPLETED` never implies workspace finalization or production release because those results belong to `ProductionReleaseController` outputs.

The projection declares:

```text
projection_only = true
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

A49.3 adds deterministic regression under:

```text
benchmarks/lifecycle-parity-v1.json
core/benchmarks/lifecycle_parity_regression.py
scripts/validate_lifecycle_parity_benchmark.py
```

The benchmark scope is explicitly `projection_parity_not_execution_or_release_evidence`. A PASS cannot prove equivalent real-run design quality, trusted evidence, runtime behavior or release readiness.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity/lifecycle-parity corpora before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood.

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default pending separate live-provider/governance evidence.
2. Lifecycle convergence is complete at the **read-only reconciliation/projection/parity layer**. No mutable shared lifecycle state machine has been introduced; any future mutation-level unification requires a separate architecture decision.
3. A broader declarative Knowledge OS is not implemented as one canonical subsystem; methodology remains correctly owned by `skills_UIUX`.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

After A49.2/A49.3 are green and merged, proceed to **A50.1 — Knowledge OS Architecture**. Define knowledge taxonomy/contracts/retrieval boundaries while preserving `skills_UIUX` as methodology owner, typed memory as project-history owner, and evidence as current-truth owner. Do not copy skill bodies into a parallel Knowledge OS.