# Cleanup candidates

Candidates are removed only after repository-wide search shows they are not required by the active cloud-first path.

Initial candidates:
- local Workbench UI (`apps/web`)
- localhost bridge server (`apps/bridge`)
- free-tier provider router and its checks/docs
- local preview/job queue/run-lock surfaces that only support Workbench execution
- Workbench-only workflows/docs

Keep unless proven replaceable:
- `skills_UIUX`
- active `uiux-factory/core` contracts/skills/orchestration/verification/evidence
- MetaGPT integration
- runtime presets
- BrowserQA/VisualCritic/Repair/quality loop
