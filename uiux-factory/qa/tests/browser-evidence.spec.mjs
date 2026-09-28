import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const artifactsDir = path.resolve(process.env.QA_ARTIFACTS_DIR || 'artifacts');
fs.mkdirSync(artifactsDir, { recursive: true });
const routes = (process.env.QA_ROUTES || '/fixture/')
  .split(',')
  .map(route => route.trim())
  .filter(Boolean);

for (const route of routes) {
  test(`captures browser evidence for ${route}`, async ({ page }) => {
    const consoleMessages = [];
    const pageErrors = [];
    page.on('console', message => consoleMessages.push({ type: message.type(), text: message.text() }));
    page.on('pageerror', error => pageErrors.push(String(error)));

    const response = await page.goto(route, { waitUntil: 'domcontentloaded' });
    expect(response, `No navigation response for ${route}`).not.toBeNull();
    expect(response.ok(), `Navigation failed for ${route} with HTTP ${response.status()}`).toBeTruthy();

    const main = page.locator('main').first();
    const hasMain = (await main.count()) > 0;
    const evidenceRoot = hasMain ? main : page.locator('body').first();
    const target = page.locator(
      'button, a, input, select, textarea, [role="button"], main, body'
    ).first();

    const box = await target.boundingBox();
    const computedStyle = await target.evaluate(el => {
      const style = getComputedStyle(el);
      return {
        color: style.color,
        backgroundColor: style.backgroundColor,
        fontSize: style.fontSize,
        minWidth: style.minWidth,
        minHeight: style.minHeight
      };
    });
    const dom = await evidenceRoot.evaluate(el => el.outerHTML);
    const ariaSnapshot = await page.locator('body').ariaSnapshot();
    const viewport = page.viewportSize() || {};
    const safeRoute = route.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '') || 'root';
    const screenshotName = `${safeRoute}-render.png`;
    await page.screenshot({ path: path.join(artifactsDir, screenshotName), fullPage: true });

    const evidence = {
      route,
      url: page.url(),
      title: await page.title(),
      viewport,
      hasMain,
      dom,
      ariaSnapshot,
      box,
      computedStyle,
      screenshot: screenshotName,
      consoleMessages,
      pageErrors
    };
    fs.writeFileSync(
      path.join(artifactsDir, `browser-evidence-${safeRoute}.json`),
      JSON.stringify(evidence, null, 2)
    );

    expect(box).not.toBeNull();
    expect(pageErrors).toEqual([]);
    expect(consoleMessages.filter(item => item.type === 'error')).toEqual([]);
  });
}
