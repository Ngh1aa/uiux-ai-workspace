# A48.6 — Controlled Provider Integration

Status: **IMPLEMENTED / VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A48.2 capability reconciliation, A48.3 artifact bridge, A48.4 managed compatibility adapter, A48.5 provider parity benchmark

## Purpose

A48.6 exposes the A48.4 compatibility adapter to the Factory manager as an explicit migration lane while preserving the existing legacy provider path as the default.

This task does **not** make the managed compatibility adapter the default and does not remove `FreeProvider`.

## Selection contract

The Factory manager reads exactly one integration flag:

```text
UIUX_FACTORY_PROVIDER_LANE
```

Allowed values:

```text
legacy
managed_compat
```

Behavior:

```text
flag absent            -> legacy (default)
flag = legacy          -> legacy (explicit)
flag = managed_compat  -> ManagedArtifactCompletionAdapter (explicit)
unknown value          -> fail closed
```

There is no `auto` value and no silent cross-lane fallback.

## Legacy default

The existing path remains the default:

```text
core.runtime.free_provider.FreeProvider.from_env(root)
```

A user/operator must deliberately set:

```text
UIUX_FACTORY_PROVIDER_LANE=managed_compat
```

to exercise the managed compatibility bridge.

## Managed compatibility lane

The opt-in path constructs:

```text
core.runtime.flow_os.factory_provider_adapter.ManagedArtifactCompletionAdapter.from_env(root)
```

A48.4 already proves this adapter preserves the Factory async `complete(...) -> str` contract, bounds context/call budgets, offloads synchronous managed providers from the event loop, and rejects lifecycle/evidence/tool authority in artifact-carrier responses.

A48.6 does not change those semantics.

## Fail-closed migration behavior

A48.6 deliberately does not implement automatic fallback from `managed_compat` to `legacy`.

If managed compatibility construction or execution fails, the run fails visibly. An automatic fallback would hide migration regressions and make provider-lane provenance ambiguous.

Rollback is configuration-only for the **next run**:

```text
unset UIUX_FACTORY_PROVIDER_LANE
# or
UIUX_FACTORY_PROVIDER_LANE=legacy
```

The currently running process is not rewritten mid-run.

## Provider-lane provenance

AI-engine runs write:

```text
<run_dir>/provider-lane.json
```

and register it as the `provider_lane` artifact.

The artifact records only bounded non-secret execution metadata:

```text
schema_version
engine
lane
selection_source
feature_flag
provider_class
provider name/model descriptors
automatic_cross_lane_fallback = false
rollback instruction
```

It never persists API keys.

The run event bus also receives:

```text
provider.lane_selected
```

with the selected lane and provenance path.

## Truth / authority boundary

`provider-lane.json` is execution provenance only.

It declares:

```text
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

It is not runtime QA evidence, does not satisfy a gate, does not validate an artifact, and does not authorize merge/deploy/release.

## Non-goals

A48.6 does not:

- change the default provider lane;
- delete or deprecate `FreeProvider`;
- change provider transport;
- change provider artifact/evidence semantics;
- change Flow OS stage routing;
- change runtime gates or evidence trust;
- add automatic cross-lane fallback;
- claim live-provider parity from offline benchmark evidence;
- migrate top-level Factory/managed lifecycle APIs.

## Acceptance criteria

A48.6 is complete when:

- [x] absent flag resolves to legacy default;
- [x] explicit `legacy` resolves to legacy;
- [x] explicit `managed_compat` resolves to the A48.4 adapter;
- [x] unknown lane fails closed;
- [x] no automatic cross-lane fallback exists;
- [x] provider lane provenance is persisted without secrets;
- [x] provider lane provenance has no evidence/gate/release effect;
- [x] old A48.4 regression guard is updated to require explicit opt-in rather than prohibit all manager wiring;
- [ ] final head passes UIUX Factory CI;
- [ ] final head passes A20 full regression/security/dogfood;
- [ ] path-triggered A13/A14 lanes pass if triggered;
- [ ] PR is mergeable.

## Handoff

After A48.6 is green and merged, provider convergence has an explicit controlled migration lane but **legacy remains default**.

The next architecture package should move to A49 lifecycle reconciliation before any default provider migration decision. Provider default migration, if ever justified, requires separate live-provider evidence and an explicit human/governance decision.
