# Current Runtime Map

Status: **CURRENT THROUGH FLOW 2 / A53.2 / PROVIDER LIVE-EVIDENCE HOLD / LIFECYCLE MUTATION HOLD / COMPATIBILITY SUNSET GOVERNED**  
Audit date: **2026-10-02**  
Baseline before Flow 2 / A53.2: `main@a9313567da25059a580c4f86fb7d58161d5820c6`

This map describes current executable ownership. Historical A-series plans may describe earlier gaps; current source/tests win when they disagree.

## 1. Product entry and orchestration

Primary Factory entry/lifecycle:

```text
uiux-factory/run.py
uiux-factory/core/manager/
```

Provider-neutral managed entry:

```text
skills_UIUX/scripts/uiux-agent.py
```

Both route through the canonical Flow OS owner instead of maintaining independent routing logic. The managed/provider-neutral surface is **not a second Flow OS**; `uiux-factory/core/runtime/flow_os/` remains the shared executable owner.

## 2. Canonical Flow OS

Shared executable owner:

```text
uiux-factory/core/runtime/flow_os/
```

Responsibilities include task interpretation, flow planning/replanning, managed lifecycle/checkpoints, evidence wiring and provider-neutral runtime contracts.

Declarative owners remain under:

```text
skills_UIUX/flows/
skills_UIUX/runtime/runtime-policy.json
skills_UIUX/schemas/
skills_UIUX/<skill>/SKILL.md
```

`skills_UIUX/runtime/*.py` are deprecated compatibility shims. New runtime authority must not be added there.

A52.3 measured the pre-migration first-party compatibility debt as:

```text
8 declared compatibility shims
8 consumer files
19 deprecated runtime.* module imports
```

Flow 1 / A53.1 migrated every known first-party consumer to canonical `core.runtime.flow_os.*` imports. Current executable census is:

```text
8 declared compatibility shims
0 first-party consumer files
0 deprecated runtime.* module imports
shim_contract_clear = true
identity_checks_clear = true
```

Flow 2 / A53.2 governs the retained public surface rather than deleting it:

```text
retain_indefinitely = 0
deprecate_with_sunset = 8
open_removal_governance = 0
external_usage_status = UNKNOWN
observation_window_days = 90
earliest_removal_review_date = 2026-12-31
removal_governance_open = false
shim_deletion_allowed = false
```

Zero first-party consumers is necessary but not sufficient evidence that external integrations are absent. The shims remain thin, public compatibility-only wrappers during the observation window.

## 3. Provider layer

Current provider surfaces:

```text
core/runtime/free_provider.py                    Factory legacy lane
core/runtime/provider_compat_contract.py         lane/shared compatibility contract
core/runtime/flow_os/provider*.py                provider-neutral managed contracts
core/runtime/flow_os/factory_provider_adapter.py bounded compatibility adapter
```

A48 established explicit provider capability reconciliation, artifact bridging, parity dogfood and a controlled opt-in compatibility lane.

Historical A48 described the pre-convergence mismatch as **different provider entry/capability contracts**. That phrase remains an architecture regression anchor; current state is the bounded compatibility lane, not duplicate provider authority.

Current rule:

```text
legacy = default
managed_compat = explicit opt-in
no automatic cross-lane fallback
```

A51.1 adds the fail-closed live-provider readiness layer:

```text
benchmarks/provider-default-migration-readiness-v1.json
benchmarks/provider-live-trial-receipts-v1.json
core/benchmarks/provider_default_migration_readiness.py
scripts/validate_provider_default_migration_readiness.py
scripts/run_provider_live_trial.py
```

Current A51.1 truth:

```text
collection_status = NOT_RUN
receipts = 0 / 8
decision = KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
migration_governance_allowed = false
default_change_allowed = false
```

Offline parity preserves the caller contract but is not live-provider or product evidence. A future live trial is operator-explicit and cannot persist secrets, prompt/system bodies or response bodies.

A52.3 re-checked this state and excluded provider-default migration from successor selection while live receipts remain `0/8`. Flow 1 and Flow 2 change no provider lane/default behavior.

## 4. Lifecycle layer

A49 reconciles lifecycle meaning across Factory and managed surfaces using:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

Historical A48/A49 debt described the Factory and managed surfaces as **distinct top-level lifecycle APIs**. A49 made their meaning comparable through read-only projection/parity; it did not erase their separate mutation owners.

`LifecycleProjection` remains read-only observability and does not introduce a third state machine or equate completion with release.

Current mutation owners remain intentionally distinct:

```text
Factory -> core.runtime.run_context.RunContext
Managed -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

A52.1 evaluates mutation-level convergence readiness rather than assuming projection parity implies state-machine parity:

```text
benchmarks/lifecycle-mutation-convergence-readiness-v1.json
core/benchmarks/lifecycle_mutation_convergence_readiness.py
scripts/validate_lifecycle_mutation_convergence_readiness.py
```

Current audited mutation blockers remain:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

A52.1 decision remains:

```text
KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED
event_interop_proposal_allowed = true
mutation_governance_allowed = false
```

A52.2 implements only that additive interoperability allowance:

```text
core/runtime/lifecycle_event_interop.py
benchmarks/lifecycle-event-interop-v1.json
core/benchmarks/lifecycle_event_interop_regression.py
scripts/validate_lifecycle_event_interop.py
```

Normalized `LifecycleEventReceipt` values are observation-only. They do not own transitions.

Chronology remains intentionally asymmetric:

```text
Factory -> durable_append_only
Managed -> derived_checkpoint_delta
```

Factory receipts preserve native event `seq` and `timestamp`. Managed receipts never fabricate those fields; they carry checkpoint hashes and deterministic projection ordering only.

Interop vocabulary covers safely derivable run/stage start/completion, failure/block, replan, human-approval observation, fork and unknown/native fallback. Unknown events fail safe as `native_event_observed`.

Managed completion remains distinct from finalize/release. Approval receipts do not satisfy gates. All receipts keep:

```text
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

A52.2 does not clear the six A52.1 mutation blockers and does not open mutation governance. A52.3 re-checks the same six blockers and therefore excludes direct lifecycle mutation convergence from the next bounded package. Flow 1 and Flow 2 change no lifecycle state owner or transition.

## 5. Post-interop debt selection, runtime convergence and compatibility governance

A52.3 added the audit-only selector:

```text
benchmarks/post-interop-executable-debt-audit-v1.json
core/benchmarks/post_interop_executable_debt_audit.py
scripts/validate_post_interop_executable_debt_audit.py
tests/test_post_interop_executable_debt_audit_a52.py
```

It selected compatibility retirement readiness from the historical exact census:

```text
8 declared compatibility shims
8 first-party consumer files
19 deprecated runtime.* module imports
shim_contract_clear = true
```

That 8/19 topology remains preserved as historical evidence and is frozen after the A53 convergence contract appears.

Flow 1 / A53.1 current-state owners:

```text
benchmarks/runtime-compatibility-convergence-v1.json
core/benchmarks/runtime_compatibility_convergence.py
scripts/validate_runtime_compatibility_convergence.py
tests/test_runtime_compatibility_convergence_a53.py
```

Flow 1 migrated the eight selected first-party consumers to canonical imports and verifies compatibility identity for all symbols used by those callers, including:

```text
DevelopmentManager -> FlowPlanner
DevelopmentManagerAgent -> ManagedFlowController
ProviderNeutralAgentHarness
PermissionGate
ToolRegistry
build_context_manifest
FlowResolver
validate_flow_document
ProviderStageResponse
ScriptedProvider
ProviderManagedRunner
GoalInterpreter
```

The four migrated `skills_UIUX/scripts` consumers use the same canonical Factory-root bootstrap as the managed CLI.

Flow 1 decision:

```text
FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS
```

Current census:

```text
internal_consumer_files = 0
internal_consumer_imports = 0
zero_internal_consumers = true
shim_count = 8
shim_contract_clear = true
identity_checks_clear = true
script_bootstrap_clear = true
governance_boundary_clear = true
```

Flow 2 / A53.2 current-state owners:

```text
benchmarks/compatibility-surface-governance-v1.json
core/benchmarks/compatibility_surface_governance.py
scripts/validate_compatibility_surface_governance.py
tests/test_compatibility_surface_governance_a53.py
```

Flow 2 classifies all eight public wrappers `DEPRECATE_WITH_SUNSET`. Public-code discovery returned zero hits for the strongest legacy aliases on 2026-10-02, but that discovery is explicitly non-authoritative. External usage remains `UNKNOWN`.

The repository had no GitHub Releases at the audit point and no root Python package metadata establishing a semver removal boundary, so the sunset uses a minimum 90-day public observation window instead of inventing a version boundary.

Current Flow 2 decision:

```text
DEPRECATE_WITH_SUNSET_REMOVAL_GOVERNANCE_CLOSED
```

Current removal boundary:

```text
retain_indefinitely = 0
deprecate_with_sunset = 8
open_removal_governance = 0
earliest_removal_review_date = 2026-12-31
observation_window_elapsed = false
external_usage_audit_complete = false
no_known_supported_downstream_dependency = false
explicit_owner_removal_task = false
removal_governance_open = false
shim_deletion_allowed = false
external_removal_safety_inferred = false
```

Flow 1 and Flow 2 do **not** authorize runtime mutation, provider-default change, lifecycle state-owner change, routing change, evidence/gate/release authority change, GenAI promotion or vector-search activation. Their execution/authority/gate/evidence/release effects remain `none`.

## 6. Evidence / provenance / QA

Canonical current-run evidence truth:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Browser/rendered QA remains evidence-bearing for visual/runtime claims when applicable. Brain/model/provider/knowledge/lifecycle-observation/debt-audit metadata cannot silently become trusted evidence.

## 7. Terminal evaluation

Canonical terminal evaluator:

```text
core/evaluation/run_evaluator.py::RunEvaluator
```

It derives outcomes from latest-effective trusted evidence. Completed lifecycle without sufficient trusted PASS evidence remains insufficient evidence.

## 8. Brain OS

Bounded reasoning/control owner:

```text
uiux-factory/core/brain_os/
```

Implemented surfaces:

```text
typed task/reasoning contracts
flow-selection adapters
critics
repair proposals + lineage
evidence relationships/integrity adapters
project-scoped semantic memory
provenance-aware scorecard
deterministic Knowledge OS retrieval
```

Canonical implementation anchors:

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

These are owners inside the bounded Brain layer, not additional runtimes.

## 9. Memory

Evaluation/pattern memory:

```text
core/memory/evaluation_memory.py
```

Typed project-scoped Brain memory:

```text
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
```

Memory is historical/advisory and cannot select flows, activate skills, validate hypotheses, satisfy current-run gates or approve release.

## 10. Brain scorecard

Current owner:

```text
core/brain_os/scorecard.py
```

It aggregates canonical runtime evaluation + critic + evidence-integrity reports while preserving provenance. It has no synthetic PASS/release authority.

## 11. Knowledge OS

Declarative Knowledge OS is implemented and current.

Canonical owners:

```text
skills_UIUX/knowledge/
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-record.schema.json
skills_UIUX/schemas/knowledge-index.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

Retrieval remains:

```text
post-flow-selection
metadata-first
deterministic
context-bounded
provenance-bearing
vector-free
advisory-only
```

Current canonical corpus contains five domain records:

```text
financial-services
art-culture
industrial-services
mobility-ev
education-edtech
```

Canonical EV:

```text
knowledge.domain.ev-charging-ocpp-transaction-semantics.v1
```

Canonical EdTech:

```text
knowledge.domain.edtech-lti-context-roles-services.v2
```

Current post-promotion truth contract:

```text
uiux-factory/benchmarks/knowledge-canonical-state-v3.json
uiux-factory/core/benchmarks/knowledge_edtech_canonical_apply.py
uiux-factory/scripts/validate_knowledge_edtech_canonical_apply.py
```

A50.13 verifies exact five-record topology, canonical content/record integrity, financial/art/industrial/EV/EdTech retrieval regression, AI negative isolation, context budgets, rollback contract, vector-disabled state, owner delegation and GenAI HOLD.

A50.14 freshness truth:

```text
uiux-factory/benchmarks/knowledge-genai-nist-freshness-review-v1.json
uiux-factory/core/benchmarks/knowledge_genai_nist_freshness_review.py
uiux-factory/scripts/validate_knowledge_genai_nist_freshness_review.py
```

GenAI/NIST has an evidence-backed `KEEP_HOLD_FRESHNESS_REVIEW` decision. It remains unindexed, uncanonicalized, non-evidence-bearing and non-promotable until the explicit NIST framework status-change trigger occurs.

A52.3 re-checks both the freshness HOLD and `vector_search_change_allowed=false`, so neither became the selected successor debt package. Flow 1 and Flow 2 leave those boundaries unchanged.

## 12. Benchmarks / regression / dogfood

Current regression surfaces include:

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
uiux-factory/benchmarks/post-interop-executable-debt-audit-v1.json
uiux-factory/benchmarks/runtime-compatibility-convergence-v1.json
uiux-factory/benchmarks/compatibility-surface-governance-v1.json
uiux-factory/core/benchmarks/
skills_UIUX/scripts/eval-harness.py
.github/workflows/a13-*.yml
.github/workflows/a14-fix-once-validate-across-projects.yml
.github/workflows/a20-release-candidate.yml
.github/workflows/uiux-factory-ci.yml
```

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider/lifecycle/retrieval contracts, A51.1 provider migration readiness, A52.1 lifecycle mutation readiness, A52.2 lifecycle event interoperability, Flow 1 / A53.1 runtime compatibility convergence, Flow 2 / A53.2 compatibility surface governance, active five-record Knowledge OS truth, A50.14 freshness HOLD and full pytest.

A52.3 remains historical debt-selection evidence; its 8/19 current-census validator is removed from active current-state CI after convergence. Historical topology-bound A50 governance/canary/shadow tests likewise remain preserved but frozen once their assumptions no longer represent current canonical topology.

A20 remains release-candidate regression/security/dogfood over pinned Nova, Lumen and CENNEXT. A13 remains real Nova browser dogfood when path-triggered.

## 13. External collaborator / GitHub control plane

Bounded collaboration:

```text
external collaborator
→ task metadata / manifest
→ canonical Flow OS interpretation
→ target branch / PR
→ Actions / browser evidence
→ review / repair / release authority
```

Relevant surfaces:

```text
.github/workflows/external-agent-runner.yml
.github/workflows/external-agent-connector-bridge.yml
skills_UIUX/scripts/github-external-agent-runner.py
skills_UIUX/scripts/github-connector-task-request.py
```

These transport/compile governed work; they do not prove implementation or QA PASS themselves.

## 14. Capability ownership snapshot

| Capability | Current owner | Classification |
|---|---|---|
| Product entry lifecycle | `run.py` + `core/manager/` + `RunContext` | KEEP / FACTORY MUTATION OWNER |
| Managed lifecycle checkpoints | `core/runtime/flow_os/managed.py` | KEEP / MANAGED MUTATION OWNER |
| Lifecycle projection | `core/runtime/lifecycle_projection.py` | KEEP / READ-ONLY |
| Lifecycle mutation readiness | A52.1 benchmark/evaluator | IMPLEMENTED / NON-AUTHORITATIVE |
| Lifecycle event interoperability | `core/runtime/lifecycle_event_interop.py` | IMPLEMENTED / OBSERVATION-ONLY |
| Post-interop executable debt selection | A52.3 benchmark/evaluator | HISTORICAL / AUDIT-ONLY |
| First-party runtime compatibility convergence | A53.1 benchmark/evaluator | IMPLEMENTED / CURRENT ZERO-CONSUMER GATE |
| Compatibility surface governance | A53.2 benchmark/evaluator | IMPLEMENTED / DEPRECATED WITH SUNSET / REMOVAL CLOSED |
| Task interpretation / flow planning | `core/runtime/flow_os/` | KEEP / CANONICAL |
| Skills / methodology | `skills_UIUX/<skill>/SKILL.md` | KEEP / DECLARATIVE |
| Runtime policy | `skills_UIUX/runtime/runtime-policy.json` | KEEP |
| `skills_UIUX/runtime/*.py` | compatibility shims | DEPRECATED WITH SUNSET / REVIEW NOT BEFORE 2026-12-31 / NO DELETION AUTHORITY |
| Factory provider lane | `core/runtime/free_provider.py` | ADAPT / LEGACY DEFAULT |
| Provider compatibility contract | `core/runtime/provider_compat_contract.py` | IMPLEMENTED / BOUNDED |
| Provider default readiness | A51.1 benchmark/evaluator | IMPLEMENTED / LIVE EVIDENCE HOLD |
| Provider-neutral contracts | `core/runtime/flow_os/provider*.py` | KEEP / CANONICAL CONTRACT |
| Runtime evidence | `core/runtime/flow_os/evidence.py` | KEEP |
| Provenance | `core/provenance/` | KEEP |
| Browser/render QA | `uiux-factory/qa/` + adapters | KEEP |
| Terminal evaluation | `core/evaluation/run_evaluator.py` | KEEP |
| Brain reasoning/control | `core/brain_os/` | IMPLEMENTED / BOUNDED |
| Critics + repair | `core/brain_os/critics/` + repair surfaces | IMPLEMENTED / ADVISORY / PROPOSAL ONLY |
| Typed semantic memory | `core/brain_os/memory_contracts.py` + `core/memory/brain_memory.py` | IMPLEMENTED / ADVISORY |
| Brain scorecard | `core/brain_os/scorecard.py` | IMPLEMENTED / AGGREGATION ONLY |
| Declarative Knowledge OS | `skills_UIUX/knowledge/` + `core/brain_os/knowledge_retrieval.py` | IMPLEMENTED / ADVISORY |

## 15. Standing owner delegation

Current continuation policy:

```text
uiux-factory/benchmarks/governance-owner-delegation-v1.json
```

It permits bounded follow-up work when mandatory gates pass. It forbids bypassing failed/missing checks or fabricating independent-human evidence. Final retrospective owner review remains deferred until the broader upgrade completes.

## 16. Remaining convergence / debt

1. Provider default remains `legacy`; A51.1 live evidence is `0/8`, so no provider-default migration governance is open.
2. Lifecycle event interoperability is implemented as read-only observation, but direct mutation unification remains blocked by all six A52.1 semantic differences.
3. GenAI/NIST is freshness-held with an explicit official-source re-review trigger; no active promotion path exists now.
4. Vector/semantic retrieval remains deferred and disabled.
5. First-party `runtime.*` compatibility-import debt is closed at 0 files / 0 imports. Eight public shim files remain under a documented criteria-based sunset; removal governance is closed and the earliest fresh removal-readiness review is 2026-12-31.
6. Time-sensitive factual/regulatory knowledge still requires current source verification.

## 17. Rules for next convergence work

Future work must preserve:

```text
Brain OS reasoning/control
→ canonical task interpretation / flow planning
→ Factory manager or ManagedFlowController
→ specialist execution / tools
→ existing evidence + QA
→ canonical evaluation
→ advisory memory/scorecard/knowledge
```

It must not create a third runtime/provider-policy abstraction, copy skill methodology into Brain/provider constants, let advisory/observation/audit channels satisfy runtime gates, replace evidence truth with model-authored records, silently rewrite benchmark history, or treat compatibility shims as active owners.

Lifecycle convergence work additionally must not make the normalized event vocabulary into a shared mutation engine by accident.

Compatibility-surface governance must preserve the zero first-party census, keep shims logic-free, treat zero internal consumers as necessary but not sufficient evidence for external removal safety, and never interpret the sunset review date as automatic deletion authority.

## 18. Next architecture task

Flow 2 / A53.2 governs all eight retained compatibility shims as `DEPRECATE_WITH_SUNSET` while keeping removal governance closed.

The next compatibility-surface action is:

```text
Fresh removal-readiness audit no earlier than 2026-12-31
```

That later audit must refresh external-usage/downstream-dependency evidence and explicitly open a bounded owner-governed removal task before any file deletion can be proposed.

Provider migration remains separately blocked on A51.1 live evidence. Direct lifecycle mutation remains blocked by the six A52.1 differences. GenAI/NIST remains freshness-held. Vector search remains deferred.
