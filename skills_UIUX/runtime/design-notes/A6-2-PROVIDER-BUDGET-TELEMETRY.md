# A6.2 — Provider Budget + Usage Telemetry

Status: **CANONICAL RUNTIME CONTRACT**

A6.2 extends A6.1 stage-routable providers with operator-owned per-stage budgets and persisted provider usage telemetry.

## Goal

Each canonical Flow stage may have its own bounded provider budget without allowing task text, provider output, recalled memory or tool observations to raise that budget.

Executable ownership:

```text
uiux-factory/core/runtime/flow_os/provider_budget.py
skills_UIUX/scripts/uiux-agent.py
skills_UIUX/runtime/runtime-policy.json
```

## Budget resolution

Budget source priority is:

```text
provider_budget.default
→ provider_budget.by_agent[agent]
→ provider_budget.by_stage[stage_id]
```

More specific entries override less specific entries.

The A6.1 routed `max_turns` remains the caller/runtime ceiling. A6.2 `max_calls` may reduce that ceiling but cannot increase it.

Supported budget fields:

```text
max_calls
max_estimated_total_tokens
output_reserve_tokens_per_call
timeout_seconds
max_cost_usd
pricing.input_usd_per_million
pricing.output_usd_per_million
```

`provider_budget.enabled = false` is the compatibility default.

## Authority boundary

Budget authority belongs to runtime policy only.

The following are **not** budget inputs:

- task prompt or Task Contract prose;
- provider/model output;
- provider summaries or evidence claims;
- recalled evaluation/quality memory;
- browser/DOM content;
- tool observations;
- generated source code.

A provider cannot ask for, encode or return a larger budget and have the runtime accept it.

## Call budget

`max_calls` is cumulative for the same managed stage and persists across replans/resume through `provider_usage_by_stage`.

Re-entering a stage therefore does not reset an already-consumed call budget.

## Timeout budget

`timeout_seconds` is a stage-level elapsed-time ceiling.

When the underlying provider exposes its own timeout, A6.2 may only reduce it:

```text
provider timeout = min(existing provider timeout, remaining stage budget)
```

A6.2 never increases an adapter's existing timeout.

## Token telemetry and reservation

The current provider-neutral contract records:

```text
estimated_input_tokens
estimated_output_tokens
estimated_total_tokens
```

These are deterministic runtime estimates based on bounded UTF-8 serialized request/response bytes. They are **not represented as provider-reported billing tokens**.

Before a call, the runtime reserves:

```text
estimated request tokens
+ output_reserve_tokens_per_call
```

If that reservation would exceed `max_estimated_total_tokens`, the provider call is blocked before execution.

If the returned structured response causes the estimate to exceed the configured budget, the stage becomes budget-blocked rather than treating the provider response as authority to continue.

## Cost telemetry

Cost is also explicitly an estimate unless a future provider adapter supplies trusted billing usage.

A configured `max_cost_usd` requires explicit operator-provided pricing:

```text
pricing.input_usd_per_million
pricing.output_usd_per_million
```

The runtime does not fetch, infer or invent model prices.

Before a call, A6.2 checks the worst-case configured reservation against the remaining estimated cost budget. If insufficient, it blocks the call.

This is a runtime reservation policy, not a guarantee about an external provider's invoice when that provider does not expose a hard output-token cap through the canonical adapter.

## Persisted telemetry

Manager checkpoint:

```text
provider_budget_by_stage
provider_usage_by_stage
provider_usage_totals
provider_usage_history
```

Specialist stage checkpoint:

```text
provider_budget
provider_usage
```

Persisted usage is deliberately metadata-only:

- provider;
- model;
- call count;
- estimated token counts;
- estimated cost;
- elapsed time;
- exhaustion state/reason;
- budget values and source.

It does **not** persist through this telemetry channel:

- prompts;
- provider response prose;
- API keys/secrets;
- DOM/HTML;
- source code;
- screenshots;
- raw tool output.

## Budget exhaustion

When a budget is exhausted, the budget wrapper returns a bounded `BLOCKED` provider-stage result.

The underlying provider is not called when the runtime can prove before execution that the next call would exceed call/token/cost/time budget.

## Relationship to A6.1

```text
A6.1 StageProviderRouter
        ↓ provider/model/max-turn routing
A6.2 StageProviderBudgetResolver
        ↓ immutable stage budget
BudgetedProvider
        ↓ calls + runtime telemetry
canonical ProviderManagedRunner
```

A6.2 does not create another orchestration path or another provider transport implementation.

## Regression requirements

Tests must prove at least:

1. stage budget specificity is deterministic;
2. configured calls cannot exceed the A6.1 caller ceiling;
3. explicit cost budget without pricing fails closed;
4. provider output cannot raise call budget;
5. token reservation can block before a provider call;
6. consumed budget survives stage re-entry/replan;
7. timeout policy can reduce but never increase provider timeout;
8. budget/usage metadata persists at manager and specialist checkpoints;
9. telemetry persistence does not contain prompts, API keys or provider output prose.

## Trust model

```text
runtime policy       = budget authority
provider/model       = budget consumer
runtime observations = usage telemetry
provider prose       = no budget authority
```
