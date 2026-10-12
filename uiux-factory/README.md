# UIUX Factory

The v1 operator entrypoint is intentionally small.

- Start with [`docs/V1-QUICKSTART.md`](docs/V1-QUICKSTART.md).
- Natural-language creative/product pipeline: `python run.py "<goal>" --authority branch_write`.
- Provider-neutral autonomous project execution:
  `python scripts/run_autonomous_flow.py --project-root <repo> --goal "<goal>" --authority branch_write`.
- Runtime authority, sandbox, provider and release rules remain canonical in
  `../skills_UIUX/runtime/runtime-policy.json`.

For `run.py`, `--authority branch_write` is an explicit opt-in to implementation/repair
writes; omission keeps the `read_only` default. Build examples declare authority
explicitly. This grants no merge/deploy permission and changes no entrypoint defaults.

Do not copy the internal workflow into every prompt. State the target, users/intent,
constraints and observable success condition; Factory owns adaptive Flow selection,
specialist routing, evidence gates and bounded replanning.
