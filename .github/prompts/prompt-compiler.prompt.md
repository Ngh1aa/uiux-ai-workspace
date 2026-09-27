# Prompt Compiler

Use `skills_UIUX/prompt-compiler/SKILL.md` as the governing skill.

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
authority = spec_only | branch_write | create_pr_only | merge_only | merge_and_deploy
output = full_build_prompt | prompt_pack
```

## Task

Audit the target repository directly and compile an evidence-grounded project specification.

Default for substantial projects:

```text
output = prompt_pack
authority = spec_only
```

Required logical outputs:

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

Do not implement target code during the compile task unless the user explicitly authorizes implementation separately.

Use exact repository evidence (selectors, routes, functions, tokens, breakpoints, workflows) when available. Distinguish VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED.

Before returning, run the self-review gate defined in `skills_UIUX/prompt-compiler/SKILL.md`.
