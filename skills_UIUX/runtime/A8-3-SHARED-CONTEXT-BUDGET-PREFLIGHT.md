# A8.3 — Shared Provider Context Budget & Atomic JIT Activation

A8.3 closes a remaining context-safety gap after A8–A8.2.

Before A8.3, `load_context_documents()` bounded skill documents and source documents independently. A provider request could therefore load up to the configured ceiling once for skills and again for sources. JIT activation was also count-bounded only: a skill name could be checkpointed successfully and the next provider turn could then fail because the resulting document context was too large.

A8.3 makes the request document envelope explicit and preflights JIT activation before mutating checkpoint state.

## Shared request ceiling

Runtime policy now owns:

```json
{
  "provider_context": {
    "max_document_chars_per_request": 180000
  }
}
```

The ceiling applies to the combined provider-facing document payload:

```text
loaded mandatory skill docs
+ loaded active JIT skill docs
+ explicit source-of-truth docs
+ project-config docs
<= max_document_chars_per_request
```

The measurement is Unicode character count, matching the existing `UIUX_PROVIDER_CONTEXT_CHARS` contract.

`UIUX_PROVIDER_CONTEXT_CHARS` remains a compatibility/operator control, but it may only lower the runtime-policy ceiling:

```text
effective ceiling = min(runtime policy, environment ceiling when present)
```

An environment value can never raise the policy-owned maximum.

## One budget, not two

Each category is still Safe Read validated independently, but `ProviderManagedRunner` now checks the combined skill + source total before constructing `ProviderStageRequest`.

A request that would exceed the shared ceiling raises a typed `ProviderContextBudgetError` before any provider call.

When this happens during normal stage execution, the stage and managed run become `BLOCKED` with a bounded limitation message. The runtime does not spend a provider call and does not attempt to disguise a policy/configuration problem as successful execution.

## Atomic JIT activation

`activate_skill_context` now performs this sequence:

1. validate the requested skill against the explicit Flow-owned JIT pool;
2. validate the per-stage active-skill count ceiling;
3. construct the candidate active set in memory;
4. Safe Read the exact next-turn mandatory/JIT skill documents and source/project documents;
5. verify the combined document payload fits the shared provider context ceiling;
6. only then persist `jit_active_skills` to the stage checkpoint.

If the candidate would exceed the budget, activation returns a structured rejection:

```text
accepted=false
activated=null
available_next_turn=false
```

and leaves checkpoint state unchanged. This is intentionally recoverable: the provider may continue with current context or choose another already-routed JIT skill instead of turning a context-sizing decision into a corrupted stage state.

Successful activation reports bounded post-activation telemetry:

- `document_chars_after_activation`;
- `document_char_limit`;
- `remaining_document_chars`.

These values are context telemetry only.

## Provider-facing budget metadata

Each provider request receives:

```text
task_context.provider_context_budget
```

with:

- `max_document_chars_per_request`;
- `loaded_document_chars`;
- `skill_document_chars`;
- `source_document_chars`;
- `remaining_document_chars`;
- `source` (`runtime_policy` or `runtime_policy+env_ceiling`);
- `measurement=unicode_chars`;
- `authority_effect=none`;
- `gate_effect=none`;
- `evidence_effect=none`.

The metadata cannot change authority, Flow routing, gates, evidence, merge, deploy or release behavior.

## Fail-closed policy parsing

`provider_context.max_document_chars_per_request` must be an integer between `1` and `2,000,000`. Booleans, numeric strings, zero/negative values and values beyond the hard runtime maximum fail closed.

`UIUX_PROVIDER_CONTEXT_CHARS`, when present, must also be a positive integer within the same hard range.

## A8 compatibility

A8.3 does not change:

- `ResolvedStage.skills`, `mandatory_skills`, `jit_skills` or `jit_skill_sources` semantics;
- the A8 activation count ceiling;
- A8.2 provenance semantics;
- provider/tool authority;
- gate evidence rules;
- replanning ownership;
- merge/deploy/release authorization.

It only makes provider document context accounting shared, observable and atomic at the JIT activation boundary.

## Regression coverage

`uiux-factory/tests/test_provider_context_budget_a8_3.py` covers:

- provider-facing budget metadata;
- shared skill + source accounting;
- atomic rejected activation with unchanged checkpoint state;
- successful activation budget telemetry;
- pre-provider-call blocking for initial context overflow;
- strict policy validation;
- environment ceiling behavior that can lower but never raise runtime policy.
