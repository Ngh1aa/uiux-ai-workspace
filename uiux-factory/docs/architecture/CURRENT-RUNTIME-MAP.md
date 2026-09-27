# A1 — Current Runtime Map

Status: **CURRENT ARCHITECTURE TRUTH**  
Audit date: **2026-09-28**  
Baseline branch: `main`  
Baseline commit: `0d564b184ab54017caedb85e9074822ff74a1c17`

This document freezes the verified runtime topology before A2+ changes. It is descriptive, not a migration plan.

## 1. Canonical product surface

The repository-level canonical product source remains:

```text
uiux-factory/
```

Primary local Factory entrypoint:

```text
uiux-factory/run.py
```

`run.py` currently instantiates `CreativeDirectorDevelopmentManager`, applies the exclusive `RunLock`, supports `engine=ai` and `engine=external`, and owns the standard local Factory run lifecycle.

Current Factory manager chain:

```text
uiux-factory/run.py
→ CreativeDirectorDevelopmentManager
→ VisualBrainDevelopmentManager
→ DevelopmentManager lineage
→ specialist stages / skills / implementation / QA
```

The Factory persists run artifacts below `uiux-factory/runs/` and generated outputs below `uiux-factory/generated/`.

## 2. Active managed Flow OS surface

A second active execution surface exists under:

```text
skills_UIUX/runtime/
```

Public CLI entrypoint:

```text
skills_UIUX/scripts/uiux-agent.py
```

Current managed path:

```text
uiux-agent.py
→ ProviderNeutralAgentHarness
→ DevelopmentManagerAgent
→ GoalInterpreter
→ FlowResolver
→ resolved specialist stage
→ ProviderManagedRunner (optional)
→ provider → tool → observation loop
```

The managed runtime currently supplies:

- declarative flow resolution;
- bounded replanning;
- role/authority enforcement;
- local checkpoint/resume;
- provider-neutral OpenAI / Anthropic / command adapters;
- MCP skeleton;
- tool registry and trace recording.

This runtime is **active and validated**, but it is not yet the repository's single canonical executable product runtime. Consolidation belongs to A4.

## 3. Flow and skill ownership

Current declarative flow source:

```text
skills_UIUX/flows/*.json
```

Current shared capability/policy source:

```text
skills_UIUX/*/SKILL.md
skills_UIUX/** policy/reference files
```

`skills_UIUX` owns reusable UI/UX knowledge, policies, flow documents and managed-runtime contracts. `uiux-factory` owns the canonical Factory product implementation and cloud QA harness.

A1 does not move these responsibilities.

## 4. Provider surfaces

Two provider paths currently coexist.

### Factory internal AI path

```text
uiux-factory/core/runtime/free_provider.py
```

This path is used by the local Factory `engine=ai` flow and is intentionally bounded around its configured provider policy.

### Provider-neutral managed runtime

```text
skills_UIUX/runtime/provider.py
```

This path currently supports:

```text
openai
anthropic
command
auto
```

These are different execution surfaces. Do not infer whole-repository provider support from `free_provider.py` alone.

## 5. External-brain path

The root README defines ChatGPT / external collaborator usage through the Factory's `engine=external` handoff model:

```text
External AI collaborator
→ Factory intelligence/design artifacts
→ target GitHub repository
→ branch / pull request
→ GitHub Actions / browser evidence
→ creative review / repair
```

`handoff_ready` is not equivalent to completed implementation or rendered QA PASS.

## 6. QA ownership

Canonical cloud QA remains under:

```text
uiux-factory/qa/
.github/workflows/cloud-qa-toolchain.yml
.github/workflows/post-render-evaluator-smoke.yml
```

The managed Flow OS also contains a lightweight Playwright capture adapter under:

```text
skills_UIUX/integrations/playwright/
```

The lightweight adapter must not be treated as equivalent to the full Factory QA harness.

## 7. MetaGPT role

`MetaGPT/` is vendored framework source. It is not the repository's canonical UI/UX knowledge owner.

The Factory currently uses MetaGPT abstractions for specialist role/team execution, while orchestration policy, skills, gates and product-specific lifecycle remain owned by the UIUX Factory / Flow OS layers.

## 8. Current architecture debt explicitly frozen by A1

The following are verified current-state overlaps, not A1 fixes:

1. `uiux-factory` and `skills_UIUX/runtime` both contain orchestration/runtime responsibility.
2. Provider policy exists in both the bounded Factory AI path and the newer provider-neutral managed path.
3. MCP exists only as a limited managed-runtime adapter, not yet as the Factory control plane.
4. Browser/render evidence exists in multiple layers with different capability depth.
5. Prompt Compiler, Factory execution and managed Flow OS are related but still expose multiple task-entry surfaces.

A4 is responsible for runtime consolidation. A5+ must build on the canonical result of A4 rather than creating a third orchestration path.

## 9. Baseline validation snapshot

Baseline commit:

```text
0d564b184ab54017caedb85e9074822ff74a1c17
```

Latest `UIUX Factory CI` run for that commit completed successfully. Its `foundation` job passed all recorded steps, including:

- recursive checkout/submodules;
- pinned Anthropic skill verification;
- Motion Primitives corpus verification;
- active Python compilation for `uiux-factory` and `skills_UIUX/runtime`;
- declarative Flow Agent OS validation;
- runtime foundation validation;
- `uiux-factory` foundation pytest suite.

The same baseline commit also completed the `Post-render Evaluator Smoke` workflow successfully.

This baseline is the A1 regression reference for A2+.

## 10. A1 rule for future changes

Until A4 completes:

- do not delete either runtime surface;
- do not silently redirect one CLI to the other;
- do not move skill ownership into provider code;
- do not treat legacy planning documents as runtime truth;
- preserve the baseline CI invariants before advancing to the next A-step.
