# Architecture Truth Index

Status: **A40–A50.10C MERGED / EV CANONICAL / EDTECH CANARY_PASS**  
Audit date: **2026-10-02**  
Current merged architecture baseline: `main@538f3551445832291142f2c7d3d555284e69064d`

This directory contains current architecture truth for UIUX Factory / Flow OS / Brain OS. Current source and executable tests are authoritative when historical A-series notes describe an earlier topology.

## Read order

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, ownership and remaining debt.
2. `MIGRATION-BOUNDARIES.md` — runtime/Brain ownership boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` + `A40-ARCHITECTURE-GUARDRAILS.md` — architecture invariants.
4. A41–A47 — Brain contracts, evidence graph, routing/JIT, critics/repair, memory and scorecard.
5. A48 — provider capability reconciliation, artifact bridge, compatibility adapter, parity dogfood and controlled integration.
6. A49 — lifecycle contract reconciliation and read-only adapter parity.
7. `A50-KNOWLEDGE-OS-ARCHITECTURE.md` + `A50-BOUNDED-KNOWLEDGE-RETRIEVAL.md` — Knowledge OS ownership/retrieval.
8. A50.3–A50.10B documents — historical seed, usefulness/value trials, candidate drafting/revision, controlled-index and promotion evidence.
9. `A50-EV-CANONICAL-APPLY.md` — current EV canonical promotion state.

Historical/current truth anchors retained for A48 regression coverage:

```text
A46-TYPED-BRAIN-MEMORY.md
A46-MEMORY-RECALL-CONTEXT.md
A46-MEMORY-BOUNDARY-BENCHMARK.md
A47-BRAIN-SCORECARD.md
A47-SCORECARD-BENCHMARK.md
A48-ARCHITECTURE-TRUTH-RECONCILIATION.md
```

These filenames remain part of the architecture index because later A49/A50 truth builds on them; retaining the anchors does not make their historical topology assertions override current source/tests.

## Current architecture statement

A4 runtime consolidation remains in force. The shared executable Flow OS owner is:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` remains declarative ownership for skills, flows, policies, schemas and reusable Knowledge OS content/metadata. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`. The provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS boundary

Brain OS under `uiux-factory/core/brain_os/` is a bounded reasoning/control layer, not a third execution runtime. Current implemented surfaces include:

```text
contracts + adapters
critics
repair proposals / lineage
Evidence Graph relationships
project-scoped semantic memory
provenance-aware scorecard
deterministic Knowledge OS retrieval
```

Brain-authored memory, critique, scorecard and retrieved knowledge remain advisory. They cannot manufacture current-run evidence, satisfy release gates or override canonical runtime evaluation.

## Evidence / evaluation truth

Canonical evidence truth remains owned by:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Canonical terminal runtime evaluation remains owned by:

```text
core/evaluation/run_evaluator.py
```

A completed lifecycle without sufficient trusted PASS evidence remains insufficient evidence; model/knowledge/memory claims cannot upgrade it.

## Provider convergence boundary

A48 is implemented through a controlled provider convergence lane. `ManagedArtifactCompletionAdapter` preserves Factory async completion shape; offline provider parity is benchmarked; `UIUX_FACTORY_PROVIDER_LANE=managed_compat` is explicit opt-in while `legacy` remains default.

There is no automatic cross-lane fallback. Provider-lane provenance has no evidence/gate/release authority. Default-lane migration remains a separate governance decision requiring stronger live-provider evidence.

## Lifecycle boundary

A49 uses the comparison vocabulary:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

`LifecycleProjection` is read-only observability, not a third state machine. Factory completion does not imply production release; Managed completion does not imply worktree finalization or release. Mutation-level lifecycle unification remains a separate decision.

## Knowledge OS boundary

The ownership split is:

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

Retrieval occurs only after flow selection/stage resolution. It remains deterministic, context-bounded, provenance-bearing and vector-free.

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

A50.3 began with a three-record seed. After A50.9B canary, A50.10A governance proposal, A50.10B shadow apply and A50.10C canonical apply, the canonical corpus now contains **four** records:

```text
financial-services  → Unicode CLDR / UTS #35 number/currency reference
art-culture         → IIIF Presentation API 3.0 cultural-object metadata/rights reference
industrial-services → U.S. DOE Motor Systems context
mobility-ev         → Open Charge Alliance OCPP 2.1 Edition 2 / Errata 2026-06
```

Current canonical state is executable in:

```text
benchmarks/knowledge-canonical-state-v2.json
core/benchmarks/knowledge_ev_canonical_apply.py
scripts/validate_knowledge_ev_canonical_apply.py
```

A50.10C derives `CANONICAL_APPLY_PASS` only when the exact 4-record topology, record/content integrity, retrieval isolation, negative-domain isolation, context budget, rollback contract, GenAI HOLD and governance boundaries all remain clear.

Historical A50.4–A50.10B topology-bound validators/tests remain preserved as audit evidence. Active CI does not reinterpret three-record historical assertions as current four-record truth.

## EdTech status

A50.9A produced EdTech/LTI v2 and completed its blind acceptance retry:

```text
knowledge.domain.edtech-lti-context-roles-services.v2
verdict = ACCEPT_FOR_INDEX_TRIAL
```

A50.9C then ran the controlled index trial and derived:

```text
CANARY_PASS
promotion_proposal_allowed = true
```

EdTech remains unindexed. It is now eligible for its own bounded canonical-promotion proposal/governance path. EV promotion does not implicitly promote EdTech.

## GenAI/NIST status

The GenAI/NIST candidate remains:

```text
HOLD_FRESHNESS_REVIEW
```

No canonical record, index mutation or product evidence is authorized from that candidate while freshness review remains unresolved.

## Regression and dogfood

Main UIUX Factory CI now validates active post-promotion truth rather than replaying stale pre-promotion topology assumptions. Active Knowledge checks include:

```text
knowledge retrieval benchmark
four-record project retrieval dogfood
versioned knowledge-value trial history
A50.10C canonical-state validator
full pytest suite
```

Generic architecture/retrieval tests continue to run. Pre-promotion governance tests are frozen only when the EV canonical ref exists and remain available for audit.

A20 continues full Factory regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. A13 continues real Nova browser dogfood when path-triggered.

## Standing owner delegation

Repository owner `Haign12` explicitly authorized bounded continuation after mandatory gates pass. Canonical artifact:

```text
benchmarks/governance-owner-delegation-v1.json
```

The delegation permits follow-up implementation tasks and PR continuation when evidence/CI are clear. It does **not** permit:

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
3. EdTech/LTI v2 has `CANARY_PASS` and is eligible for canonical-promotion proposal/governance, but remains unindexed.
4. GenAI/NIST remains on freshness HOLD.
5. Time-sensitive factual/regulatory claims still require current source verification; Knowledge OS does not replace research/evidence acquisition.
6. Vector/semantic retrieval remains deferred and disabled.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

The next bounded A50 task is:

```text
EdTech/LTI canonical-promotion proposal + governance review
```

It must start from the verified A50.9C `CANARY_PASS`, preserve the current 4-record EV-inclusive canonical baseline, verify source freshness and rollback/cross-domain risk, and may only open a **separate explicit EdTech promotion implementation task**. It must not mutate the canonical index inside the proposal/governance phase.

GenAI/NIST remains on freshness HOLD. Vector search remains deferred.
