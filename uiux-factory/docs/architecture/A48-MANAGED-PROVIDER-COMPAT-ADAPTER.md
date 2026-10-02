# A48.4 — Managed Provider Compatibility Adapter

Status: **MERGED / VERIFIED**  
Date: **2026-10-02**  
Depends on: A48.3 Provider Artifact Bridge Contract

## 1. Purpose

A48.4 adds an opt-in compatibility adapter that preserves the existing Factory provider caller contract:

```text
await complete(stage, system, prompt, json_mode=False) -> str
```

while delegating execution to an already-existing canonical managed `ModelProvider`.

Implementation:

```text
core/runtime/flow_os/factory_provider_adapter.py
::ManagedArtifactCompletionAdapter
```

The adapter is a migration bridge only. It is not a third provider transport, provider policy owner, Flow runtime or lifecycle controller.

## 2. Async safety

Managed providers are synchronous today:

```text
run_stage(ProviderStageRequest) -> ProviderStageResponse
```

Factory provider callers are asynchronous. The adapter therefore always executes `run_stage(...)` through:

```text
asyncio.to_thread(...)
```

wrapped in `asyncio.wait_for(...)`.

This prevents the current synchronous managed provider call from directly blocking the Factory event loop. Provider-level timeout is temporarily aligned to the existing Factory stage timeout during the call and restored afterwards.

## 3. Artifact-carrier mode

A48.4 does not reinterpret managed lifecycle PASS as a Factory completion.

The adapter creates a bounded compatibility request with:

```text
flow_id = factory-provider-compatibility
authority = factory-provider-compatibility-only
tools = []
gates = []
```

and requires the managed provider response to be exactly a neutral carrier:

```text
status = CONTINUE
actions = []
evidence = []
replan_signal = null
artifact = <raw requested completion>
```

The adapter consumes that response locally and returns only `artifact` to the Factory caller.

The `CONTINUE` value in this compatibility envelope is **not forwarded to ManagedFlowController** and is not treated as a lifecycle decision. It is only the least-authoritative existing response status that can carry output without fabricating PASS evidence.

Any `PASS`, `FAIL`, `BLOCKED`, tool action, evidence item or replan signal in compatibility mode fails closed rather than being translated into a Factory completion.

## 4. Factory parity retained

A48.4 extracted the dependency-light compatibility values into:

```text
core/runtime/provider_compat_contract.py
```

Both the legacy `FreeProvider` and compatibility adapter consume the same:

```text
PROVIDER_CONTEXT_CHAR_LIMIT
PROVIDER_MAX_CALLS_PER_RUN
PROVIDER_STAGE_MAX_TOKENS
PROVIDER_STAGE_TIMEOUT
ProviderError
```

This preserves the established Factory 80k context ceiling, 20-call run ceiling and stage token/timeout budgets without forcing canonical Flow OS imports to load the legacy `aiohttp` transport.

The adapter also retains:

- async `complete(...)` interface;
- stage-specific preferred-provider ordering through `UIUX_PROVIDER_<STAGE>`;
- one retry on transient/network/timeout failures before moving to the next configured provider;
- per-attempt `calls` and `history` records used by Factory run artifacts;
- JSON mode requiring the returned artifact to decode to a JSON object.

Temporary managed-provider token/timeout values are restored after each call.

## 5. Configuration bridge and import boundary

`ManagedArtifactCompletionAdapter.from_env(root)` reuses:

```text
FreeProvider.from_env(root)
```

for the current free-tier opt-in, key, model and provider-list validation. The already-validated configs are then converted to canonical `OpenAICompatibleFreeTierProvider` instances.

`FreeProvider` is imported **lazily inside `from_env()`**. The adapter has no module-scope import of `core.runtime.free_provider`, so importing canonical Flow OS does not pull `aiohttp` into the foundation dependency graph.

This avoids both a third free-tier configuration policy and transport dependency leakage.

## 6. Truth / authority boundary

Compatibility request context declares:

```text
artifact_is_evidence = false
authority_effect = none
gate_effect = none
evidence_effect = none
```

The adapter itself:

- creates no `EvidenceRecord`;
- passes no runtime gate;
- performs no Flow replanning;
- performs no merge/deploy/release action;
- does not expose managed lifecycle status to the Factory caller;
- rejects compatibility responses that attempt to carry evidence or authority-bearing status.

## 7. Not wired by default

A48.4 intentionally does **not** modify:

```text
core/manager/provider_intelligent_manager.py
```

The Factory manager continues to construct:

```text
FreeProvider.from_env(self.root)
```

by default.

A48.4 therefore changes no current production/default execution path.

## 8. Verification

Final head `e32ec3ec78a26947ab372456eed7d1e1ca547002` passed:

- UIUX Factory CI #1251;
- A20 UIUX Factory v1 Release Candidate #91;
- A13 Nova Real-Project Dogfood #52;
- A14 Fix Once Validate Across Projects #42;
- A14 focused regressions;
- A14 golden Nova/Lumen/CENNEXT/LuxRoom;
- A14 current-head canary Nova/Lumen/CENNEXT/LuxRoom.

Merged to `main` at:

```text
834a84d7c6783f7889538c00cc96b0755a1da631
```

The first foundation attempt correctly exposed the module-scope `aiohttp` dependency leak. The fix extracted the shared compatibility contract and added a regression test rather than adding `aiohttp` to canonical foundation dependencies or weakening CI.

## 9. Handoff

A48.5 validates parity rather than changing defaults. It exercises representative Factory completion contracts and performs deterministic compatibility smoke across Nova/Lumen/CENNEXT/LuxRoom task profiles while keeping the result explicitly separate from product/rendered evidence.

Only after A48.5 proves acceptable parity should A48.6 consider a controlled manager opt-in integration.