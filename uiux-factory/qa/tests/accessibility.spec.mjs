import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';

fs.mkdirSync('artifacts', { recursive: true });
const routes = (process.env.QA_ROUTES || '/fixture/')
  .split(',')
  .map(route => route.trim())
  .filter(Boolean);

for (const route of routes) {
test(`${route} has no automatically detectable WCAG A/AA violations`, async ({ page }) => {
  await page.goto(route);
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();
  const safeRoute = route.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '') || 'root';
  fs.writeFileSync(`artifacts/axe-${safeRoute}.json`, JSON.stringify(result, null, 2));
  expect(result.violations).toEqual([]);
});
}
