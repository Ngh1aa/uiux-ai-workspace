# Prompt Compiler

Use `skills_UIUX/prompt-compiler/SKILL.md` and `skills_UIUX/prompt-compiler/SPEC-FIRST-EXECUTION.md` as the governing contracts.

## Input

```text
repo = [TARGET_REPOSITORY_URL]
goal = [1–3 sentences]
```

Optional:

```text
preserve = [...]
change = [...]
responsive_scope = desktop_only | responsive_all
deployment = [...]
mode = compile_only | compile_then_execute
authority = spec_only | branch_write | create_pr_only | merge_only | merge_and_deploy
output = full_build_prompt | prompt_pack
```

## Task

Audit the target repository directly and compile an evidence-grounded, project-specific prompt/specification before implementation.

Do not use Mostar or any other example as the target structure. Examples are quality bars for specificity only.

Required logical outputs for substantial work:

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

The full build spec must be concrete enough that another capable agent can implement without hidden chat history. When applicable, include exact file paths, routes, selectors/functions, tokens, breakpoints, motion rules, deployment config/snippets, SEO markup, accessibility semantics, binary QA checkpoints and exact deliverables.

Use exact repository evidence when available. Distinguish:

```text
VERIFIED
INFERRED
ASSUMED
UNKNOWN
PROPOSED
N/A_JUSTIFIED
```

A deliberate new design/architecture value is normally `PROPOSED`, not `ASSUMED`.

## Mode behavior

### `compile_only`

Compile the prompt pack, run the self-review/consistency gate, return or persist the pack, and stop. Do not implement target code.

### `compile_then_execute`

1. Compile the prompt pack first.
2. Run the consistency gate.
3. Persist/freeze `02-FULL-BUILD-SPEC.md` as the implementation source of truth.
4. Make the implementation agent read that exact spec before editing code.
5. Make QA/remediation evaluate against that exact spec.
6. If implementation must deviate from the spec, record the deviation and evidence explicitly.
7. Continue only within the declared authority.

Do not require a second user message between compile and implementation unless the user explicitly requested an approval gate or the compiled spec exposes a blocking UNKNOWN/conflict.

## Default selection

If the user explicitly says “Prompt Compile”, “spec only”, “chưa implement”, or equivalent:

```text
mode = compile_only
output = prompt_pack
```

If the user asks the Factory to actually build/redesign/extend a substantial project and says to use the Prompt Compiler/spec-first workflow:

```text
mode = compile_then_execute
output = prompt_pack
```

Before continuing, run the self-review gate defined in `skills_UIUX/prompt-compiler/SKILL.md` and the compile gate in `SPEC-FIRST-EXECUTION.md`.