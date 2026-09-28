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
- isolated Git worktree writes and controlled finalization;
- bounded file/search/edit tools;
- container/network-sandboxed target command execution;
- typed runtime evidence and gate evaluation;
- Playwright browser-rendered evidence ingestion/capture;
- explicit human-owned production release/deploy authority;
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

## A4.1 — Safe Read

`safe_read.py` is the single read boundary for model/provider-facing project and skill text. It rejects root escape, symlinks, credentials, binary/invalid UTF-8, oversized text and internal/generated directories while preserving safe environment templates.

## A4.2–A4.5 — Isolated execution, target runner, evidence and file tools

- branch-write mutations live in a clean, branch-scoped Git worktree;
- target commands use exact argv allowlists and bounded cwd/timeout/output;
- provider claims never count as trusted gate evidence;
- runtime observations become typed evidence records;
- bounded recursive search/list, atomic writes and exact text replacement share the same workspace boundary.

See `skills_UIUX/runtime/A4-2-A4-5-RUNTIME-HARDENING.md`.

## A4.6 — Container / network sandbox

Provider-facing target commands are now executed by `ContainerSandbox`, not directly on the host. The runtime requires a pre-provisioned Docker/Podman engine and image and fails closed when unavailable.

Default security controls include:

- network `none`;
- read-only root filesystem;
- writable mount limited to the isolated worktree;
- all capabilities dropped;
- `no-new-privileges`;
- bounded PIDs, memory, CPU, timeout, output and tmpfs;
- no implicit image pull;
- no host-execution fallback.

## A4.7 — Worktree finalization

`WorktreeManager.finalize()` can commit, fast-forward merge and clean a completed isolated run. The source `HEAD` is pinned to the original base commit; source drift, conflicts, dirty state or branch changes stop the operation. Git hooks are disabled for runtime-managed Git commands. Cleanup uses `git worktree remove`, then deletes the merged temporary branch and prunes metadata.

Automatic merge is a human-owned `external_write` boundary and is exposed through `ProductionReleaseController`, not provider tools.

## A4.8 — Production release authority

Production deploy is a `release`-authority boundary and requires:

- explicit `PRODUCTION` confirmation;
- managed flow `COMPLETED`;
- isolated changes finalized/merged;
- no failing trusted runtime evidence;
- at least one successful validator/target-command result;
- at least one `PASS` browser-render record.

The generic command deploy adapter consumes operator-configured exact argv from `UIUX_PRODUCTION_DEPLOY_ARGV_JSON`, runs with `shell=False`, and forwards only explicitly allowlisted environment names. Provider roles remain capped below release authority.

## A4.9 — Browser-rendered evidence

`PlaywrightBrowserEvidenceAdapter` bridges the existing Playwright Cloud QA output into trusted Flow OS evidence. Browser records include screenshot and JSON hashes, route, URL, viewport, ARIA snapshot, representative bounding box and browser/console errors. Remote capture is denied by default; localhost is the default trusted target.

See `skills_UIUX/runtime/A4-6-A4-9-SANDBOX-RELEASE.md` for the operational contract and CLI examples.
