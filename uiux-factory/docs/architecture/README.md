# Architecture Truth Index

Status: **A40–A50.9B MERGED + A50.9A HUMAN REVIEW COMPLETE / ACCEPT_FOR_INDEX_TRIAL**  
Audit date: **2026-10-02**  
Current merged architecture baseline: `main@de8a466bfa3d6b71d4a648ce36763c33ba011ec3`

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
34. `A50-KNOWLEDGE-VALUE-TRIAL.md` — two versioned model-assisted A/B trials and their human governance results.
35. `A50-KNOWLEDGE-REVISION-ROUND2.md` — targeted Nova/CENNEXT revision and completed round-two verdict.
36. `A50-KNOWLEDGE-CORPUS-EXPANSION-PROPOSAL.md` — bounded proposal-only source/ownership review for potential corpus growth.
37. `A50-KNOWLEDGE-READY-CANDIDATE-DRAFT-VALIDATION.md` — two READY drafts, shadow-index retrieval/isolation and bounded usefulness proxy.
38. `A50-KNOWLEDGE-CANDIDATE-ACCEPTANCE-TRIAL.md` — completed blind candidate acceptance review before any index trial.
39. `A50-EDTECH-DRAFT-REVISION-TRIAL.md` — versioned EdTech v2 revision with concrete states/recovery and completed blind acceptance retry.
40. `A50-EV-CONTROLLED-INDEX-TRIAL.md` — verified EV canary index trial, rollback and cross-domain regression checks.

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

The corpus remains deliberately small. It stores concise paraphrased domain/reference context, not copied source articles and not skill procedures.

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

Round one completed with:

```text
Nova     → knowledge preferred
Lumen    → knowledge preferred
CENNEXT  → tie
knowledge_preferred_count = 2
baseline_preferred_count = 0
tie_count = 1
material_regression_count = 0
joint_usefulness_win_count = 1
```

The unchanged evaluator derived:

```text
REVISE_BEFORE_EXPANSION
```

### A50.5R round-two human result

A50.5R revised only Nova and CENNEXT knowledge while preserving the round-one baselines and keeping Lumen as the unchanged control.

Round-two surfaces remain versioned separately:

```text
benchmarks/knowledge-value-trial-v2.json
benchmarks/knowledge-value-trial-mapping-v2.json
benchmarks/knowledge-value-human-reviews-v2.json
benchmarks/knowledge-value-review-packet-v2.md
```

The human review was completed blind-first before unblinding. After mapping was opened:

```text
Nova     knowledge condition = A → knowledge preferred
Lumen    knowledge condition = B → knowledge preferred
CENNEXT  knowledge condition = A → knowledge preferred
```

Canonical derived counts:

```text
human_review_complete = true
reviewed_case_count = 3
knowledge_preferred_count = 3
baseline_preferred_count = 0
tie_count = 0
insufficient_count = 0
material_regression_count = 0
joint_usefulness_win_count = 3
```

The unchanged evaluator therefore derives:

```text
CONSIDER_EXPANSION
```

This recommendation is advisory only:

```text
expand_allowed = false
auto_mutation_allowed = false
```

### A50.6 proposal-only corpus expansion

A50.6 is merged and verified. It does not mutate the corpus. It adds an executable proposal review for exactly three unpopulated domain candidates:

```text
education-edtech → LTI 1.3 / LTI Advantage context
mobility-ev      → OCPP 2.1 Edition 2 charging-system context
ai-software      → NIST AI 600-1 Generative AI risk context
```

Canonical proposal status:

```text
EdTech/LTI   → READY_FOR_CONTENT_DRAFT
EV/OCPP      → READY_FOR_CONTENT_DRAFT
GenAI/NIST   → HOLD_FRESHNESS_REVIEW
```

The GenAI candidate is held because NIST states AI RMF 1.0 is being revised in 2026. Proposal symmetry is not a goal; truthful freshness handling is.

A50.6 verifies that the canonical knowledge index remains exactly three records and forbids index/record/vector mutation.

### A50.7 READY candidate drafts

A50.7 is merged and verified. It drafts only the two READY candidates under `skills_UIUX/knowledge/drafts/` and runs the real retriever against a temporary five-record shadow index:

```text
3 canonical + 2 drafts = 5 shadow records
```

Final A50.7 result:

```text
KEEP_DRAFT = 2
REVISE_DRAFT = 0
canonical index = 3
canonical_acceptance_allowed = false
human_usefulness_claimed = false
```

`KEEP_DRAFT` is not canonical `KEEP`, not corpus acceptance and not proof of human/model usefulness.

### A50.8 completed candidate acceptance trial

A50.8 completed blind human review for the two A50.7 drafts. The unchanged evaluator derived:

```text
EdTech / LTI → REVISE_DRAFT
EV / OCPP    → ACCEPT_FOR_INDEX_TRIAL
reviewed = 2/2
HOLD = 0
REJECT = 0
```

EdTech knowledge was preferred and passed correctness/risk guards, but `decision_usefulness` tied baseline (`1 == 1`), so the strict joint-usefulness gate did not clear.

EV knowledge was preferred with no material regression and was strictly better on specificity/actionability and decision usefulness while remaining non-worse on correctness and unsupported-claim risk.

Even `ACCEPT_FOR_INDEX_TRIAL` does not authorize canonical promotion:

```text
index_mutation_allowed = false
canonical_acceptance_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

The canonical index remains exactly three records.

### A50.9A completed EdTech revision retry

A50.9A preserves the v1 EdTech draft/history and adds a v2 revision with concrete launch/NRPS/Deep Linking/AGS state and recovery boundaries.

Engineering guards require:

```text
prior A50.8 EdTech verdict = REVISE_DRAFT
A50.8 baseline held fixed
v2 record remains unindexed
shadow retrieval returns only the EdTech v2 record
concrete state/recovery concepts present
canonical index = 3
vector search = false
```

The independent blind-first human review completed with:

```text
Preferred output = B
knowledge condition = B
baseline condition = A
material regression = false

A: correctness 1 / specificity 1 / relevance 2 / risk 2 / usefulness 1
B: correctness 2 / specificity 2 / relevance 2 / risk 2 / usefulness 2
```

The unchanged evaluator therefore derives:

```text
ACCEPT_FOR_INDEX_TRIAL
```

The reviewer's main remaining caveats are that the revision does not explicitly name a generic empty state and does not identify role initiators as explicitly as the older A50.8 packet. These were judged minor and not material regressions.

Deep Linking verification also clarifies that `content_selection_cancelled` is a product-level derived state, not a literal protocol status. The 1EdTech workflow permits cancellation/no-selection paths, but the state may only be used when project/implementation truth can actually distinguish that outcome.

All mutation/acceptance authority remains false:

```text
index_mutation_allowed = false
canonical_acceptance_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

### A50.9B verified EV controlled index trial

A50.9B is merged and verified. The temporary canary topology was:

```text
3 canonical records + EV/OCPP draft = 4-record canary
```

The real retriever produced:

```text
decision = CANARY_PASS
usefulness_evidence_clear = true
ev_retrieval_isolated = true
canonical_retrieval_regression_clear = true
negative_domain_isolation_clear = true
context_budget_clear = true
rollback_verified = true
genai_hold_preserved = true
promotion_proposal_allowed = true
```

The canary did not change canonical `skills_UIUX/knowledge/index.json`. Nova/Lumen/CENNEXT retrieval remained unchanged with EV present, EdTech/AI negative-domain queries did not leak into EV, and rollback restored the exact canonical record set with the canonical index bytes/hash unchanged.

`CANARY_PASS` still does not authorize canonical promotion:

```text
index_mutation_allowed = false
canonical_promotion_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

GenAI/NIST remains `HOLD_FRESHNESS_REVIEW`.

## Regression and dogfood

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider-parity/lifecycle-parity/knowledge-retrieval corpora, curated project retrieval dogfood, knowledge-usefulness governance, both versioned knowledge-value trial histories, A50.6 expansion proposal, A50.7 draft/shadow-index validation, the completed A50.8 acceptance result, the completed A50.9A EdTech human result and the A50.9B EV canary before the full pytest suite. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. A13 continues real Nova browser dogfood when path-triggered.

A50 regression covers source provenance, exact three-record seed governance, knowledge-vs-skill separation, cross-domain isolation, freshness, context budgets, traversal fail-closed behavior, post-routing flow immutability, usefulness proxy boundaries, paired-trial provenance, completed human review histories, proposal trigger integrity, skill-owner paths, draft metadata/provenance alignment, shadow-index isolation, blind acceptance mapping, all four A50.8 verdict paths, A50.9A v1-history preservation, completed-review and pending-review branches, A50.9B rollback/cross-domain regression and the no-auto-promotion boundary.

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default pending separate live-provider/governance evidence.
2. Lifecycle convergence remains intentionally read-only at the reconciliation/projection/parity layer; mutation-level unification requires a separate decision.
3. EdTech/LTI v2 now has `ACCEPT_FOR_INDEX_TRIAL` but remains unindexed until a separate controlled canary/shadow index trial passes.
4. EV/OCPP has `CANARY_PASS`; canonical promotion still requires a separate explicit promotion proposal/governance decision.
5. The GenAI/NIST candidate remains on freshness HOLD while AI RMF 1.0 is under active revision.
6. Time-sensitive factual/regulatory claims still require current source verification; Knowledge OS does not replace research/evidence acquisition.
7. Vector/semantic retrieval remains deferred.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

Two bounded follow-ups are now eligible:

1. run an EdTech controlled index trial with the same rollback, canonical-regression, cross-domain-isolation and usefulness boundaries proven by A50.9B;
2. prepare an EV canonical-promotion proposal/governance review based on the verified `CANARY_PASS`, without mutating `skills_UIUX/knowledge/index.json` until that decision is explicitly approved.

GenAI/NIST remains on freshness HOLD. Vector search remains deferred.
