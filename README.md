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
External AI collaborator / cloud model
→ Factory skills + design contracts
→ target GitHub repository
→ GitHub branch / pull request
→ GitHub Actions runner
→ browser / accessibility / performance / media evidence
→ creative review and root-cause repair
→ merge
```

GitHub Actions owns repeatable execution. `uiux-factory/qa/` provides the cloud-native browser evidence stack using Playwright, axe-core, Lighthouse CI and Sharp.

The Factory can still run directly from the CLI for development and unattended automation. Provider-backed `engine=ai` remains available. For ChatGPT + GitHub collaboration, use `engine=external`: Factory generates governed research/design artifacts and an `external-handoff.json`, then stops without calling an internal provider, generating the deterministic ecommerce fixture, or claiming implementation/QA PASS.

A run with status `handoff_ready` is **not** a completed website. It means the target repository is ready for an external implementation agent to consume the Factory artifacts. Rendered QA must run after the target implementation exists.

## Local development (optional)

From `uiux-factory/`:

```bash
python -m pip install -r requirements-metagpt-core.txt
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
```

For provider-backed visual work when an approved provider is configured:

```bash
python run.py "Design a distinctive ecommerce website" --engine ai --runtime-preset visual-first
```

For an external-brain handoff, provide a design-context JSON with `brain: "external"` plus a target repository contract, then run:

```bash
python run.py "Redesign the target project" \
  --context ./design-context.json \
  --engine external \
  --runtime-preset visual-first
```

Local execution output is written under `uiux-factory/runs/` and `uiux-factory/generated/`, which are ignored by Git. The run lock remains because direct CLI/provider-backed runs may still execute outside GitHub Actions.

The old deterministic ecommerce generator remains available only as an internal regression-fixture path used by existing tests; it is no longer exposed as a production CLI engine.

## Cloud QA

The cloud QA workflow installs and exercises:

- Playwright Test / Chromium for browser evidence;
- `@axe-core/playwright` for automated accessibility checks;
- Lighthouse CI for performance/accessibility/best-practice budgets;
- Sharp for WebP/AVIF media processing smoke tests.

QA evidence is uploaded as GitHub Actions artifacts. Automated checks support, but do not replace, visual/creative review.

### Target-project QA

`Cloud QA Toolchain` can audit the website that actually changed instead of treating the Factory fixture as product evidence.

For `workflow_dispatch`, provide:

- `target_repository` — `owner/name`; blank means this repository;
- `target_ref` — branch/tag/SHA; blank uses the target repository default branch;
- `target_dir` — project root inside that repository;
- `routes` — comma-separated routes such as `/,/about.html,/contact.html`;
- `install_command` — optional dependency install command;
- `build_command` — optional production build command;
- `serve_command` — optional preview command; blank uses static HTTP serving.

When the target repository differs from `uiux-ai-workspace`, the workflow checks it out into an isolated `target-project/` directory before QA. Public repositories can use the workflow token; private cross-repository checkout may require the `UIUX_TARGET_REPO_TOKEN` Actions secret with read access to the target repository.

The workflow executes install/build from the declared target root, starts the preview server, waits until the first declared route responds successfully, then runs Playwright and axe across all declared routes. Lighthouse CI receives all declared routes instead of auditing only the first page.

For local/manual harness use:

```bash
cd uiux-factory/qa
QA_TARGET_DIR=/absolute/path/to/project \
QA_ROUTES=/,/about.html,/contact.html \
QA_INSTALL_COMMAND='npm ci' \
QA_BUILD_COMMAND='npm run build' \
QA_SERVE_COMMAND='npm run preview -- --host 0.0.0.0 --port 4173' \
node scripts/serve-target.mjs
```

The `/fixture/` route remains only a toolchain smoke test. A green fixture run proves the QA stack works; it must never be reported as evidence that an unrelated target website passed QA.

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
9. External-brain runs never invoke an internal provider or claim rendered QA before target implementation exists.
10. Toolchain-smoke fixtures are never used as acceptance evidence for a different project.

## Capability upgrades

See `uiux-factory/docs/AI-CAPABILITY-UPGRADE-SOURCES.md` for the remaining optional capabilities that would improve model routing, vision review, browser observation and evaluation depth.
