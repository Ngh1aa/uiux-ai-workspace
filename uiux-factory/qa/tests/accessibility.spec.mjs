import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';
import { qaViewports } from '../scripts/ux-regression.mjs';

fs.mkdirSync('artifacts', { recursive: true });
const routes = (process.env.QA_ROUTES || '/fixture/')
  .split(',')
  .map(route => route.trim())
  .filter(Boolean);

for (const route of routes) {
for (const viewport of qaViewports(process.env.QA_VIEWPORTS_JSON)) {
test(`${route} @ ${viewport.name} has no automatically detectable WCAG A/AA violations`, async ({ page }) => {
  await page.setViewportSize({ width: viewport.width, height: viewport.height });
  await page.goto(route);
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();
  const safeRoute = route.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '') || 'root';
  fs.writeFileSync(`artifacts/axe-${safeRoute}-${viewport.name}.json`, JSON.stringify(result, null, 2));
  expect(result.violations).toEqual([]);
});
}
}
