# Architecture Truth Index

Status: **A40–A50.1 MERGED + A50.2 BOUNDED KNOWLEDGE RETRIEVAL IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@ca8f9d09318c14fdc0386b0691dffd8c4664242e`

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
30. `A50-KNOWLEDGE-OS-ARCHITECTURE.md` — declarative knowledge taxonomy, ownership and truth-boundary contract.
31. `A50-BOUNDED-KNOWLEDGE-RETRIEVAL.md` — deterministic post-routing index/retrieval, freshness and context-budget contract.

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is `uiux-factory/core/runtime/flow_os/`. `skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas, runtime policy and reusable Knowledge OS metadata/content. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS is an implemented bounded reasoning/control layer under `uiux-factory/core/brain_os/`. It adds contracts, adapters, critique, repair proposals, evidence relationships, typed semantic memory, scorecard aggregation and a typed deterministic Knowledge OS retrieval view above canonical runtime/evidence/evaluation owners. It is not a third execution runtime and does not own declarative knowledge content.

## Evidence / evaluation truth

Canonical evidence truth remains owned by `core/runtime/flow_os/evidence.py`, `core/provenance/`, and `uiux-factory/qa/`. Canonical terminal runtime evaluation remains owned by `core/evaluation/run_evaluator.py`. Brain relationship/integrity/scorecard/knowledge surfaces reference or aggregate canonical owners without replacing current truth.

## Provider convergence boundary

A48.2–A48.6 establish a controlled provider convergence path. `ManagedArtifactCompletionAdapter` preserves Factory async `complete(...) -> str`; provider parity is benchmarked offline; the Factory manager exposes `UIUX_FACTORY_PROVIDER_LANE=managed_compat` as an explicit opt-in while `legacy` remains default. There is no automatic cross-lane fallback, and provider-lane provenance has no evidence/gate/release authority.

Provider default migration remains a separate governance decision requiring stronger live-provider evidence.

## Lifecycle reconciliation and projection boundary

A49.1 defines the comparison phases `INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE`; this remains a vocabulary, not a third lifecycle runtime.

A49.2 projects Factory `RunContext`-like and Managed `ManagedWebsiteRun`-like snapshots into `LifecycleProjection` for observability/comparison only. Unknown managed stages fail safe instead of being guessed. Factory completion never implies production release, and Managed completion never implies workspace finalization/release.

A49.3 locks those semantics with deterministic lifecycle-parity regression. A PASS remains projection regression evidence only, not product/runtime/release evidence.

## Knowledge OS boundary

A50.1 established the hard ownership split:

```text
SKILL     = procedural methodology / how to perform work
KNOWLEDGE = reusable principles, domain context, patterns and references
MEMORY    = project/run-specific rationale, hypotheses, decisions and history
EVIDENCE  = current provenance-bearing observed truth
```

Canonical declarative owner:

```text
skills_UIUX/knowledge/
```

A50.2 adds the canonical empty index and deterministic retrieval layer:

```text
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-index.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

The canonical index is intentionally empty until reusable content is actually curated. Benchmark fixtures live outside the canonical corpus.

Retrieval is allowed only after a `FlowSelectionDecision` exists and a concrete stage is known. Category/domain/stage constraints are hard filters when supplied. Eligible records use transparent deterministic domain/stage/tag/term relevance points, with curatorial confidence only as a tie-breaker.

`time_sensitive` records are filtered by explicit `as_of` + `time_sensitive_max_age_days`; this is repository freshness filtering, not live source verification.

Context is bounded by record count, per-record characters and total characters. Every hit preserves record/source provenance, full-content SHA-256, delivered/source character counts and explicit truncation state.

All Knowledge OS retrieval surfaces remain:

```text
advisory_only = true
current_run_evidence = false
deterministic_metadata_first = true
vector_search_used = false
flow_effect = none
skill_activation_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

A50.2 does not auto-wire retrieval into all manager/provider stages and does not create or activate a knowledge corpus by itself.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity/lifecycle-parity/knowledge-retrieval corpora before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood.

A50.2 tests additionally cover canonical empty-index shape, deterministic domain/stage ranking, stale time-sensitive exclusion, explicit context truncation, path-traversal fail-closed behavior, and post-routing flow immutability.

Knowledge retrieval benchmark scope is explicitly:

```text
deterministic_metadata_retrieval_not_product_or_runtime_evidence
```

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default pending separate live-provider/governance evidence.
2. Lifecycle convergence is complete at the **read-only reconciliation/projection/parity layer**. No mutable shared lifecycle state machine has been introduced; any mutation-level unification requires a separate architecture decision.
3. Knowledge retrieval infrastructure exists, but the canonical knowledge index intentionally has no real records yet.
4. Retrieval usefulness, duplication risk and domain/stage fit have not yet been dogfooded against a human-curated corpus on materially different real projects.
5. Time-sensitive freshness is age-based only; current external factual claims still require appropriate source verification.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

Proceed to **A50.3 — Curated Seed Knowledge + Real-Project Retrieval Dogfood** only after A50.2 is green and merged. Add a deliberately small, traceable corpus and measure whether retrieval materially improves context on Nova, Lumen and CENNEXT without duplicating existing skill methodology. Keep vector search deferred until deterministic retrieval usefulness is proven.
