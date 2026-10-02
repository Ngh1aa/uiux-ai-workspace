# Architecture Truth Index

Status: **A40–A50.5 MERGED + A50.5R KNOWLEDGE REVISION / ROUND 2 IMPLEMENTED — HUMAN REVIEW PENDING**  
Audit date: **2026-10-02**  
Current merged architecture baseline before A50.5R: `main@a95df7102dda40dae25a6032fff94017326664a2`

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
33. `A50-KNOWLEDGE-USEFULNESS-GOVERNANCE.md` — deterministic usefulness proxies and corpus expansion governance.
34. `A50-KNOWLEDGE-VALUE-TRIAL.md` — round-one model-assisted A/B trial, completed human review and `REVISE_BEFORE_EXPANSION` result.
35. `A50-KNOWLEDGE-REVISION-ROUND2.md` — targeted Nova/CENNEXT knowledge revision and round-two blind trial contract.

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

The canonical index still contains exactly three curated records:

```text
financial-services  → Unicode CLDR / UTS #35 number/currency reference
art-culture         → IIIF Presentation API 3.0 cultural-object metadata/rights reference
industrial-services → U.S. DOE Motor Systems repair/system-performance reference
```

The corpus is deliberately small. It stores concise paraphrased domain/reference context, not copied source articles and not skill procedures.

Main CI dogfoods retrieval against Nova, Lumen and CENNEXT. Each project must retrieve only its intended domain record while the other two records are excluded by `domain_mismatch`.

### A50.4 usefulness and corpus governance

A50.4 evaluates deterministic proxies:

```text
actionable_delta
domain_specificity
skill_duplication_clear
retrieval_noise_clear
provenance_clear
context_budget_clear
```

Allowed record decisions remain:

```text
KEEP
REVISE
REMOVE
```

Deterministic checks cannot establish human usefulness or model-output improvement, so they cannot authorize corpus expansion.

### A50.5 round-one human result

Round one compared baseline vs knowledge-assisted outputs for Nova, Lumen and CENNEXT under the same five-dimension rubric.

The human review was completed before unblinding. After mapping was opened:

```text
Nova     → knowledge preferred
Lumen    → knowledge preferred
CENNEXT  → tie
baseline preferred = 0
material regressions = 0
```

However, only Lumen had the knowledge-assisted condition strictly higher on **both** `specificity_actionability` and `decision_usefulness`. The unchanged evaluator therefore derived:

```text
REVISE_BEFORE_EXPANSION
```

The threshold was not changed to fit the review result.

### A50.5R revision and round-two trial

A50.5R revises only the two underperforming existing records:

```text
Nova
  locale/currency correctness retained
  + shared formatting boundary
  + explicit locale fallback
  + concrete QA matrix

CENNEXT
  technical claim taxonomy retained
  + buyer decision path
  + traceable proof modules
  + approval / repair-vs-replace decision support
```

Lumen remains the unchanged control.

Round-two surfaces are versioned separately:

```text
benchmarks/knowledge-value-trial-v2.json
benchmarks/knowledge-value-trial-mapping-v2.json
benchmarks/knowledge-value-human-reviews-v2.json
benchmarks/knowledge-value-review-packet-v2.md
```

Nova and CENNEXT keep their round-one baseline outputs exactly fixed. Only their knowledge-assisted outputs change. Lumen keeps the same control pair with A/B position swapped. This makes the revision effect more interpretable than regenerating both sides.

Round-two blinding is still procedural, not cryptographic. Prior exposure to round-one outputs creates a documented same-reviewer carryover risk.

Until the new human review is complete:

```text
HOLD_PENDING_HUMAN
expand_allowed = false
auto_mutation_allowed = false
```

The positive threshold remains unchanged:

```text
material_regression_count = 0
baseline_preferred_count = 0
knowledge_preferred_count >= 2 of 3
knowledge condition strictly stronger on both:
  specificity_actionability
  decision_usefulness
in at least 2 of 3 cases
```

Even a later `CONSIDER_EXPANSION` remains advisory and cannot mutate the canonical index.

Benchmark scope remains:

```text
model_assisted_blind_pair_trial_not_human_or_product_evidence
```

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity/lifecycle-parity/knowledge-retrieval corpora, curated project retrieval dogfood, knowledge-usefulness governance and both versioned knowledge-value trial states before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. A13 continues real Nova browser dogfood when path-triggered.

A50 regression covers source provenance, exact three-record seed governance, knowledge-vs-skill separation, cross-domain isolation, freshness, context budgets, traversal fail-closed behavior, post-routing flow immutability, usefulness proxy boundaries, paired-trial provenance, non-fabricated human review fields, round-one history, round-two baseline preservation, mixed A/B mappings and the corpus-expansion block.

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default pending separate live-provider/governance evidence.
2. Lifecycle convergence remains intentionally read-only at the reconciliation/projection/parity layer; mutation-level unification requires a separate decision.
3. A50.5 round one established `REVISE_BEFORE_EXPANSION`; A50.5R round-two human review is pending.
4. Broader Knowledge OS categories remain intentionally unpopulated and corpus expansion remains blocked until round two satisfies the unchanged governance threshold.
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

Complete the **A50.5R round-two human review** using `benchmarks/knowledge-value-review-packet-v2.md`. Update only `benchmarks/knowledge-value-human-reviews-v2.json` with blind judgments first, then let the unchanged evaluator derive `CONSIDER_EXPANSION` or `REVISE_BEFORE_EXPANSION`.

Only if round two derives `CONSIDER_EXPANSION` should a separate **A50.6 Corpus Expansion Proposal** be opened. Vector search remains deferred.
