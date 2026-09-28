# Runtime Contracts and Compatibility

`skills_UIUX` owns **declarative runtime inputs**, not the executable Python runtime.

The single executable owner is:

```text
uiux-factory/core/runtime/flow_os/
```

See `uiux-factory/core/runtime/flow_os/README.md` for the canonical A4+ runtime ownership contract.

## What remains authoritative here

- `runtime-policy.json` — roles, authorities, sandbox/release/evaluation-memory policy consumed by Factory;
- `TASK-CONTRACT.md` — Task Contract semantics;
- `ADAPTIVE-FLOW.md` — adaptive change-surface semantics;
- `SAFE-READ.md` — A4.1 read contract;
- `A4-2-A4-5-RUNTIME-HARDENING.md` — worktree, target runner, typed evidence and file tools;
- `A4-6-A4-9-SANDBOX-RELEASE.md` — container/network sandbox, finalize/merge, production release and browser evidence;
- `A5-EVALUATION-MEMORY.md` — evidence-derived run evaluation and bounded advisory cross-run memory;
- `TOOL-OBSERVATION-CONTRACT.md` — tool/observation contract;
- `../flows/*.json` — declarative flow definitions;
- `../policies/*.json` — delivery policies;
- `../schemas/*.json` — declarative schemas;
- root skill folders and `SKILL.md` content.

## Deprecated Python compatibility surface

These files remain only so existing scripts/imports do not break during migration:

```text
runtime/adaptive_surface.py
runtime/agent.py
runtime/flow.py
runtime/manager.py
runtime/mcp_server.py
runtime/provider.py
runtime/provider_runner.py
runtime/task_context.py
```

They bootstrap `uiux-factory/` and re-export canonical symbols. **Do not add executable decision logic to these wrappers.** New runtime behavior belongs under `uiux-factory/`; Flow OS execution remains under `uiux-factory/core/runtime/flow_os/`, while canonical evaluation/memory behavior lives under `uiux-factory/core/evaluation/` and `uiux-factory/core/memory/`.

Legacy names are intentionally mapped onto canonical concepts:

```text
runtime.flow.DevelopmentManager
→ core.runtime.flow_os.flow.FlowPlanner

runtime.manager.DevelopmentManagerAgent
→ core.runtime.flow_os.managed.ManagedFlowController
```

This compatibility naming does not create a second Development Manager. The authoritative product-level Development Manager remains in `uiux-factory/core/manager/`.

## Flow OS boundary

```text
user goal
→ canonical GoalInterpreter / Task Contract
→ canonical FlowPlanner
→ declarative skills_UIUX flow + policy inputs
→ Factory execution adapter or ManagedFlowController
→ Safe Read + isolated worktree
→ provider/tool loop
→ container-sandboxed target execution
→ typed evidence + gates
→ browser-rendered evidence
→ evidence-derived terminal run evaluation
→ bounded project-scoped advisory evaluation memory
→ explicit external_write finalize/merge
→ explicit release-authority production deploy
```

Memory is attached only after canonical flow selection and is removed from replanning policy context. It never counts as current-run evidence and never changes authority, gates, merge or release decisions.

Provider code never owns stage order, handoff, merge or production release authority.

## Public managed CLI

```bash
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Redesign a B2B fintech settlement product" \
  --authority branch_write
```

The script imports `core.runtime.flow_os.*` directly; it does not execute a second runtime in `skills_UIUX`.

Release/finalize examples are documented in `A4-6-A4-9-SANDBOX-RELEASE.md`. Evaluation-memory behavior is documented in `A5-EVALUATION-MEMORY.md`.

## Validation

From `skills_UIUX/`:

```bash
python -B scripts/validate-flows.py
python -B scripts/validate-runtime-foundation.py
python -B scripts/validate-provider-runtime.py
```

From `uiux-factory/`:

```bash
python -m pytest -q tests
```

A4.1 through A4.9 form the canonical runtime hardening stack: safe read, isolated writes, bounded tools, trusted evidence, container/network sandboxing, controlled worktree finalization, browser-rendered proof and human-owned production release.

A5.1 through A5.3 add evidence-derived terminal evaluation and bounded project-scoped learning memory without weakening those A4 trust/authority boundaries.
