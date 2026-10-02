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

## Compatibility sunset governance

Flow 1 removed all known first-party imports of the deprecated Python wrappers, but **zero first-party consumers is necessary but not sufficient** evidence for deletion. This repository is public, the compatibility surface has been documented for existing imports, and external usage remains UNKNOWN. Public code search is discovery-only; zero search hits do not prove that no downstream consumer exists.

All eight wrappers are therefore classified as **deprecated with a criteria-based sunset**. They are not classified for indefinite retention, and removal governance is not open yet.

Earliest removal-governance review: **2026-12-31**.

That date is a review boundary after a minimum 90-day public observation window, not a removal event. **No shim is deleted automatically on or after that date.** A later removal-governance task must separately prove all of the following:

- the first-party AST census is still zero;
- thin-wrapper and symbol/class identity parity still passes;
- public guidance uses canonical imports rather than recommending the legacy modules;
- the minimum observation window has elapsed;
- an explicit external-usage audit has been completed;
- there is no known supported downstream dependency that still requires the wrappers;
- the repository owner explicitly opens a bounded removal task;
- mandatory CI/A20 gates pass on the exact removal-task head.

No import-time `DeprecationWarning` is added by this governance step because warning behavior itself can affect consumers and test environments.

Canonical migration map:

```text
runtime.adaptive_surface → core.runtime.flow_os.adaptive_surface
runtime.agent            → core.runtime.flow_os.agent
runtime.flow             → core.runtime.flow_os.flow
runtime.manager          → core.runtime.flow_os.managed
runtime.mcp_server       → core.runtime.flow_os.mcp_server
runtime.provider         → core.runtime.flow_os.provider
runtime.provider_runner  → core.runtime.flow_os.provider_runner
runtime.task_context     → core.runtime.flow_os.task_context
```

Compatibility aliases remain available during the observation window:

```text
runtime.flow.DevelopmentManager
→ core.runtime.flow_os.flow.FlowPlanner

runtime.manager.DevelopmentManagerAgent
→ core.runtime.flow_os.managed.ManagedFlowController
```

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
