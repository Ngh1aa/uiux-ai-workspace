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

Use when you want to inspect the specification before any implementation:

```text
mode = compile_only
```

The Factory stops after producing the prompt pack.

### Compile, then execute

Use when you want the Factory to generate the detailed prompt pack first and then build from that exact spec:

```text
mode = compile_then_execute
```

Pipeline:

```text
repo + goal
→ audit / research / design intelligence
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

## File roles

- `SKILL.md` — operating contract and trigger logic;
- `SPEC-FIRST-EXECUTION.md` — compile-before-code execution contract;
- `PROJECT-AUDIT.schema.md` — forensic repository audit structure;
- `FULL-BUILD-PROMPT.schema.md` — standalone build-spec structure;
- `PROMPT-PACK.schema.md` — five-file output contract;
- `QA-CONTRACT.schema.md` — browser/runtime/deploy QA contract;
- `examples/mostar-guide.md` — one **resolution example only** for specificity and preservation discipline.

## Important: examples are not templates

Mostar is not the default project model.

Do **not** copy its:

- sitemap;
- routes;
- file tree;
- deployment setup;
- animations;
- selectors;
- assets;
- design language;
- accessibility implementation;
- section order.

Use it only as an example of how concrete a specification can become when the target project contains enough evidence.

Each project must generate its own prompt pack from its own source of truth.

## Detail standard

A good full build spec may contain exact:

- paths/files/routes;
- selectors/functions/state owners;
- layout/token values;
- breakpoints;
- motion timing and choreography;
- literal config snippets;
- SEO markup;
- accessibility semantics;
- deployment commands/settings;
- binary QA checkpoints;
- exact delivery inventory.

These details must be `VERIFIED`, `PROPOSED`, or otherwise explicitly evidence-labelled. Do not add requirements just to make the prompt longer.

## Design principle

Do not optimize for prompt length.

Optimize for:

```text
Grounding
→ exact project truth
→ explicit preserve/change boundaries
→ concrete project-specific decisions
→ executable detail
→ verifiable acceptance criteria
→ no hidden chat dependency
```

A simple project may produce a shorter prompt. A complex multi-route, animation-heavy, deployment-sensitive, or preserve-heavy project may produce a very long one.

## Example invocation — compile only

```text
Prompt Compile:
repo = https://github.com/Ngh1aa/Lumen
goal = Turn the current visual prototype into a complete digital museum experience while preserving its strongest visual identity and interactions.
mode = compile_only
```

## Example invocation — compile then execute

```text
@GitHub use uiux-ai-workspace.

repo = https://github.com/OWNER/PROJECT
goal = Redesign and complete this project to portfolio-grade quality.
mode = compile_then_execute
```

The Factory should inspect the target directly, load only applicable UIUX skills, compile a project-specific prompt pack, freeze it as the implementation source of truth, then implement and QA against that pack.