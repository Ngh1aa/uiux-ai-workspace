# Universal AI Prompt System

This repository includes a reusable layered prompt system for AI-assisted project work.

The goal is to avoid rewriting a giant prompt for every task. Stable operating rules live at the repository level, project-specific truth lives in a context packet, task-specific instructions stay small and explicit, and the Prompt Compiler can synthesize those layers plus live repository evidence into an executable project specification.

## Files

### `AGENTS.md`

Persistent operating contract shared across project work.

It defines:

- source-of-truth precedence;
- evidence states;
- context acquisition;
- execution and change-safety rules;
- research/tool policy;
- validation requirements;
- root-cause repair behavior;
- Definition of Done;
- completion reporting.

Copy this file into another repository when you want the same agent behavior there.

### `PROJECT-CONTEXT.template.md`

Reusable project-level input template.

For a new project:

1. copy it to `PROJECT-CONTEXT.md`;
2. fill only facts that are actually known;
3. leave missing facts as `UNKNOWN`;
4. keep source-of-truth paths and Definition of Done current.

Do not treat the template itself as actual project context.

### `.github/prompts/universal-task.prompt.md`

Reusable task-level prompt.

Use it when requesting a specific feature, fix, audit, research task, refactor, review, or release action.

The task prompt supplies:

- task and rationale;
- scope;
- inputs;
- acceptance criteria;
- constraints;
- execution contract;
- verification contract;
- failure policy;
- output contract.

### `skills_UIUX/prompt-compiler/`

Repository-to-spec compiler for substantial UI/UX/product work.

Use it when the user has a target repository and a short goal but wants a detailed build prompt or prompt pack before implementation.

Minimal invocation:

```text
Prompt Compile:
repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
```

Default substantial-project output:

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

The compiler audits the target repository first, extracts exact project truth, classifies evidence, identifies Preserve/Can-change boundaries, loads only applicable UIUX skills, and then compiles an implementation-ready specification. It does **not** implement the target during the default `spec_only` compile.

Use `.github/prompts/prompt-compiler.prompt.md` as the short task entrypoint and `skills_UIUX/prompt-compiler/examples/mostar-guide.md` as the golden example for precision.

## Recommended context architecture

```text
Repository
│
├── AGENTS.md                      # stable operating rules
├── PROJECT-CONTEXT.md             # actual project-specific truth
├── PROJECT-CONTEXT.template.md    # reusable template
│
├── docs/
│   ├── architecture.md
│   ├── requirements.md
│   └── decisions/
│
└── .github/
    └── prompts/
        ├── universal-task.prompt.md
        └── prompt-compiler.prompt.md
```

## Recommended usage

### Starting a new project

1. Copy `AGENTS.md`.
2. Copy `PROJECT-CONTEXT.template.md` to `PROJECT-CONTEXT.md`.
3. Fill project facts, constraints, source-of-truth paths, quality requirements, and Definition of Done.
4. Keep detailed domain knowledge in normal project docs rather than inflating `AGENTS.md`.

### Starting a normal task

Provide the concrete task using `.github/prompts/universal-task.prompt.md`.

You do not need to fill every field. Include only context that materially changes the work.

### Compiling a substantial project prompt

Use Prompt Compiler when a repository already exists and the detailed implementation contract should be derived from the repository rather than manually described.

```text
Prompt Compile:
repo = https://github.com/OWNER/REPO
goal = Turn the current prototype into a complete multi-page experience while preserving its strongest existing interaction model.
```

The compiler should:

1. audit the target source;
2. extract exact architecture, routes, selectors, tokens, functions, breakpoints, workflows and protected behavior;
3. distinguish `VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED`;
4. compile the prompt pack;
5. self-review for contradictions and hidden-chat dependencies;
6. stop before implementation unless the user explicitly changes authority.

### Updating context

Update project context when one of these changes:

- architecture;
- canonical source paths;
- technology/runtime versions;
- quality gates;
- deployment process;
- hard constraints;
- Definition of Done.

Avoid storing short-lived task details in the persistent operating contract.

## Prompt layering

The intended precedence is:

```text
LATEST USER TASK
      ↓
PROJECT-SPECIFIC INSTRUCTIONS / CONTEXT
      ↓
AGENTS.md OPERATING CONTRACT
      ↓
SOURCE CODE / TESTS / RUNTIME / ARTIFACTS
      ↓
APPLICABLE skills_UIUX CONTRACTS
      ↓
OFFICIAL EXTERNAL SOURCES
      ↓
INFERENCE / ASSUMPTION
```

A lower-confidence source must not silently override a higher-confidence one.

Prompt Compiler is a synthesis layer, not a new source of truth. It must not invent project facts that are absent from the layers above.

## Minimal task form

For small tasks, this shorter form is sufficient:

```text
Task:
[what to do]

Source of truth:
[files / repo / URL]

Acceptance criteria:
- [criterion]
- [criterion]

Constraints:
- [constraint]

Verify with:
- [tests / browser / sources / runtime evidence]
```

The full task contract is most useful for substantial or high-risk work.

## Why the system is split into layers

A single mega-prompt creates several problems:

- repeated context consumes attention and tokens;
- project facts become stale inside copied prompts;
- task details get mixed with permanent operating rules;
- conflicts become harder to resolve;
- agents are more likely to overlook acceptance criteria.

Separating stable instructions, project context, task context and repository-to-spec compilation makes the operating contract easier to reuse and audit.

Prompt Compiler does not change this philosophy: it generates a detailed spec **from** those separated layers instead of forcing the user to manually merge them.

## Evidence-first behavior

The system deliberately separates:

- `VERIFIED`;
- `INFERRED`;
- `ASSUMED`;
- `UNKNOWN`.

Prompt Compiler additionally uses:

- `PROPOSED` — new design/product/architecture decisions introduced by the specification;
- `N/A_JUSTIFIED` — explicitly not applicable to the declared project/scope.

This is especially important for generated software and design work. A successful generation step, build, or CI check does not automatically prove product quality.

Use evidence appropriate to the claim:

- code → compile/test/runtime evidence;
- UI → rendered/browser evidence;
- visual quality → screenshot/visual review evidence;
- current facts → authoritative current sources;
- deployment → deployment/workflow evidence.

## Root-cause repair

When validation fails, the default behavior is:

```text
FAILURE EVIDENCE
      ↓
EARLIEST RESPONSIBLE OWNER
      ↓
INVALIDATE / REPAIR FROM OWNER
      ↓
RERUN DOWNSTREAM WORK
      ↓
REVALIDATE
```

Do not repeatedly patch downstream symptoms when the failure originates upstream.

## Research basis

The structure of this prompt system was informed by current guidance from multiple primary sources, especially:

- OpenAI prompt engineering guidance: https://developers.openai.com/api/docs/guides/latest-model
- Anthropic prompt engineering overview and templates: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- Anthropic prompt templates and variables: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables
- Google Vertex AI prompt design strategies: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-design-strategies
- GitHub Copilot custom instructions: https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot
- GitHub Copilot response customization concepts: https://docs.github.com/en/copilot/concepts/prompting/response-customization

These sources converge on a few useful ideas reflected here: give clear instructions, separate context from task intent, specify constraints/output expectations, keep persistent project instructions focused, and evaluate prompts by the quality of the resulting work rather than by prompt length.

## Maintenance rule

Treat the operating contract as stable. Prompt Compiler schemas may evolve as a reusable skill, but do not continuously expand `AGENTS.md` with project-specific lessons.

Add a global rule only when it is broadly reusable across projects. Keep domain-specific knowledge in project docs, skills, compiled specs, or task prompts.
