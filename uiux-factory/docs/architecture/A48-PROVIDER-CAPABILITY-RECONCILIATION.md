# A48.2 — Provider Capability Reconciliation

Status: **MERGED / VERIFIED**  
Date: **2026-10-02**  
Depends on: A48.1 Architecture Truth Reconciliation

## 1. Purpose

A48.2 maps the two existing free-tier provider entry paths before any execution-path migration.

Current paths:

```text
Factory internal AI lane
core/runtime/free_provider.py::FreeProvider.complete(...)

Managed Flow OS lane
core/runtime/flow_os/free_tier_provider.py::OpenAICompatibleFreeTierProvider.run_stage(...)
```

The goal is to make compatibility gaps executable and reviewable, not to replace either working lane prematurely.

Canonical reconciliation surface:

```text
core/runtime/flow_os/provider_capabilities.py
```

This module is descriptive/read-only. It is not a third provider runner or transport.

## 2. Shared capabilities

Both current free-tier paths:

- require explicit free-tier opt-in;
- support Groq and Gemini through OpenAI-compatible chat endpoints;
- use non-streaming completions;
- bound provider response size;
- receive stage identity;
- have no authority to change flow order, gates, evidence trust, merge or release decisions.

## 3. Factory `complete(...)` lane

Current Factory callers depend on:

```text
async complete(stage, system, prompt, json_mode=False) -> str
```

Important behavior:

- async entrypoint;
- returns raw artifact/provider text;
- JSON mode is optional;
- stage-specific token/time budgets;
- ordered multi-provider fallback;
- per-run call budget;
- provider history persisted by Factory run artifacts.

Direct callers include:

```text
core/team/team_runner.py
core/team/intelligent_team_runner.py
core/orchestration/ai_frontend_builder.py
```

and the Factory manager constructs the provider in:

```text
core/manager/provider_intelligent_manager.py
```

## 4. Managed `run_stage(...)` lane

The canonical managed provider contract is:

```text
run_stage(ProviderStageRequest) -> ProviderStageResponse
```

Important behavior:

- synchronous entrypoint today;
- typed request and response contracts;
- mandatory structured JSON stage envelope;
- `CONTINUE / PASS / FAIL / BLOCKED` status;
- explicit bounded tool actions;
- explicit evidence envelope;
- managed replan signal contract;
- declared hard output-limit capability.

These semantics are owned by:

```text
core/runtime/flow_os/provider.py
```

A48.2 does not copy or redefine those classes.

## 5. Why direct substitution is unsafe

A48.2 records:

```text
direct_substitution_safe = false
adapter_required = true
```

Current blockers include:

1. async Factory `complete(...)` versus synchronous managed `run_stage(...)`;
2. raw artifact return versus structured `ProviderStageResponse`;
3. Factory specialist observation loops parse a separate bounded response contract above `complete(...)`;
4. `AIFrontendBuilder` expects a complete JSON frontend bundle rather than a managed-stage envelope;
5. Factory call-budget/history semantics live on the current provider instance.

Replacing one provider object with the other without an adapter would therefore change behavior and potentially block the event loop or break output contracts.

## 6. Read-only/fail-closed behavior

`provider_capabilities.py` checks the audited entrypoint signatures with `inspect.signature` and coroutine detection.

If either source interface drifts, reconciliation fails and requires review rather than silently claiming parity.

The module never calls:

```text
FreeProvider.complete(...)
OpenAICompatibleFreeTierProvider.run_stage(...)
```

and does not perform network I/O.

## 7. Authority boundary

Capability reconciliation declares:

```text
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
```

It cannot:

- route or execute a stage;
- call a provider;
- create runtime evidence;
- pass/fail gates;
- replan a flow;
- merge/deploy/release.

## 8. Acceptance criteria

A48.2 is complete when:

- [x] both current provider entrypoint signatures are executable assertions;
- [x] async/sync mismatch is explicit;
- [x] shared and lane-specific capabilities are recorded;
- [x] direct substitution is explicitly unsafe;
- [x] Factory `complete(...)` call sites are regression-tested as migration surface;
- [x] reconciliation does not execute either provider;
- [x] no third ProviderStageRequest/ProviderStageResponse/runner contract is introduced;
- [x] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood;
- [x] A13 Nova dogfood passes;
- [x] A14 focused + golden/canary Nova/Lumen/CENNEXT/LuxRoom passes.

Verified final head: `4c97ce3a47265a9a68b838ca603f83c6a12b5694`.  
Merged to `main`: `da42c1d222edca440943be02671432247dd4a91c`.

## 9. Handoff

A48.3 now provides the missing bounded raw-artifact carrier on canonical `ProviderStageResponse`. After A48.3 is green and merged, A48.4 may implement an **opt-in async compatibility adapter** preserving the Factory `complete(...) -> str` caller contract while delegating through a managed provider.

The adapter must address async/sync execution, raw-artifact extraction, Factory call-budget/history compatibility and must not weaken managed evidence/tool semantics. It must remain opt-in until A48.5 parity/dogfood proves equivalence.