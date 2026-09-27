# Universal AI Prompt System

This repository includes a reusable layered prompt system for AI-assisted project work.

The goal is to avoid rewriting a giant prompt for every task. Stable operating rules live at the repository level, project-specific truth lives in a context packet, task-specific instructions stay small and explicit, and Prompt Compiler synthesizes those layers plus repository/research/design evidence into a **project-specific executable specification before substantial implementation begins**.

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

Reusable task-level prompt for a specific feature, fix, audit, research task, refactor, review, or release action.

### `skills_UIUX/prompt-compiler/`

Repository-to-spec compiler for substantial UI/UX/product work.

Use it when the user has a target repository and a short goal and wants either:

- a detailed prompt/specification to review first; or
- the Factory to compile that specification first and then implement from it.

Minimal invocation:

```text
repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
mode = compile_then_execute
```

Canonical substantial-project output:

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

The compiler audits project truth, consumes applicable research/design artifacts, classifies evidence, identifies Preserve/Can-change boundaries, loads only relevant UIUX skills, and compiles an implementation-ready specification.

Read `skills_UIUX/prompt-compiler/SPEC-FIRST-EXECUTION.md` for the compile-before-code contract.

## Important: examples are resolution references, not templates

`skills_UIUX/prompt-compiler/examples/mostar-guide.md` is one example showing how detailed a spec can become when a project has enough evidence.

It must **not** be used as a default source for another project's:

- sitemap;
- routes;
- file tree;
- selectors/functions;
- assets;
- animation engine;
- deployment targets;
- SEO metadata;
- accessibility markup;
- visual direction;
- section order.

The transferable property is **specificity and executability**, not Mostar's content or architecture.

## Spec-first execution modes

### `compile_only`

Use when the user wants to inspect the prompt/spec before implementation.

```text
TARGET REPO + GOAL
      ↓
AUDIT / RESEARCH / DESIGN INTELLIGENCE
      ↓
PROMPT PACK
      ↓
CONSISTENCY GATE
      ↓
STOP
```

### `compile_then_execute`

Use when substantial work should actually be implemented.

```text
TARGET REPO + GOAL
      ↓
AUDIT / RESEARCH / DESIGN INTELLIGENCE
      ↓
PROMPT PACK
      ↓
CONSISTENCY GATE
      ↓
FREEZE 02-FULL-BUILD-SPEC.md + HASH
      ↓
IMPLEMENTATION READS FROZEN SPEC
      ↓
RENDERED QA READS SAME SPEC
      ↓
ROOT-CAUSE REPAIR
      ↓
RELEASE WITHIN AUTHORITY
```

A second approval turn is only required when the user asks for one or when a blocking conflict/UNKNOWN makes safe execution impossible.

## Why compile before implementation

The generated Full Build Spec becomes a single project-specific handoff that can include, when applicable:

- exact routes/pages/anchors;
- file paths and ownership;
- selectors/classes/IDs/functions/state owners;
- visual tokens and breakpoints;
- typography/grid/media rules;
- motion timing/choreography;
- literal configuration snippets;
- GitHub Pages/Vercel settings;
- SEO/meta markup;
- accessibility semantics/keyboard behavior;
- binary QA checkpoints;
- exact delivery inventory.

This prevents the implementation agent from independently reinterpreting a vague original request after design/research decisions have already been made.

## Detail is project-specific

The system should be capable of producing a long prompt like the detailed Mostar example, but it should not optimize for length.

For example, when a static project genuinely needs Vercel configuration, a spec may state concrete proposed content such as:

```json
{
  "cleanUrls": true,
  "trailingSlash": false
}
```

When SEO is DUE NOW, a spec may include literal `<meta>` examples. When accessibility requires a skip link, it may specify exact placement and markup. When GitHub Pages is a release target, it may define exact workflow/settings and base-path rules.

Those requirements must come from the **current project evidence or deliberate `PROPOSED` decisions**. They are never copied simply because another project's prompt contained them.

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

### Starting a normal small task

Provide the concrete task using `.github/prompts/universal-task.prompt.md`.

A full prompt pack is unnecessary when a small direct edit is safer and clearer.

### Compiling a substantial project prompt only

```text
Prompt Compile:
repo = https://github.com/OWNER/REPO
goal = [desired outcome]
mode = compile_only
```

The compiler should:

1. audit the target source;
2. extract exact architecture, routes, selectors, tokens, functions, breakpoints, workflows and protected behavior when available;
3. distinguish `VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED`;
4. compile the prompt pack;
5. self-review for contradictions and hidden-chat dependencies;
6. stop before implementation.

### Compiling and executing a substantial project

```text
@GitHub use uiux-ai-workspace.

repo = https://github.com/OWNER/REPO
goal = [desired outcome]
mode = compile_then_execute
```

The Factory should:

1. run the normal project intelligence/design stages;
2. compile the five-file prompt pack;
3. validate pack consistency;
4. persist/freeze `02-FULL-BUILD-SPEC.md` and record its SHA-256;
5. make the implementation stage consume that exact spec;
6. make QA/remediation consume that exact spec lineage;
7. invalidate/re-run downstream evidence if the frozen spec changes materially.

## Prompt layering

The intended precedence before compilation is:

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

During implementation after compilation:

```text
LATEST EXPLICIT USER CORRECTION
      ↓
FROZEN 02-FULL-BUILD-SPEC.md
      ↓
PROJECT CONTRACTS / CURRENT SOURCE TRUTH
      ↓
UPSTREAM DESIGN ARTIFACTS
      ↓
INFERENCE / ASSUMPTION
```

Prompt Compiler is a synthesis layer, not permission to invent project facts.

## Evidence-first behavior

The system separates:

- `VERIFIED`;
- `INFERRED`;
- `ASSUMED`;
- `UNKNOWN`;
- `PROPOSED` — deliberate new design/product/architecture decision;
- `N/A_JUSTIFIED` — explicitly not applicable.

A design value selected by the compiler is normally `PROPOSED`, not `ASSUMED`.

A successful generation step, build, or CI check does not automatically prove product quality.

Use evidence appropriate to the claim:

- code → compile/test/runtime evidence;
- UI → rendered/browser evidence;
- visual quality → screenshot/visual review evidence;
- current facts → authoritative current sources;
- deployment → deployment/workflow evidence.

## Root-cause repair

When validation fails:

```text
FAILURE EVIDENCE
      ↓
EARLIEST RESPONSIBLE OWNER
      ↓
INVALIDATE / REPAIR FROM OWNER
      ↓
RERUN DOWNSTREAM WORK
      ↓
REVALIDATE AGAINST FROZEN SPEC
```

Do not repeatedly patch downstream symptoms when the failure originates upstream. Do not weaken QA to force implementation to match a PASS state.

## Maintenance rule

Treat `AGENTS.md` as stable. Evolve project-specific intelligence in project docs, skills, contracts, and compiled specs.

Prompt Compiler schemas may evolve, but global examples must remain examples—not hidden templates.