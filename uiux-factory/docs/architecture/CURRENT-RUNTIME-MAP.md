# Current Runtime Map

Status: **CURRENT THROUGH A52.1 / PROVIDER LIVE-EVIDENCE HOLD / LIFECYCLE MUTATION HOLD**  
Audit date: **2026-10-02**  
Baseline before A52.1: `main@f860a47b7c629974736f14c95eb13b7b9824f47f`

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

`skills_UIUX/runtime/*.py` are compatibility shims. New runtime authority must not be added there.

## 3. Provider layer

Current provider surfaces:

```text
core/runtime/free_provider.py                    Factory legacy lane
core/runtime/provider_compat_contract.py         lane/shared compatibility contract
core/runtime/flow_os/provider*.py                provider-neutral managed contracts
core/runtime/flow_os/factory_provider_adapter.py bounded compatibility adapter
```

A48 established explicit provider capability reconciliation, artifact bridging, parity dogfood and a controlled opt-in compatibility lane.

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

## 4. Lifecycle layer

A49 reconciles lifecycle meaning across Factory and managed surfaces using:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

`LifecycleProjection` remains read-only observability and does not introduce a third state machine or equate completion with release.

Current state owners remain intentionally distinct:

```text
Factory -> core.runtime.run_context.RunContext
Managed -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

A52.1 now evaluates mutation-level convergence readiness rather than assuming projection parity implies state-machine parity:

```text
benchmarks/lifecycle-mutation-convergence-readiness-v1.json
core/benchmarks/lifecycle_mutation_convergence_readiness.py
scripts/validate_lifecycle_mutation_convergence_readiness.py
```

Current audited mutation blockers:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

Expected/current A52.1 decision:

```text
KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED
event_interop_proposal_allowed = true
mutation_governance_allowed = false
```

This permits only a later additive lifecycle-event interoperability proposal. It does not authorize replacing `RunContext`, replacing `ManagedWebsiteRun`, sharing mutable state, changing transitions, or changing release/evidence/gate authority.

## 5. Evidence / provenance / QA

Canonical current-run evidence truth:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Browser/rendered QA remains evidence-bearing for visual/runtime claims when applicable. Brain/model/provider/knowledge metadata cannot silently become trusted evidence.

## 6. Terminal evaluation

Canonical terminal evaluator:

```text
core/evaluation/run_evaluator.py::RunEvaluator
```

It derives outcomes from latest-effective trusted evidence. Completed lifecycle without sufficient trusted PASS evidence remains insufficient evidence.

## 7. Brain OS

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

## 8. Memory

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

## 9. Brain scorecard

Current owner:

```text
core/brain_os/scorecard.py
```

It aggregates canonical runtime evaluation + critic + evidence-integrity reports while preserving provenance. It has no synthetic PASS/release authority.

## 10. Knowledge OS

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

## 11. Benchmarks / regression / dogfood

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
uiux-factory/core/benchmarks/
skills_UIUX/scripts/eval-harness.py
.github/workflows/a13-*.yml
.github/workflows/a14-fix-once-validate-across-projects.yml
.github/workflows/a20-release-candidate.yml
.github/workflows/uiux-factory-ci.yml
```

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider/lifecycle/retrieval contracts, A51.1 provider migration readiness, A52.1 lifecycle mutation readiness, active five-record Knowledge OS truth, A50.14 freshness HOLD and full pytest.

Historical topology-bound A50 governance/canary/shadow tests remain preserved but are frozen once their assumptions no longer represent current canonical topology.

A20 remains release-candidate regression/security/dogfood over pinned Nova, Lumen and CENNEXT. A13 remains real Nova browser dogfood when path-triggered.

## 12. External collaborator / GitHub control plane

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

## 13. Capability ownership snapshot

| Capability | Current owner | Classification |
|---|---|---|
| Product entry lifecycle | `run.py` + `core/manager/` + `RunContext` | KEEP / FACTORY MUTATION OWNER |
| Managed lifecycle checkpoints | `core/runtime/flow_os/managed.py` | KEEP / MANAGED MUTATION OWNER |
| Lifecycle projection | `core/runtime/lifecycle_projection.py` | KEEP / READ-ONLY |
| Lifecycle mutation readiness | A52.1 benchmark/evaluator | IMPLEMENTED / NON-AUTHORITATIVE |
| Task interpretation / flow planning | `core/runtime/flow_os/` | KEEP / CANONICAL |
| Skills / methodology | `skills_UIUX/<skill>/SKILL.md` | KEEP / DECLARATIVE |
| Runtime policy | `skills_UIUX/runtime/runtime-policy.json` | KEEP |
| `skills_UIUX/runtime/*.py` | compatibility shims | DEPRECATE LATER / NO NEW LOGIC |
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

## 14. Standing owner delegation

Current continuation policy:

```text
uiux-factory/benchmarks/governance-owner-delegation-v1.json
```

It permits bounded follow-up work when mandatory gates pass. It forbids bypassing failed/missing checks or fabricating independent-human evidence. Final retrospective owner review remains deferred until the broader upgrade completes.

## 15. Remaining convergence / debt

1. Provider default remains `legacy`; A51.1 live evidence is `0/8`, so no provider-default migration governance is open.
2. Lifecycle mutation unification remains blocked by six A52.1 semantic differences; only additive event interoperability is eligible as the next bounded lifecycle proposal.
3. GenAI/NIST is freshness-held with an explicit official-source re-review trigger; no active promotion path exists now.
4. Vector/semantic retrieval remains deferred and disabled.
5. Time-sensitive factual/regulatory knowledge still requires current source verification.

## 16. Rules for next convergence work

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

It must not create a third runtime/provider-policy abstraction, copy skill methodology into Brain/provider constants, let advisory channels satisfy runtime gates, replace evidence truth with model-authored records, silently rewrite benchmark history, or treat compatibility shims as active owners.

Lifecycle convergence work additionally must not make a normalized event vocabulary into a shared mutation engine by accident.

## 17. Next architecture task

After A52.1 passes and merges, next bounded task:

```text
A52.2 — Lifecycle Event Interoperability Contract
```

That task may normalize read-only lifecycle events/receipts across Factory append-only chronology and Managed checkpoint transitions for observability/regression. It must preserve both mutation owners and have:

```text
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

Provider migration remains separately blocked on A51.1 live evidence. GenAI/NIST remains freshness-held. Vector search remains deferred.
