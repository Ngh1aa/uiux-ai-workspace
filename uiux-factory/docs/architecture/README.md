# Architecture Truth Index

Status: **A40–A50.2 MERGED + A50.3 CURATED SEED KNOWLEDGE / PROJECT DOGFOOD IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@2516b85e0e0f3fb6d7792470b867152b3220f47d`

This directory contains current architecture truth for UIUX Factory / Flow OS / Brain OS evolution. Current source and executable tests remain authoritative when older A-series prose disagrees with this index.

## Read order

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, owners and remaining convergence debt.
2. `MIGRATION-BOUNDARIES.md` — active post-A4 architecture contract and Brain OS boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` — capability/ownership reconciliation.
4. `A40-ARCHITECTURE-GUARDRAILS.md` — executable architecture invariants.
5. `A41-BRAIN-CORE-CONTRACTS.md` — BrainTaskFrame / Uncertainty / Hypothesis / Decision contracts.
6. `A41-CRITIQUE-REPAIR-CONTRACTS.md` — critique / root-cause / repair / retest contracts.
7. `A42-EVIDENCE-GRAPH-FOUNDATION.md` — evidence relationship graph.
8. `A42-EVIDENCE-INTEGRITY.md` — evidence truth protection.
9. `A43-FLOW-SELECTION-ENGINE.md` — canonical routing adapter.
10. `A43-JIT-CONTEXT-LOADER.md` — mandatory/JIT skill projection.
11. `A43-ROUTING-BENCHMARK.md` — routing regression corpus.
12. `A44-CORE-DESIGN-CRITICS.md` — core design critic pack.
13. `A44-PRODUCT-TRUTH-CRITICS.md` — product/runtime/evidence critic pack.
14. `A45-CRITIQUE-REPAIR-ORCHESTRATOR.md` — proposal-only repair orchestration.
15. `A45-REPAIR-LINEAGE-GRAPH.md` — proposed repair lineage projection.
16. `A45-REPAIR-PROPOSAL-BENCHMARK.md` — repair policy regression.
17. `A46-TYPED-BRAIN-MEMORY.md` — typed advisory memory contracts.
18. `A46-MEMORY-RECALL-CONTEXT.md` — post-routing historical-memory context.
19. `A46-MEMORY-BOUNDARY-BENCHMARK.md` — memory truth/scope regression.
20. `A47-BRAIN-SCORECARD.md` — provenance-aware scorecard aggregation.
21. `A47-SCORECARD-BENCHMARK.md` — scorecard truth regression.
22. `A48-ARCHITECTURE-TRUTH-RECONCILIATION.md` — post-A47 architecture reconciliation.
23. `A48-PROVIDER-CAPABILITY-RECONCILIATION.md` — provider capability gap map.
24. `A48-PROVIDER-ARTIFACT-BRIDGE.md` — bounded raw artifact carrier.
25. `A48-MANAGED-PROVIDER-COMPAT-ADAPTER.md` — async Factory completion adapter.
26. `A48-PROVIDER-PARITY-DOGFOOD.md` — deterministic provider parity + project-profile smoke.
27. `A48-CONTROLLED-PROVIDER-INTEGRATION.md` — explicit managed provider lane and rollback.
28. `A49-LIFECYCLE-CONTRACT-RECONCILIATION.md` — Factory vs managed lifecycle comparison contract.
29. `A49-LIFECYCLE-ADAPTER-PARITY.md` — read-only lifecycle projection + parity regression.
30. `A50-KNOWLEDGE-OS-ARCHITECTURE.md` — knowledge ownership/taxonomy.
31. `A50-BOUNDED-KNOWLEDGE-RETRIEVAL.md` — deterministic post-routing retrieval/index.
32. `A50-CURATED-SEED-KNOWLEDGE-DOGFOOD.md` — three-source seed governance and Nova/Lumen/CENNEXT retrieval dogfood.

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is `uiux-factory/core/runtime/flow_os/`. `skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas, runtime policy and reusable Knowledge OS metadata/content. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS under `uiux-factory/core/brain_os/` is a bounded reasoning/control layer. It adds typed contracts, adapters, critique, repair proposals, evidence relationships, semantic memory, scorecard aggregation and deterministic knowledge retrieval above canonical runtime/evidence/evaluation owners. It is not a third execution runtime.

## Evidence / evaluation truth

Canonical evidence truth remains owned by `core/runtime/flow_os/evidence.py`, `core/provenance/`, and `uiux-factory/qa/`. Canonical terminal runtime evaluation remains owned by `core/evaluation/run_evaluator.py`. Brain surfaces may reference or aggregate those owners but cannot manufacture current truth or runtime PASS.

## Provider convergence boundary

A48 establishes controlled provider convergence. `ManagedArtifactCompletionAdapter` preserves Factory async `complete(...) -> str`; offline provider parity is benchmarked; `UIUX_FACTORY_PROVIDER_LANE=managed_compat` is explicit opt-in while `legacy` remains default. There is no automatic cross-lane fallback and provider-lane provenance has no evidence/gate/release authority.

Provider default migration remains a separate governance decision requiring stronger live-provider evidence.

## Lifecycle boundary

A49 uses the comparison vocabulary:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

The vocabulary and `LifecycleProjection` are read-only observability surfaces, not a third state machine. Factory completion does not imply production release; Managed completion does not imply worktree finalization or release. Unknown stages fail safe instead of being guessed.

## Knowledge OS boundary

The ownership split remains:

```text
SKILL     = procedural methodology / how to perform work
KNOWLEDGE = reusable domain/reference context
MEMORY    = project/run-specific rationale, hypotheses, decisions and history
EVIDENCE  = current provenance-bearing observed truth
```

Canonical owners:

```text
skills_UIUX/knowledge/                         declarative knowledge
skills_UIUX/knowledge/index.json              explicit canonical index
skills_UIUX/schemas/knowledge-*.schema.json   metadata/index contracts
core/brain_os/knowledge_retrieval.py          deterministic retrieval
core/brain_os/adapters/knowledge_context.py   post-routing context adapter
```

Retrieval runs only after a `FlowSelectionDecision` exists and a stage is known. It remains deterministic, context-bounded, provenance-bearing and vector-free.

All knowledge outputs remain:

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

### A50.3 canonical seed

The canonical index now contains exactly three curated records:

```text
financial-services  → Unicode CLDR / UTS #35 number/currency reference
art-culture         → IIIF Presentation API 3.0 cultural-object metadata/rights reference
industrial-services → U.S. DOE Motor Systems repair/system-performance reference
```

The corpus is deliberately small. It stores concise paraphrased domain/reference context, not copied source articles and not skill procedures.

Existing methodology remains outside Knowledge OS, including financial workflow/state/evidence reasoning, asset/art-direction procedure and accessibility workflow. Regression guards reject a parallel `SKILL.md` corpus and common procedural skill-section structure in seed content.

### A50.3 project dogfood

Main CI evaluates the canonical corpus against three project profiles:

```text
Nova    / financial-services  / implementation → financial record only
Lumen   / art-culture         / research       → IIIF record only
CENNEXT / industrial-services / research       → DOE record only
```

For each case, the other two records must be excluded by `domain_mismatch`. The dogfood measures retrieval precision/isolation only; it is not product-quality, user-validation or product-outcome evidence.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity/lifecycle-parity/knowledge-retrieval corpora plus curated project retrieval dogfood before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. A13 continues real Nova browser dogfood when path-triggered.

A50 regression now covers source provenance, exact three-record seed governance, knowledge-vs-skill separation, cross-domain isolation, freshness, context budgets, traversal fail-closed behavior and post-routing flow immutability.

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default pending separate live-provider/governance evidence.
2. Lifecycle convergence remains intentionally read-only at the reconciliation/projection/parity layer; mutation-level unification requires a separate decision.
3. Knowledge OS has only three curated domain records. Broader categories are intentionally unpopulated until usefulness/noise/duplication are measured.
4. Project dogfood proves deterministic retrieval fit for selected contexts, not whether reasoning or product outcomes improve.
5. Time-sensitive factual/regulatory claims still require current source verification; Knowledge OS does not replace research/evidence acquisition.
6. Vector/semantic retrieval remains deferred.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

Proceed to **A50.4 — Knowledge Usefulness Evaluation + Corpus Governance** only after A50.3 is green and merged. Compare representative context/reasoning with vs without the seed, measure actionability and duplication/noise, and make explicit KEEP / REVISE / REMOVE / EXPAND decisions before adding broader knowledge. Vector search remains deferred.
