# UIUX Factory Cloud QA

This directory is the repository-owned QA harness for GitHub Actions. It does not require the removed local Workbench or localhost bridge.

Current toolchain:

- Playwright Test + Chromium: browser rendering, DOM/style/box/console evidence and screenshots.
- `@axe-core/playwright`: automated WCAG-oriented accessibility scanning.
- Lighthouse CI: performance/accessibility/best-practice budgets.
- Sharp: WebP/AVIF media processing smoke coverage.

Run locally only when desired:

```bash
npm install
npx playwright install chromium
python3 -m http.server 4173 --directory .
npm test
npx lhci autorun --config=lighthouserc.json
```

The canonical execution path is `.github/workflows/cloud-qa-toolchain.yml`, which uploads evidence artifacts for review. Automated checks do not replace creative/visual judgment.

The harness is intentionally independent of `apps/web`, the removed localhost bridge, and ad-hoc migration/manual-test scripts. Foundation tests live under `uiux-factory/tests/`; browser/a11y/performance/media evidence lives here.
