# V5 Agent Skill Ecosystem Benchmark

Purpose: record the external public sources reviewed while hardening `skills_UIUX` V5. These sources are **benchmark inputs**, not project source-of-truth and not content to copy verbatim.

Checked: 2026-08-31.

## 1. Anthropic / Claude official plugin ecosystem

Sources reviewed:

- https://github.com/anthropics/claude-plugins-official/blob/main/plugins/claude-code-setup/skills/claude-automation-recommender/references/skills-reference.md
- https://github.com/anthropics/claude-plugins-official/blob/main/plugins/claude-code-setup/README.md
- https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/README.md
- https://github.com/anthropics/claude-plugins-official/blob/main/plugins/plugin-dev/skills/hook-development/SKILL.md

Useful patterns:

- skills as packaged expertise with workflows + references + examples/scripts;
- progressive disclosure rather than one monolithic context;
- explicit invocation controls/tool restrictions where the agent platform supports them;
- hooks for recurring enforcement such as formatting, linting or completion validation;
- specialized subagents/reviewers for security/performance/accessibility when appropriate;
- frontend craft should be distinctive/context-specific rather than generic AI aesthetics.

Adaptation in this repo:

- `MASTER-PROMPT-V5.0.md` becomes a lean orchestrator;
- specialist details remain in `SKILL.md` and progressive resources;
- `adaptive-skill-routing-and-context-budget` remains the routing authority;
- V5 does not hardcode Claude-only metadata into provider-neutral skills unless the consumer environment supports it.

## 2. obra/superpowers

Sources reviewed:

- https://github.com/obra/superpowers
- https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md

Useful patterns:

- plan before substantial implementation;
- isolate risky work in a branch/worktree when available;
- independently verifiable task boundaries;
- verification before completion;
- review spec compliance separately from code quality;
- preserve evidence that the change actually works.

Adaptation in this repo:

- planning is **proportional to risk**; tiny UI fixes do not need heavyweight plans;
- `ai-agent-coding-guardrails` adds task ownership/dependencies/verification;
- `code-review-and-release` uses two-stage review;
- isolation is preferred when useful, not mandatory for every task;
- V5 does not require one specific TDD methodology for all website/UI work.

## 3. Vercel agent-skills / Web Interface Guidelines

Sources reviewed:

- https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md
- https://github.com/vercel-labs/agent-skills

Useful patterns:

- fetch current guidelines rather than rely on stale embedded rules;
- audit actual files/code rather than only provide generic advice;
- report concrete findings tied to affected source/surface;
- combine accessibility, forms, animation, typography, images and performance rules in UI review.

Adaptation in this repo:

- V5 adds `Fresh-standard review` for time-sensitive guidance;
- project truth and domain context still outrank generic web rules;
- the repo does not require Vercel-specific output/tooling.

## 4. OWASP ASVS / Cheat Sheet practice

Sources reviewed:

- https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/
- https://cheatsheetseries.owasp.org/IndexASVS.html

Useful patterns:

- security requirements and verification need explicit scope/rigor;
- architecture, authentication, session, access control, validation/encoding, data protection, APIs, files and configuration are separate concerns;
- verification level should match application consequence/risk.

Adaptation in this repo:

- `security-and-privacy` moves from a universal header/regex checklist to risk + trust-boundary reasoning;
- current OWASP guidance should be fetched when exact implementation requirements matter;
- checklist completion cannot justify a blanket `secure/compliant` claim.

## 5. W3C/WAI WCAG-EM

Source family:

- https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/

Useful pattern:

- formal conformance needs explicit scope, representative samples/complete processes, appropriate evaluation methods and limitations.

Adaptation:

- existing `accessibility-conformance-evaluation` remains the authority for formal claims;
- V5 keeps automated baseline review separate from manual/AT/conformance evidence.

## 6. GOV.UK Service Manual

Sources reviewed:

- https://www.gov.uk/service-manual/user-research/start-by-learning-user-needs
- https://www.gov.uk/service-manual/measuring-success/how-to-set-performance-metrics-for-your-service
- https://www.gov.uk/service-manual/service-standard/point-10-define-success-publish-performance-data

Useful patterns:

- user needs should be evidence-based and revisited throughout delivery;
- service purpose should drive metrics;
- performance data and user research should be combined;
- success definition belongs early, not only post-launch.

Adaptation:

- V5 keeps owner goal ↔ user intent and evidence hierarchy central;
- `journey-outcome-and-service-health` and analytics remain linked to real service outcomes.

## 7. web.dev performance budget practice

Sources reviewed:

- https://web.dev/articles/performance-budgets-101
- https://web.dev/articles/use-lighthouse-for-performance-budgets

Useful patterns:

- define performance limits intentionally;
- use resource/metric budgets to prevent regressions;
- lab tools are useful but field data is needed to understand real users.

Adaptation:

- `web-quality-and-performance` removes universal one-size-fits-all resource/Lighthouse gates;
- budgets are route/project-specific and reported as approved/proposed;
- lab vs field evidence is explicit.

## What V5 intentionally did NOT copy

- vendor-specific skill metadata as universal schema;
- mandatory subagents/worktrees/TDD for every task;
- fixed Lighthouse score as universal release truth;
- one external design guideline as project source-of-truth;
- award-site popularity as UX evidence;
- security/header snippets without architecture/risk context.

## Resulting V5 principles

1. **Progressive disclosure over mega-context.**
2. **Project truth over generic best practice.**
3. **Evidence and exact claim discipline.**
4. **Reference principles, not surface copying.**
5. **Rendered UI is not system reality.**
6. **Planning and isolation proportional to risk.**
7. **Every material change has a verification contract.**
8. **Spec compliance and code/experience quality are separate review gates.**
9. **Performance uses budgets and lab/field distinction.**
10. **Security/accessibility/reliability claims require methods matching the claim.**
11. **Release needs safe rollback + post-deploy smoke.**
12. **Production feedback becomes research/tests/regression learning.**
