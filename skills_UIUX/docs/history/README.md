# Historical revisions

The working tree keeps only the current canonical prompt set and current V5 architecture guidance. Superseded prompt/architecture documents are intentionally removed from the active root to reduce routing ambiguity and root clutter.

Git history remains the archive. The cleanup baseline before removal is:

`85d53ef90c56b40c6383c2e63e03ac5d2d3ab7d8`

## Current canonical redesign prompt set

- `MASTER-PRE-DESIGN-RESEARCH-PROMPT-V4.2.md`
- `MASTER-PROMPT-V7.2.md`
- `FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.2.md`
- `LATEST-3-PROMPT-REDESIGN-PIPELINE.md`
- `DESIGN-INTELLIGENCE-AUGMENTED-REDESIGN-PROMPT.md`

## Removed superseded prompt revisions

- `MASTER-PRE-DESIGN-RESEARCH-PROMPT-V3.0.md`
- `MASTER-PRE-DESIGN-RESEARCH-PROMPT-V4.0.md`
- `MASTER-PRE-DESIGN-RESEARCH-PROMPT-V4.1.md`
- `MASTER-PROMPT-V4.0.md`
- `MASTER-PROMPT-V5.0.md`
- `MASTER-PROMPT-V6.0.md`
- `MASTER-PROMPT-V7.0.md`
- `MASTER-PROMPT-V7.1.md`
- `FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V2.0.md`
- `FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.0.md`
- `FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.1.md`

## Removed superseded architecture revisions

- `V2-ARCHITECTURE.md`
- `V3-ARCHITECTURE.md`
- `V4-ARCHITECTURE.md`

Backward-compatible profiles/config schemas remain supported. Removing old architecture prose does not remove those runtime/profile contracts.

## Removed non-canonical standalone documents

- `Website-Research-Generation-Architect-Skill.md` — legacy standalone monolith overlapping the current routed skill graph and not a packaged `<skill>/SKILL.md` capability.
- `Mango-Ops-Technical-Proposal.md` — unrelated project-specific proposal, not part of the reusable UI/UX skill library.

To inspect any removed revision, open the file at the cleanup baseline commit above or use normal Git history. Do not restore an old prompt into the active root unless it becomes canonical again through an explicit migration decision.
