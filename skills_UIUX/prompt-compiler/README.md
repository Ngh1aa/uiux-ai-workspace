# Prompt Compiler / Prompt OS v1 — Quick Start

Prompt OS v1 converts a repository plus a short goal into a detailed, evidence-grounded project prompt pack **before implementation begins**, then can execute and QA against that frozen specification.

Stable v1 contract: [`PROMPT-OS-V1.md`](./PROMPT-OS-V1.md)  
Machine capability manifest: [`prompt-os-v1.json`](./prompt-os-v1.json)

## Smallest useful request

```text
@GitHub use https://github.com/Ngh1aa/uiux-ai-workspace

repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
mode = compile_then_execute
```

Use `mode = compile_only` when you want to inspect the prompt pack before any implementation.

## Stable v1 pipeline

```text
repo / brief / reference
→ deep reference evidence + motion sampling when applicable
→ research / UX / art direction
→ select spec profile
→ compile prompt pack
→ consistency gate
→ freeze 02-FULL-BUILD-SPEC.md
→ implementation reads frozen spec
→ BrowserQA
→ profile-aware reference visual QA
→ semantic VisualCritic
→ evidence contract
→ root-cause repair / re-render
```

The implementation agent must not skip the compiled specification or silently reinterpret the original request in parallel.

## Canonical prompt pack

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

For smaller tasks the Factory may collapse the pack when doing so does not remove material implementation/QA context.

## Profile-aware specification

Read `PROFILE-ROUTING.md` before applying a specialized profile.

- `profiles/pixel-faithful.md` — exact reconstruction from authoritative visual/runtime evidence;
- `profiles/preserve-and-extend.md` — protect a proven core while adding/changing surfaces;
- `profiles/redesign.md` — preserve product truth while materially changing UX/visual structure;
- `profiles/original-design.md` — greenfield/original design with deliberate `PROPOSED` decisions.

A reference URL does **not** automatically mean `pixel_faithful`.

Different evidence classes may coexist inside the same surface. Label each material value/decision independently rather than forcing an entire section into one mode.

## Evidence vocabulary

```text
VERIFIED
INFERRED
ASSUMED
UNKNOWN
PROPOSED
N/A_JUSTIFIED
```

`PROPOSED` is for deliberate new decisions. `ASSUMED` is for missing context temporarily assumed to continue.

Use `BLOCKING_UNKNOWN` only when unresolved information can materially change architecture, preservation boundaries, asset/legal ownership, core product behavior, real-vs-simulated behavior, or release authority.

## Deep reference evidence

When a live reference is available, Factory can persist `reference-evidence.v1.json` containing measured DOM/style/asset/media-query/color evidence and runtime motion checkpoints.

Evidence provenance records stable `EVID-...` anchors. Screenshot palette and choreography interpretation remain `INFERRED` unless directly measured by the browser/runtime.

References are evidence, not authorization to clone.

## Reference-aware visual QA

Read `REFERENCE-AWARE-VISUAL-QA.md`.

```text
pixel_faithful      → strict same-viewport reference gate
preserve_and_extend → strict only for explicit protected visual surfaces
redesign            → new frozen art direction/spec owns visual acceptance
original_design     → frozen spec + quality rubric owns visual acceptance
```

Machine pixel metrics are heuristics and do not replace semantic/human visual review.

## Prototype quality rubric

`PROTOTYPE-QUALITY-RUBRIC.md` contains adaptive visual/UX guidance extracted from common prototype checklists.

It is a **rubric, not a universal law**. Values such as touch-target size, nav-count ranges, feedback timing, font-family count and type-scale ratios are useful defaults unless project/platform evidence justifies another decision.

Simulated prototype behavior must be labelled `SIMULATED`; do not present fake waits/data as backend capability.

## Important file roles

- `SKILL.md` — operating contract and trigger logic;
- `PROMPT-OS-V1.md` — stable v1 capability/release contract;
- `prompt-os-v1.json` — machine-readable v1 capability manifest;
- `SPEC-FIRST-EXECUTION.md` — compile-before-code execution contract;
- `SPEC-WRITER-SYSTEM.md` — universal Spec Writer role contract;
- `PROFILE-ROUTING.md` — profile classification and blocking-unknown rules;
- `PROTOTYPE-QUALITY-RUBRIC.md` — adaptive visual/interaction rubric;
- `REFERENCE-AWARE-VISUAL-QA.md` — rendered reference comparison rules;
- `PROMPT-OS-V1-BENCHMARK.md` — four-profile regression benchmark;
- `PROJECT-AUDIT.schema.md` — forensic repository audit structure;
- `FULL-BUILD-PROMPT.schema.md` — standalone universal build-spec structure;
- `PROMPT-PACK.schema.md` — five-file output contract;
- `QA-CONTRACT.schema.md` — browser/runtime/deploy QA contract;
- `profiles/` — specialized compilation profiles;
- `examples/mostar-guide.md` — one **resolution example only** for specificity and preservation discipline.

## Examples are not templates

Mostar is not the default project model. Do **not** copy its sitemap, routes, file tree, deployment setup, animations, selectors, assets, design language, accessibility implementation or section order.

Use it only as an example of how concrete a specification can become when a target contains enough evidence.

## Detail standard

A strong full build spec may contain exact paths/files/routes, selectors/functions/state owners, layout/token values, breakpoints, motion timing/choreography, config snippets, metadata, accessibility semantics, deployment commands/settings, binary QA checkpoints and exact delivery inventory **when those details are applicable**.

Do not optimize for prompt length. Optimize for:

```text
Grounding
→ correct profile
→ exact project truth
→ explicit preserve/change boundaries
→ concrete project-specific decisions
→ executable detail
→ verifiable acceptance criteria
→ no hidden chat dependency
```

## Verify Prompt OS v1

From `uiux-factory/`:

```bash
python scripts/run_prompt_os_v1_benchmark.py
python scripts/verify_prompt_os_v1.py
```

Both commands must PASS before a release may claim the Prompt OS v1 contract is intact.
