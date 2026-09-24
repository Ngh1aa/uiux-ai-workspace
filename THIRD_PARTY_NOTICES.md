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

## Motion Primitives Website

This repository also vendors the public `itsjwill/motion-primitives-website` repository as a pinned Git submodule at:

`skills_UIUX/upstream/motion-primitives-website`

Pinned upstream revision:

`6ff894dee5afd29d1bebe234e61637786d553f31`

Upstream repository:

`https://github.com/itsjwill/motion-primitives-website`

The UIUX Factory uses this upstream repository as a **motion/component intelligence corpus**. Local orchestration, candidate retrieval, adoption rules, reduced-motion requirements and project adaptation live outside the submodule in:

- `skills_UIUX/motion-component-intelligence/`
- `uiux-factory/core/orchestration/motion_component_intelligence.py`

The upstream source is intentionally kept unmodified so provenance, updates and diffs remain clear. At the pinned revision, the upstream README and `package.json` declare MIT licensing and `CONTRIBUTING.md` states contributions are MIT licensed. GitHub repository metadata does not expose a detected license and the root listing does not contain a standalone `LICENSE` file at that revision. Keep provenance intact and perform any additional license review required before redistributing copied source outside project use.

The Factory does not treat Motion Primitives as a canonical design system or automatic template source. Components are shortlisted and adapted only after project truth, art direction, stack compatibility, accessibility, performance and responsive constraints are established.

## Anthropic Reference Upstreams

The following public Anthropic repositories are tracked as pinned Git submodules under `upstream/anthropics/`. They are reference corpora, not automatic runtime dependencies of UIUX Factory.

### Claude Code

Path:

`upstream/anthropics/claude-code`

Pinned upstream revision:

`cbab6f4598e975b382507dab4392f61f42dd1b94`

Upstream repository:

`https://github.com/anthropics/claude-code`

Intended local use: study agentic coding, repository understanding, Git workflow and plugin/agent organization patterns. Do not treat upstream source as a UI design system.

### Claude Cookbooks

Path:

`upstream/anthropics/claude-cookbooks`

Pinned upstream revision:

`c5ff1dc523e28d9b8fbd5c6ecd63204e20b8a0ed`

Upstream repository:

`https://github.com/anthropics/claude-cookbooks`

Intended local use: reference patterns for tool use, multimodal/vision workflows, sub-agents, retrieval and evaluation. Do not automatically import cookbook code into production paths.

### Financial Services

Path:

`upstream/anthropics/financial-services`

Pinned upstream revision:

`574ed3624aebd0418c7e96cd101262f30210ab26`

Upstream repository:

`https://github.com/anthropics/financial-services`

Intended local use: finance-domain terminology, workflow decomposition, skills/agent structure and human-review patterns. It is not a source of visual style rules and does not replace project-specific product research.

For all three repositories, preserve upstream provenance and review the license/terms that apply to the specific upstream files before copying or redistributing source. Local adaptations should live outside the submodules so upstream diffs remain inspectable.
