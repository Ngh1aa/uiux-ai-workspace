# Architecture Truth Index

Status: **A40–A50.13 MERGED / EV + EDTECH CANONICAL / FIVE-RECORD KNOWLEDGE OS**  
Audit date: **2026-10-02**  
Current merged architecture baseline: `main@52af7d738e46adafe0d0a61fd99bc95a0c0c473e`

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

The Factory lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

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

A48 established controlled convergence across **different provider entry/capability contracts**. `ManagedArtifactCompletionAdapter` preserves Factory completion shape; `UIUX_FACTORY_PROVIDER_LANE=managed_compat` is explicit opt-in and `legacy` remains default. There is no automatic cross-lane fallback. Default-lane migration remains a separate governance decision requiring stronger live-provider evidence.

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

## A50 current canonical truth

The corpus now contains exactly **five** canonical records:

```text
financial-services  → Unicode CLDR / UTS #35 number/currency reference
art-culture         → IIIF Presentation API 3.0 cultural-object metadata/rights reference
industrial-services → U.S. DOE Motor Systems context
mobility-ev         → Open Charge Alliance OCPP 2.1 Edition 2 / Errata 2026-06
education-edtech     → 1EdTech LTI 1.3 + LTI Advantage service/state boundaries
```

Current executable truth:

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

The GenAI/NIST candidate remains:

```text
HOLD_FRESHNESS_REVIEW
```

No canonical record, index mutation or product evidence is authorized while freshness review remains unresolved.

## Regression and dogfood

Active CI now validates current five-record truth:

```text
knowledge retrieval benchmark
five-record project retrieval dogfood
versioned knowledge-value history
A50.13 canonical-state validator
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

1. Provider convergence has a controlled opt-in lane, but `legacy` remains default pending separate live-provider/governance evidence.
2. Lifecycle convergence remains intentionally read-only at reconciliation/projection/parity level; mutation-level unification requires a separate decision.
3. GenAI/NIST remains on freshness HOLD and requires a dedicated source-freshness review before any acceptance/canary/promotion path can exist.
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

The next bounded A50 task is:

```text
GenAI/NIST freshness review only
```

It must verify current official NIST source/version provenance and whether the existing candidate scope remains accurate. This review must **not** canonicalize, index, or promote GenAI knowledge. Any later acceptance/canary/promotion work requires a separate evidence-backed path.

Vector search remains deferred.
