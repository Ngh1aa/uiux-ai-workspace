# QA stack verification notes

Official sources checked on 2026-09-11:

- Playwright visual comparisons: use `expect(page).toHaveScreenshot()`; keep baselines in a consistent OS/browser environment.
- Playwright accessibility guidance: use `@axe-core/playwright` with Playwright Test; automated scans complement, not replace, manual accessibility review.
- Lighthouse CI: designed for CI assertions, regression detection and performance/resource budgets.
- Sharp: candidate media pipeline dependency for resize/crop/WebP/AVIF; to be pinned only after package/runtime compatibility is verified in CI.

Only dependencies that are actually wired into the repository and exercised by CI should remain in the final stack.
