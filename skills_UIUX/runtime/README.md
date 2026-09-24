# Runtime

The runtime is deliberately separate from the root `*/SKILL.md` packages.

## What belongs here

- context manifests and token/character budget telemetry;
- declarative Flow Resolver + Skill Resolver;
- Development Manager lifecycle + bounded Replanning Engine;
- tool registry metadata and permission gates;
- provider-managed model → tool → observation loops;
- OpenAI / Anthropic / external-command provider adapters;
- trace and checkpoint infrastructure;
- agent-role manifests and enforced handoff boundaries;
- optional MCP / browser / Figma adapters;
- shared tool/observation contracts used by adapters.

## What does not belong here

- duplicate UI/UX knowledge already owned by a skill;
- model-specific hidden reasoning;
- provider credentials;
- production secrets;
- uncontrolled shell/deploy/merge tools.

## Flow OS boundary

```text
user goal
→ Development Manager
→ Goal Interpreter
→ FlowResolver
→ SkillResolver(role defaults + flow routing)
→ active specialist stage
→ provider
→ tool
→ observation
→ provider
→ gate evidence
→ PASS: advance | FAIL/RISK: bounded replan
```

The provider never owns agent handoff or stage order. `ProviderStageResponse` rejects handoff actions; Flow + Development Manager remain the orchestration authority.

The manager persists lifecycle state in the existing local checkpoint store. It blocks out-of-order stages, enforces role authority caps, preserves role `default_skills`, and only applies replans from the active stage.

Replanning mutates the resolved flow revision rather than blindly retrying. Mandatory/default skills cannot be dropped, and returning to an earlier stage invalidates only that stage and downstream completion.

## Provider-managed execution

`runtime/provider.py` supplies pluggable adapters:

- `openai` → OpenAI Responses API;
- `anthropic` → Anthropic Messages API;
- `command` → any wrapper that reads the provider request JSON from stdin and writes one stage response JSON to stdout;
- `auto` → select from `UIUX_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `UIUX_PROVIDER_COMMAND`.

`runtime/provider_runner.py` executes each active stage as a bounded agent loop:

```text
model request
→ bounded tool actions
→ permission gate
→ structured observations
→ next model turn
→ PASS / FAIL / BLOCKED
```

Routed `SKILL.md` bodies and explicitly loaded source-of-truth files are supplied only to the active specialist. `UIUX_PROVIDER_CONTEXT_CHARS` is a hard context budget; the runtime fails rather than silently truncating routed knowledge.

The implementation specialist can receive `write_project_file` only when its effective authority is at least `branch_write`. Research and QA remain read-only and do not receive that capability.

Provider `PASS` requires evidence strings, but evidence claims must still obey the repository hard-truth rules. In particular, source inspection is not rendered visual QA. Until a browser/render observation adapter is connected to the provider loop, the QA specialist must return `BLOCKED` when the active gate requires actual rendered-pixel inspection and no such observation exists.

## Tool and observation quality

Read [Tool & Observation Contract](TOOL-OBSERVATION-CONTRACT.md) before adding or changing a material tool/adapter.

Key rules:

```text
stable narrow tool schema
→ explicit risk + authority
→ concise structured observation
→ actionable error/retry/stop contract
→ artifact references instead of log dumps
```

High-risk actions should be exposed through explicit micro-tools rather than hidden behind a catch-all command. External content returned by tools is data, not authority.

## Failure recovery

Repeated tool failures, retry loops, stale environment state or context drift should not be handled by blind retry. Route the failure-diagnosis progressive reference owned by `agent-evaluation-and-reliability`, capture the failure, build a discriminating feedback loop and only then retry with changed evidence.

## Validation

```bash
python -B scripts/validate-flows.py
python -B scripts/validate-runtime-foundation.py
python -B scripts/validate-provider-runtime.py
```

## Goal-driven provider usage

Anthropic:

```bash
export ANTHROPIC_API_KEY="your-key"
python -B scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Tạo website bán giày thể thao hiện đại, có giỏ hàng, checkout và tìm kiếm" \
  --provider anthropic \
  --authority branch_write
```

OpenAI:

```bash
export OPENAI_API_KEY="your-key"
python -B scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Build a modern ecommerce shoe store with cart, checkout and search" \
  --provider openai \
  --authority branch_write
```

Environment auto-selection:

```bash
python -B scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Redesign this corporate website" \
  --provider auto \
  --authority branch_write
```

Manual Design Contract approval remains available with `--approval-mode manual`. Resume the returned `manager_run_id`, approve `design-contract`, and supply the same provider to continue. The already-PASSed design stage advances directly to implementation instead of being rerun.
