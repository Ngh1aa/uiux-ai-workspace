# A40.1 — Current Runtime Map v2

Status: **CURRENT ARCHITECTURE TRUTH**  
Audit date: **2026-10-02**  
Baseline branch: `main`  
Baseline commit: `304baefb6999e552708150a20e5c01491aa3663e`

This document reconciles the repository after A4–A39 work. It replaces the A1-era topology description that was frozen at `0d564b184ab54017caedb85e9074822ff74a1c17`.

The A1 baseline remains a historical regression reference only. Current source and executable tests are authoritative when older A-series prose conflicts with this map.

## 1. Reconciliation summary

Between the historical A1 baseline and this audit baseline, `main` advanced by 92 commits. The most important architectural change is that A4 runtime consolidation is no longer future work:

```text
uiux-factory/core/runtime/flow_os/
```

is now the **single executable owner** for the shared Flow OS runtime.

Python modules under:

```text
skills_UIUX/runtime/*.py
```

are compatibility shims or declarative/runtime documentation inputs. They are not an independent executable Flow OS.

The repository therefore has **multiple supported entry/control surfaces, but one shared Flow OS execution owner**.

## 2. Canonical product entrypoint

The repository-level product source remains:

```text
uiux-factory/
```

Primary local Factory entrypoint:

```text
uiux-factory/run.py
```

Current product path:

```text
uiux-factory/run.py
→ CreativeDirectorDevelopmentManager
→ VisualBrainDevelopmentManager / DevelopmentManager lineage
→ ProfessionalWebsiteFlow adapter
→ canonical GoalInterpreter + FlowPlanner
→ Factory specialist stages
→ implementation / browser QA / visual QA / repair
```

`run.py` still owns the standard local Factory lifecycle and exclusive `RunLock`. It supports the Factory `ai` and `external` implementation lanes plus revision flows.

## 3. Canonical shared Flow OS runtime

Executable shared runtime ownership is:

```text
uiux-factory/core/runtime/flow_os/
```

This package owns executable behavior for:

- natural-language Task Contract interpretation;
- change-surface classification;
- declarative flow selection and skill resolution;
- managed lifecycle/checkpoint progression and bounded replanning;
- provider-neutral managed agent/provider loops;
- safe reads, bounded file tools and isolated worktree behavior;
- sandboxed target command execution;
- typed runtime evidence and gate semantics;
- browser-render evidence ingestion/capture;
- external-task packet compilation;
- explicit finalize/release authority boundaries;
- optional MCP/control adapters.

The canonical runtime owner is asserted by `tests/test_canonical_runtime_a4.py`.

## 4. Declarative knowledge, flow and policy ownership

`skills_UIUX/` remains authoritative for reusable declarative design/product knowledge and configuration:

```text
skills_UIUX/flows/*.json
skills_UIUX/<skill>/SKILL.md
skills_UIUX/policies/*.json
skills_UIUX/schemas/*.json
skills_UIUX/runtime/runtime-policy.json
skills_UIUX/runtime/*.md
```

The split is deliberate:

```text
skills_UIUX   → declarative knowledge / flow / policy contracts
uiux-factory  → executable runtime / orchestration / evidence / QA
```

Executable Python decision logic must not migrate back into `skills_UIUX/runtime/`.

## 5. Managed CLI and compatibility surface

The public managed CLI remains:

```text
skills_UIUX/scripts/uiux-agent.py
```

but it imports the canonical `core.runtime.flow_os.*` implementations directly.

Legacy Python files under `skills_UIUX/runtime/` remain for compatibility. They bootstrap/re-export Factory symbols and must not define independent GoalInterpreter, FlowPlanner, managed controller, provider runner, agent harness, evaluation engine or memory engine.

Canonical identity tests verify that legacy names resolve to the Factory runtime classes.

## 6. Manager and orchestration boundaries

There is one authoritative product-level manager lineage under:

```text
uiux-factory/core/manager/
```

`DevelopmentManager` owns the detailed Factory A→Z specialist-stage lifecycle.

`uiux-factory/core/orchestration/intelligent_flow.py` is an adapter over the canonical Flow OS planner. It maps canonical high-level stages such as:

```text
research → design → implementation → qa
```

onto the Factory's more detailed specialist stages. It does not own a competing GoalInterpreter or flow-selection algorithm.

`ManagedFlowController` in Flow OS is a managed lifecycle/checkpoint controller for the managed CLI. It is not a second product-level Development Manager.

### Remaining execution-surface distinction

Two supported execution experiences remain:

1. the full Factory product lifecycle through `uiux-factory/run.py`;
2. the provider-neutral managed Flow OS CLI through `skills_UIUX/scripts/uiux-agent.py`.

They share canonical task interpretation and flow planning but do not yet expose one identical top-level lifecycle API. This is an **adapter/convergence concern**, not evidence of two independent Flow OS implementations.

## 7. Provider surfaces

Provider transport remains an area with more than one active path:

### Factory internal AI lane

```text
uiux-factory/core/runtime/free_provider.py
```

is still used by the Factory product manager for its internal `ai` implementation lane.

### Managed/provider-neutral Flow OS lane

Provider-neutral managed behavior lives under:

```text
uiux-factory/core/runtime/flow_os/provider*.py
```

The two paths must not be mistaken for two flow runtimes. However, future Brain OS/provider work should converge their capability contract where practical instead of adding a third provider abstraction.

Provider/model output never owns stage order, authority, gate truth, merge or release decisions.

## 8. Evidence and provenance stack

The repository already contains multiple complementary evidence primitives.

### Runtime evidence

```text
uiux-factory/core/runtime/flow_os/evidence.py
uiux-factory/core/runtime/flow_os/browser_evidence.py
uiux-factory/core/runtime/flow_os/browser_observation.py
```

These own typed managed-run evidence and browser evidence integration.

### Fine-grained provenance

```text
uiux-factory/core/provenance/evidence_lineage.py
uiux-factory/core/provenance/release_evidence_registry.py
uiux-factory/core/contracts/evidence_provenance_schema.py
```

Fine-grained evidence lineage already creates stable, individually addressable evidence records for browser/reference facts. Future Brain OS Evidence Graph work must **adapt and extend these primitives**, not create a competing evidence truth system.

### QA ground truth

```text
uiux-factory/qa/
.github/workflows/cloud-qa-toolchain.yml
.github/workflows/post-render-evaluator-smoke.yml
```

plus newer state/deployment truth workflows provide rendered/runtime acceptance evidence.

A manifest, provider summary, model claim or generated artifact inventory is not equivalent to target runtime/rendered evidence.

## 9. Evaluation and memory

Canonical executable evaluation behavior lives under:

```text
uiux-factory/core/evaluation/
```

`RunEvaluator` derives terminal run outcomes from latest-effective trusted runtime evidence. A completed lifecycle without trusted PASS evidence is `insufficient_evidence`, not PASS.

Project-scoped advisory memory lives under:

```text
uiux-factory/core/memory/
```

`EvaluationMemoryStore` persists bounded evidence-derived outcomes and normalized quality patterns below the target project's `.uiux-agent-runs/memory/` area.

Current memory is deliberately advisory:

- it is attached after flow selection;
- it cannot select/modify flow;
- it cannot change authority;
- it cannot satisfy gates;
- it cannot become current-run evidence;
- it cannot approve merge/release.

Semantic design rationale, hypothesis/decision memory and generalized knowledge retrieval remain future Brain OS capabilities rather than current runtime truth.

## 10. Critique surface

A real visual critic already exists under:

```text
uiux-factory/core/agents/visual_critic.py
```

and is grounded in browser/design evidence rather than pixel/DOM proxy claims alone.

The repository does **not** yet have the proposed unified Brain OS Critique Orchestrator covering Product, UX/IA, Design System, Accessibility, Runtime and Evidence/Truth critics with one repair graph. Future critique work should adapt the current VisualCritic rather than replace it with an incompatible parallel schema.

## 11. Benchmarks, regression and dogfood

Current evaluation/regression surfaces include:

```text
uiux-factory/core/benchmarks/
uiux-factory/benchmarks/corpus/
skills_UIUX/scripts/eval-harness.py
.github/workflows/a13-*.yml
.github/workflows/a14-fix-once-validate-across-projects.yml
.github/workflows/a20-release-candidate.yml
```

The repository therefore already has domain regression, real-project dogfood and provider-neutral reliability primitives. A future unified Brain OS benchmark should aggregate/adapt these existing sources instead of silently replacing their corpus truth.

## 12. External collaborator / GitHub control plane

The external-collaborator path is now an explicit control plane:

```text
external collaborator
→ bounded task metadata / manifest
→ canonical Flow OS interpretation
→ target repository branch / PR
→ GitHub Actions / browser evidence
→ review / repair / release authority
```

Relevant surfaces include:

```text
.github/workflows/external-agent-runner.yml
.github/workflows/external-agent-connector-bridge.yml
skills_UIUX/scripts/github-external-agent-runner.py
skills_UIUX/scripts/github-connector-task-request.py
```

These compile/transport governed work. They do not by themselves constitute LLM execution or product QA PASS.

## 13. MetaGPT boundary

`MetaGPT/` remains vendored framework/dependency source used by parts of the specialist role/team implementation. It is not the canonical UI/UX methodology owner, Flow OS owner, product manager, knowledge store or future Brain OS.

## 14. Capability ownership snapshot

| Capability | Current canonical owner | A40.1 classification |
|---|---|---|
| Product entry lifecycle | `uiux-factory/run.py` + `core/manager/` | KEEP |
| Shared Task Contract / Goal interpretation | `core/runtime/flow_os/task_context.py` | KEEP |
| Flow planning / bounded replanning | `core/runtime/flow_os/flow.py` + `skills_UIUX/flows/*.json` | KEEP |
| Skills / design methodology | `skills_UIUX/<skill>/SKILL.md` | KEEP |
| Runtime authority/policy | `skills_UIUX/runtime/runtime-policy.json` consumed by Factory | KEEP |
| Managed Flow OS runtime | `core/runtime/flow_os/` | KEEP |
| `skills_UIUX/runtime/*.py` legacy runtime names | compatibility shims | DEPRECATE LATER; DO NOT ADD LOGIC |
| Detailed Factory stage mapping | `core/orchestration/intelligent_flow.py` | KEEP / ADAPT |
| Product Development Manager | `core/manager/` | KEEP |
| Managed lifecycle/checkpoints | `core/runtime/flow_os/managed.py` | KEEP / ADAPT |
| Factory internal provider lane | `core/runtime/free_provider.py` | ADAPT / CONVERGE |
| Managed provider-neutral lane | `core/runtime/flow_os/provider*.py` | KEEP |
| Runtime evidence | `core/runtime/flow_os/evidence.py` | KEEP |
| Fine-grained evidence provenance | `core/provenance/evidence_lineage.py` | KEEP / EXTEND |
| Release evidence registry | `core/provenance/release_evidence_registry.py` | KEEP |
| Browser/render QA | `uiux-factory/qa/` + Flow OS browser adapters | KEEP |
| Terminal evaluation | `core/evaluation/run_evaluator.py` | KEEP / EXTEND |
| Advisory evaluation memory | `core/memory/evaluation_memory.py` | KEEP / EXTEND |
| Visual critique | `core/agents/visual_critic.py` | ADAPT into future critique orchestration |
| Brain OS reasoning/control layer | not implemented | NEW, future; MUST NOT become a runtime |
| Semantic Knowledge OS | not implemented as one canonical subsystem | NEW, future |
| Unified multi-critic orchestrator | not implemented | NEW, future |
| Unified Brain benchmark scorecard | not implemented | NEW, future; aggregate existing evals |

## 15. Duplicate/overlap audit

### Resolved by A4

- `skills_UIUX/runtime` no longer owns an independent executable Flow OS.
- Goal interpretation and FlowPlanner class identity are shared.
- the managed CLI imports Factory Flow OS directly.

### Intentional adapters, not duplicates

- `ProfessionalWebsiteFlow` maps high-level canonical stages to detailed Factory specialist stages.
- `ManagedFlowController` manages checkpointed CLI lifecycle while the product DevelopmentManager owns the full Factory product lifecycle.
- Flow OS browser adapters and the larger `uiux-factory/qa/` harness operate at different integration depths but share the same truth boundary: rendered/runtime evidence must be explicit.

### Remaining convergence/debt

1. Factory internal `free_provider.py` and Flow OS provider-neutral adapters expose different provider entry paths.
2. Factory product execution and the managed CLI share routing but still expose distinct top-level lifecycle APIs.
3. Evidence is strong but distributed across runtime evidence, provenance lineage, release registry and QA artifacts; Brain OS needs an adapter graph, not another source of truth.
4. Memory is currently evaluation/pattern oriented; design rationale, hypotheses and decisions are not yet a typed persistent memory layer.
5. Visual critique exists, but multi-discipline critique orchestration and repair synthesis do not.
6. Benchmarks/evals exist in several layers and do not yet produce one provenance-aware Brain OS scorecard.

## 16. A40.1 rule for Brain OS work

Future Brain OS implementation must build **above and through** the canonical owners documented here:

```text
Brain OS reasoning/control
→ canonical GoalInterpreter / FlowPlanner
→ existing Factory / ManagedFlowController execution
→ existing evidence + QA
→ existing evaluation/memory
```

It must not:

- create a third execution runtime;
- copy `skills_UIUX` methodology into Python planner prompts;
- create a competing evidence truth model when adapters can extend current evidence/provenance primitives;
- allow memory/model claims to satisfy gates;
- treat compatibility shims as active implementation owners;
- silently replace benchmark corpus truth.

A40.2 should turn these boundaries into executable architecture guardrail tests before Brain Core Contracts are introduced.
