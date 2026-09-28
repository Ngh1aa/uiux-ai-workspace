# Canonical Flow OS Runtime

`uiux-factory/core/runtime/flow_os/` is the **single executable owner** for the shared Flow OS runtime.

## Ownership

Factory runtime owns executable Python behavior for:

- natural-language Task Contract compilation;
- change-surface classification;
- declarative flow selection and skill resolution;
- managed lifecycle progression and bounded replanning;
- provider-stage contracts and managed provider loops;
- provider-neutral agent/checkpoint/permission harness behavior;
- canonical Safe Read enforcement for model/provider-facing file reads;
- the optional MCP runtime adapter.

`skills_UIUX/` remains the declarative knowledge/configuration owner for:

- `flows/*.json`;
- `policies/*.json`;
- `schemas/*.json`;
- skill folders and `SKILL.md` content;
- `runtime/runtime-policy.json` and runtime documentation.

The canonical runtime consumes those resources; it does not copy them into Factory.

## Compatibility rule

Python files under `skills_UIUX/runtime/` are deprecated compatibility shims. They may bootstrap `uiux-factory/` and re-export canonical symbols, but they must not define an independent `GoalInterpreter`, `FlowResolver`, `FlowPlanner`, managed Development Manager, provider runner, or agent harness.

The public managed CLI may stay at `skills_UIUX/scripts/uiux-agent.py` for backward compatibility, but it imports `core.runtime.flow_os.*` directly.

## Development Manager boundary

There is one authoritative product-level Development Manager: `uiux-factory/core/manager/development_manager.py` and its subclasses. `FlowPlanner` owns declarative routing decisions. `ManagedFlowController` is a lifecycle/checkpoint controller for the managed CLI; it is deliberately not named or implemented as another Development Manager.

`core/orchestration/intelligent_flow.py` is an execution adapter only. It maps the canonical high-level stages (`research`, `design`, `implementation`, `qa`) to Factory specialist stages and may add stage-specific skills, but it does not own a second Task Contract or flow-selection algorithm.

## A4 migration invariant

For the same goal:

1. Factory adapters and the managed CLI use the same `GoalInterpreter` class.
2. Both route through the same `FlowPlanner` implementation.
3. Legacy `skills_UIUX/runtime/*.py` imports resolve to the same canonical class identities.
4. Declarative flows/policies remain in `skills_UIUX`; executable decisions remain in `uiux-factory`.

## A4.1 Safe Read

`safe_read.py` is the single read boundary for model/provider-facing project and skill text.

It is intentionally fail-closed:

- reads must remain below an explicit trust root;
- symlink paths are rejected;
- credential-bearing paths, `.git`, `.uiux-agent-runs` and `node_modules` are denied;
- `.env.example`, `.env.sample` and `.env.template` remain readable as non-secret templates;
- reads are bounded to 512 KiB per file by default;
- binary/NUL, invalid UTF-8 and obvious private-key material are rejected;
- directory listing hides denied and symlink entries;
- context manifests record `read_root` provenance;
- provider context revalidates every path against harness-allowlisted project/skills roots at load time;
- old checkpoints without `read_root` are accepted only when the current allowlist can safely infer their root.

Internal checkpoint reads and trusted Factory policy/config reads are not routed through the project Safe Read surface; otherwise the runtime would block its own private state. The contract is documented in `skills_UIUX/runtime/SAFE-READ.md`.

A4.1 does **not** implement worktree/write isolation, a target runner, typed evidence/gates, or expanded file tools. Those remain A4.2–A4.5 follow-up hardening work.
