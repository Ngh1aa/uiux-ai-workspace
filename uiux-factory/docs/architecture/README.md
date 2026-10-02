# Architecture Truth Index

Status: **CURRENT THROUGH FLOW 3 / A53.3 / ARCHITECTURE DEBT LEDGER CLOSED FOR UPGRADE / FIVE-RECORD KNOWLEDGE OS**  
Audit date: **2026-10-02**  
Baseline before Flow 3 / A53.3: `main@9dacfd966cac7656bec01cf8cd290842a38b54cd`

This directory is the current architecture truth for UIUX Factory / Flow OS / Brain OS. Current executable source, active validators and tests win when historical notes describe an earlier topology.

## Read order

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, ownership, explicit holds and upgrade-closure state.
2. `MIGRATION-BOUNDARIES.md` — runtime/Brain ownership boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` + `A40-ARCHITECTURE-GUARDRAILS.md` — architecture invariants.
4. A41–A47 — Brain contracts, routing/JIT, critics/repair, memory, evidence relationships and scorecard.
5. A48 — provider capability reconciliation and architecture-truth history.
6. A49 — lifecycle contract reconciliation and read-only projection parity.
7. A50 — Knowledge OS architecture, bounded retrieval, value/canary/promotion history and current five-record state.
8. `A50-GENAI-NIST-FRESHNESS-REVIEW.md` — current GenAI/NIST freshness HOLD and official-source trigger.
9. `A51-PROVIDER-DEFAULT-MIGRATION-READINESS.md` — live-evidence gate; `legacy` remains default.
10. `A52-LIFECYCLE-MUTATION-CONVERGENCE-READINESS.md` — six semantic blockers and separate mutation owners.
11. `A52-LIFECYCLE-EVENT-INTEROPERABILITY.md` — observation-only lifecycle event receipts.
12. `A52-POST-INTEROP-EXECUTABLE-DEBT-AUDIT.md` — historical 8/19 compatibility-consumer selection evidence.
13. `A53-RUNTIME-COMPATIBILITY-CONVERGENCE.md` — Flow 1, first-party deprecated-import convergence to 0/0.
14. `A53-COMPATIBILITY-SURFACE-GOVERNANCE.md` — Flow 2, eight-shim criteria-based sunset governance.
15. `A53-ARCHITECTURE-DEBT-CLOSURE-AUDIT.md` — Flow 3, current architecture-debt classification and Flow 4 readiness.

Historical/current truth anchors retained for A48 regression coverage:

```text
A46-TYPED-BRAIN-MEMORY.md
A46-MEMORY-RECALL-CONTEXT.md
A46-MEMORY-BOUNDARY-BENCHMARK.md
A47-BRAIN-SCORECARD.md
A47-SCORECARD-BENCHMARK.md
A48-ARCHITECTURE-TRUTH-RECONCILIATION.md
```

## Current architecture statement

Shared executable Flow OS owner:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` owns declarative skills, flows, runtime policy, schemas and reusable Knowledge OS content. Python under `skills_UIUX/runtime/` is compatibility-only and is not an independent runtime.

Canonical current-run evidence owner:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Canonical terminal evaluator:

```text
core/evaluation/run_evaluator.py
```

A completed lifecycle without sufficient trusted PASS evidence remains `insufficient_evidence`; model/provider/Brain/Knowledge/observation channels cannot manufacture a PASS or release.

## Flow 1 / A53.1 — first-party runtime compatibility convergence

Historical A52.3 census:

```text
8 compatibility shims
8 first-party consumer files
19 deprecated runtime.* imports
```

Flow 1 migrated known first-party consumers to canonical `core.runtime.flow_os.*` imports while retaining all eight thin wrappers.

Current truth:

```text
internal_consumer_files = 0
internal_consumer_imports = 0
shim_count = 8
shim_contract_clear = true
identity_checks_clear = true
FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS
```

Zero internal consumers does not establish external removal safety.

## Flow 2 / A53.2 — compatibility surface governance

All eight public compatibility wrappers are classified:

```text
retain_indefinitely = 0
deprecate_with_sunset = 8
open_removal_governance = 0
external_usage_status = UNKNOWN
```

Current decision:

```text
DEPRECATE_WITH_SUNSET_REMOVAL_GOVERNANCE_CLOSED
```

Public observation window begins 2026-10-02. Earliest fresh removal-governance review is 2026-12-31. That is a review boundary, never an automatic deletion date. A later task must refresh external/downstream usage evidence and explicitly open owner-governed removal work before deletion can even be proposed.

## Flow 3 / A53.3 — architecture debt closure audit

Flow 3 audits remaining architecture state without implementing speculative features. Every area must be exactly one of:

```text
CLOSED
INTENTIONAL_HOLD
NEW_ACTIONABLE_DEBT
```

Current executable ledger:

| Area | Classification | Current truth / trigger |
|---|---|---|
| Runtime / Flow OS single owner | `CLOSED` | Canonical runtime is `core.runtime.flow_os.*`; first-party deprecated-import census is 0/0. |
| Provider default migration | `INTENTIONAL_HOLD` | `legacy` remains default; real sanitized A51.1 8/8 live-provider matrix is required before separate migration governance. |
| Lifecycle mutation convergence | `INTENTIONAL_HOLD` | Factory and managed mutation owners remain distinct; six A52.1 semantic blockers remain. |
| Brain OS authority boundary | `CLOSED` | Brain scorecard/advisory channels have no PASS, evidence, gate or release authority. |
| Knowledge OS canonical corpus | `CLOSED` | Exactly five canonical records; deterministic metadata-first retrieval; advisory-only and vector-free. |
| GenAI/NIST expansion | `INTENTIONAL_HOLD` | Re-review only on explicit official NIST framework-status change. |
| Vector / semantic retrieval | `INTENTIONAL_HOLD` | Optional future capability; requires product need + benchmark evidence that deterministic bounded retrieval is insufficient. |
| Evidence + terminal evaluation | `CLOSED` | Trusted evidence is runtime-origin; lifecycle completion without trusted PASS remains insufficient evidence. |
| Compatibility-surface removal | `INTENTIONAL_HOLD` | Fresh review no earlier than 2026-12-31 plus external/downstream audit and explicit owner removal task. |

Expected aggregate:

```text
closed = 4
intentional_holds = 5
new_actionable_debt = 0
ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE
```

The five holds are explicit safety/external-dependency boundaries and are **not blockers for completing the current workspace upgrade**. They must not be converted into invented work merely to make the ledger visually empty.

Executable owner set:

```text
benchmarks/architecture-debt-closure-audit-v1.json
core/benchmarks/architecture_debt_closure_audit.py
scripts/validate_architecture_debt_closure_audit.py
tests/test_architecture_debt_closure_audit_a53.py
```

## Provider boundary

A48 established controlled compatibility across **different provider entry/capability contracts**. `legacy` remains default and `managed_compat` remains explicit opt-in; there is no automatic cross-lane fallback.

A51.1 current live state:

```text
collection_status = NOT_RUN
receipts = 0 / 8
decision = KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
default_change_allowed = false
provider_migration_allowed = false
```

Offline parity is regression evidence, not live-provider/product evidence. Flow 3 therefore classifies provider-default migration as an intentional, non-blocking HOLD rather than actionable debt.

## Lifecycle boundary

A49 reconciles **distinct top-level lifecycle APIs** through read-only projection. Current mutation owners remain:

```text
Factory -> core.runtime.run_context.RunContext
Managed -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

The managed CLI uses the canonical Flow OS and is **not a second Flow OS**.

Six A52.1 blockers remain explicit:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

A52.2 event interoperability is observation-only:

```text
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

It does not create shared mutable lifecycle state or authorize mutation convergence.

## Brain OS boundary

Brain OS remains a bounded reasoning/control layer, not a third runtime. Current implementation anchors include:

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

Memory, critique, repair proposals, scorecards and retrieved knowledge remain advisory/proposal channels and cannot override `core/evaluation/run_evaluator.py`.

## Knowledge OS boundary

```text
SKILL     = procedural methodology
KNOWLEDGE = reusable reference/domain context
MEMORY    = project/run rationale and history
EVIDENCE  = current provenance-bearing observed truth
```

Canonical Knowledge OS owners:

```text
skills_UIUX/knowledge/
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-*.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

Current canonical index contains exactly five records:

```text
financial-services
art-culture
industrial-services
mobility-ev
education-edtech
```

Retrieval remains deterministic, metadata-first, context-bounded, provenance-bearing, advisory-only and vector-free.

GenAI/NIST remains:

```text
KEEP_HOLD_FRESHNESS_REVIEW
promotion_allowed = false
vector_search_change_allowed = false
```

Vector retrieval is intentionally optional, not a hidden prerequisite for completing this upgrade.

## Regression and dogfood

Active CI validates:

```text
routing / repair / memory / scorecard benchmarks
provider parity
A51.1 provider-default readiness
A49 lifecycle projection parity
A52.1 lifecycle mutation readiness
A52.2 lifecycle event interoperability
Flow 1 / A53.1 runtime compatibility convergence
Flow 2 / A53.2 compatibility surface governance
Flow 3 / A53.3 architecture debt closure
five-record Knowledge OS retrieval and project dogfood
A50.13 canonical-state truth
A50.14 GenAI/NIST freshness HOLD
full pytest suite
```

A20 remains release-candidate regression/security/dogfood over pinned Nova, Lumen and CENNEXT. A13 remains real Nova browser dogfood when path-triggered.

## Standing owner delegation

Canonical artifact:

```text
benchmarks/governance-owner-delegation-v1.json
```

Repository owner `Haign12` permits bounded continuation after mandatory gates pass. Delegation does not allow failed/missing checks to be bypassed, independent-human evidence to be fabricated, protected history to be rewritten, or secrets/permissions to be changed.

Final retrospective owner review remains deferred until the broader `uiux-ai-workspace` upgrade is complete.

## Current intentional holds

These are explicit and non-blocking for this upgrade:

1. Provider default migration — requires real sanitized 8/8 live-provider evidence plus separate migration governance.
2. Lifecycle mutation convergence — requires actual resolution/reconciliation of all six semantic blockers.
3. GenAI/NIST expansion — depends on the official NIST framework-status trigger.
4. Vector/semantic retrieval — requires explicit product need plus comparative benchmark evidence.
5. Compatibility-shim removal — fresh external/downstream audit no earlier than 2026-12-31 and explicit owner removal task.

No other architecture debt is currently classified `NEW_ACTIONABLE_DEBT` by Flow 3.

## Source-of-truth priority

When documents disagree:

1. current executable source and tests;
2. root `AGENTS.md`, runtime policy and ownership contracts;
3. this architecture truth set;
4. current capability/QA docs matching source;
5. historical A-series notes.

## Next architecture task

When Flow 3 passes on the exact final PR head, the next bounded flow is:

```text
Flow 4 — Final Regression & Cross-project Dogfood
```

Flow 4 must validate the completed upgrade across representative projects; it must not silently clear the five intentional holds or turn them into product/release evidence.
