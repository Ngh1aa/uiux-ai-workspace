---
name: prompt-compiler
description: Compiles a target repository plus a short product/design goal into an evidence-grounded, project-specific prompt pack or standalone full build specification before implementation. Use when substantial work should be specified first, then implemented and QA'd against the same frozen spec.
---

# Prompt Compiler — Repository-to-Executable-Spec Skill

## Purpose

Turn a target repository plus a short product/design goal into a grounded, implementation-ready prompt pack **before target implementation begins**.

This skill exists so users do **not** need to hand-write giant prompts for every project. It compiles project truth, relevant UIUX Factory rules, research/design artifacts, and task intent into an executable specification that another agent can implement with minimal ambiguity.

`examples/mostar-guide.md` is only a **resolution example** for specificity and preservation discipline. It is not a reusable project template.

Read `SPEC-FIRST-EXECUTION.md` for the compile-before-code execution contract.

## Trigger

Use this skill when the user asks for any of the following:

- "Prompt Compile" / "compile prompt" / "generate full build prompt";
- a detailed project build specification from an existing repository;
- a reusable prompt pack before coding;
- a repository audit that should become a design/engineering contract;
- substantial build/redesign/extension work where the system should compile a detailed spec first and then execute it.

For tiny, obvious edits where a full specification adds no value, normal direct execution is allowed.

## Minimal input

The user should only need to provide:

```text
repo = https://github.com/OWNER/REPOSITORY
goal = 1–3 sentences describing the desired outcome
```

Optional overrides:

```text
preserve = [known protected areas]
change = [known desired changes]
responsive_scope = desktop_only | responsive_all
deployment = GitHub Pages | Vercel | other | UNKNOWN
mode = compile_only | compile_then_execute
authority = spec_only | branch_write | create_pr_only | merge_only | merge_and_deploy
output = full_build_prompt | prompt_pack
```

If optional fields are absent, infer only when evidence supports the inference. Otherwise use `UNKNOWN` or `N/A_JUSTIFIED`.

## Execution modes

### `compile_only`

Use when the user asks only for the prompt/spec or explicitly says not to implement yet.

Pipeline:

```text
AUDIT → COMPILE → CONSISTENCY GATE → RETURN/PERSIST PACK → STOP
```

### `compile_then_execute`

Use for substantial work when the user wants the system to actually build/redesign/extend the project using a spec-first workflow.

Pipeline:

```text
AUDIT / RESEARCH / DESIGN INTELLIGENCE
    ↓
COMPILE PROMPT PACK
    ↓
CONSISTENCY GATE
    ↓
FREEZE 02-FULL-BUILD-SPEC.md
    ↓
IMPLEMENTATION READS FROZEN SPEC
    ↓
RENDERED QA READS SAME SPEC
    ↓
ROOT-CAUSE REPAIR
    ↓
RELEASE WITHIN AUTHORITY
```

Do not require a second user approval message between compile and implementation unless the user requested an approval gate or the compiled spec exposes a blocking UNKNOWN/conflict.

## Mandatory operating sources

Before compiling, read only the relevant current versions of:

1. repository-root `AGENTS.md`;
2. `PROJECT-CONTEXT.md` in the target if present, otherwise use `PROJECT-CONTEXT.template.md` as a schema only;
3. `docs/AI-PROMPT-SYSTEM.md`;
4. `.github/prompts/universal-task.prompt.md`;
5. `checklist-prototype-ui-ux.md` when the target is a visual/UI prototype;
6. `skills_UIUX/LATEST-3-PROMPT-REDESIGN-PIPELINE.md` for substantial redesigns;
7. `skills_UIUX/MASTER-PRE-DESIGN-RESEARCH-PROMPT-V4.2.md` when research is due now;
8. `skills_UIUX/MASTER-PROMPT-V7.2.md` for substantial structural implementation planning;
9. `skills_UIUX/FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.2.md` for QA contracts;
10. `skills_UIUX/PHASE-AWARE-GATING.md` for phase/scope ownership;
11. `skills_UIUX/prompt-compiler/SPEC-FIRST-EXECUTION.md` for spec freeze/consumption rules;
12. other `skills_UIUX` files only when they materially apply.

Do not preload the entire skills corpus merely because it exists.

## Core principle

The compiler must convert **target-project evidence** into **explicit project-specific specification**.

Prefer exact evidence:

```text
normalizeSlider()
--hero-progress
@media (max-width: 640px)
section.checkout-summary
560–1620
```

instead of vague descriptions such as:

```text
the slider logic
the animation
the mobile CSS
the summary section
```

Never invent selectors, functions, routes, assets, breakpoints, metrics, research, or runtime behavior.

## Example isolation rule

No example project may become an implicit source of truth.

Do not copy from Mostar or any other example:

- routes/sitemap;
- file tree;
- selectors/functions;
- assets;
- timings;
- deployment targets;
- SEO copy;
- accessibility markup;
- visual direction;
- section order.

Examples demonstrate how **concrete** a spec can be, not what another project should contain.

## Evidence vocabulary

Every material statement should be classified as one of:

- `VERIFIED` — directly supported by source, runtime, test, tool result, or authoritative source;
- `INFERRED` — reasonable conclusion derived from evidence;
- `ASSUMED` — temporary assumption required to proceed;
- `UNKNOWN` — insufficient evidence;
- `PROPOSED` — new design/product/architecture decision introduced intentionally by the compiler;
- `N/A_JUSTIFIED` — intentionally not applicable to this project/scope.

A deliberate new design value is normally `PROPOSED`, not `ASSUMED`.

Never let `PROPOSED`, `ASSUMED`, or `UNKNOWN` masquerade as current project truth.

## Compilation pipeline

```text
SHORT USER GOAL
    ↓
LOAD OPERATING CONTRACT
    ↓
AUDIT TARGET REPOSITORY
    ↓
EXTRACT PROJECT TRUTH
    ↓
CLASSIFY EVIDENCE
    ↓
IDENTIFY PRESERVE / CHANGE BOUNDARIES
    ↓
LOAD ONLY APPLICABLE UIUX SKILLS
    ↓
DEFINE PRODUCT / UX / VISUAL DIRECTION
    ↓
COMPILE EXECUTABLE SPEC
    ↓
COMPILE IMPLEMENTATION PROMPT
    ↓
COMPILE QA / REMEDIATION PROMPT
    ↓
SELF-CRITIQUE FOR CONTRADICTIONS
    ↓
FREEZE OR RETURN PROMPT PACK
```

## Repository forensic audit

Inspect the target directly before writing the specification. Determine what is applicable from:

- repository structure and canonical implementation root;
- entry points;
- routes/sitemap;
- DOM/component hierarchy;
- CSS architecture and tokens;
- typography, spacing and grid;
- JS modules/functions/state;
- animation engines, timelines and thresholds;
- media/assets and remote URLs;
- APIs/data/schema ownership;
- responsive breakpoints and transformation behavior;
- accessibility behavior;
- SEO/metadata;
- package/build/runtime configuration;
- deployment configuration;
- GitHub Actions;
- current broken links, unfinished sections and missing states;
- fragile or high-coupling areas;
- generated/vendor code;
- areas that must not be modified.

Use `PROJECT-AUDIT.schema.md` as the audit structure.

## Preserve contract

Every substantial compile must produce an explicit:

```text
IMMUTABLE / DO NOT BREAK
```

section containing the exact files, selectors, functions, algorithms, timings, assets, routes, visual signatures, data/API contracts, and working interactions that must survive.

When preservation is requested, distinguish:

- byte-for-byte preservation;
- behavior preservation;
- API/DOM contract preservation;
- visual-DNA preservation;
- content/data preservation.

Do not claim byte-for-byte preservation unless that level is actually required and verifiable.

## Gap contract

For each verified current issue, use:

```text
CURRENT
→ PROBLEM
→ IMPACT
→ PROPOSED RESOLUTION
```

Do not manufacture problems merely to make the prompt longer.

## Product / UX expansion rules

Add only what materially supports the goal:

- routes/pages;
- sitemap/IA;
- critical journeys;
- recovery/alternate paths;
- missing states;
- content hierarchy;
- component behavior;
- navigation relationships;
- portfolio/case-study evidence surfaces when relevant.

A larger website is not automatically a better project.

## Art-direction contract

For visual work, explicitly compile:

- 3 style adjectives;
- visual concept;
- palette/tokens;
- typography;
- grid/spacing;
- image direction;
- icon direction;
- signature motif;
- motion language;
- hover/focus language;
- responsive transformation;
- anti-template rules;
- what must **not** look generic/AI-generated.

Preserve strong existing visual DNA when the task is an extension rather than a redesign.

## Page-role specification

For every material page/route, define when applicable:

```text
PURPOSE
USER GOAL
OWNER GOAL
CONTENT
SECTION ORDER
LAYOUT
COMPONENTS
INTERACTIONS
MOTION
RESPONSIVE BEHAVIOR
ACCESSIBILITY
LINK DESTINATIONS
DEPENDENCIES
```

Do not use lorem ipsum when content is part of the design decision.

## Detail-resolution contract

When a category is applicable, make it **implementation-ready**, not label-only.

### Deployment

Do not write only “deploy to Vercel/GitHub Pages”. Specify applicable exact:

- config path and keys/content;
- framework preset;
- build command;
- output directory;
- base/relative-path rules;
- workflow path/steps;
- Pages source setting;
- environment ownership;
- production verification.

### SEO / metadata

When applicable specify exact:

- title/description ownership;
- OG tags;
- canonical behavior;
- favicon/theme color;
- robots/sitemap;
- structured data when justified.

Use literal markup examples when that removes ambiguity. Label proposed copy `PROPOSED`.

### Accessibility

When applicable specify exact:

- semantic/heading structure;
- skip-link placement;
- focus-visible behavior;
- keyboard/touch behavior;
- aria/name relationships;
- alt/decorative-image rules;
- reduced-motion behavior;
- automated gates.

### QA

Use exact routes, viewport widths, selectors/states, animation checkpoints, console/network expectations and thresholds where applicable.

### Deliverables

Name the exact files/routes/docs/assets/tests/workflows/evidence expected from the milestone.

## Technical contract

The build spec must identify:

- target file tree;
- protected files;
- files allowed to change;
- new files;
- module ownership;
- path/base-path rules;
- dependency/framework restrictions;
- progressive-enhancement rules;
- reduced-motion behavior;
- deployment assumptions;
- source-of-truth ownership.

Prefer isolated extension scopes over contaminating a protected core system.

## Phase-aware rules

Respect `PHASE-AWARE-GATING.md` and `MASTER-PROMPT-V7.2.md`.

Use requirement states:

```text
DONE_VERIFIED
N/A_JUSTIFIED
PENDING_FUTURE_PHASE
BLOCKED
```

Only current-phase requirements participate in the current exit gate.

Do not invent mobile requirements for `desktop_only` work. Do not claim full responsiveness for desktop-only scope.

## QA compilation

Use `QA-CONTRACT.schema.md`.

Acceptance criteria should be binary/verifiable wherever possible.

Bad:

```text
Looks premium.
Animation is smooth.
```

Better:

```text
No horizontal overflow at 390 / 768 / 1440 px.
All declared routes return status < 400.
No serious or critical Axe violations on representative routes.
Existing protected scroll ranges produce the same CSS-variable behavior after extension.
No project-code console errors during the critical journey.
```

A green build alone is not sufficient UI evidence.

## Output modes

### `full_build_prompt`

Return one standalone executable specification using `FULL-BUILD-PROMPT.schema.md`.

### `prompt_pack` (default for substantial projects)

Return the five-file logical pack defined in `PROMPT-PACK.schema.md`:

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

The assistant may present them inline or save them to the target/project workspace when authorized.

## Spec freeze / consumption gate

In `compile_then_execute` mode:

1. persist the prompt pack;
2. run the pack consistency gate;
3. freeze `02-FULL-BUILD-SPEC.md` as the implementation source of truth;
4. record a content hash when runtime support exists;
5. implementation must read that exact artifact before editing target code;
6. QA/repair must evaluate against that exact artifact;
7. material changes to the frozen spec invalidate affected downstream implementation/QA evidence.

## Self-review gate

Before returning or executing a compiled prompt, check for:

- contradictions;
- stale assumptions;
- missing material routes;
- undefined selectors/functions;
- fake facts or fake evidence;
- vague acceptance criteria;
- conflict between Preserve and Can Change;
- deployment/base-path mistakes;
- responsive-scope contradictions;
- future-phase work incorrectly blocking the present phase;
- missing reduced-motion/accessibility handling when applicable;
- label-only deployment/SEO/accessibility sections that need concrete detail;
- vague delivery inventory;
- example-project leakage;
- output that depends on hidden conversation context.

The final spec must be usable by a second capable agent that has access to only:

1. the target repository;
2. the compiled prompt/spec;
3. `uiux-ai-workspace`.

## Default invocation

Compile only:

```text
@GitHub use uiux-ai-workspace.

Prompt Compile:
repo = https://github.com/OWNER/REPOSITORY
goal = [1–3 sentences]
mode = compile_only
```

Compile then execute:

```text
@GitHub use uiux-ai-workspace.

repo = https://github.com/OWNER/REPOSITORY
goal = [1–3 sentences]
mode = compile_then_execute
```

## Non-negotiables

Do not:

- implement target code during a `compile_only` run;
- begin substantial implementation before the compile gate passes in `compile_then_execute` mode;
- paraphrase away protected exact contracts;
- fabricate research/results/metrics;
- force irrelevant skills into the spec;
- treat an example/template as project truth;
- call an unrendered UI visually verified;
- create requirements solely to make the document longer;
- depend on details that exist only in chat history;
- let implementation silently bypass or reinterpret the frozen spec.

Optimize for:

`Grounding → Precision → Executability → Verification → Reusability → Brevity`.