# UIUX Factory

The v1 operator entrypoint is intentionally small.

- Start with [`docs/V1-QUICKSTART.md`](docs/V1-QUICKSTART.md).
- Natural-language creative/product pipeline: `python run.py "<goal>"`.
- Provider-neutral autonomous project execution:
  `python scripts/run_autonomous_flow.py --project-root <repo> --goal "<goal>"`.
- Runtime authority, sandbox, provider and release rules remain canonical in
  `../skills_UIUX/runtime/runtime-policy.json`.

Do not copy the internal workflow into every prompt. State the target, users/intent,
constraints and observable success condition; Factory owns adaptive Flow selection,
specialist routing, evidence gates and bounded replanning.
