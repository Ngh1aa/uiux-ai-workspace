# Repository Structure Cleanup Audit

Checked: 2026-09-06 (Asia/Ho_Chi_Minh)

## Phase classification

- Scope: `system`
- Type: `release / post-release verification`
- Risk: `medium`
- Mode: `production`
- Cleanup baseline: `85d53ef90c56b40c6383c2e63e03ac5d2d3ab7d8`
- Upstream UI UX Pro Max comparison ref: `314307f156aeab0c6b567bbaa1ce4e7aabd5a636`
- Cleanup branch: `chore/reorganize-clean-repo-structure`
- PR: `#13`
- Merge commit: `22ddd2ed3352316495bef7b56467caad218cb900`
- Release authorization: `explicitly authorized by user on 2026-09-06`

## Skill Activation Plan

| Task | Trigger/risk | Skill | Expected impact | Verification |
|---|---|---|---|---|
| Preserve source truth while cleaning | system-level repository change | `project-context` | avoid deleting runtime/project truth by filename guess | inspect current main + canonical docs |
| Keep context/routing lean | root/version-history clutter | `adaptive-skill-routing-and-context-budget` | reduce ambiguous active prompt surface | current canonical entrypoints remain unique |
| Remove overlap safely | skill-library maintenance | `skill-authoring-and-governance` | remove legacy/duplicate capability prose without deleting real skill packages | SKILL structure + V5 validation |
| Preserve lifecycle contracts | prompt/governance cleanup | `website-delivery-pipeline` | keep phase-aware canonical pipeline intact | latest pipeline + eval/install smoke |
| Release safely | explicit merge request | `code-review-and-release` | verify exact PR head/base, merge safely and run post-merge gate | PR-head + main post-merge Actions |

## Findings

### FACT — vendor snapshot is correctly separated and unchanged

The local vendor remains split into:

- `vendor/ui-ux-pro-max/skills` = upstream `.claude/skills` tree;
- `vendor/ui-ux-pro-max/engine` = upstream `src/ui-ux-pro-max` tree.

Tree hashes remain:

- skills: `a23882a2d113b30e94adb8a5d3fc35bbc690591e`;
- engine: `a393798fc862de6176d0c3422c16e0dfa3425821`.

Decision: **KEEP VERBATIM**. Cleanup did not rewrite, deduplicate or reorganize files inside the vendor snapshot.

### FACT — active root contained superseded prompt history

The cleanup baseline contained multiple generations of the same three prompt families. Current canonical orchestration names only:

- `MASTER-PRE-DESIGN-RESEARCH-PROMPT-V4.2.md`;
- `MASTER-PROMPT-V7.2.md`;
- `FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.2.md`.

Decision: superseded revisions were removed from the working tree. Git history remains the historical archive.

### DRIFT/WARNING — README pointed at an obsolete implementation prompt

The pre-cleanup README described `MASTER-PROMPT-V5.0.md` as a master orchestrator while the canonical latest redesign pipeline uses `MASTER-PROMPT-V7.2.md` for implementation and `LATEST-3-PROMPT-REDESIGN-PIPELINE.md` for orchestration.

Decision: README now distinguishes library V5 from prompt versions and names only current canonical entrypoints.

### IMPROVEMENT — local repository lacked a root `.gitignore`

The upstream comparison repo ignores common OS, Python cache, editor, dependency, build, test and environment artifacts. This repository previously had no root `.gitignore`.

Decision: add a conservative root `.gitignore` without ignoring the vendored runtime.

### FACT — unrelated/legacy standalone documents were present in root

- `Mango-Ops-Technical-Proposal.md` was project-specific and unrelated to this reusable UI/UX skill library.
- `Website-Research-Generation-Architect-Skill.md` was a legacy standalone monolith, not a packaged `<skill>/SKILL.md`, and overlapped current routed capabilities.

Decision: both were removed from the active working tree. Their prior content remains available in Git history.

### FACT — historical architecture prose is not a runtime compatibility contract

`V2-ARCHITECTURE.md`, `V3-ARCHITECTURE.md` and `V4-ARCHITECTURE.md` described superseded architecture generations. Backward-compatible profiles/config schemas remain implemented elsewhere.

Decision: remove historical prose files from the active root while keeping `V5-ARCHITECTURE.md` canonical.

## Upstream comparison

Useful organization principles adopted from `nextlevelbuilder/ui-ux-pro-max-skill`:

1. keep skills/runtime in explicit source boundaries instead of mixing generated/runtime data with root documentation;
2. maintain a root `.gitignore` for common generated artifacts;
3. treat `.claude/skills` as skill source and `src/ui-ux-pro-max` as searchable runtime/data source;
4. do not copy upstream repository-maintenance/plugin metadata into the local vendor runtime unless required by the local consumer contract.

Not copied blindly:

- upstream CLI/package/release/plugin repository structure is specific to its npm/plugin distribution model;
- `skills_UIUX` intentionally keeps local skill folders at root because profiles/installers/validators resolve `<skill>/SKILL.md` there.

## Cleanup actions

### KEEP

- all root `<skill>/SKILL.md` packages;
- `README.md`, `SKILL-CATALOG.md`;
- current canonical prompt trio + latest pipeline;
- phase-aware governance docs;
- `V5-ARCHITECTURE.md` and `V5-RELEASE-NOTES.md`;
- `profiles/`, `packs/`, `evals/`, `scripts/`, `examples/`, `.github/`;
- entire `vendor/ui-ux-pro-max/` snapshot unchanged.

### REMOVED FROM ACTIVE WORKING TREE

- superseded Prompt 1/2/3 versions listed in `docs/history/README.md`;
- `V2-ARCHITECTURE.md`, `V3-ARCHITECTURE.md`, `V4-ARCHITECTURE.md`;
- `Website-Research-Generation-Architect-Skill.md`;
- `Mango-Ops-Technical-Proposal.md`.

### ADDED / UPDATED

- `.gitignore`;
- canonical-focused `README.md`;
- `docs/history/README.md`;
- cleanup/version-lock/phase-state evidence.

## Verification evidence

Cleanup implementation commit: `621f9cad95b495916d0bbaaca81a37226f4cdc98`.

Pre-merge verification:

- `main` still matched cleanup base `85d53ef90c56b40c6383c2e63e03ac5d2d3ab7d8`;
- PR #13 head = `a0bef3018655a1a08d2d1457ad57764221e1aea9`;
- PR #13 = `mergeable=true`;
- exact-head `Validate Skills` run `34024108520` = `success`.

Release:

- PR #13 merged with expected-head guard;
- merge commit = `22ddd2ed3352316495bef7b56467caad218cb900`.

Post-merge verification:

- `main` resolves to `22ddd2ed3352316495bef7b56467caad218cb900`;
- `Validate Skills` run `34024255317` = `success`;
- structure, V5 profiles/packs/project configs/eval/resources, vendor integrity, source retrieval, core installer, installed consumer dependency, project-aware installer, bootstrap/sync and eval-harness smoke all passed.

## Skill usage evidence

| Skill | Trigger | Requirement applied | Change created | Verification | Evidence |
|---|---|---|---|---|---|
| `project-context` | system cleanup | source truth before edit | preserved canonical/runtime boundaries | source/tree inspection | cleanup baseline + current tree |
| `adaptive-skill-routing-and-context-budget` | version-history clutter | smallest active routing surface | removed superseded active prompt revisions | canonical root inspection | current prompt trio only |
| `skill-authoring-and-governance` | library maintenance | avoid duplicate/legacy capability surface | removed standalone legacy monolith, preserved real SKILL packages | structural validator | Actions success |
| `website-delivery-pipeline` | lifecycle continuity | phase-aware handoff and verification | maintained canonical pipeline/governance docs | V5/install/eval gates | Actions success |
| `code-review-and-release` | explicit release request | exact scope/head/base, non-destructive merge, post-release verification | merged PR #13 via merge commit | pre-merge and post-merge Actions | runs `34024108520`, `34024255317` |

## Requirement coverage

| ID | Requirement | OWNER_PHASE | Status | Verification |
|---|---|---|---|---|
| CLEAN-001 | Compare repository structure with current pinned upstream | audit | DONE_VERIFIED | upstream/local branch + tree inspection |
| CLEAN-002 | Preserve complete UI UX Pro Max vendor skills/runtime | remediation | DONE_VERIFIED | post-change tree hashes unchanged |
| CLEAN-003 | Remove clearly superseded prompt revisions | remediation | DONE_VERIFIED | active root contains only canonical prompt revisions |
| CLEAN-004 | Remove unrelated/legacy standalone root documents | remediation | DONE_VERIFIED | commit diff/path absence |
| CLEAN-005 | Reduce generated-artifact risk | remediation | DONE_VERIFIED | root `.gitignore` added |
| CLEAN-006 | Preserve skill/profile/install/eval behavior | verification | DONE_VERIFIED | pre/post merge Actions success |
| CLEAN-007 | Merge cleanup to `main` | release | DONE_VERIFIED | PR #13 merged as `22ddd2ed3352316495bef7b56467caad218cb900` |
| CLEAN-008 | Verify released `main` | post-release verification | DONE_VERIFIED | Actions run `34024255317` = success |

## Phase result

`PASSED`

No runtime BUG/BLOCKER was introduced by cleanup or release. The repository cleanup is merged and post-merge verification is complete.
