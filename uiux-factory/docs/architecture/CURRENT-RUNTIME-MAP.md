# Current Runtime Map

Status: **CURRENT THROUGH A50.14 / FIVE-RECORD KNOWLEDGE OS / GENAI HOLD EVIDENCED**  
Audit date: **2026-10-02**  
Baseline: `main@f84a3f4a606ada958a1dfa0e9f1c23c409aafb4c`

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

Historical A48 used **different provider entry/capability contracts** to name the pre-convergence mismatch between Factory legacy entry and managed/provider-neutral surface. Current state is the controlled compatibility lane, not duplicate provider authority.

Current rule:

```text
legacy = default
managed_compat = explicit opt-in
no automatic cross-lane fallback
```

Offline parity preserves the caller contract but is explicitly not live-provider or product evidence. Moving the default requires a separate live-provider readiness/evidence decision.

## 4. Lifecycle layer

A49 reconciles lifecycle meaning across Factory and managed surfaces using:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

Historical A48/A49 debt described these surfaces as **distinct top-level lifecycle APIs**. A49 provides read-only lifecycle projection/parity; mutation-level lifecycle unification remains intentionally deferred.

`LifecycleProjection` is read-only observability and does not introduce a third state machine or equate completion with release.

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

Canonical A48 regression anchors:

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

GenAI/NIST now has an evidence-backed `KEEP_HOLD_FRESHNESS_REVIEW` decision. It remains unindexed, uncanonicalized, non-evidence-bearing and non-promotable until the explicit NIST framework status-change trigger occurs.

## 11. Benchmarks / regression / dogfood

Current regression surfaces include:

```text
uiux-factory/benchmarks/corpus/
uiux-factory/benchmarks/routing-v1.json
uiux-factory/benchmarks/repair-proposals-v1.json
uiux-factory/benchmarks/memory-boundary-v1.json
uiux-factory/benchmarks/scorecard-v1.json
uiux-factory/benchmarks/provider-parity-v1.json
uiux-factory/core/benchmarks/
skills_UIUX/scripts/eval-harness.py
.github/workflows/a13-*.yml
.github/workflows/a14-fix-once-validate-across-projects.yml
.github/workflows/a20-release-candidate.yml
.github/workflows/uiux-factory-ci.yml
```

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider/lifecycle/retrieval contracts, active five-record Knowledge OS truth, A50.14 freshness HOLD and full pytest.

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
| Product entry lifecycle | `run.py` + `core/manager/` | KEEP |
| Task interpretation / flow planning | `core/runtime/flow_os/` | KEEP / CANONICAL |
| Skills / methodology | `skills_UIUX/<skill>/SKILL.md` | KEEP / DECLARATIVE |
| Runtime policy | `skills_UIUX/runtime/runtime-policy.json` | KEEP |
| `skills_UIUX/runtime/*.py` | compatibility shims | DEPRECATE LATER / NO NEW LOGIC |
| Factory provider lane | `core/runtime/free_provider.py` | ADAPT / LEGACY DEFAULT |
| Provider compatibility contract | `core/runtime/provider_compat_contract.py` | IMPLEMENTED / BOUNDED |
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

1. Provider default remains `legacy`; moving default requires live-provider readiness evidence beyond the existing offline parity benchmark.
2. Lifecycle parity is read-only; mutation-level convergence remains separate.
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

## 17. Next architecture task

Next bounded task:

```text
A51.1 — Provider Default Migration Readiness
```

This task must keep `legacy` as the default and define a fail-closed live-provider evidence path for evaluating `managed_compat`. It must not put credentials into repository artifacts or CI requirements, must not persist prompt/response bodies as evidence, and must not infer product quality from provider transport success. Default migration may only become a later explicit governance task after sufficient live receipts exist.
