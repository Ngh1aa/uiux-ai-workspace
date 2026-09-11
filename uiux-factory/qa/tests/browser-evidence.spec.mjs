import { test, expect } from '@playwright/test';
import fs from 'node:fs';

fs.mkdirSync('artifacts', { recursive: true });

test('captures DOM, box, computed style, console and screenshot evidence', async ({ page }) => {
  const consoleMessages = [];
  const pageErrors = [];
  page.on('console', message => consoleMessages.push({ type: message.type(), text: message.text() }));
  page.on('pageerror', error => pageErrors.push(String(error)));

  await page.goto('/fixture/');
  const button = page.getByRole('button', { name: 'Run evidence checks' });
  const box = await button.boundingBox();
  const computedStyle = await button.evaluate(el => {
    const style = getComputedStyle(el);
    return {
      color: style.color,
      backgroundColor: style.backgroundColor,
      fontSize: style.fontSize,
      minWidth: style.minWidth,
      minHeight: style.minHeight
    };
  });
  const dom = await page.locator('main').evaluate(el => el.outerHTML);
  await page.screenshot({ path: 'artifacts/fixture-1440.png', fullPage: true });

  const evidence = { dom, box, computedStyle, consoleMessages, pageErrors };
  fs.writeFileSync('artifacts/browser-evidence.json', JSON.stringify(evidence, null, 2));

  expect(box).not.toBeNull();
  expect(box.width).toBeGreaterThanOrEqual(44);
  expect(box.height).toBeGreaterThanOrEqual(44);
  expect(pageErrors).toEqual([]);
  expect(consoleMessages.filter(item => item.type === 'error')).toEqual([]);
});
