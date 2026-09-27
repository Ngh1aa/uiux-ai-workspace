# Prompt OS v1 — Four-Profile Benchmark

This benchmark prevents the Spec-First pipeline from collapsing different project intents into one universal template.

## Cases

1. `pixel_faithful` — explicit exact rebuild intent. Missing authoritative comparison evidence must be `cantTell` and blocking.
2. `preserve_and_extend` — existing implementation/reference exists, but only protected surfaces may become strict. Whole-page visual difference is non-blocking.
3. `redesign` — existing product truth remains relevant, but old-reference pixel similarity is not a success criterion.
4. `original_design` — no existing implementation truth; design decisions are proposed and visual acceptance is spec-driven.

## Deterministic benchmark path

```text
fixture goal/reference context
→ infer_spec_profile()
→ write a frozen-profile spec fixture
→ ReferenceAwareVisualQA policy evaluation
→ assert expected mode/status/blocking behavior
→ assert no example-project leakage
```

The benchmark intentionally omits deep screenshots so missing-evidence behavior is observable without network/provider dependencies.

## Run locally

From `uiux-factory/`:

```bash
python scripts/run_prompt_os_v1_benchmark.py
```

The command writes:

```text
benchmark-results/prompt-os-v1-profile-benchmark.json
```

and exits non-zero when any profile contract regresses.

## What this benchmark proves

- explicit clone intent is required for `pixel_faithful`;
- the mere existence of a reference does not authorize cloning;
- preserve/extend does not become whole-page pixel matching;
- redesign/original work cannot be rejected for visual distance from an old/reference UI;
- all four modes remain available as distinct frozen-spec strategies.

## What it does not prove

This deterministic suite does not prove visual quality, user outcomes, live-site availability, or provider reasoning quality. Those remain separate rendered/browser/human gates.
