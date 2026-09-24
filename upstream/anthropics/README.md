# Anthropic Reference Upstreams

This directory contains pinned Git submodules used as **reference corpora** by UIUX AI Workspace.

They do not become active UIUX Factory runtime dependencies merely by being present here. A local skill, policy or orchestrator must explicitly adapt a pattern before it affects project delivery.

## Repositories

| Repository | Local path | Pinned revision | Intended use |
|---|---|---|---|
| anthropics/claude-code | `upstream/anthropics/claude-code` | `cbab6f4598e975b382507dab4392f61f42dd1b94` | Agentic coding, repo understanding, Git workflow, plugin/agent organization |
| anthropics/claude-cookbooks | `upstream/anthropics/claude-cookbooks` | `c5ff1dc523e28d9b8fbd5c6ecd63204e20b8a0ed` | Tool use, vision, sub-agents, retrieval, eval patterns |
| anthropics/financial-services | `upstream/anthropics/financial-services` | `574ed3624aebd0418c7e96cd101262f30210ab26` | Financial-domain workflow and terminology reference |

`anthropics/skills` is already integrated separately at:

`skills_UIUX/upstream/anthropic-skills`

It stays there because it is the active upstream source for selected skill integrations.

## Usage rule

Project truth and local UIUX skills remain authoritative. Use these repositories to learn patterns, then adapt those patterns into local skills/policies with provenance. Never let a reference repository silently override a project's brief, brand, design contract, accessibility requirements or validated runtime behavior.
