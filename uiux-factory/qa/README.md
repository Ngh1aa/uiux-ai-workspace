# UIUX Factory Cloud QA

This directory is the repository-owned QA harness for GitHub Actions. It does not require the removed local Workbench or localhost bridge.

Current toolchain:

- Playwright Test + Chromium: browser rendering, DOM/style/box/console evidence and screenshots.
- `@axe-core/playwright`: automated WCAG-oriented accessibility scanning.
- Lighthouse CI: performance/accessibility/best-practice budgets.
- Sharp: WebP/AVIF media processing smoke coverage and automatic lifecycle-state matrix composition.
- State Coverage Gate: contract-driven Normal/Empty/Loading/Error/Edge rendering with semantic assertions across declared viewports.
- Rendered UX regression safety net: computed foreground/surface collapse, overflow, visible images and optional target-declared geometry/overlay/toggle invariants. Desktop/mobile are the default browser matrix.
- Infra failure classifier: separates product QA failures from provider rate limits, auth blockers, build/deploy failures and release-state gaps.

Run locally only when desired:

```bash
npm ci
npx playwright install chromium
python3 -m http.server 4173 --directory .
npm test
QA_STATE_CONTRACT=fixture/state-coverage.contract.json npm run test:state
npx lhci autorun --config=lighthouserc.json
```

The canonical execution path is `.github/workflows/cloud-qa-toolchain.yml`, which uploads evidence artifacts for review. Automated checks do not replace creative/visual judgment.

See `docs/UX-FEEDBACK-REGRESSION.md` for `QA_UX_CONTRACT`, `QA_MOTION_MODES`, normalized A5 feedback recording and reviewed cross-project prevention. `npm run test:ux` tests the evaluator against actual browser regressions; fixture success is tooling evidence, not target acceptance.

The harness is intentionally independent of `apps/web`, the removed localhost bridge, and ad-hoc migration/manual-test scripts. Foundation tests live under `uiux-factory/tests/`; browser/a11y/performance/media/state evidence lives here.

## State Coverage Gate

Target projects opt in with a JSON contract matching `state-coverage.schema.json`. The contract declares the State Lab route, optional iframe owner, state query parameters, semantic assertions and focus selectors. Non-normal states must carry semantic evidence; a route that says `state=empty` while showing Normal UI fails the gate.

Outputs live under `artifacts/state-coverage/` and include state × viewport screenshots, `state-coverage-report.json`, semantic assertion results, overflow/console/page-error evidence, and an automatically composed `state-matrix-2x2.png` when matrix output is enabled.

The internal fixture contract is `fixture/state-coverage.contract.json`. Cloud QA always runs it for this repository so the gate tests itself rather than trusting its implementation.

See `docs/STATE-COVERAGE-INFRASTRUCTURE.md` for the contract format, failure taxonomy and GitHub-native runner.

## Infra failure classifier

Use `scripts/infra-failure-classifier.mjs` when a provider or deployment status is red. It returns a machine-readable category such as `PRODUCT_QA_FAILED`, `PROVIDER_RATE_LIMITED`, `AUTH_BLOCKED`, `BUILD_FAILED`, `DEPLOY_FAILED`, `READY_BUT_NOT_DEPLOYED` or `DEPLOYED_VERIFIED`.

A provider quota failure is not evidence that product UI is broken, and a semantic state failure must never be dismissed as infrastructure noise.

## Workflow-dispatch defaults

When `target_repository` is set to another repository:

- blank `target_dir` means that repository root;
- blank `routes` means `/`;
- blank `state_contract` skips State Coverage while preserving browser/a11y/performance/media QA.

When `target_repository` is blank, the workflow keeps the internal toolchain smoke defaults:

- `target_dir=uiux-factory/qa`;
- `routes=/fixture/,/fixture/index.html`;
- `state_contract=fixture/state-coverage.contract.json`.

This prevents external-project audits from accidentally looking for this repository's fixture paths while ensuring the Factory's own State Coverage infrastructure is continuously dogfooded.
