# A48.1 — Current Runtime Map v3

Status: **CURRENT ARCHITECTURE TRUTH**  
Audit date: **2026-10-02**  
Baseline branch: `main`  
Baseline commit: `38b11b347281cba8f8dd0b3cd6f99dcba62fdb95`

This document reconciles the repository after A40–A47. It supersedes the A40.1 v2 map wherever that map described Brain OS, critique, typed memory or unified scorecard work as future/unimplemented.

Current source and executable tests remain authoritative when historical A-series prose disagrees with this map.

## 1. Runtime ownership

The shared executable Flow OS owner remains:

```text
uiux-factory/core/runtime/flow_os/
```

This package owns executable task interpretation, change-surface classification, flow planning, skill resolution, managed lifecycle/checkpoints, provider-neutral managed loops, bounded tools/sandboxing, runtime evidence, browser-evidence integration and finalize/release authority boundaries.

`skills_UIUX/runtime/*.py` remains compatibility-only. New executable decision logic must not be added there.

## 2. Declarative knowledge / policy ownership

`skills_UIUX/` remains authoritative for reusable declarative methodology and configuration:

```text
skills_UIUX/flows/*.json
skills_UIUX/<skill>/SKILL.md
skills_UIUX/policies/*.json
skills_UIUX/schemas/*.json
skills_UIUX/runtime/runtime-policy.json
skills_UIUX/runtime/*.md
```

The split remains:

```text
skills_UIUX   → declarative knowledge / flow / policy contracts
uiux-factory  → executable runtime / orchestration / evidence / QA / Brain adapters
```

## 3. Product and managed execution surfaces

The primary Factory product path remains:

```text
uiux-factory/run.py
→ core/manager/
→ core/orchestration/intelligent_flow.py
→ canonical GoalInterpreter / FlowPlanner
→ specialist stages
→ implementation / browser QA / visual QA / repair
```

The public managed CLI remains:

```text
skills_UIUX/scripts/uiux-agent.py
```

and imports the canonical `core.runtime.flow_os.*` runtime.

These are two supported execution experiences sharing canonical routing/runtime owners. They do **not** yet expose one identical top-level lifecycle API; that remains an adapter/convergence concern, not a second Flow OS.

## 4. Provider surfaces

Two provider entry paths remain active.

### Factory internal AI lane

```text
uiux-factory/core/runtime/free_provider.py
```

`FreeProvider.complete(...)` is used by the Factory internal AI implementation lane and returns provider text after its own free-tier transport/retry/fallback handling.

### Managed provider-neutral lane

```text
uiux-factory/core/runtime/flow_os/provider.py
uiux-factory/core/runtime/flow_os/provider_*.py
uiux-factory/core/runtime/flow_os/free_tier_provider.py
```

This lane uses canonical typed `ProviderStageRequest` / `ProviderStageResponse` contracts and enforces managed-stage tool/evidence/replan semantics.

The paths are **not** two flow runtimes, but their provider capability shapes differ. Future convergence must reuse/adapt the canonical managed contracts where practical and must not introduce a third provider-policy surface.

Provider/model output never owns stage order, authority, gate truth, evidence trust, merge or release decisions.

## 5. Evidence / provenance / QA truth

Canonical evidence truth remains distributed intentionally across complementary owners:

```text
core/runtime/flow_os/evidence.py
core/runtime/flow_os/browser_evidence.py
core/runtime/flow_os/browser_observation.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
core/contracts/evidence_provenance_schema.py
uiux-factory/qa/
```

Brain OS does not replace these owners.

A42 adds relationship and integrity views under:

```text
core/brain_os/reasoning/evidence_graph.py
core/brain_os/adapters/evidence.py
core/brain_os/reasoning/evidence_integrity.py
core/brain_os/reasoning/lineage_integrity.py
```

These surfaces reference/adapt canonical evidence IDs and validate lineage. They cannot upgrade trust, mark runtime gates passed or declare release readiness.

## 6. Brain OS reasoning/control layer

Brain OS is now implemented as a bounded control/reasoning layer under:

```text
uiux-factory/core/brain_os/
```

Implemented slices include:

```text
A41 — task / uncertainty / hypothesis / decision + critique/repair contracts
A42 — evidence relationship graph + integrity / lineage validation
A43 — canonical flow-selection adapter + JIT context projection + routing benchmark
A44 — advisory design/product/runtime/evidence critics
A45 — proposal-only root-cause / repair / retest synthesis + graph projection + benchmark
A46 — typed project-scoped semantic memory + post-routing recall + benchmark
A47 — provenance-aware scorecard aggregation + benchmark
```

Brain OS remains above/through canonical owners and is **not** an execution runtime.

## 7. Critique and repair

A44 provides advisory critics for:

```text
Visual
UX / IA
Design System
Accessibility
Product
Runtime
Evidence / Truth
```

Critic findings start as `OBSERVED`; critic reports do not PASS runtime gates or create trusted evidence.

A45 adds proposal-only repair synthesis:

```text
CritiqueIssue
→ RootCause(PROPOSED)
→ RepairDirective(PROPOSED)
→ RetestRequirement(PENDING)
```

and projects only:

```text
CAUSED_BY
REPAIRED_BY
REQUIRES_RETEST
```

into the EvidenceGraph. It deliberately creates no `VERIFIED_BY`/`RETESTED_BY` relationship and executes no repair/retest.

## 8. Evaluation and typed memory

Canonical terminal runtime evaluation remains:

```text
core/evaluation/run_evaluator.py::RunEvaluator
```

It derives run outcomes from latest-effective trusted runtime evidence. A completed lifecycle without sufficient trusted PASS evidence remains `insufficient_evidence`.

Evaluation/pattern memory remains under:

```text
core/memory/evaluation_memory.py
```

A46 additionally implements typed project-scoped historical Brain memory:

```text
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
```

Typed memory includes rationale, hypothesis and decision records with explicit provenance. Recall is attached only after canonical flow selection and excludes current-run memory from historical context.

All memory remains advisory:

```text
current_run_evidence = false
flow_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
```

It cannot select/replan flows, activate skills, validate hypotheses, select decisions, satisfy current-run gates or approve merge/deploy/release.

A broader general-purpose declarative Knowledge OS is still not implemented as one canonical subsystem; reusable methodology continues to belong in `skills_UIUX`.

## 9. Provenance-aware Brain scorecard

A47 implements:

```text
core/brain_os/scorecard.py
```

The scorecard aggregates already-produced channels:

```text
canonical RunEvaluation
+ A44 critic reports
+ A42 integrity reports
→ BrainScorecard
```

It mirrors the canonical runtime outcome verbatim and keeps critic/integrity channels separate. It intentionally has no synthetic PASS flag, release-readiness flag or numeric overall score.

The scorecard has no authority/gate/evidence/release effect and does not call `RunEvaluator.evaluate`, runtime gates or release controllers.

## 10. Benchmarks / regression / dogfood

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
```

Main UIUX Factory CI validates the deterministic benchmark corpora before running the full pytest suite. A20 remains the release-candidate regression/security/dogfood lane over pinned Nova, Lumen and CENNEXT.

Benchmark fixtures never substitute for target runtime/rendered evidence.

## 11. External collaborator / GitHub control plane

External collaboration remains a bounded control plane:

```text
external collaborator
→ bounded task metadata / manifest
→ canonical Flow OS interpretation
→ target branch / PR
→ Actions / browser evidence
→ review / repair / release authority
```

Relevant surfaces include:

```text
.github/workflows/external-agent-runner.yml
.github/workflows/external-agent-connector-bridge.yml
skills_UIUX/scripts/github-external-agent-runner.py
skills_UIUX/scripts/github-connector-task-request.py
```

These compile/transport governed work. They do not by themselves prove implementation or QA PASS.

## 12. Capability ownership snapshot

| Capability | Current owner | Current classification |
|---|---|---|
| Product entry lifecycle | `uiux-factory/run.py` + `core/manager/` | KEEP |
| Task interpretation | `core/runtime/flow_os/task_context.py` | KEEP |
| Flow planning / bounded replanning | `core/runtime/flow_os/flow.py` + `skills_UIUX/flows/*.json` | KEEP |
| Skills / methodology | `skills_UIUX/<skill>/SKILL.md` | KEEP |
| Runtime authority/policy | `skills_UIUX/runtime/runtime-policy.json` consumed by Factory | KEEP |
| Managed Flow OS runtime | `core/runtime/flow_os/` | KEEP |
| `skills_UIUX/runtime/*.py` | compatibility shims | DEPRECATE LATER; DO NOT ADD LOGIC |
| Product Development Manager | `core/manager/` | KEEP |
| Managed lifecycle/checkpoints | `core/runtime/flow_os/managed.py` | KEEP / ADAPT |
| Factory internal provider lane | `core/runtime/free_provider.py` | ADAPT / CONVERGE |
| Managed provider-neutral lane | `core/runtime/flow_os/provider*.py` | KEEP / CANONICAL CONTRACT |
| Runtime evidence | `core/runtime/flow_os/evidence.py` | KEEP |
| Evidence provenance | `core/provenance/` | KEEP |
| Browser/render QA | `uiux-factory/qa/` + Flow OS adapters | KEEP |
| Terminal evaluation | `core/evaluation/run_evaluator.py` | KEEP |
| Evaluation/pattern memory | `core/memory/evaluation_memory.py` | KEEP |
| Brain reasoning/control contracts | `core/brain_os/contracts.py` + adapters | IMPLEMENTED / BOUNDED |
| Multi-discipline critics | `core/brain_os/critics/` | IMPLEMENTED / ADVISORY |
| Repair synthesis | `core/brain_os/repair_orchestrator.py` | IMPLEMENTED / PROPOSAL ONLY |
| Typed semantic project memory | `core/brain_os/memory_contracts.py` + `core/memory/brain_memory.py` | IMPLEMENTED / ADVISORY |
| Brain scorecard | `core/brain_os/scorecard.py` | IMPLEMENTED / AGGREGATION ONLY |
| General declarative Knowledge OS | not implemented as one subsystem | FUTURE / DO NOT DUPLICATE `skills_UIUX` |

## 13. Remaining convergence / debt

Resolved since A40 v2:

- Brain reasoning/control contracts are implemented without adding a third runtime.
- Evidence Graph adapters/integrity exist over canonical evidence owners.
- Multi-discipline critics and proposal-only repair synthesis exist.
- Typed rationale/hypothesis/decision memory exists with project scope and provenance.
- A provenance-aware Brain scorecard exists without competing gate truth.

Active execution/convergence debt is now narrower:

1. `core/runtime/free_provider.py` and `core/runtime/flow_os/provider*.py` expose different provider entry/capability contracts.
2. Factory product execution and managed CLI execution still expose distinct top-level lifecycle APIs despite sharing canonical routing/runtime owners.
3. Architecture documents must continue to track source/test truth; A48 adds regression coverage against reintroducing resolved “not implemented” claims.

## 14. Rules for next convergence work

Future work must continue:

```text
Brain OS reasoning/control
→ canonical GoalInterpreter / FlowPlanner
→ Factory manager or ManagedFlowController
→ specialist execution / tools
→ existing evidence + QA
→ canonical evaluation + advisory memory/scorecard
```

It must not:

- create a third execution runtime;
- create a third provider-policy abstraction;
- copy `skills_UIUX` methodology into provider/Brain constants;
- let memory/model/critic/scorecard claims satisfy runtime gates;
- replace canonical evidence truth with Brain-authored records;
- silently rewrite benchmark corpus truth;
- treat compatibility shims as active implementation owners.

## 15. Next architecture task

A48.2 should map the two current provider entry paths into one explicit **provider capability reconciliation contract** before changing execution. The first objective is parity/adapter tests, not immediate deletion or replacement of either working lane.
