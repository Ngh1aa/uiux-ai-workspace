# Prompt Compiler — Quick Start

Use this directory when you want to convert a repository plus a short goal into a detailed, evidence-grounded project prompt pack.

## Smallest useful request

```text
@GitHub use https://github.com/Ngh1aa/uiux-ai-workspace

Prompt Compile:
repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
```

Default behavior:

```text
output = prompt_pack
authority = spec_only
```

No target implementation should happen during the compile step unless the user explicitly changes authority/scope later.

## What the compiler produces

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

For smaller tasks it may produce only `02-FULL-BUILD-SPEC.md`.

## File roles

- `SKILL.md` — operating contract and trigger logic;
- `PROJECT-AUDIT.schema.md` — forensic repository audit structure;
- `FULL-BUILD-PROMPT.schema.md` — standalone build-spec structure;
- `PROMPT-PACK.schema.md` — five-file output contract;
- `QA-CONTRACT.schema.md` — browser/runtime/deploy QA contract;
- `examples/mostar-guide.md` — golden example for precision and preservation discipline.

## Design principle

Do not optimize for prompt length.

Optimize for:

```text
Grounding
→ exact project truth
→ explicit preserve/change boundaries
→ executable decisions
→ verifiable acceptance criteria
→ no hidden chat dependency
```

A good compiled prompt is allowed to be short when the project is simple and long when the project has protected behavior, multiple routes, or release risk.

## Example invocation

```text
Prompt Compile:
repo = https://github.com/Ngh1aa/Lumen
goal = Turn the current visual prototype into a complete digital museum experience while preserving its strongest visual identity and interactions.
```

The compiler should inspect Lumen directly, load only applicable UIUX skills, then produce a pack specific to Lumen. It must not copy the Mostar file tree or requirements just because Mostar is the golden example.
