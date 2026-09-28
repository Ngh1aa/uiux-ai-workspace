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

const viewportPayload = process.env.QA_VIEWPORTS_JSON || '';
let requestedViewports = [null];
if (viewportPayload) {
  const parsed = JSON.parse(viewportPayload);
  if (!Array.isArray(parsed) || parsed.length < 1 || parsed.length > 6) {
    throw new Error('QA_VIEWPORTS_JSON must be an array with 1..6 entries');
  }
  requestedViewports = parsed.map(raw => {
    if (!raw || typeof raw !== 'object') throw new Error('viewport entry must be an object');
    const name = String(raw.name || '').trim().toLowerCase();
    const width = Number(raw.width);
    const height = Number(raw.height);
    if (!/^[a-z0-9][a-z0-9_-]{0,31}$/.test(name)) throw new Error(`invalid viewport name: ${name}`);
    if (!Number.isInteger(width) || !Number.isInteger(height)) throw new Error(`invalid viewport dimensions: ${name}`);
    if (width < 240 || width > 4096 || height < 240 || height > 4096) {
      throw new Error(`viewport dimensions out of bounds: ${name}`);
    }
    return { name, width, height };
  });
  if (new Set(requestedViewports.map(item => item.name)).size !== requestedViewports.length) {
    throw new Error('viewport names must be unique');
  }
}

for (const route of routes) {
  for (const requestedViewport of requestedViewports) {
    const viewportLabel = requestedViewport ? ` @ ${requestedViewport.name}` : '';
    test(`captures browser evidence for ${route}${viewportLabel}`, async ({ page }) => {
      if (requestedViewport) {
        await page.setViewportSize({ width: requestedViewport.width, height: requestedViewport.height });
      }

      const consoleMessages = [];
      const pageErrors = [];
      const blockedRequests = [];
      const failedRequests = [];
      const sanitizedRemoteStylesheets = [];
      page.on('console', message => consoleMessages.push({ type: message.type(), text: message.text() }));
      page.on('pageerror', error => pageErrors.push(String(error)));
      page.on('requestfailed', request => {
        failedRequests.push(`${request.method()} ${request.url()} :: ${request.failure()?.errorText || 'failed'}`);
      });

      await page.route('**/*', async intercepted => {
        const request = intercepted.request();
        const rawUrl = request.url();
        let parsed;
        try {
          parsed = new URL(rawUrl);
        } catch {
          blockedRequests.push(rawUrl);
          await intercepted.abort('blockedbyclient');
          return;
        }
        if ((parsed.protocol === 'http:' || parsed.protocol === 'https:') && parsed.origin !== allowedOrigin) {
          // Keep the browser lane offline. Remote stylesheets are replaced with an empty,
          // local response so optional web-font CSS cannot turn successful isolation into
          // a false-negative render failure. The evidence records the limitation explicitly.
          // Every other cross-origin resource remains a hard failure.
          if (request.resourceType() === 'stylesheet') {
            sanitizedRemoteStylesheets.push({ url: rawUrl, resourceType: 'stylesheet' });
            await intercepted.fulfill({
              status: 200,
              contentType: 'text/css; charset=utf-8',
              body: '/* cross-origin stylesheet sanitized by UIUX Factory browser QA */\n'
            });
            return;
          }
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
      expect(blockedRequests, `Unsafe cross-origin network request detected for ${route}`).toEqual([]);

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
      const viewportSize = page.viewportSize() || {};
      const viewport = requestedViewport
        ? { name: requestedViewport.name, width: viewportSize.width, height: viewportSize.height }
        : viewportSize;
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
      const viewportSuffix = requestedViewport ? `-${requestedViewport.name}` : '';
      const evidenceStem = `${safeRoute}${viewportSuffix}`;
      const screenshotName = `${evidenceStem}-render.png`;
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
        failedRequests,
        sanitizedRemoteStylesheets
      };
      fs.writeFileSync(
        path.join(artifactsDir, `browser-evidence-${evidenceStem}.json`),
        JSON.stringify(evidence, null, 2)
      );

      expect(box).not.toBeNull();
      expect(pageErrors).toEqual([]);
      expect(consoleMessages.filter(item => item.type === 'error')).toEqual([]);
    });
  }
}