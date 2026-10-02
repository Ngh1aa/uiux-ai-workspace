# A53.2 — Compatibility Surface Governance

Status: **DEPRECATE WITH SUNSET / REMOVAL GOVERNANCE CLOSED**  
Audit date: **2026-10-02**  
Input baseline: Flow 1 / A53.1 runtime compatibility convergence.

## Decision

All eight deprecated Python wrappers under `skills_UIUX/runtime/*.py` are classified:

```text
DEPRECATE_WITH_SUNSET
```

No shim is classified `RETAIN_INDEFINITELY` and no shim is classified `OPEN_REMOVAL_GOVERNANCE`.

Current derived decision:

```text
DEPRECATE_WITH_SUNSET_REMOVAL_GOVERNANCE_CLOSED
```

This is a compatibility-governance decision only. It does not delete files, alter import behavior, add warnings, change runtime authority, or open a removal task.

## Why zero internal consumers is not enough

Flow 1 proves:

```text
internal_consumer_files = 0
internal_consumer_imports = 0
shim_count = 8
shim_contract_clear = true
identity_checks_clear = true
```

Those facts are necessary migration evidence, not external-removal evidence.

The repository is public and the runtime README has historically described the wrappers as compatibility support for existing imports. External usage is therefore treated as:

```text
UNKNOWN
```

Two public-code discovery queries returned zero hits on 2026-10-02, but the search result is explicitly classified `NON_AUTHORITATIVE_DISCOVERY_ONLY`. Zero hits do not prove zero downstream users.

The repository also had no GitHub Releases at audit time and no root Python package metadata establishing a semver removal boundary. A calendar-backed public observation window is therefore used instead of pretending a version boundary exists.

## Sunset policy

Public governance notice date:

```text
2026-10-02
```

Minimum public observation window:

```text
90 days
```

Earliest removal-governance review:

```text
2026-12-31
```

This is **not** an automatic deletion date. Reaching the date only makes a fresh removal-readiness audit temporally eligible.

## Requirements before removal governance may open

A later bounded task must independently prove all conditions:

```text
Flow 1 zero-internal-consumer census still clear
shim thin-wrapper + identity parity still clear
public guidance recommends canonical imports only
minimum observation window elapsed
explicit external-usage audit complete
no known supported downstream dependency requires the wrappers
explicit owner-governed removal task opened
exact-head mandatory CI/A20 green
```

Failure or uncertainty in any condition keeps removal governance closed.

## Migration map

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

Legacy aliases remain compatibility-only during the observation window:

```text
runtime.flow.DevelopmentManager
→ core.runtime.flow_os.flow.FlowPlanner

runtime.manager.DevelopmentManagerAgent
→ core.runtime.flow_os.managed.ManagedFlowController
```

## Why no import-time warning was added

Adding `DeprecationWarning` at import time is itself observable behavior and can affect strict-warning test environments or downstream tooling. A53.2 publishes deprecation through documentation and executable governance only. Any warning behavior change requires its own compatibility evidence.

## Executable governance

```text
benchmarks/compatibility-surface-governance-v1.json
core/benchmarks/compatibility_surface_governance.py
scripts/validate_compatibility_surface_governance.py
tests/test_compatibility_surface_governance_a53.py
```

The evaluator consumes Flow 1 directly and fails closed if first-party consumers return, shim parity regresses, public guidance recommends legacy imports, public notice drifts, or removal authority appears prematurely.

## Non-authority boundary

A53.2 preserves:

```text
shim_deletion_allowed = false
removal_governance_open = false
external_removal_safety_inferred = false
runtime_behavior_change_allowed = false
import_warning_behavior_change_allowed = false
provider_default_change_allowed = false
lifecycle_state_owner_change_allowed = false
routing_change_allowed = false
evidence_authority_change_allowed = false
gate_authority_change_allowed = false
release_authority_change_allowed = false
product_evidence = false
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## Next compatibility task

No shim-removal implementation task is authorized now.

The next compatibility-surface action is a **fresh removal-readiness audit no earlier than 2026-12-31**, and only when the external-usage/downstream-dependency evidence can be collected. Until then, the eight wrappers remain thin compatibility surfaces under active deprecation.
