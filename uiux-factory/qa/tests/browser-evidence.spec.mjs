import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const artifactsDir = path.resolve(process.env.QA_ARTIFACTS_DIR || 'artifacts');
fs.mkdirSync(artifactsDir, { recursive: true });
const baseUrl = process.env.QA_BASE_URL || 'http://127.0.0.1:4173';
const allowedOrigin = process.env.QA_ALLOWED_ORIGIN || new URL(baseUrl).origin;
const routes = (process.env.QA_ROUTES || '/fixture/')
  .split(',')
  .map(route => route.trim())
  .filter(Boolean);

for (const route of routes) {
  test(`captures browser evidence for ${route}`, async ({ page }) => {
    const consoleMessages = [];
    const pageErrors = [];
    const blockedRequests = [];
    const failedRequests = [];
    page.on('console', message => consoleMessages.push({ type: message.type(), text: message.text() }));
    page.on('pageerror', error => pageErrors.push(String(error)));
    page.on('requestfailed', request => {
      failedRequests.push(`${request.method()} ${request.url()} :: ${request.failure()?.errorText || 'failed'}`);
    });

    await page.route('**/*', async intercepted => {
      const rawUrl = intercepted.request().url();
      let parsed;
      try {
        parsed = new URL(rawUrl);
      } catch {
        blockedRequests.push(rawUrl);
        await intercepted.abort('blockedbyclient');
        return;
      }
      if ((parsed.protocol === 'http:' || parsed.protocol === 'https:') && parsed.origin !== allowedOrigin) {
        blockedRequests.push(rawUrl);
        await intercepted.abort('blockedbyclient');
        return;
      }
      await intercepted.continue();
    });

    const response = await page.goto(route, { waitUntil: 'domcontentloaded' });
    expect(response, `No navigation response for ${route}`).not.toBeNull();
    expect(response.ok(), `Navigation failed for ${route} with HTTP ${response.status()}`).toBeTruthy();
    expect(new URL(page.url()).origin, `Cross-origin navigation detected for ${route}`).toBe(allowedOrigin);
    expect(blockedRequests, `Cross-origin network request detected for ${route}`).toEqual([]);

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
        fontFamily: style.fontFamily,
        fontSize: style.fontSize,
        fontWeight: style.fontWeight,
        lineHeight: style.lineHeight,
        minWidth: style.minWidth,
        minHeight: style.minHeight,
        overflow: style.overflow
      };
    });
    const dom = await evidenceRoot.evaluate(el => el.outerHTML);
    const ariaSnapshot = await page.locator('body').ariaSnapshot();
    const viewport = page.viewportSize() || {};
    const elements = await page.locator(
      'a, button, input, select, textarea, img, [role], h1, h2, h3, main, nav, header, footer'
    ).evaluateAll(nodes => nodes.slice(0, 24).map(el => {
      const style = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      const role = el.getAttribute('role') || '';
      const checked = 'checked' in el && typeof el.checked === 'boolean' ? el.checked : null;
      const expandedRaw = el.getAttribute('aria-expanded');
      const expanded = expandedRaw === 'true' ? true : expandedRaw === 'false' ? false : null;
      const image = el instanceof HTMLImageElement
        ? {
            src: el.currentSrc || el.src || '',
            naturalWidth: el.naturalWidth,
            naturalHeight: el.naturalHeight,
            renderedWidth: rect.width,
            renderedHeight: rect.height
          }
        : null;
      return {
        tag: el.tagName.toLowerCase(),
        role,
        text: (el.textContent || '').trim().slice(0, 300),
        ariaLabel: el.getAttribute('aria-label') || '',
        name: el.getAttribute('name') || '',
        type: el.getAttribute('type') || '',
        disabled: 'disabled' in el ? Boolean(el.disabled) : false,
        checked,
        expanded,
        box: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        style: {
          display: style.display,
          position: style.position,
          color: style.color,
          backgroundColor: style.backgroundColor,
          fontFamily: style.fontFamily,
          fontSize: style.fontSize,
          fontWeight: style.fontWeight,
          lineHeight: style.lineHeight,
          width: style.width,
          height: style.height,
          overflow: style.overflow
        },
        image
      };
    }));
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
      elements,
      screenshot: screenshotName,
      consoleMessages,
      pageErrors,
      blockedRequests,
      failedRequests
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
