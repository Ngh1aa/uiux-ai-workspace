# Legacy core prototype

This top-level `core/` directory is an earlier/prototype implementation and is **not** the active UIUX Factory runtime.

The current product source of truth is:

```text
uiux-factory/core/
```

Do not add new production features here and do not make `uiux-factory/` depend on this package. When running the Factory, use `uiux-factory/` as the working directory so Python resolves the active `core` package.

This directory is kept temporarily for historical comparison and should eventually be archived or removed once any remaining useful code has been migrated.
