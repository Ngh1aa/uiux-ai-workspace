# UIUX AI Workspace

UIUX Factory is a design-engineering operating system for moving a goal from **project truth → research/design decisions → implementation → rendered verification → repair → handoff/release** without treating model self-report as evidence.

## Start here

For a human or external AI collaborator, read **`START-HERE.md` first**. Do not preload the whole repository.

Normative ownership is defined in `docs/CONTRACT-OWNERSHIP.md`:

- `AGENTS.md` — universal operating/evidence contract;
- `skills_UIUX/runtime/runtime-policy.json` — authority, tools, sandbox, provider and release policy;
- `uiux-factory/core/runtime/flow_os/task_context.py` — natural-language Task Contract;
- `skills_UIUX/flows/*.json` + canonical Flow OS runtime — stage/skill/gate/replanning decisions;
- `skills_UIUX/<skill>/SKILL.md` — specialist capability knowledge;
- target-project source/runtime/tests — project truth and acceptance evidence.

## One-command external collaborator mode

Use this when ChatGPT, Codex, Claude, another cloud model, or a GitHub-connected agent will perform the target-repository work instead of an internal Factory provider:

```bash
python -B skills_UIUX/scripts/prepare-external-task.py \
  --repository owner/repo \
  --task "Redesign the portfolio toward Product Designer and make AI workflow evidence inspectable" \
  --authority branch_write \
  --qa-route / \
  --output external-task-manifest.json
```

The command compiles the natural-language goal into:

- Task Contract + effective authority;
- resolved Flow;
- ordered stages;
- active skills and exact `SKILL.md` paths;
- gate-derived acceptance criteria;
- optional QA routes;
- research packet when evidence-led validation is required;
- explicit evidence/claim boundaries.

The initial status is always `READY_FOR_EXTERNAL_COLLABORATOR`. A generated manifest **never means implementation or QA passed**. The collaborator must still audit the target repository, work within authority, verify the actual changed target, repair failures and attach evidence.

Machine-readable context loading profiles live in `skills_UIUX/runtime/context-routing.json`.

## Portfolio / career positioning

Broad portfolio builds, rebuilds and role-positioning upgrades now have a dedicated `portfolio-career-system` Flow. It treats the portfolio as a recruiter-facing product and checks:

- primary target role and scan hierarchy;
- public identity/GitHub/CV consistency;
- flagship/supporting case routes;
- case-study product reasoning and evidence classes;
- inspectable AI-assisted workflow proof;
- technical/framework claims against source;
- link/CV/source hygiene;
- desktop/mobile rendered recruiter paths;
- user-research and outcome gaps without fabricated evidence.

Narrow portfolio edits such as “fix this hero/card” still route to focused UI flows instead of invoking the full career system.

## Real-user evidence pipeline

Evidence-led work can use `research-evidence-pipeline` together with the existing validation/planning/synthesis skills. It provides reusable templates for:

- decision-mapped research plans;
- participant screeners;
- interview guides;
- usability-test scripts;
- traceable JSONL evidence ledger records;
- findings and decision logs.

If participants are unavailable, the correct result is a runnable plan marked `PLANNED_VALIDATION` or `BLOCKED_USER_EVIDENCE` — never fictional participants, quotes, counts, percentages or findings.

## Canonical product source

The Factory runtime lives in:

```text
uiux-factory/
```

Key surfaces:

```text
uiux-factory/run.py
uiux-factory/core/runtime/flow_os/
uiux-factory/core/manager/development_manager.py
uiux-factory/core/
uiux-factory/qa/
skills_UIUX/flows/
skills_UIUX/runtime/runtime-policy.json
.github/workflows/uiux-factory-ci.yml
.github/workflows/cloud-qa-toolchain.yml
```

Active top-level surfaces:

- `uiux-factory/` — canonical Factory runtime and cloud QA harness;
- `skills_UIUX/` — shared UI/UX skills, flows and runtime policy;
- `upstream/anthropics/` — pinned reference repositories; reference-only unless intentionally adapted;
- `MetaGPT/` — vendored framework source; modify only for intentional framework integration;
- `scripts/` — active repository utilities/migrations;
- `docs/` — operating and architecture documentation;
- `AGENTS.md` — universal operating contract;
- `PROJECT-CONTEXT.template.md` — reusable project-context template.

Historical backup copies are not active source and should not live beside canonical runtime files.

## Cloud-first collaboration

Preferred model:

```text
User goal
→ Task Contract
→ resolved Flow + active-stage skills
→ external AI collaborator / managed provider
→ target GitHub branch
→ implementation
→ GitHub Actions / target browser evidence
→ accessibility / performance / media / creative review
→ root-cause repair
→ pull request
→ merge/release within authority
```

GitHub Actions owns repeatable execution. `uiux-factory/qa/` provides Playwright/Chromium, axe-core, Lighthouse CI and Sharp-based evidence.

The older direct `uiux-factory/run.py --engine external` handoff remains supported for Factory-pipeline runs. `skills_UIUX/scripts/prepare-external-task.py` is the lightweight route when the external collaborator needs a governed manifest without running the full generation pipeline.

## Managed Flow OS CLI

For local/provider-managed execution from the repository root:

```bash
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Redesign a B2B fintech settlement product" \
  --authority branch_write
```

Explicit project-truth overrides are available when inference should not decide:

```bash
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../my-site \
  --managed \
  --task "Redesign the product" \
  --website-type saas \
  --domain financial-services \
  --product-archetype payments-infrastructure \
  --validation-lane production-learning \
  --mode production-candidate \
  --authority branch_write
```

See `skills_UIUX/FLOW-AGENT-OS.md` for lifecycle, provider, approval and replanning commands.

## Local development

From `uiux-factory/`:

```bash
python -m pip install -r requirements-metagpt-core.txt
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
```

Provider-backed direct pipeline work remains available when an approved provider is configured:

```bash
python run.py "Design a distinctive ecommerce website" --engine ai --runtime-preset visual-first
```

## Cloud QA

`Cloud QA Toolchain` can audit the website that actually changed. For `workflow_dispatch` provide the target repository/ref/root, routes and optional install/build/serve commands.

The workflow:

1. checks out the declared target in isolation;
2. runs declared install/build steps;
3. starts the preview server;
4. waits for target routes;
5. runs Playwright + axe on declared routes;
6. runs Lighthouse against the declared target URLs;
7. uploads QA artifacts.

The internal `/fixture/` is only a toolchain smoke test. A green fixture never proves another target website passed QA.

For local/manual target harness use:

```bash
cd uiux-factory/qa
QA_TARGET_DIR=/absolute/path/to/project \
QA_ROUTES=/,/about.html,/contact.html \
QA_INSTALL_COMMAND='npm ci' \
QA_BUILD_COMMAND='npm run build' \
QA_SERVE_COMMAND='npm run preview -- --host 0.0.0.0 --port 4173' \
node scripts/serve-target.mjs
```

## Change invariants

Keep these green before expanding the pipeline:

1. active Python source compiles;
2. foundation tests pass;
3. pinned skills/corpora verify;
4. generated files cannot escape their owned root;
5. cloud browser/a11y/performance/media QA remains executable;
6. evidence/run artifacts stay truthful and inspectable;
7. vendor/framework changes stay isolated and intentional;
8. external-brain/manifests never claim rendered QA before target implementation exists;
9. fixture evidence is never substituted for target evidence;
10. authority never escalates implicitly;
11. missing direct-user evidence remains planned, blocked or unknown rather than invented.

## Capability upgrades

See `uiux-factory/docs/AI-CAPABILITY-UPGRADE-SOURCES.md` for optional future improvements to model routing, vision review, browser observation and evaluation depth.
