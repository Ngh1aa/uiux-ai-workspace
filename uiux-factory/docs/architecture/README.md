# Architecture Truth Index

Status: **A40–A50.14 MERGED / FIVE-RECORD KNOWLEDGE OS / GENAI FRESHNESS HOLD EVIDENCED**  
Audit date: **2026-10-02**  
Current merged architecture baseline: `main@f84a3f4a606ada958a1dfa0e9f1c23c409aafb4c`

This directory contains current architecture truth for UIUX Factory / Flow OS / Brain OS. Current source and executable tests are authoritative when historical A-series notes describe an earlier topology.

## Read order

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, ownership and remaining debt.
2. `MIGRATION-BOUNDARIES.md` — runtime/Brain ownership boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` + `A40-ARCHITECTURE-GUARDRAILS.md` — architecture invariants.
4. A41–A47 — Brain contracts, evidence graph, routing/JIT, critics/repair, memory and scorecard.
5. A48 — provider capability reconciliation, artifact bridge, compatibility adapter, parity dogfood and controlled integration.
6. A49 — lifecycle contract reconciliation and read-only adapter parity.
7. `A50-KNOWLEDGE-OS-ARCHITECTURE.md` + `A50-BOUNDED-KNOWLEDGE-RETRIEVAL.md` — Knowledge OS ownership/retrieval.
8. A50.3–A50.12 — seed/value trials, candidate drafting/revision, canaries, governance and shadow-apply evidence.
9. `A50-EV-CANONICAL-APPLY.md` — EV canonical apply history.
10. `A50-EDTECH-CANONICAL-APPLY.md` — current five-record EdTech-inclusive canonical truth.
11. `A50-GENAI-NIST-FRESHNESS-REVIEW.md` — current GenAI/NIST freshness HOLD evidence and re-review trigger.

Historical/current truth anchors retained for A48 regression coverage:

```text
A46-TYPED-BRAIN-MEMORY.md
A46-MEMORY-RECALL-CONTEXT.md
A46-MEMORY-BOUNDARY-BENCHMARK.md
A47-BRAIN-SCORECARD.md
A47-SCORECARD-BENCHMARK.md
A48-ARCHITECTURE-TRUTH-RECONCILIATION.md
```

These filenames remain part of the architecture index because later A49/A50 truth builds on them; historical topology assertions do not override current source/tests.

## Current architecture statement

A4 runtime consolidation remains in force. Shared executable Flow OS owner:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` owns declarative skills, flows, policy, schemas and reusable Knowledge OS content/metadata. Python under `skills_UIUX/runtime/` is compatibility-only, not an independent runtime.

The Factory lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py` and is **not a second Flow OS**.

## Brain OS boundary

Brain OS under `uiux-factory/core/brain_os/` is a bounded reasoning/control layer, not a third execution runtime. Implemented surfaces include:

```text
contracts + adapters
critics
repair proposals / lineage
Evidence Graph relationships
project-scoped semantic memory
provenance-aware scorecard
deterministic Knowledge OS retrieval
```

Canonical implementation anchors include:

```text
core/brain_os/contracts.py
core/brain_os/reasoning/evidence_graph.py
core/brain_os/critics/
core/brain_os/repair_orchestrator.py
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
core/brain_os/scorecard.py
```

Brain-authored memory, critique, scorecard and retrieved knowledge remain advisory. They cannot manufacture current-run evidence, satisfy release gates or override canonical runtime evaluation.

## Evidence / evaluation truth

Canonical evidence truth:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Canonical terminal evaluation:

```text
core/evaluation/run_evaluator.py
```

A completed lifecycle without sufficient trusted PASS evidence remains insufficient evidence.

## Provider convergence boundary

A48 established controlled convergence across **different provider entry/capability contracts**. `ManagedArtifactCompletionAdapter` preserves Factory completion shape; `UIUX_FACTORY_PROVIDER_LANE=managed_compat` is explicit opt-in and `legacy` remains default. There is no automatic cross-lane fallback. Offline provider parity is regression evidence only; default-lane migration remains a separate governance decision requiring live-provider evidence.

## Lifecycle boundary

A49 reconciles **distinct top-level lifecycle APIs** using:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

`LifecycleProjection` remains read-only observability. Mutation-level lifecycle unification remains a separate decision.

## Knowledge OS boundary

```text
SKILL     = procedural methodology / how to perform work
KNOWLEDGE = reusable domain/reference context
MEMORY    = project/run-specific rationale, hypotheses, decisions and history
EVIDENCE  = current provenance-bearing observed truth
```

Canonical owners:

```text
skills_UIUX/knowledge/
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-*.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

Retrieval is post-flow-selection, deterministic, context-bounded, provenance-bearing and vector-free.

All canonical knowledge remains:

```text
advisory_only = true
current_run_evidence = false
vector_search_used = false
flow_effect = none
skill_activation_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## A50 canonical truth

The corpus contains exactly **five** canonical records:

```text
financial-services  → Unicode CLDR / UTS #35 number/currency reference
art-culture         → IIIF Presentation API 3.0 cultural-object metadata/rights reference
industrial-services → U.S. DOE Motor Systems context
mobility-ev         → Open Charge Alliance OCPP 2.1 Edition 2 / Errata 2026-06
education-edtech     → 1EdTech LTI 1.3 + LTI Advantage service/state boundaries
```

Current executable canonical-state truth:

```text
benchmarks/knowledge-canonical-state-v3.json
core/benchmarks/knowledge_edtech_canonical_apply.py
scripts/validate_knowledge_edtech_canonical_apply.py
```

A50.13 derives `CANONICAL_APPLY_PASS` only when exact five-record topology, canonical-copy integrity, source metadata, retrieval isolation/regression, AI negative isolation, context budget, rollback, owner-delegation boundaries, vector-disabled state and GenAI HOLD all remain clear.

Historical 3/4-record topology-bound validators/tests remain preserved as audit evidence and are frozen when their assumptions cease to represent current truth.

## EV status

EV/OCPP is canonical and remains advisory-only. Its source basis is Open Charge Alliance OCPP 2.1 Edition 2 / Errata 2026-06. EdTech promotion preserves EV as part of the rollback baseline.

## EdTech status

EdTech/LTI v2 completed:

```text
A50.9A  ACCEPT_FOR_INDEX_TRIAL
A50.9C  CANARY_PASS
A50.11  APPROVED_FOR_EXPLICIT_PROMOTION_TASK
A50.12  READY_FOR_CANONICAL_APPLY
A50.13  CANONICAL_APPLY_PASS
```

Canonical record:

```text
knowledge.domain.edtech-lti-context-roles-services.v2
```

It remains advisory-only and does not become product evidence merely because it is canonical.

## GenAI/NIST status

A50.14 completed an official-source freshness review and derived:

```text
KEEP_HOLD_FRESHNESS_REVIEW
freshness_risk = HIGH
canonical_index_expected_count = 5
promotion_allowed = false
```

NIST AI 600-1 remains an official GenAI Profile resource, while AI RMF 1.0 remains under active revision. The existing revision caveat is still accurate, but the dependency is not stable enough to open drafting, acceptance, canary or promotion work.

Re-review only when NIST publishes a revised AI RMF replacing 1.0 or explicitly states the active revision is complete/stable enough for profile-context reuse. Until then there is no GenAI follow-up promotion task.

Executable freshness truth:

```text
benchmarks/knowledge-genai-nist-freshness-review-v1.json
core/benchmarks/knowledge_genai_nist_freshness_review.py
scripts/validate_knowledge_genai_nist_freshness_review.py
```

## Regression and dogfood

Active CI validates current five-record truth plus the A50.14 freshness HOLD:

```text
knowledge retrieval benchmark
five-record project retrieval dogfood
versioned knowledge-value history
A50.13 canonical-state validator
A50.14 GenAI/NIST freshness validator
full pytest suite
```

A20 continues full Factory regression/security/dogfood over pinned Nova/Lumen/CENNEXT. A13 continues real Nova browser dogfood when path-triggered.

## Standing owner delegation

Canonical artifact:

```text
benchmarks/governance-owner-delegation-v1.json
```

Repository owner `Haign12` authorized bounded continuation after mandatory gates pass. Delegation permits follow-up implementation/PR work but does not permit:

```text
bypassing failed/missing checks
fabricating independent-human evidence
rewriting protected history
changing secrets/repository permissions
```

Final retrospective owner review remains deferred until the broader `uiux-ai-workspace` upgrade is complete.

## Remaining architecture debt

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default because current parity evidence is offline-only; default migration requires a separate live-provider readiness/evidence path.
2. Lifecycle convergence remains intentionally read-only at reconciliation/projection/parity level; mutation-level unification requires a separate decision.
3. GenAI/NIST is on an evidence-backed freshness HOLD with an explicit external re-review trigger; no active promotion work is allowed now.
4. Time-sensitive factual/regulatory claims still require current source verification; Knowledge OS does not replace evidence acquisition.
5. Vector/semantic retrieval remains deferred and disabled.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs matching source;
5. historical A-series notes.

## Next architecture task

The next bounded architecture task is:

```text
A51.1 — Provider Default Migration Readiness
```

It must preserve `legacy` as the default while defining and validating the evidence required to consider `managed_compat` as a future default. Offline parity alone is insufficient. The task may add a fail-closed live-trial harness/receipt contract, but it must not require secrets in CI, persist credentials/prompts, silently fall back across lanes, or change routing/evidence/gate/release authority.

Lifecycle mutation convergence remains deferred until provider migration readiness has an explicit result. GenAI/NIST remains freshness-held. Vector search remains deferred.
