# A48.6 — Controlled Factory Provider Lane Integration

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A48.5 Provider Parity + Compatibility Dogfood

## 1. Purpose

A48.6 is the first task that allows the Factory manager to select the A48.4 compatibility adapter, but only through an explicit operator-controlled feature flag.

The proven legacy provider remains the default.

Canonical selection contract:

```text
core/runtime/provider_lane.py
```

Manager integration:

```text
core/manager/provider_intelligent_manager.py
```

## 2. Feature flag

The only selection variable is:

```text
UIUX_FACTORY_PROVIDER_LANE
```

Accepted values:

```text
legacy
managed-compat
```

Semantics:

```text
unset / blank  -> legacy
legacy         -> legacy
managed-compat -> A48.4 ManagedArtifactCompletionAdapter
anything else  -> fail closed
```

There is no `auto`, percentage rollout or implicit provider migration in A48.6.

## 3. Default and rollback

`legacy` remains the default lane. Managed compatibility requires explicit opt-in.

Rollback is immediate and operator-controlled:

```text
unset UIUX_FACTORY_PROVIDER_LANE
```

or:

```text
UIUX_FACTORY_PROVIDER_LANE=legacy
```

A48.6 deliberately does **not** catch a managed-compat failure and silently rerun the same work through legacy. Silent fallback would hide migration regressions and make run provenance ambiguous.

## 4. Lazy transport construction

`core/runtime/provider_lane.py` resolves only a dependency-light lane decision. It does not import or construct a provider.

Inside the AI engine branch, the manager lazily imports exactly one selected implementation:

```text
legacy         -> FreeProvider.from_env(root)
managed-compat -> ManagedArtifactCompletionAdapter.from_env(root)
```

Template/external engines do not resolve or construct an internal AI provider lane.

This preserves the A48.4 fix that prevents canonical module imports from pulling legacy `aiohttp` transport dependencies unnecessarily.

## 5. Run provenance

Every AI run writes:

```text
provider-lane.json
```

and registers it as the `provider_lane` run artifact.

The payload contains only:

- schema version;
- selected lane;
- selection source (`default` or feature flag);
- whether managed compatibility was explicitly opted into;
- default lane;
- rollback instruction;
- `contains_credentials=false`;
- explicit `none` effects for authority/gate/evidence/release.

It contains no API key, token, model secret or raw provider environment.

The manager also emits:

```text
provider.lane_selected
```

with lane, opt-in state and artifact path only.

The existing `flow-plan.json` receives the same secret-free provider-lane payload so run topology and provider migration provenance remain reviewable together.

## 6. Authority boundary

Provider lane selection changes only which AI completion implementation is used by the Factory AI engine.

It cannot change:

- `GoalInterpreter` or `FlowPlanner` output;
- skills/JIT routing;
- stage order;
- runtime authority;
- evidence trust;
- QA gate truth;
- merge/deploy/release authority;
- Brain scorecard truth.

The provenance payload declares:

```text
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## 7. No default migration

A48.6 is a controlled opt-in integration only.

It does not:

- change the default from `legacy`;
- remove `FreeProvider`;
- make managed compatibility automatic;
- add traffic splitting;
- change Groq/Gemini account configuration policy;
- turn provider output into evidence;
- authorize release based on provider lane.

Any future default migration requires a separate architecture decision backed by opt-in run evidence.

## 8. Acceptance criteria

A48.6 is complete when:

- [x] missing flag resolves to legacy;
- [x] explicit `legacy` remains legacy;
- [x] `managed-compat` is the only adapter opt-in;
- [x] unknown values fail closed;
- [x] provider transports remain lazy imports;
- [x] no silent managed-to-legacy fallback exists;
- [x] every AI run records secret-free provider-lane provenance;
- [x] flow plan includes the provider-lane provenance when present;
- [x] template/external engines do not select an internal provider lane;
- [x] manager/provider lane changes have no authority/gate/evidence/release effect;
- [ ] final head passes UIUX Factory CI, A20, A13 and A14 where triggered.

## 9. Handoff

After A48.6 is green and merged, provider convergence is complete at the **controlled opt-in** level. The next major debt should move to A49 lifecycle reconciliation rather than immediately flipping the provider default.

A future provider-default decision, if ever needed, should be evidence-driven and independently reviewed; A48.6 does not pre-authorize it.