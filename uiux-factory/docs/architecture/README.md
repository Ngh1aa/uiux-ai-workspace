# Architecture Truth Index

Status: **A40–A49.3 MERGED + A50.1 KNOWLEDGE OS ARCHITECTURE IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@f3db05ddb1fedcd04ae3605c411af4a4bf5982c9`

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

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is `uiux-factory/core/runtime/flow_os/`. `skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas, runtime policy and reusable Knowledge OS metadata/content. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS is an implemented bounded reasoning/control layer under `uiux-factory/core/brain_os/`. It adds contracts, adapters, critique, repair proposals, evidence relationships, typed semantic memory, scorecard aggregation and a typed Knowledge OS read model above canonical runtime/evidence/evaluation owners. It is not a third execution runtime and does not own declarative knowledge content.

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

A49.2 projects Factory `RunContext`-like and Managed `ManagedWebsiteRun`-like snapshots into `LifecycleProjection` for observability/comparison only. Unknown managed stages fail safe instead of being guessed. Factory completion never implies production release, and Managed completion never implies workspace finalization/release.

A49.3 locks those semantics with deterministic lifecycle-parity regression. A PASS remains projection regression evidence only, not product/runtime/release evidence.

## Knowledge OS boundary

A50.1 establishes the declarative Knowledge OS owner:

```text
skills_UIUX/knowledge/
```

and metadata schema:

```text
skills_UIUX/schemas/knowledge-record.schema.json
```

The typed Brain read model lives at:

```text
core/brain_os/knowledge_contracts.py
```

The hard ownership split is:

```text
SKILL     = procedural methodology / how to perform work
KNOWLEDGE = reusable principles, domain context, patterns and references
MEMORY    = project/run-specific rationale, hypotheses, decisions and history
EVIDENCE  = current provenance-bearing observed truth
```

Knowledge records are advisory-only and fixed to:

```text
current_run_evidence = false
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

A50.1 reserves seven categories: `foundations`, `product`, `research`, `management`, `domain`, `pattern`, `platform`.

A50.1 intentionally creates no knowledge corpus, no retrieval runtime and no vector database. Existing `SKILL.md` bodies must not be bulk-copied into the Knowledge OS. Project memory and current-run evidence IDs cannot become knowledge ownership refs.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity/lifecycle-parity corpora before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood.

A50.1 adds architecture drift tests for knowledge ownership, taxonomy/schema parity, no memory/evidence ownership refs, no parallel `SKILL.md` corpus, and explicit `retrieval_implemented=false` / `vector_database_required=false`.

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default pending separate live-provider/governance evidence.
2. Lifecycle convergence is complete at the **read-only reconciliation/projection/parity layer**. No mutable shared lifecycle state machine has been introduced; any mutation-level unification requires a separate architecture decision.
3. Knowledge OS architecture/ownership is defined, but deterministic bounded retrieval, freshness enforcement, corpus validation and retrieval benchmarking are not implemented yet.
4. Real reusable knowledge content has not been authored or validated; A50.1 intentionally avoids inventing a corpus.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

Proceed to **A50.2 — Bounded Knowledge Retrieval + Index** only after A50.1 is green and merged. Implement deterministic metadata-first retrieval after canonical task/flow context is known, with explicit freshness/context budgets and retrieval provenance. Keep knowledge advisory-only and do not introduce vector search until deterministic retrieval has regression coverage and real-project dogfood evidence.
