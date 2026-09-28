# A6.5 — Zero-Cost Provider Guard + Free-Tier Managed Routing

Status: **CANONICAL RUNTIME CONTRACT**

A6.4 global money-budget work was intentionally skipped. A6.5 instead makes the managed Flow OS align with the repository's zero-cost operating goal.

## Goal

Managed provider execution defaults to a fail-closed zero-cost lane:

```text
Groq / Gemini (explicitly confirmed free-tier accounts)
```

OpenAI and Anthropic are classified as paid-capable transports and may never be selected implicitly by the managed zero-cost path.

Executable ownership:

```text
uiux-factory/core/runtime/flow_os/provider_access.py
uiux-factory/core/runtime/flow_os/free_tier_provider.py
uiux-factory/core/runtime/flow_os/provider_routing.py
skills_UIUX/scripts/uiux-agent.py
skills_UIUX/runtime/runtime-policy.json
```

This does not replace the existing Factory `core/runtime/free_provider.py`; it applies the same explicit free-tier confirmation boundary to the provider-neutral managed Flow OS.

## Provider classes

Provider class membership is code-owned:

```text
zero-cost/free-tier lane: groq, gemini
paid-capable lane:        openai, anthropic
operator-managed lane:    command
```

Task text, model output, recalled memory, flow documents and arbitrary runtime-policy fields cannot reclassify a paid provider as free.

`command` remains operator-managed because its actual backing service may be local, free, or paid. It is never chosen automatically by the zero-cost resolver.

## Free-tier confirmation

Groq/Gemini execution requires all of the following:

```text
UIUX_FREE_TIER_CONFIRMED=1
UIUX_CLOUD_PROVIDERS includes the provider
provider API key exists
provider model ID exists
```

Environment names:

```text
Groq:
  GROQ_API_KEY
  UIUX_GROQ_MODEL

Gemini:
  GEMINI_API_KEY
  UIUX_GEMINI_MODEL
```

`UIUX_FREE_TIER_CONFIRMED=1` is an operator assertion that the account/tier has been checked. The runtime does not claim that an external provider's commercial terms will remain free forever.

## `provider=auto`

Managed `auto` is **zero-cost-only**.

Resolution is limited to explicitly configured Groq/Gemini entries in `UIUX_CLOUD_PROVIDERS`.

It does not inspect OpenAI/Anthropic keys as fallback candidates and it does not auto-select `command`.

Therefore this state:

```text
OPENAI_API_KEY exists
ANTHROPIC_API_KEY exists
no confirmed Groq/Gemini configuration
```

must fail closed rather than silently spend money.

## Paid-provider opt-in

OpenAI/Anthropic require two independent approvals:

1. runtime policy:

```json
"provider_access": {
  "mode": "zero_cost",
  "allow_paid_providers": true
}
```

2. current invocation:

```text
--allow-paid-provider
```

Both are required. An API key by itself is never permission to use a paid-capable provider.

The canonical policy defaults to:

```json
"provider_access": {
  "mode": "zero_cost",
  "allow_paid_providers": false,
  "allow_command_provider": true
}
```

## Stage routing

A6.1 stage routing now recognizes:

```text
groq
gemini
openai
anthropic
command
```

However routing permission and provider-access permission are separate gates.

Canonical order:

```text
caller provider request
→ ProviderAccessGuard
→ zero-cost auto resolution if requested
→ StageProviderRouter
→ ProviderAccessGuard again on routed provider
→ provider adapter creation
→ A6.2/A6.3 budget + usage boundary
→ ProviderManagedRunner
```

The second guard prevents a stage route from switching a zero-cost invocation to a paid provider behind the caller's back.

## Free-tier managed adapter

Groq and Gemini use their OpenAI-compatible chat-completions transports and return the existing canonical `ProviderStageResponse` contract.

The adapter preserves:

- structured JSON stage responses;
- bounded response size;
- explicit timeouts;
- A6.2/A6.3 hard output-token ceilings;
- no persisted API keys;
- no hidden paid fallback.

A6.3 trusted billing/token telemetry remains restricted to canonical OpenAI/Anthropic transport metadata. Groq/Gemini model-authored or generic response usage fields are not promoted to trusted billing truth by A6.5.

## Security and authority boundary

The following cannot grant paid-provider access:

- task prompt;
- Task Contract content;
- provider/model response;
- recalled evaluation or quality memory;
- browser/DOM content;
- generated source code;
- tool observations;
- presence of a paid-provider API key.

Paid access is controlled only by runtime policy plus the explicit invocation flag.

## Regression requirements

Tests must prove at least:

1. `auto` selects a confirmed Groq/Gemini configuration;
2. paid-provider keys do not influence zero-cost auto selection;
3. `auto` fails closed when no confirmed free-tier provider exists;
4. OpenAI/Anthropic require both policy permission and invocation opt-in;
5. policy payloads cannot reclassify paid providers as free;
6. Groq/Gemini are valid A6.1 routed providers;
7. free-tier adapters require explicit account-tier confirmation;
8. hard output cap reaches the free-tier transport request;
9. model-authored usage fields cannot become A6.3 trusted usage.

## Trust model

```text
runtime code classification    = provider cost class authority
runtime policy                 = whether paid-capable transport may be used
explicit invocation flag       = current-run paid opt-in
UIUX_FREE_TIER_CONFIRMED       = operator confirmation of free-tier account state
provider/model output          = no provider-access authority
API key presence               = credentials only, not spending permission
```
