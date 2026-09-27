# Prompt Pack Schema

For substantial project work, Prompt Compiler should produce this logical five-file pack.

The pack may be returned inline or saved to a repository/workspace when the user authorizes writes.

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

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

## 02-FULL-BUILD-SPEC.md

Purpose: standalone executable specification.

Use `FULL-BUILD-PROMPT.schema.md` exactly as the structural baseline.

This is the primary deliverable and should contain enough exact repository evidence that a second implementation agent can work without chat history.

## 03-IMPLEMENTATION-PROMPT.md

Purpose: execute the approved specification without reinterpreting it.

Recommended structure:

```text
# [Project] — Implementation Prompt

Use:
- AGENTS.md
- target PROJECT-CONTEXT.md
- approved Design Contract / research output
- 02-FULL-BUILD-SPEC.md
- applicable skills_UIUX only

Authority:
[branch_write / create_pr_only / merge_only / merge_and_deploy]

Implement the approved specification.

Rules:
1. Inspect target source before editing.
2. Preserve every item in IMMUTABLE / DO NOT BREAK at its declared preservation level.
3. Do not reinterpret the visual direction unless implementation evidence reveals a contradiction or blocker.
4. Prefer feature branch → coherent implementation → rendered representative verification → root-cause repair → PR.
5. Avoid unrelated refactors.
6. Keep new behavior isolated from protected core owners where the spec requires isolation.
7. Do not weaken tests to manufacture a PASS.
8. Record any unavoidable deviation from the spec with evidence and rationale.

Implementation sequence:
1. source verification
2. structural changes
3. representative page/route implementation
4. rendered representative review
5. repair
6. full rollout
7. current-phase checks
8. PR / merge / deploy only within authority

Completion report:
- status
- material changes
- verification evidence
- files/artifacts
- remaining risks
```

The implementation prompt should be much shorter than the full build spec; do not duplicate thousands of tokens unnecessarily.

## 04-QA-REMEDIATION-PROMPT.md

Purpose: compare the implementation against project truth and approved specification, then repair root causes.

Use `QA-CONTRACT.schema.md`.

Recommended opening:

```text
Do not redesign from scratch.
Audit the implemented target against:
1. source-of-truth project contracts;
2. protected preserve contract;
3. approved full build spec;
4. rendered visual evidence;
5. declared responsive scope;
6. release authority.

When evidence and implementation disagree, identify the earliest responsible owner, repair there, and rerun downstream validation.
```

## Pack consistency gate

Before returning the pack, verify:

- [ ] Project Context and Full Build Spec use the same goal/scope;
- [ ] Research Prompt does not research questions already VERIFIED unless revalidation is justified;
- [ ] Preserve contract is identical in Build and Implementation prompts;
- [ ] responsive scope is identical across files;
- [ ] release authority is identical across files;
- [ ] QA gates map to actual acceptance criteria in Build Spec;
- [ ] Implementation Prompt does not silently widen scope;
- [ ] no file depends on hidden chat history;
- [ ] proposed facts are labeled as proposed;
- [ ] unknowns remain visible.

## Minimal user invocation

```text
@GitHub use uiux-ai-workspace.

Prompt Compile:
repo = https://github.com/OWNER/REPO
goal = [1–3 sentences]
```

Default behavior for substantial projects:

```text
output = prompt_pack
authority = spec_only
```

The compiler must not implement target code unless the user explicitly changes authority/scope after reviewing or approving the specification.
