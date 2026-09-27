# Prompt Compiler — Quick Start

Use this directory when you want to convert a repository plus a short goal into a detailed, evidence-grounded project prompt pack **before implementation begins**.

## Smallest useful request

```text
@GitHub use https://github.com/Ngh1aa/uiux-ai-workspace

Prompt Compile:
repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
```

## Two execution modes

### Compile only

```text
mode = compile_only
```

The Factory stops after producing and checking the prompt pack.

### Compile, then execute

```text
mode = compile_then_execute
```

Pipeline:

```text
repo + goal
→ audit / research / design intelligence
→ select spec profile
→ prompt pack
→ consistency gate
→ freeze 02-FULL-BUILD-SPEC.md
→ implementation reads frozen spec
→ rendered QA reads frozen spec
→ root-cause repair
```

The implementation agent must not skip the compiled specification or silently reinterpret the original request in parallel.

## What the compiler produces

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

For smaller tasks it may produce only `02-FULL-BUILD-SPEC.md` when that does not remove material context.

## Profile-aware specification

Prompt Compiler is universal, but its specification emphasis changes with the target.

Read `PROFILE-ROUTING.md` before applying a specialized profile.

Available profiles:

- `profiles/pixel-faithful.md` — exact reconstruction from authoritative visual/runtime evidence;
- `profiles/preserve-and-extend.md` — protect a proven core while adding/changing surfaces;
- `profiles/redesign.md` — preserve product truth while materially changing UX/visual structure;
- `profiles/original-design.md` — greenfield/original design with deliberate `PROPOSED` decisions.

A reference URL does **not** automatically mean `pixel_faithful`.

Different evidence classes may coexist inside the same surface. Label each material value/decision independently rather than forcing an entire section into one mode.

## Prototype quality rubric

`PROTOTYPE-QUALITY-RUBRIC.md` contains adaptive visual/UX guidance extracted from common prototype checklists.

It is a **rubric, not a universal law**. Values such as touch-target size, nav-count ranges, feedback timing, font-family count, and type-scale ratios are useful defaults unless project/platform evidence justifies a different decision.

Simulated prototype behavior must be labelled `SIMULATED`; do not present fake waits/data as backend capability.

## File roles

- `SKILL.md` — operating contract and trigger logic;
- `SPEC-FIRST-EXECUTION.md` — compile-before-code execution contract;
- `PROFILE-ROUTING.md` — profile classification and blocking-unknown rules;
- `PROTOTYPE-QUALITY-RUBRIC.md` — adaptive visual/interaction rubric;
- `PROJECT-AUDIT.schema.md` — forensic repository audit structure;
- `FULL-BUILD-PROMPT.schema.md` — standalone universal build-spec structure;
- `PROMPT-PACK.schema.md` — five-file output contract;
- `QA-CONTRACT.schema.md` — browser/runtime/deploy QA contract;
- `profiles/` — specialized compilation profiles;
- `examples/mostar-guide.md` — one **resolution example only** for specificity and preservation discipline.

## Important: examples are not templates

Mostar is not the default project model.

Do **not** copy its sitemap, routes, file tree, deployment setup, animations, selectors, assets, design language, accessibility implementation, or section order.

Use it only as an example of how concrete a specification can become when a target contains enough evidence.

Each project must generate its own prompt pack from its own source of truth.

## Evidence vocabulary

Material decisions use:

```text
VERIFIED
INFERRED
ASSUMED
UNKNOWN
PROPOSED
N/A_JUSTIFIED
```

`PROPOSED` is for deliberate new decisions. `ASSUMED` is for missing context temporarily assumed to continue.

Use `BLOCKING_UNKNOWN` only in the unresolved section when missing information can materially change architecture, preservation boundaries, asset/legal ownership, core product behavior, real-vs-simulated behavior, or release authority.

## Detail standard

A good full build spec may contain exact paths/files/routes, selectors/functions/state owners, layout/token values, breakpoints, motion timing/choreography, config snippets, metadata, accessibility semantics, deployment commands/settings, binary QA checkpoints, and exact delivery inventory **when those details are applicable**.

Do not add requirements merely to make the prompt longer.

## Design principle

Do not optimize for prompt length.

Optimize for:

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

A simple project may produce a shorter prompt. A complex multi-route, animation-heavy, deployment-sensitive, or preserve-heavy project may produce a very long one.

## Example invocation

```text
@GitHub use uiux-ai-workspace.

repo = https://github.com/OWNER/PROJECT
goal = Redesign and complete this project to portfolio-grade quality.
mode = compile_then_execute
```

The Factory should inspect the target directly, classify the work, load only applicable UIUX skills/profile/rubric, compile a project-specific prompt pack, freeze it as the implementation source of truth, then implement and QA against that pack.