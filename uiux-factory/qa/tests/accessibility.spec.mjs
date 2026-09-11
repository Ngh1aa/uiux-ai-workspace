import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';

fs.mkdirSync('artifacts', { recursive: true });

test('fixture has no automatically detectable WCAG A/AA violations', async ({ page }) => {
  await page.goto('/fixture/');
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();
  fs.writeFileSync('artifacts/axe.json', JSON.stringify(result, null, 2));
  expect(result.violations).toEqual([]);
});
