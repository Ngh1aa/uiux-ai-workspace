# Runtime Contracts and Compatibility

`skills_UIUX` owns **declarative runtime inputs**, not the executable Python runtime.

The single executable owner is:

```text
uiux-factory/core/runtime/flow_os/
```

See `uiux-factory/core/runtime/flow_os/README.md` for the A4 ownership contract.

## What remains authoritative here

- `runtime-policy.json` — role, authority and permission policy consumed by Factory;
- `TASK-CONTRACT.md` — Task Contract semantics;
- `ADAPTIVE-FLOW.md` — adaptive change-surface semantics;
- `SAFE-READ.md` — A4.1 model/provider-facing filesystem read contract;
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

They bootstrap `uiux-factory/` and re-export canonical symbols. **Do not add executable decision logic to these wrappers.** New runtime behavior belongs under `uiux-factory/core/runtime/flow_os/`.

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
→ Safe Read for model/provider-facing project + skill text
→ specialist/provider/tool loop
→ evidence + gates
→ advance or bounded replan
```

Provider code never owns stage order or handoff. Managed lifecycle state, provider loops, permission/checkpoint harness code, Safe Read enforcement and the optional MCP adapter are all implemented in the canonical Factory runtime.

## A4.1 Safe Read

Safe Read is active for:

- `read_text`;
- safe project directory listing;
- project/source context manifest reads;
- provider skill/source context loading.

It rejects traversal/root escape, symlinks, credential-bearing paths, `.git`, `.uiux-agent-runs`, `node_modules`, oversized files, binary/NUL content, invalid UTF-8 and obvious private-key material. Provider context revalidates stored paths against roots supplied by the active harness instead of trusting checkpoint metadata.

See [`SAFE-READ.md`](SAFE-READ.md) for the complete contract and scope boundary.

## Public managed CLI

The compatibility command remains stable:

```bash
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Redesign a B2B fintech settlement product" \
  --authority branch_write
```

The script imports `core.runtime.flow_os.*` directly; it does not execute a second runtime in `skills_UIUX`.

Provider examples remain supported:

```bash
export OPENAI_API_KEY="your-key"
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Build a modern ecommerce store" \
  --provider openai \
  --authority branch_write
```

```bash
export ANTHROPIC_API_KEY="your-key"
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Build a modern ecommerce store" \
  --provider anthropic \
  --authority branch_write
```

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

A4.1 is the read-safety hardening milestone. Worktree isolation, target-runner isolation, typed evidence/gates and expanded file tools remain A4.2–A4.5 follow-up work.
