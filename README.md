# UIUX AI Workspace

This repository contains the active **UIUX Factory** design-engineering harness, its UI/UX skill library, and the framework/runtime dependencies used by the Factory.

## Source of truth

The canonical product source lives in:

```text
uiux-factory/
```

Use that directory for design intelligence, agents, contracts, skill routing, orchestration, generation, verification, evidence and repair.

Key surfaces:

```text
uiux-factory/run.py
uiux-factory/core/manager/development_manager.py
uiux-factory/core/
uiux-factory/qa/
.github/workflows/uiux-factory-ci.yml
.github/workflows/cloud-qa-toolchain.yml
```

## Active top-level surfaces

- `uiux-factory/` — canonical Factory runtime and cloud QA harness.
- `skills_UIUX/` — shared UI/UX skills and website-delivery policies.
- `MetaGPT/` — vendored MetaGPT framework source; modify only for intentional framework integration work.
- `scripts/` — repository-level utilities/migrations that still have an active owner.
- `docs/` — repository-level operating/prompt documentation.
- `AGENTS.md` — repository operating contract.
- `PROJECT-CONTEXT.template.md` — reusable project-context template.

The old top-level `core/` prototype, standalone `showcase/`, local Workbench UI and localhost Workbench bridge have been removed. The only canonical `core` implementation is `uiux-factory/core/`.

## Cloud-first collaboration

The preferred operating model does not require a powerful local LLM or a local Workbench:

```text
AI collaborator
→ GitHub branch / pull request
→ GitHub Actions runner
→ browser / accessibility / performance / media evidence
→ review and root-cause repair
→ merge
```

GitHub Actions owns repeatable execution. `uiux-factory/qa/` provides the cloud-native browser evidence stack using Playwright, axe-core, Lighthouse CI and Sharp.

The Factory can still run directly from the CLI for development and unattended automation. `engine=ai` remains an optional provider-backed mode; it is not required for ChatGPT + GitHub collaboration.

## Local development (optional)

From `uiux-factory/`:

```bash
python -m pip install -r requirements-metagpt-core.txt
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
python run.py "Design a modern ecommerce website"
```

For provider-backed visual work when an approved provider is configured:

```bash
python run.py "Design a distinctive ecommerce website" --engine ai --runtime-preset visual-first
```

Local execution output is written under `uiux-factory/runs/` and `uiux-factory/generated/`, which are ignored by Git. The run lock remains because direct CLI/provider-backed runs may still execute outside GitHub Actions.

## Cloud QA

The cloud QA workflow installs and exercises:

- Playwright Test / Chromium for browser evidence;
- `@axe-core/playwright` for automated accessibility checks;
- Lighthouse CI for performance/accessibility/best-practice budgets;
- Sharp for WebP/AVIF media processing smoke tests.

QA evidence is uploaded as GitHub Actions artifacts. Automated checks support, but do not replace, visual/creative review.

## Change policy

Before expanding the design pipeline, keep these invariants green:

1. Active Python source compiles.
2. Foundation tests pass.
3. Pinned skills verify successfully.
4. Generated files cannot escape the generated project root.
5. Cloud browser/a11y/performance/media QA remains executable on the GitHub runner.
6. `run.json` and evidence artifacts remain truthful and inspectable.
7. Changes to MetaGPT/vendor code are isolated and intentional.
8. Removed local UI/server surfaces are not reintroduced merely to satisfy obsolete tests.

## Capability upgrades

See `uiux-factory/docs/AI-CAPABILITY-UPGRADE-SOURCES.md` for the remaining optional capabilities that would improve model routing, vision review, browser observation and evaluation depth.
