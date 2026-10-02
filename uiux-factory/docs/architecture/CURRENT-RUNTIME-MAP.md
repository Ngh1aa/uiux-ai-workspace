# Current Runtime Map

Status: **CURRENT THROUGH FLOW 3 / A53.3 / ARCHITECTURE DEBT LEDGER CLOSED FOR UPGRADE**  
Audit date: **2026-10-02**  
Baseline before Flow 3 / A53.3: `main@9dacfd966cac7656bec01cf8cd290842a38b54cd`

This map describes current executable ownership and explicit architecture holds. Historical A-series plans remain audit history; current source/tests are authoritative.

## 1. Product entry and shared Flow OS

Primary Factory entry/lifecycle:

```text
uiux-factory/run.py
uiux-factory/core/manager/
```

Provider-neutral managed entry:

```text
skills_UIUX/scripts/uiux-agent.py
```

Shared executable owner:

```text
uiux-factory/core/runtime/flow_os/
```

The managed/provider-neutral surface is **not a second Flow OS**. It shares canonical Flow OS execution rather than owning duplicate routing/provider/lifecycle policy.

Declarative ownership remains under:

```text
skills_UIUX/
skills_UIUX/flows/
skills_UIUX/runtime/runtime-policy.json
skills_UIUX/schemas/
skills_UIUX/<skill>/SKILL.md
```

## 2. Runtime compatibility surface

`skills_UIUX/runtime/*.py` contains compatibility-only wrappers, not runtime authority.

Historical A52.3 census:

```text
8 declared compatibility shims
8 first-party consumer files
19 deprecated runtime.* module imports
```

Flow 1 / A53.1 current census:

```text
8 declared compatibility shims
0 first-party consumer files
0 deprecated runtime.* imports
shim_contract_clear = true
identity_checks_clear = true
```

Flow 2 / A53.2 governance:

```text
retain_indefinitely = 0
deprecate_with_sunset = 8
open_removal_governance = 0
external_usage_status = UNKNOWN
earliest_removal_review_date = 2026-12-31
removal_governance_open = false
shim_deletion_allowed = false
```

Zero first-party consumers is necessary but not sufficient evidence for external removal safety. The 2026-12-31 date is only the earliest fresh review boundary, not an automatic deletion date.

## 3. Provider layer

Current provider surfaces:

```text
core/runtime/free_provider.py                    Factory legacy lane
core/runtime/provider_compat_contract.py         lane/shared compatibility contract
core/runtime/flow_os/provider*.py                provider-neutral managed contracts
core/runtime/flow_os/factory_provider_adapter.py bounded compatibility adapter
```

Historical A48 described **different provider entry/capability contracts**. Current code has a bounded compatibility path, not duplicate provider authority.

Current lane rule:

```text
legacy = default
managed_compat = explicit opt-in
no automatic cross-lane fallback
```

A51.1 current truth:

```text
collection_status = NOT_RUN
receipts = 0 / 8
decision = KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
migration_governance_allowed = false
default_change_allowed = false
provider_migration_allowed = false
auto_migration_allowed = false
product_evidence = false
```

Offline parity is regression evidence only. Flow 3 classifies provider-default migration as `INTENTIONAL_HOLD`, not `NEW_ACTIONABLE_DEBT` and not an upgrade blocker. Reopen only after a real sanitized 8/8 Groq/Gemini × legacy/managed_compat × plain/JSON live matrix passes and a separate migration-governance task opens.

## 4. Lifecycle layer

A49 reconciles **distinct top-level lifecycle APIs** through read-only projection:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

Current mutation owners remain separate:

```text
Factory -> core.runtime.run_context.RunContext
Managed -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

A52.1 current decision:

```text
KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED
```

Six executable semantic blockers remain:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

A52.2 adds observation-only lifecycle interoperability:

```text
core/runtime/lifecycle_event_interop.py
benchmarks/lifecycle-event-interop-v1.json
core/benchmarks/lifecycle_event_interop_regression.py
scripts/validate_lifecycle_event_interop.py
```

Chronology remains intentionally asymmetric:

```text
Factory -> durable_append_only
Managed -> derived_checkpoint_delta
```

Lifecycle receipts preserve:

```text
observation_only = true
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

Managed completion does not imply FINALIZE/RELEASE. Approval receipts observe state; they do not satisfy human approvals. Flow 3 classifies mutation convergence as `INTENTIONAL_HOLD`, reopened only if the six semantic blockers are actually eliminated or explicitly reconciled in separate owner governance.

## 5. Evidence / provenance / QA

Canonical current-run evidence truth:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Trusted evidence must remain runtime-origin. Provider/model-authored claims remain untrusted and cannot be upgraded into trusted PASS evidence by metadata alone.

## 6. Terminal evaluation

Canonical terminal evaluator:

```text
core/evaluation/run_evaluator.py
```

Current invariant:

```text
managed lifecycle COMPLETED
+ no sufficient trusted PASS evidence
= insufficient_evidence
```

Completion is not release and does not manufacture product evidence.

## 7. Brain OS

Bounded reasoning/control owner:

```text
uiux-factory/core/brain_os/
```

Implemented ownership anchors:

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

Brain OS is not a third runtime. Critique, repair proposals, memory, scorecard and retrieved knowledge are advisory/proposal channels. The scorecard mirrors canonical runtime outcome and preserves:

```text
advisory_only = true
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

Flow 3 classifies the Brain authority boundary as `CLOSED` because current executable checks preserve this non-authority contract.

## 8. Knowledge OS

Canonical declarative owners:

```text
skills_UIUX/knowledge/
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-record.schema.json
skills_UIUX/schemas/knowledge-index.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

Current canonical corpus is exactly five records:

```text
financial-services
art-culture
industrial-services
mobility-ev
education-edtech
```

Retrieval remains:

```text
deterministic_metadata_first = true
vector_search_used = false
advisory_only = true
current_run_evidence = false
```

Flow 3 classifies the five-record canonical corpus as `CLOSED`.

### GenAI/NIST

Current decision:

```text
KEEP_HOLD_FRESHNESS_REVIEW
promotion_allowed = false
draft_creation_allowed = false
vector_search_change_allowed = false
```

This is an `INTENTIONAL_HOLD`. Re-review only on the explicit official NIST framework-status trigger.

### Vector / semantic retrieval

Vector retrieval remains disabled and is an `INTENTIONAL_HOLD`, not an upgrade blocker. It requires a separate explicit product need plus benchmark evidence that current deterministic bounded retrieval is insufficient.

## 9. Flow 3 / A53.3 architecture debt closure

Executable owner set:

```text
benchmarks/architecture-debt-closure-audit-v1.json
core/benchmarks/architecture_debt_closure_audit.py
scripts/validate_architecture_debt_closure_audit.py
tests/test_architecture_debt_closure_audit_a53.py
```

Classification vocabulary:

```text
CLOSED
INTENTIONAL_HOLD
NEW_ACTIONABLE_DEBT
```

Current ledger expected from executable source:

| Area | Classification |
|---|---|
| Runtime / Flow OS single owner | `CLOSED` |
| Provider default migration | `INTENTIONAL_HOLD` |
| Lifecycle mutation convergence | `INTENTIONAL_HOLD` |
| Brain OS authority boundary | `CLOSED` |
| Knowledge OS canonical corpus | `CLOSED` |
| GenAI/NIST expansion | `INTENTIONAL_HOLD` |
| Vector / semantic retrieval | `INTENTIONAL_HOLD` |
| Evidence + terminal evaluation | `CLOSED` |
| Compatibility-surface removal | `INTENTIONAL_HOLD` |

Aggregate target:

```text
closed = 4
intentional_holds = 5
new_actionable_debt = 0
```

Current Flow 3 decision, only when all live executable checks pass:

```text
ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE
```

The five intentional holds are explicit safety/external-dependency boundaries with triggers. They do not silently become PASS claims, and they do not block completion of the present workspace upgrade.

## 10. Regression surfaces

Active regression owners include:

```text
uiux-factory/benchmarks/corpus/
uiux-factory/benchmarks/routing-v1.json
uiux-factory/benchmarks/repair-proposals-v1.json
uiux-factory/benchmarks/memory-boundary-v1.json
uiux-factory/benchmarks/scorecard-v1.json
uiux-factory/benchmarks/provider-parity-v1.json
uiux-factory/benchmarks/provider-default-migration-readiness-v1.json
uiux-factory/benchmarks/lifecycle-parity-v1.json
uiux-factory/benchmarks/lifecycle-mutation-convergence-readiness-v1.json
uiux-factory/benchmarks/lifecycle-event-interop-v1.json
uiux-factory/benchmarks/runtime-compatibility-convergence-v1.json
uiux-factory/benchmarks/compatibility-surface-governance-v1.json
uiux-factory/benchmarks/architecture-debt-closure-audit-v1.json
uiux-factory/core/benchmarks/
.github/workflows/uiux-factory-ci.yml
.github/workflows/a20-release-candidate.yml
```

UIUX Factory CI validates current architecture contracts plus the full pytest suite. A20 remains release-candidate regression/security/dogfood over pinned Nova, Lumen and CENNEXT. A13 remains real Nova browser dogfood when path-triggered.

## 11. Standing owner delegation

Current policy:

```text
uiux-factory/benchmarks/governance-owner-delegation-v1.json
```

Mandatory failures cannot be bypassed. Independent-human evidence cannot be fabricated. Final retrospective owner review remains deferred until the broader workspace upgrade is complete.

## 12. Architecture debt ledger after Flow 3

### CLOSED

1. Runtime / Flow OS canonical ownership and first-party deprecated-import convergence.
2. Brain OS authority boundary.
3. Five-record canonical Knowledge OS baseline.
4. Evidence/trusted-evaluation ownership.

### INTENTIONAL_HOLD — non-blocking for this upgrade

1. Provider-default migration — real A51.1 8/8 live evidence required.
2. Lifecycle mutation convergence — six semantic blockers must be resolved/reconciled.
3. GenAI/NIST expansion — official NIST framework-status trigger required.
4. Vector/semantic retrieval — explicit product need + comparative benchmark required.
5. Compatibility-shim removal — fresh external/downstream audit no earlier than 2026-12-31 plus explicit owner removal task.

### NEW_ACTIONABLE_DEBT

```text
none
```

## 13. Rules for future convergence work

Future work must preserve:

```text
Brain OS reasoning/control
→ canonical task interpretation / Flow OS planning
→ Factory manager or ManagedFlowController
→ specialist execution / tools
→ existing evidence + QA
→ canonical evaluation
→ advisory memory/scorecard/knowledge
```

It must not create a third runtime/provider-policy abstraction, treat lifecycle observation as shared mutation state, let advisory channels satisfy runtime gates, rewrite historical benchmark evidence, infer external compatibility safety from zero internal consumers, or promote external holds into PASS without their required evidence.

## 14. Next bounded flow

If Flow 3 passes on the exact final PR head:

```text
Flow 4 — Final Regression & Cross-project Dogfood
```

Flow 4 validates the upgrade end-to-end across representative projects. It does not clear or weaken the five intentional holds.
