# A13 — Nova Real-Project Dogfood

A13 is the first phase whose primary acceptance target is not another synthetic runtime fixture. It runs the canonical Factory against a pinned checkout of the real `Ngh1aa/Nova` project and records only claims that the runtime can actually prove.

## Pinned target

```text
repository: Ngh1aa/Nova
commit: e206f51f2fda006adcf52497d8b827e048e157ec
route: /app.html?screen=home
```

The target commit is intentionally pinned. A moving `main` branch would make a dogfood failure ambiguous: Factory regression and target-project change would be indistinguishable.

## What A13 proves

The dedicated `A13 Nova Real-Project Dogfood` workflow checks out both repositories and exercises this chain:

```text
Nova source truth
  ↓
.uiux-profile.json + PROJECT-CONTEXT.md
  ↓
canonical Flow selection
  ↓
professional-website-redesign / research
  ↓
financial-services conditional routing
  ↓
financial-product-intelligence
  ↓
A8.5 exact section capability read + SHA-256 ledger
  ↓
A8.4 same-revision stage resume
  ↓
A9 trusted Playwright render at 3 real viewports
  ↓
A9 bounded model-readable browser observation
  ↓
A10 screenshot validation / zero-cost truth boundary
  ↓
A12 canonical benchmark manifest binding
  ↓
A13 JSON report
```

The target is opened as a local static server inside GitHub Actions. No production deployment is touched.

## Responsive evidence

A13 closes a dogfood-discovered integration gap between A9 and A10: the canonical Playwright path previously used one fixed desktop viewport while A10 recommends multi-screen review.

`PlaywrightBrowserEvidenceAdapter.capture()` now accepts an optional bounded viewport list. A13 uses:

- desktop — `1440 × 1000`;
- tablet — `768 × 1024`;
- mobile — `390 × 844`.

Viewport requests are limited to six entries, names are constrained, names must be unique, dimensions must be integers, and each edge must stay between 240 and 4096 pixels. Existing callers that omit the viewport list keep the old single-viewport behavior and old artifact naming.

## Truth boundary

A13 deliberately distinguishes deterministic integration evidence from capabilities that are unavailable in zero-cost CI.

A passing A13 report means:

- the pinned Nova source truth could be safely read;
- the canonical Flow routed Nova as expected;
- the financial skill was actually routed;
- one exact skill section was retrieved through the A8.5 capability ledger;
- A8.4 resume continuity preserved the specialist run;
- real rendered browser evidence passed at desktop/tablet/mobile;
- A9 produced bounded advisory browser context;
- A10 revalidated the real screenshots;
- the A12 benchmark corpus manifest is valid and bound into the report.

A13 does **not** manufacture any of these claims:

```text
provider_reasoning.status = NOT_RUN
vision.status             = NOT_RUN when no analyzer is configured
human_review.status       = pending
release.status            = NOT_ATTEMPTED
benchmark.scoring_status  = NOT_RUN
```

The CI job carries no external provider or visual-model credentials. `NOT_RUN` is the correct outcome, not a fake PASS.

## Dogfood findings in Nova

The initial A13 audit found two target-workflow drifts before runtime execution:

1. Nova is currently a static HTML project with no root `package.json`, but `.github/workflows/nova-cloud-qa.yml` still attempts `npm ci` / `npm install` in Nova.
2. The same workflow still invokes the removed legacy Factory surface `uiux-factory/run.py qa`.

A13 records these as target findings instead of confusing them with visual/browser failure. After the Factory-side A13 contract is merged, Nova's workflow should be migrated to the new dogfood CLI pinned to the A13 Factory merge commit.

## CI contract

Two CI layers remain separate:

- `UIUX Factory CI` runs the complete deterministic foundation test suite;
- `A13 Nova Real-Project Dogfood` installs canonical Playwright QA dependencies, serves the pinned Nova checkout locally, captures three viewport evidence packs, runs the A13 report, and uploads the JSON + screenshots as a GitHub Actions artifact.

A13 must be green in both layers before merge.

## Regression coverage

`uiux-factory/tests/test_nova_dogfood_a13.py` protects:

- financial Nova profile requirements;
- static-project detection;
- real Flow and financial-skill routing through the dogfood orchestrator;
- exact A8.5 section retrieval and A8.4 resume continuity;
- explicit `NOT_RUN` / pending / no-release truth boundaries;
- detection of the two stale Nova workflow assumptions;
- strict multi-viewport input validation;
- pinned target SHA fail-closed behavior.
