# Current Runtime Map

Status: **CURRENT THROUGH A50.10C**  
Audit date: **2026-10-02**  
Baseline: `main@538f3551445832291142f2c7d3d555284e69064d`

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
core/runtime/free_provider.py                 Factory legacy lane
core/runtime/flow_os/provider*.py             provider-neutral managed contracts
core/runtime/flow_os/provider_compat.py       bounded compatibility adapter surfaces
```

A48 established explicit provider capability reconciliation, artifact bridging, parity dogfood and a controlled opt-in compatibility lane.

Historical A48 used the phrase **different provider entry/capability contracts** to name the pre-convergence mismatch between the Factory legacy entry and the managed/provider-neutral surface. That phrase is retained as regression vocabulary; the current state is the controlled compatibility lane described below, not an unresolved duplicate-provider architecture.

Current rule:

```text
legacy = default
managed_compat = explicit opt-in
no automatic cross-lane fallback
```

Moving the default requires separate live-provider/governance evidence.

## 4. Lifecycle layer

A49 reconciles lifecycle meaning across Factory and managed surfaces using:

```text
INTAKE → INTERPRET → PLAN → RESEARCH → DESIGN → IMPLEMENT → QA → REPLAN → FINALIZE → RELEASE
```

Historical A48/A49 debt described the Factory and managed surfaces as **distinct top-level lifecycle APIs**. That phrase remains here as regression vocabulary: A49 now provides read-only lifecycle projection/parity across those surfaces, while mutation-level lifecycle unification is still intentionally deferred.

`LifecycleProjection` is read-only observability. It does not introduce a third state machine or equate completion with release.

Mutation-level lifecycle unification remains deferred pending a separate decision.

## 5. Evidence / provenance / QA

Canonical current-run evidence truth:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Browser/rendered QA remains the evidence-bearing path for visual/runtime claims when applicable.

Brain/model/provider metadata cannot silently become trusted evidence.

## 6. Terminal evaluation

Canonical terminal evaluator:

```text
core/evaluation/run_evaluator.py::RunEvaluator
```

It derives outcomes from latest-effective trusted evidence. A completed lifecycle without sufficient trusted PASS evidence remains insufficient evidence.

## 7. Brain OS

Bounded reasoning/control owner:

```text
uiux-factory/core/brain_os/
```

Implemented surfaces include:

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

Canonical implementation anchors retained for A48 architecture-regression coverage:

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

These anchors describe implemented owners, not additional runtimes. Brain OS is not a third execution runtime.

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

It aggregates canonical runtime evaluation + critic reports + evidence-integrity reports while preserving channel provenance. It has no synthetic PASS/release authority.

## 10. Knowledge OS

The declarative Knowledge OS **is implemented** and current.

Canonical owners:

```text
skills_UIUX/knowledge/
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-record.schema.json
skills_UIUX/schemas/knowledge-index.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

Retrieval is:

```text
post-flow-selection
metadata-first
deterministic
context-bounded
provenance-bearing
vector-free
advisory-only
```

Current canonical corpus after A50.10C contains four domain records:

```text
financial-services
art-culture
industrial-services
mobility-ev
```

The promoted EV record is:

```text
knowledge.domain.ev-charging-ocpp-transaction-semantics.v1
source = Open Charge Alliance OCPP 2.1 Edition 2 / Errata 2026-06
```

Current post-promotion truth contract:

```text
uiux-factory/benchmarks/knowledge-canonical-state-v2.json
uiux-factory/core/benchmarks/knowledge_ev_canonical_apply.py
uiux-factory/scripts/validate_knowledge_ev_canonical_apply.py
```

A50.10C verifies exact four-record topology, content/record integrity, Nova/Lumen/CENNEXT/EV retrieval isolation, EdTech/AI negative isolation, context budget, rollback contract, vector-search-disabled state and GenAI HOLD.

EdTech/LTI v2 has `CANARY_PASS` but remains unindexed pending its own promotion proposal/governance path.

GenAI/NIST remains `HOLD_FRESHNESS_REVIEW`.

## 11. Benchmarks / regression / dogfood

Current regression surfaces include:

```text
uiux-factory/benchmarks/corpus/
uiux-factory/benchmarks/routing-v1.json
uiux-factory/benchmarks/repair-proposals-v1.json
uiux-factory/benchmarks/memory-boundary-v1.json
uiux-factory/benchmarks/scorecard-v1.json
uiux-factory/core/benchmarks/
skills_UIUX/scripts/eval-harness.py
.github/workflows/a13-*.yml
.github/workflows/a14-fix-once-validate-across-projects.yml
.github/workflows/a20-release-candidate.yml
.github/workflows/uiux-factory-ci.yml
```

Main UIUX Factory CI validates deterministic product/routing/repair/memory/scorecard/provider/lifecycle/retrieval contracts, active four-record Knowledge OS truth and the full pytest suite.

Historical A50 topology-bound governance tests/validators are preserved but frozen after the EV canonical ref appears. This prevents valid three-record historical assertions from being misused as current four-record requirements.

A20 remains the release-candidate regression/security/dogfood lane over pinned Nova, Lumen and CENNEXT. A13 remains the real Nova browser dogfood lane when path-triggered.

Benchmark fixtures never substitute for target runtime/rendered evidence.

## 12. External collaborator / GitHub control plane

Bounded external collaboration:

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

These transport/compile governed work. They do not prove implementation or QA PASS by themselves.

## 13. Capability ownership snapshot

| Capability | Current owner | Classification |
|---|---|---|
| Product entry lifecycle | `run.py` + `core/manager/` | KEEP |
| Task interpretation / flow planning | `core/runtime/flow_os/` | KEEP / CANONICAL |
| Skills / methodology | `skills_UIUX/<skill>/SKILL.md` | KEEP / DECLARATIVE |
| Runtime policy | `skills_UIUX/runtime/runtime-policy.json` | KEEP |
| `skills_UIUX/runtime/*.py` | compatibility shims | DEPRECATE LATER / NO NEW LOGIC |
| Factory provider lane | `core/runtime/free_provider.py` | ADAPT / LEGACY DEFAULT |
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

Current repository-owner continuation policy:

```text
uiux-factory/benchmarks/governance-owner-delegation-v1.json
```

It permits bounded follow-up work when mandatory gates pass. It explicitly forbids bypassing failed/missing checks or fabricating independent-human evidence. Final retrospective owner review remains deferred until the broader upgrade completes.

## 15. Remaining convergence / debt

1. Provider default remains `legacy`; moving default requires stronger live-provider/governance evidence.
2. Lifecycle parity is read-only; mutation-level convergence remains a separate decision.
3. EdTech/LTI v2 has `CANARY_PASS` and is eligible for a bounded canonical-promotion proposal/governance path.
4. GenAI/NIST remains freshness-held.
5. Vector/semantic retrieval remains deferred and disabled.
6. Time-sensitive factual/regulatory knowledge still requires current source verification.

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

It must not:

- create a third runtime or provider-policy abstraction;
- copy skill methodology into Brain/provider constants;
- let memory/model/critic/scorecard/knowledge claims satisfy runtime gates;
- replace canonical evidence truth with model-authored records;
- silently rewrite benchmark history;
- treat compatibility shims as active owners.

## 17. Next architecture task

The next bounded Knowledge OS task is an **EdTech/LTI canonical-promotion proposal + governance review** based on the verified A50.9C `CANARY_PASS`.

The proposal must preserve the current EV-inclusive four-record canonical baseline, recheck source freshness, verify rollback/cross-domain risk and keep index mutation disabled. Even an approval may only open a separate explicit EdTech promotion implementation task.
