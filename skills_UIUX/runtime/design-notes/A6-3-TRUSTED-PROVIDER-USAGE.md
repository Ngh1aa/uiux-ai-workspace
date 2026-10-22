# A6.3 — Trusted Provider Usage + Hard Output Caps

Status: **CANONICAL RUNTIME CONTRACT**

A6.3 upgrades A6.2 provider budget telemetry from estimate-only accounting to a dual-channel model:

```text
runtime estimate/reservation
+
trusted provider transport usage, when available
```

It also converts the A6.2 per-call output reservation into a real API output-token ceiling for canonical OpenAI and Anthropic adapters.

## Goal

Use provider-reported token usage when it comes from trusted transport metadata, without allowing model-authored stage output to spoof usage or raise budget.

Executable ownership:

```text
uiux-factory/core/runtime/flow_os/provider.py
uiux-factory/core/runtime/flow_os/provider_budget.py
```

## Trust boundary

Trusted usage may only originate from canonical adapter HTTP response metadata:

```text
OpenAI Responses API `usage`
Anthropic Messages API `usage`
```

The following are **not** trusted usage sources:

- model-authored structured stage JSON;
- `summary` or `evidence` fields;
- command-provider stdout;
- task context;
- tool observations;
- recalled memory;
- generated source or DOM content.

A model cannot reduce its recorded usage by adding a `usage` object to its structured response.

## Canonical usage object

Adapters normalize trusted transport metadata into:

```text
ProviderReportedUsage
├── input_tokens
├── output_tokens
├── total_tokens
└── source
```

Canonical trusted sources are currently:

```text
openai_api_usage
anthropic_api_usage
```

`BudgetedProvider` accepts reported usage only when provider identity and trusted source agree.

## Hard output caps

When A6.2 `provider_budget.enabled = true`, the existing:

```text
output_reserve_tokens_per_call
```

is also used as the hard output cap for providers that expose a canonical output-token limit.

OpenAI:

```text
max_output_tokens
```

Anthropic:

```text
max_tokens
```

The runtime can only reduce a provider's pre-existing cap:

```text
applied cap = min(existing adapter cap, stage output reserve)
```

It never increases an existing adapter cap.

The command adapter does not claim a hard output-token capability because the canonical runtime cannot prove that an arbitrary external command honors one.

## Dual telemetry

A6.3 preserves all A6.2 estimate fields and adds:

```text
reported_calls
reported_input_tokens
reported_output_tokens
reported_total_tokens
reported_cost_usd
reported_usage_source
hard_output_cap_applied
hard_output_cap_tokens
```

The telemetry `measurement` becomes:

```text
runtime_estimate+trusted_provider_usage
```

only after trusted transport usage is observed.

If trusted usage is unavailable, the runtime remains on the A6.2 estimate path.

## Budget enforcement

Pre-call checks remain conservative runtime reservations, because reported usage does not exist before a call.

After a call:

- if every consumed call in the stage has trusted reported usage, token/cost enforcement uses the cumulative reported values;
- otherwise enforcement falls back to the cumulative runtime estimate so missing provider metadata cannot weaken the budget boundary.

This keeps resume/replan accounting conservative.

## Cost semantics

Provider APIs report tokens, not necessarily an invoice amount in the canonical response contract.

`reported_cost_usd` therefore means:

```text
trusted reported token counts
×
operator-configured A6.2 pricing
```

It is stronger than estimate-only token accounting but is still not represented as an external provider invoice.

The runtime continues to refuse to invent model pricing.

## Persistence

A6.3 extends the existing A6.2 checkpoint telemetry only. It does not create a second store.

Manager checkpoint remains:

```text
provider_budget_by_stage
provider_usage_by_stage
provider_usage_totals
provider_usage_history
```

Specialist checkpoint remains:

```text
provider_budget
provider_usage
```

No prompt, provider prose, API key, DOM, source code, screenshot or raw provider response is persisted through usage telemetry.

## Compatibility

- A6.2 estimate fields remain readable.
- Existing checkpoints without reported fields load with zero reported usage.
- `provider_budget.enabled = false` preserves previous provider output-limit behavior.
- Command/scripted providers remain estimate-only unless a future canonical transport contract explicitly promotes a trusted usage channel.

## Regression requirements

Tests must prove at least:

1. OpenAI receives the hard `max_output_tokens` ceiling;
2. Anthropic receives the hard `max_tokens` ceiling;
3. OpenAI transport `usage` is normalized as trusted usage;
4. Anthropic transport `usage` is normalized as trusted usage;
5. budget wrapping can only reduce an existing output cap;
6. model-authored `usage` content cannot become trusted telemetry;
7. trusted reported tokens can exhaust/block a stage budget;
8. estimate telemetry remains available as fallback;
9. existing A6.2 persistence/resume semantics remain valid.

## Trust model

```text
runtime policy                 = budget authority
runtime estimate               = pre-call reservation / fallback accounting
canonical HTTP usage metadata  = trusted token telemetry
operator pricing               = cost conversion authority
model-authored stage output    = no usage or budget authority
```
