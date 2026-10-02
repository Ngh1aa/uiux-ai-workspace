# Flow 1 / A53.1 — Runtime Compatibility Convergence

Status: **VERIFIED / FIRST-PARTY CONVERGENCE PASS**  
Date: **2026-10-02**  
Baseline: `main@537c999d16fa6eee5df776725d69a29807313411`  
Depends on: A52.3 Post-Interop Executable Debt Audit

## Purpose

Flow 1 removes first-party dependence on the deprecated `skills_UIUX/runtime/*.py` import surface without removing that compatibility surface or changing runtime behavior.

A52.3 selected this work from executable evidence because the repository still had exactly:

```text
8 first-party consumer files
19 deprecated runtime.* module imports
8 compatibility shim files
```

Flow 1 combines retirement readiness, first-party consumer migration and post-migration executable re-audit in one bounded convergence package.

## Historical baseline preservation

A52.3 remains historical selection evidence and is not rewritten after migration.

Its checked-in contract still records:

```text
expected_internal_consumer_file_count = 8
expected_internal_consumer_import_count = 19
```

Once the A53 convergence contract exists, the topology-bound A52.3 pytest is frozen in `tests/conftest.py`, following the same historical-evidence pattern used for earlier A50 promotion tests.

The A52.3 validator remains in-repository but is no longer an active current-state CI gate after first-party convergence.

## Canonical import target

All migrated first-party code now imports from:

```text
uiux-factory/core/runtime/flow_os/
```

The two compatibility aliases used by old callers map directly to their canonical classes:

```text
runtime.flow.DevelopmentManager
→ core.runtime.flow_os.flow.FlowPlanner

runtime.manager.DevelopmentManagerAgent
→ core.runtime.flow_os.managed.ManagedFlowController
```

Other migrated symbols are direct canonical re-exports.

## Migrated first-party consumers

Exactly eight files were migrated:

```text
uiux-factory/tests/test_adaptive_flow.py
uiux-factory/tests/test_canonical_runtime_a4.py
uiux-factory/tests/test_runtime_lifecycle_context.py
uiux-factory/tests/test_task_contract.py
skills_UIUX/scripts/context-manifest.py
skills_UIUX/scripts/validate-flows.py
skills_UIUX/scripts/validate-provider-runtime.py
skills_UIUX/scripts/validate-runtime-foundation.py
```

The test consumers import canonical modules directly from the Factory package.

The four `skills_UIUX/scripts` consumers use the existing official managed-CLI bootstrap pattern:

```python
ROOT = Path(__file__).resolve().parents[1]
FACTORY_ROOT = ROOT.parent / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))
```

No second bootstrap convention was introduced.

## Compatibility surface retained

All eight compatibility files remain present and thin:

```text
skills_UIUX/runtime/adaptive_surface.py
skills_UIUX/runtime/agent.py
skills_UIUX/runtime/flow.py
skills_UIUX/runtime/manager.py
skills_UIUX/runtime/mcp_server.py
skills_UIUX/runtime/provider.py
skills_UIUX/runtime/provider_runner.py
skills_UIUX/runtime/task_context.py
```

Flow 1 does not delete, rename or repurpose them.

They remain compatibility-only and may not gain independent routing, provider, lifecycle, evidence, gate or release authority.

## Current-state executable contract

Flow 1 adds:

```text
benchmarks/runtime-compatibility-convergence-v1.json
core/benchmarks/runtime_compatibility_convergence.py
scripts/validate_runtime_compatibility_convergence.py
tests/test_runtime_compatibility_convergence_a53.py
```

The evaluator verifies:

1. the historical A52.3 baseline still says 8 files / 19 imports;
2. all eight declared shims remain thin compatibility wrappers;
3. migrated symbols and compatibility aliases resolve to the identical canonical Python objects;
4. all eight migrated consumer files still exist;
5. all four migrated scripts use the canonical Factory-root bootstrap;
6. active first-party Python contains zero deprecated `runtime.*` consumers;
7. no authority boundary is loosened.

## Identity parity

The clean CI run verified identity for the migrated compatibility surface, including:

```text
ProviderNeutralAgentHarness
PermissionGate
ToolRegistry
build_context_manifest
FlowResolver
validate_flow_document
DevelopmentManager -> FlowPlanner
DevelopmentManagerAgent -> ManagedFlowController
ProviderStageResponse
ScriptedProvider
ProviderManagedRunner
GoalInterpreter
```

These checks use the retained shim files only as compatibility test fixtures; first-party product/scripts no longer import through `runtime.*`.

## Final current census

Verified functional head:

```text
head = 06e596a37580ee2b2b1d1faf4d2f71fb1369b6f6
historical consumers = 8 files / 19 imports
current consumers = 0 files / 0 imports
shim_count = 8
shim_contract_clear = true
identity_checks_clear = true
migrated_consumer_contract_clear = true
script_bootstrap_clear = true
zero_internal_consumers = true
governance_boundary_clear = true
```

Derived decision:

```text
FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS
```

## Verification evidence

Functional head verification:

```text
UIUX Factory CI #1684 = SUCCESS
A20 UIUX Factory v1 Release Candidate #198 = SUCCESS
A13 Nova Real-Project Dogfood #75 = SUCCESS
full pytest = 635 passed / 54 skipped
```

The four additional skips relative to the pre-Flow-1 suite are the intentionally frozen A52.3 historical census tests.

## Governance boundary

Flow 1 keeps all of the following false:

```text
shim_deletion_allowed = false
external_removal_safety_inferred = false
runtime_behavior_change_allowed = false
provider_default_change_allowed = false
lifecycle_state_owner_change_allowed = false
routing_change_allowed = false
evidence_authority_change_allowed = false
gate_authority_change_allowed = false
release_authority_change_allowed = false
product_evidence = false
```

And all effects remain:

```text
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## What Flow 1 does not prove

Zero first-party consumers does **not** prove that external users or integrations no longer depend on `skills_UIUX/runtime/*.py`.

Therefore Flow 1 explicitly does not authorize shim removal.

## Handoff

Flow 1 is complete when the exact final documentation head also passes mandatory CI/A20 gates.

The next bounded flow is compatibility-surface governance: determine whether each retained shim should remain indefinitely, enter a documented deprecation/sunset path, or become eligible for a separately governed removal task. External compatibility safety must be evaluated independently from the now-zero first-party consumer census.
