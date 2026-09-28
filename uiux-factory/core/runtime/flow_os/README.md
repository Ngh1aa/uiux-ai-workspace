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

A4 intentionally does **not** implement Safe Read, worktree isolation, a target runner, typed evidence/gates, or expanded file tools. Those are A4.1–A4.5 follow-up hardening work.
