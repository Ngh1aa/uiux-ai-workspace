# UIUX AI Workspace

This repository contains the active **UIUX Factory** application, its UI/UX skill library, and the vendored framework/runtime dependencies required by the Factory.

## Source of truth

The actively developed product lives in:

```text
uiux-factory/
```

Use that directory for runtime, pipeline, agents, contracts, Workbench, bridge, generation, QA and repair changes.

Key entry points:

```text
uiux-factory/run.py
uiux-factory/core/manager/development_manager.py
uiux-factory/apps/bridge/server.py
uiux-factory/apps/web/server.py
```

## Active top-level surfaces

- `uiux-factory/` — canonical application/runtime source.
- `skills_UIUX/` — shared UI/UX skill knowledge and website-delivery policy used by the Factory.
- `MetaGPT/` — vendored MetaGPT framework source. Treat it as framework/vendor code unless an integration change specifically requires modifying it.
- `scripts/` — repository-level migration/utility scripts.
- `docs/` — repository-level operating/prompt documentation.
- `AGENTS.md` — repository operating contract.
- `PROJECT-CONTEXT.template.md` — reusable project-context template.

The previous top-level `core/` prototype and standalone `showcase/` output were removed from the active repository surface. The only canonical `core` implementation is now `uiux-factory/core/`.

## Local runtime safety

Runtime output is written under `uiux-factory/runs/` and `uiux-factory/generated/`; both directories are ignored by Git.

`run.json` is persisted through a temporary file plus atomic replacement so Workbench polling does not observe partially-written JSON.

Expensive Factory runs are serialized by a local cross-process run lock. This prevents repeated Workbench submissions from running multiple Playwright/MetaGPT pipelines simultaneously on the same machine while the bridge still uses its lightweight local job model. Waiting jobs remain subprocesses for now, so a later bridge refactor can replace this with a persistent bounded executor without changing pipeline semantics.

The lock defaults can be tuned with:

```text
UIUX_RUN_LOCK_TIMEOUT_SECONDS=7200
UIUX_RUN_LOCK_STALE_SECONDS=14400
```

Generated frontend previews are treated as untrusted content: the Workbench iframe permits scripts but does not grant same-origin privileges, and the previous unsandboxed “open preview in a new tab” path has been removed.

## Development

From `uiux-factory/`:

```bash
python -m pip install -r requirements-metagpt-core.txt
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
python run.py "Design a modern ecommerce website"
```

For visual-first website work, prefer the AI engine plus the visual runtime preset when a configured provider is available:

```bash
python run.py "Design a distinctive ecommerce website" --engine ai --runtime-preset visual-first
```

## Change policy

Before expanding the AI/design pipeline, keep these invariants green:

1. Python and Workbench JavaScript source compile/parse successfully.
2. Foundation tests pass.
3. `run.json` remains valid throughout a run.
4. Generated files cannot escape the generated project root.
5. Generated preview content remains sandboxed from Workbench privileges.
6. Local expensive Factory runs cannot execute concurrently by accident.
7. Changes to MetaGPT/vendor code are isolated and intentional.

GitHub Actions runs these foundation checks for changes under `uiux-factory/`.

## Capability upgrades

See `uiux-factory/docs/AI-CAPABILITY-UPGRADE-SOURCES.md` for the external capabilities and source material that would most improve the Factory's ability to use its routed skills, browser evidence and creative-review loop at full strength.
