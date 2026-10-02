# A48.4 — Managed Provider Compatibility Adapter

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
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

The adapter retains the current Factory behavior that callers rely on:

- async `complete(...)` interface;
- 80,000-character combined context limit;
- stage-specific token budgets from `FreeProvider.STAGE_MAX_TOKENS`;
- stage-specific timeout budgets from `FreeProvider.STAGE_TIMEOUT`;
- `MAX_CALLS_PER_RUN` from `FreeProvider`;
- stage-specific preferred-provider ordering through `UIUX_PROVIDER_<STAGE>`;
- one retry on transient/network/timeout failures before moving to the next configured provider;
- per-attempt `calls` and `history` records used by Factory run artifacts;
- JSON mode requires the returned artifact to decode to a JSON object.

Temporary managed-provider token/timeout values are restored after each call.

## 5. Configuration bridge

`ManagedArtifactCompletionAdapter.from_env(root)` deliberately reuses:

```text
FreeProvider.from_env(root)
```

for the current free-tier opt-in, key, model and provider-list validation. The already-validated configs are then converted to canonical `OpenAICompatibleFreeTierProvider` instances.

This avoids creating a third free-tier configuration policy during migration.

No network call occurs during adapter construction.

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

## 8. Acceptance criteria

A48.4 is complete when:

- [x] adapter preserves async `complete(...) -> str` shape;
- [x] synchronous managed provider work runs off the Factory event-loop thread;
- [x] canonical A48.3 artifact field carries raw completion text;
- [x] JSON mode rejects non-object artifacts;
- [x] Factory stage token/timeout limits are applied then restored;
- [x] Factory call budget/history semantics remain available;
- [x] preferred-provider ordering is preserved;
- [x] transient retry/fallback is bounded;
- [x] managed PASS/FAIL/BLOCKED cannot be reinterpreted as completion success;
- [x] tool/evidence/replan-bearing carrier responses fail closed;
- [x] manager default path remains unchanged;
- [ ] final PR head passes UIUX Factory CI, A20, A13 and A14.

## 9. Handoff

A48.5 should validate parity rather than change defaults. It should exercise the existing Factory provider and the compatibility adapter against the same representative completion contracts (plain text, JSON stage artifacts, frontend bundle, malformed output, transient failures, call budgets/history) and dogfood the opt-in bridge on representative projects.

Only after A48.5 proves acceptable parity should A48.6 consider a controlled manager opt-in integration or default migration.