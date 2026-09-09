# Third-Party Notices

## Anthropic Skills

This repository vendors the public `anthropics/skills` repository as a pinned Git submodule at:

`skills_UIUX/upstream/anthropic-skills`

Pinned upstream revision:

`41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`

Upstream repository:

`https://github.com/anthropics/skills`

The UIUX Factory actively integrates these upstream skills:

- `skills/frontend-design`
- `skills/webapp-testing`
- `skills/skill-creator`
- `skills/web-artifacts-builder`

The submodule is intentionally kept unmodified so provenance and upstream diffs remain clear. Each upstream skill carries its own license file. The four integrated skills above are distributed under the Apache License 2.0 in the pinned upstream revision.

Local routing, orchestration, verification and VisualCritic integration are implemented outside the submodule and are project-owned modifications; they do not modify the upstream Anthropic files.
