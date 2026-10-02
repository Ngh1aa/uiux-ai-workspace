# Architecture Truth Index

Status: **CURRENT THROUGH A52.3 / FIVE-RECORD KNOWLEDGE OS / PROVIDER LIVE-EVIDENCE HOLD / LIFECYCLE MUTATION HOLD / COMPAT-SHIM RETIREMENT READINESS SELECTED**  
Audit date: **2026-10-02**  
Baseline before A52.3: `main@c8818fd9b616e9dd4dfe9d70bda79d930448a383`

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
12. `A51-PROVIDER-DEFAULT-MIGRATION-READINESS.md` — provider-default live-evidence readiness gate; `legacy` remains default.
13. `A52-LIFECYCLE-MUTATION-CONVERGENCE-READINESS.md` — mutation-level lifecycle readiness gate; current state owners remain separate.
14. `A52-LIFECYCLE-EVENT-INTEROPERABILITY.md` — read-only event/receipt interoperability over the two existing lifecycle owners.
15. `A52-POST-INTEROP-EXECUTABLE-DEBT-AUDIT.md` — evidence-driven executable-debt selection and exact compatibility-consumer census.

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

A52.3 confirms all eight `skills_UIUX/runtime/*.py` wrappers remain thin compatibility shims with no independent runtime/decision logic. They cannot be removed yet because the current exact first-party census is **8 consumer files / 19 deprecated `runtime.*` imports**.

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

A48 established controlled convergence across **different provider entry/capability contracts**. `ManagedArtifactCompletionAdapter` preserves Factory completion shape; `UIUX_FACTORY_PROVIDER_LANE=managed_compat` is explicit opt-in and `legacy` remains default. There is no automatic cross-lane fallback.

A51.1 provides the executable default-migration readiness gate. Current canonical live ledger remains:

```text
collection_status = NOT_RUN
receipts = 0 / 8
decision = KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
```

Offline provider parity is clear, but no live-provider contract matrix exists yet. Therefore provider migration/default change/auto migration remain false. Live transport success, when eventually collected, still will not be product-quality or release evidence.

A52.3 re-evaluates this debt and keeps it excluded from next-package selection while the live matrix remains empty.

## Lifecycle boundary

A49 reconciles **distinct top-level lifecycle APIs** using:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

`LifecycleProjection` remains read-only observability.

A52.1 audits whether projection parity is enough to justify mutation-level unification. Current answer is no. Executable source still proves six material blockers:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

Current A52.1 decision remains:

```text
KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED
```

A52.2 implements that allowed bounded follow-up through:

```text
core/runtime/lifecycle_event_interop.py
benchmarks/lifecycle-event-interop-v1.json
core/benchmarks/lifecycle_event_interop_regression.py
scripts/validate_lifecycle_event_interop.py
```

The shared object is an **observation receipt**, not shared mutable state.

Chronology strength remains explicit:

```text
Factory -> durable_append_only
Managed -> derived_checkpoint_delta
```

Factory receipts preserve native `seq` and `timestamp`. Managed receipts never fabricate either value; they carry previous/current checkpoint hashes and `projection_order_only=true` instead.

Every receipt remains:

```text
observation_only = true
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

Managed `COMPLETED` is normalized only as managed run completion and does not imply `FINALIZE` or `RELEASE`. Approval receipts observe gate state changes but do not satisfy human approvals. A52.2 does not clear any A52.1 blocker or authorize mutation convergence.

A52.3 re-checks those six blockers and keeps direct lifecycle mutation/unification excluded from successor selection.

## A52.3 executable debt selection

A52.3 implements a read-only selector over current executable debt:

```text
benchmarks/post-interop-executable-debt-audit-v1.json
core/benchmarks/post_interop_executable_debt_audit.py
scripts/validate_post_interop_executable_debt_audit.py
```

It checks provider/lifecycle/Knowledge governance, validates the eight deprecated compatibility shims remain thin, and scans active first-party Python imports using AST rather than documentation guesses.

Current exact census:

```text
shim_count = 8
shim_contract_clear = true
internal_consumer_files = 8
internal_consumer_imports = 19
```

The exact file/module map is now regression-locked; drift fails validation.

Derived decision:

```text
SELECT_COMPAT_SHIM_RETIREMENT_READINESS
```

Selected next bounded package:

```text
A53.1 — Runtime Compatibility Shim Retirement Readiness
```

A52.3 itself authorizes no shim deletion or runtime/provider/lifecycle/knowledge mutation.

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

A52.3 confirms this HOLD and `vector_search_change_allowed=false`, so neither GenAI promotion nor vector retrieval is selected next.

## Regression and dogfood

Active CI validates:

```text
provider parity
A51.1 provider-default migration readiness
A49 lifecycle projection parity
A52.1 lifecycle-mutation convergence readiness
A52.2 lifecycle-event interoperability
A52.3 post-interop executable-debt selection
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

1. Provider default remains `legacy`; A51.1 is implemented but live evidence is `0/8`, so provider migration governance is not open.
2. A52.2 provides safe event observability across lifecycle owners, but all six A52.1 mutation blockers remain; no direct lifecycle mutation/unification governance is open.
3. GenAI/NIST is on an evidence-backed freshness HOLD with an explicit external re-review trigger; no active promotion work is allowed now.
4. Vector/semantic retrieval remains deferred and disabled.
5. Eight deprecated `skills_UIUX/runtime/*.py` compatibility shims remain necessary for current first-party consumers. A52.3 measures 8 consumer files / 19 imports and selects retirement readiness rather than deletion.
6. Time-sensitive factual/regulatory claims still require current source verification; Knowledge OS does not replace evidence acquisition.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs matching source;
5. historical A-series notes.

## Next architecture task

A52.3 has now selected the next bounded package from executable evidence:

```text
A53.1 — Runtime Compatibility Shim Retirement Readiness
```

A53.1 may audit and migrate first-party `runtime.*` consumers to canonical `core.runtime.flow_os.*` imports under compatibility/parity evidence. It must not delete compatibility shims automatically; zero first-party consumers would be necessary but not sufficient evidence for external removal safety.

Provider default migration remains blocked on real A51.1 live receipts. Direct lifecycle mutation remains blocked by the six A52.1 blockers. GenAI/NIST remains freshness-held. Vector search remains deferred.
