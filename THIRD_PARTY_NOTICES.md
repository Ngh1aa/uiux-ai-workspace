# Third-Party Notices

The project's own work is licensed under Apache-2.0 (code and agent-facing content) and CC BY 4.0
(documentation); see `README.md#licensing`. The components below keep their own licenses. Items
marked **copied** are redistributed in this repository; items marked **submodule** are commit
pointers whose files come from upstream under upstream terms.

| Component | Location | Inclusion | License |
|---|---|---|---|
| UI UX Pro Max (Next Level Builder) | `skills_UIUX/vendor/ui-ux-pro-max/` | copied, commit `314307f` | MIT, © 2024 Next Level Builder |
| `ui-styling` sub-skill | `skills_UIUX/vendor/ui-ux-pro-max/skills/ui-styling/` | copied | Treated as Apache-2.0 (its LICENSE.txt is the Apache text and appears derived from Anthropic canvas-design), although its SKILL.md says MIT |
| Canvas fonts (29 families) | `skills_UIUX/vendor/ui-ux-pro-max/skills/ui-styling/canvas-fonts/` | copied | SIL OFL 1.1, notice file per family; Reserved Font Names include Erica One, Plex, Italiana, Libre Baskerville and Lora |
| Be Vietnam Pro | `design-system/fonts/` | copied (via @fontsource 5.3.0) | SIL OFL 1.1, `OFL.txt` |
| MetaGPT | not in the tree; `uiux-factory/requirements-metagpt.txt` pins `FoundationAgents/MetaGPT@11cdf466` | pip dependency (vendored copy removed 10/2026) | MIT, © 2024 Chenglin Wu |
| anthropics/skills | `skills_UIUX/upstream/anthropic-skills` | submodule | Per skill: Apache-2.0 for the integrated skills; `docx`/`pdf`/`pptx`/`xlsx` source-available (do not copy) |
| motion-primitives-website | `skills_UIUX/upstream/motion-primitives-website` | submodule | MIT declared in README/package.json (no LICENSE file upstream) |
| anthropics/claude-code | `upstream/anthropics/claude-code` | submodule | Proprietary, do not copy |
| anthropics/claude-cookbooks | `upstream/anthropics/claude-cookbooks` | submodule | MIT |
| anthropics/financial-services | `upstream/anthropics/financial-services` | submodule | Apache-2.0 (reported; verify at pinned revision) |

The vendored MetaGPT copy that `main` carried before 10/2026 included example data with third-party
news text marked "All rights reserved"; it is no longer part of the tree.

## Mobile knowledge references

`skills_UIUX/mobile-app-design/data/sources.json` records official Apple/Android/W3C/OWASP guidance and immutable GitHub references for Expo, SwiftUI community guidance, samples, design-system and QA tools. This extension contains original curated instructions and links; it does not vendor upstream skills/scripts, UI kits, fonts, app source or dependencies. Registry entries preserve source, checked date, revision and license/exception boundaries. Publisher/license terms must be checked for the exact file/asset before later copying or installing it. Apple Design Resources remain link-only and are not repackaged for Android. These notices do not select a license for the project-owned Factory source.

## Anthropic Skills

This repository references the public `anthropics/skills` repository as a pinned Git submodule (a commit pointer; the files are fetched from upstream, not copied into this repository) at:

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

The upstream `docx`, `pdf`, `pptx` and `xlsx` skills are **source-available, not open source**: their terms forbid copying, derivative works and redistribution. `doc-coauthoring` carries no license. None of these files are copied into this repository, and they must not be copied or adapted into it.

Local routing, orchestration, verification and VisualCritic integration are implemented outside the submodule and are project-owned modifications; they do not modify the upstream Anthropic files.

## Motion Primitives Website

This repository also references the public `itsjwill/motion-primitives-website` repository as a pinned Git submodule (commit pointer, not copied files) at:

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

License notes (from upstream metadata; re-check the pinned revision before copying anything): `claude-code` is proprietary (all rights reserved, Anthropic Commercial Terms) and must not be copied or redistributed; `claude-cookbooks` is MIT; `financial-services` is reported as Apache-2.0.

For all three repositories, preserve upstream provenance and review the license/terms that apply to the specific upstream files before copying or redistributing source. Local adaptations should live outside the submodules so upstream diffs remain inspectable.
