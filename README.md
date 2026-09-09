# UIUX AI Workspace

This repository contains the active **UIUX Factory** application together with vendored/legacy code used during its development.

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

## Other top-level directories

- `MetaGPT/` — vendored MetaGPT framework source. Treat it as framework/vendor code unless an integration change specifically requires modifying it.
- `core/` — legacy/prototype implementation kept for historical reference. New product code must not depend on this top-level package.
- `skills_UIUX/` — shared UI/UX skill knowledge used by the Factory integration.
- `scripts/` — repository-level migration/utility scripts.

Because both the repository root and `uiux-factory/` contain a directory named `core`, always run application commands from `uiux-factory/` (or set the import path explicitly) to avoid importing the legacy package accidentally.

## Development

From `uiux-factory/`:

```bash
python -m pip install -r requirements-metagpt-core.txt
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
python run.py "Design a modern ecommerce website"
```

Runtime output is written under `uiux-factory/runs/` and `uiux-factory/generated/`; both directories are ignored by Git.

## Change policy

Before expanding the AI/design pipeline, keep these invariants green:

1. Python source compiles.
2. Foundation tests pass.
3. `run.json` remains valid throughout a run.
4. Generated files cannot escape the generated project root.
5. Changes to MetaGPT/vendor code are isolated and intentional.

GitHub Actions runs these foundation checks for changes under `uiux-factory/`.
