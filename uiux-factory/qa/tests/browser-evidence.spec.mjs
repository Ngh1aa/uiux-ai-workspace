import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';

test('B09/B10 matrix truth and failure reports survive real browser/image errors', async ({}, testInfo) => {
  const { runStateCoverage } = await import(new URL('../scripts/state-coverage.mjs', import.meta.url).href);
  const target = http.createServer((_request, response) => {
    response.writeHead(200, { 'Content-Type': 'text/html' });
    response.end('<html><body><h1>Visible regression fixture</h1></body></html>');
  });
  await new Promise(resolve => target.listen(0, '127.0.0.1', resolve));
  const baseUrl = `http://127.0.0.1:${target.address().port}`;
  const state = { id: 'empty', wait_ms: 0, focus: 'body', assertions: [{ type: 'text', text: 'Visible regression fixture' }] };
  const contract = { schema_version: '1.0', name: 'Matrix truth regression', entry_route: '/',
    viewports: [{ name: 'desktop', width: 800, height: 600 }], states: [state],
    matrix: { states: ['empty'], columns: 1, tile_width: 320, tile_height: 240 } };
  try {
    const mixed = await runStateCoverage({ ...contract,
      states: [state, { ...state, id: 'error', assertions: [{ type: 'text', text: 'Missing expected text' }] }],
      matrix: { ...contract.matrix, states: ['empty', 'error'], columns: 2 }
    }, { baseUrl, artifactsDir: testInfo.outputPath('mixed') });
    expect(mixed.report.classification).toBe('PRODUCT_QA_FAILED');
    expect(mixed.report.matrix.generated).toBe(true);
    expect(mixed.report.matrix.tiles.map(tile => tile.status)).toEqual(['PASS', 'FAIL']);
    const focus = await runStateCoverage({ ...contract, states: [{ ...state, focus: '#missing' }] },
      { baseUrl, artifactsDir: testInfo.outputPath('focus') });
    expect(focus.report.failures[0].runtime_error).toContain('focus selector not found');
    expect(focus.report.matrix.error).toContain('matrix tile missing');
    expect(focus.report.classification).toBe('PRODUCT_QA_FAILED');
    expect(JSON.parse(fs.readFileSync(focus.reportPath, 'utf8'))).toEqual(focus.report);
    const artifactsDir = testInfo.outputPath('write-error');
    fs.mkdirSync(path.join(artifactsDir, 'state-coverage', 'occupied.png'), { recursive: true });
    const writeError = await runStateCoverage({ ...contract, matrix: { ...contract.matrix, output: 'state-coverage/occupied.png' } },
      { baseUrl, artifactsDir });
    expect(writeError.report.checks[0].passed).toBe(true);
    expect(writeError.report.failures).toEqual([]);
    expect(writeError.report.matrix.generated).toBe(false);
    expect(writeError.report.matrix.error).toBeTruthy();
    expect(writeError.report.classification).toBe('PRODUCT_QA_FAILED');
    expect(JSON.parse(fs.readFileSync(writeError.reportPath, 'utf8'))).toEqual(writeError.report);
  } finally { await new Promise(resolve => target.close(resolve)); }
});


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

test('B03 redirects preserve navigation origin and relative asset base', async ({ browser }) => {
  const { navigateWithinOrigin } = await import(new URL('../scripts/state-coverage.mjs', import.meta.url).href);
  let outsideRequests = 0;
  const outside = http.createServer((_request, response) => {
    outsideRequests += 1;
    response.end('Outside origin');
  });
  await new Promise(resolve => outside.listen(0, '127.0.0.1', resolve));
  const outsideUrl = `http://127.0.0.1:${outside.address().port}`;
  const target = http.createServer((request, response) => {
    const route = new URL(request.url, 'http://localhost').pathname;
    if (route === '/start' || route === '/chain' || route === '/loop' || route === '/outside') {
      const location = { '/start': '/nested/end', '/chain': '/outside', '/loop': '/loop', '/outside': `${outsideUrl}/secret` }[route];
      response.writeHead(302, { Location: location });
      response.end();
    } else if (route === '/nested/asset.js') {
      response.writeHead(200, { 'Content-Type': 'text/javascript' });
      response.end('document.body.dataset.relativeAsset = "loaded";');
    } else if (route === '/disconnected') request.socket.destroy();
    else {
      response.writeHead(200, { 'Content-Type': 'text/html' });
      response.end('<html><body>Bounded state<script src="./asset.js"></script></body></html>');
    }
  });
  await new Promise(resolve => target.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${target.address().port}`;
  try {
    for (const route of ['/start', '/outside', '/chain', '/loop', '/disconnected']) {
      const context = await browser.newContext({ serviceWorkers: 'block' });
      const page = await context.newPage();
      try {
        if (route === '/start') {
          const response = await navigateWithinOrigin(page, `${origin}${route}`);
          expect(response.status()).toBe(200);
          expect(page.url()).toBe(`${origin}/nested/end`);
          await expect(page.locator('body')).toHaveAttribute('data-relative-asset', 'loaded');
        } else {
          const errorPattern = route === '/loop' ? /exceeded 20/ : route === '/disconnected' ? /socket|reset|closed/i : /ERR_BLOCKED_BY_CLIENT/;
          await expect(navigateWithinOrigin(page, `${origin}${route}`)).rejects.toThrow(errorPattern);
        }
        expect(outsideRequests).toBe(0);
      } finally { await context.close(); }
    }
  } finally {
    await new Promise(resolve => target.close(resolve));
    await new Promise(resolve => outside.close(resolve));
  }
});
