# Prompt Pack Schema

For substantial project work, Prompt Compiler should produce this logical five-file pack **before implementation begins**.

The pack may be returned inline or saved to a repository/workspace when the user authorizes writes.

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

The pack is project-specific. No example project is a template for another project.

---

## 00-PROJECT-CONTEXT.md

Purpose: concise project truth packet derived from the target repository and user goal.

Must include:

- project identity/type/stage;
- goal and success description;
- users/priority task when evidence supports it;
- source-of-truth paths;
- technology/runtime;
- architecture/entry points;
- Must / Must not / Preserve / Can change;
- responsive scope;
- validation lane;
- deployment model;
- evidence states;
- known issues/unknowns;
- Definition of Done.

Do not copy the entire `PROJECT-CONTEXT.template.md`; fill only material fields.

---

## 01-RESEARCH-PROMPT.md

Purpose: perform only the research/design-intelligence work that can materially change the design direction.

Use when research is due now. Otherwise mark:

```text
N/A_JUSTIFIED — existing project truth/reference direction is sufficient for current compile.
```

Typical structure:

```text
# [Project] — Pre-Design Research Prompt

## Goal
## Known project truth
## Questions that can change the design
## Reference/competitor scope
## What to extract
- layout/composition
- information hierarchy
- typography
- media language
- motion/interaction
- responsive behavior
- signature patterns
- anti-patterns
## ADOPT / ADAPT / REJECT matrix
## Evidence policy
## Required output
```

Do not ask for broad trend research when it cannot change a decision.

---

## 02-FULL-BUILD-SPEC.md

Purpose: standalone executable specification and primary implementation source of truth.

Use `FULL-BUILD-PROMPT.schema.md` as the structural baseline, but tailor the section depth and content to the actual project.

This file must contain enough exact repository evidence and deliberate `PROPOSED` decisions that a second implementation agent can work without chat history.

When applicable, include literal detail such as:

- exact file tree and paths;
- routes/anchors;
- selectors/classes/IDs/functions/state owners;
- tokens and breakpoints;
- content hierarchy and real copy/proposed copy;
- motion timelines/easing/checkpoints;
- config snippets (`vercel.json`, workflow YAML, framework config, etc.);
- SEO/meta markup;
- accessibility markup/keyboard behavior;
- QA commands/checkpoints/thresholds;
- exact delivery inventory.

Do not add irrelevant sections or requirements solely to make the spec long.

### Example-quality rule

A detailed example such as Mostar demonstrates **resolution**, not reusable content.

The compiler should be capable of producing specificity such as:

```text
Create `vercel.json` with these exact keys because this target is a static site.
Add a skip-link as the first body child because the current layered stage traps pointer/focus behavior.
Verify routes X/Y/Z at widths A/B/C.
Deliver these exact files and workflows.
```

But those statements are valid only when supported by the current target's architecture or clearly labelled `PROPOSED`.

---

## 03-IMPLEMENTATION-PROMPT.md

Purpose: execute the frozen approved specification without independently reinterpreting it.

Recommended structure:

```text
# [Project] — Implementation Prompt

Use:
- AGENTS.md
- target PROJECT-CONTEXT.md
- approved research/design artifacts
- 02-FULL-BUILD-SPEC.md
- applicable skills_UIUX only

Authority:
[branch_write / create_pr_only / merge_only / merge_and_deploy]

SPEC-FIRST RULE:
Read `02-FULL-BUILD-SPEC.md` completely before editing target code.
Treat it as the implementation source of truth unless the user's latest explicit correction overrides it.

Implement the approved specification.

Rules:
1. Inspect target source before editing.
2. Preserve every item in IMMUTABLE / DO NOT BREAK at its declared preservation level.
3. Do not reinterpret the visual/product direction in parallel with the frozen spec.
4. Prefer feature branch → coherent implementation → rendered representative verification → root-cause repair → PR.
5. Avoid unrelated refactors.
6. Keep new behavior isolated from protected core owners where the spec requires isolation.
7. Do not weaken tests to manufacture a PASS.
8. Record unavoidable deviations from the spec with evidence and rationale.
9. When the spec names exact files/routes/selectors/functions/configs, verify them against current source before modification.

Implementation sequence:
1. source verification
2. read/freeze spec
3. structural changes
4. representative page/route implementation
5. rendered representative review
6. repair
7. full rollout
8. current-phase checks
9. PR / merge / deploy only within authority

Completion report:
- status
- material changes
- verification evidence
- deviations from spec
- files/artifacts
- remaining risks
```

The implementation prompt should be shorter than the full build spec; it should reference rather than duplicate thousands of tokens.

---

## 04-QA-REMEDIATION-PROMPT.md

Purpose: compare the implementation against project truth and the **same frozen specification**, then repair root causes.

Use `QA-CONTRACT.schema.md`.

Recommended opening:

```text
Do not redesign from scratch.
Audit the implemented target against:
1. source-of-truth project contracts;
2. frozen 02-FULL-BUILD-SPEC.md;
3. protected preserve contract;
4. rendered visual evidence;
5. declared responsive scope;
6. release authority.

When evidence and implementation disagree, identify the earliest responsible owner, repair there, and rerun downstream validation.
Do not weaken QA to make implementation pass.
```

QA criteria must map back to explicit requirements/acceptance criteria in `02-FULL-BUILD-SPEC.md`.

---

## Pack consistency gate

Before returning or executing the pack, verify:

- [ ] Project Context and Full Build Spec use the same goal/scope;
- [ ] Research Prompt does not research questions already VERIFIED unless revalidation is justified;
- [ ] Preserve contract is identical in Build and Implementation prompts;
- [ ] responsive scope is identical across files;
- [ ] release authority is identical across files;
- [ ] QA gates map to actual acceptance criteria in Build Spec;
- [ ] Implementation Prompt explicitly says to read `02-FULL-BUILD-SPEC.md` before editing;
- [ ] Implementation Prompt does not silently widen scope;
- [ ] no file depends on hidden chat history;
- [ ] `PROPOSED` facts remain distinguishable from current truth;
- [ ] unknowns remain visible;
- [ ] example-project facts did not leak into the target project;
- [ ] deployment/SEO/accessibility requirements are included only when applicable and concrete enough to implement.

---

## Execution modes

### `compile_only`

Compile → consistency gate → return/persist pack → STOP.

### `compile_then_execute`

Compile → consistency gate → persist/freeze pack → implementation reads frozen spec → rendered QA reads frozen spec → repair/revalidate → release within authority.

A second user approval message is required only when explicitly requested or when a blocking UNKNOWN/conflict prevents a safe implementation decision.

---

## Minimal user invocation

```text
@GitHub use uiux-ai-workspace.

repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
mode = compile_then_execute
```

For a spec-only task:

```text
Prompt Compile:
repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
mode = compile_only
```

The key invariant is the order:

```text
COMPILE THE PROJECT-SPECIFIC SPEC
→ READ/FREEZE THE SPEC
→ IMPLEMENT
→ QA AGAINST THE SAME SPEC
```