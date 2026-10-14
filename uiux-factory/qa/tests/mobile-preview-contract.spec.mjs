import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';

const { chromium } = createRequire(import.meta.url)('playwright');
const preview = new URL('../../../skills_UIUX/examples/projects/mobile-appointment/preview/', import.meta.url);
const files = {
  'index.html': ['text/html; charset=utf-8', fs.readFileSync(new URL('index.html', preview))],
  'preview.css': ['text/css; charset=utf-8', fs.readFileSync(new URL('preview.css', preview))],
  'preview.js': ['text/javascript; charset=utf-8', fs.readFileSync(new URL('preview.js', preview))]
};
const prefix = '/project-demo/';

test('Mobile browser prototype: actual interactions and Pages-style subpath', async t => {
  const server = http.createServer((request, response) => {
    const pathname = new URL(request.url, 'http://localhost').pathname;
    if (pathname === '/favicon.ico') { response.writeHead(204); response.end(); return; }
    const name = pathname.startsWith(prefix) ? pathname.slice(prefix.length) || 'index.html' : '';
    const file = files[name];
    response.writeHead(file ? 200 : 404, { 'Content-Type': file ? file[0] : 'text/plain' });
    response.end(file ? file[1] : 'Not found');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}${prefix}`;
  let browser;
  try {
    browser = await chromium.launch({ headless: true,
      ...(process.env.QA_CHROME_EXECUTABLE ? { executablePath: process.env.QA_CHROME_EXECUTABLE } : {}) });
    await t.test('book, reload, browser Back, duplicate confirmation and cancellation', async () => {
      const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(base);
      await page.getByRole('button', { name: '16:00', exact: true }).click();
      assert.equal(await page.evaluate(() => document.activeElement.textContent), '16:00');
      await page.getByRole('button', { name: 'Tiếp tục · 16:00' }).click();
      assert.equal(new URL(page.url()).searchParams.get('screen'), 'confirm');
      await page.getByRole('button', { name: 'Xác nhận lịch demo' }).click();
      assert.equal(await page.locator('.booking').count(), 1);
      await page.reload();
      assert.equal(await page.locator('.booking').count(), 1);
      await page.goBack();
      await page.getByRole('button', { name: 'Xác nhận lịch demo' }).click();
      assert.equal(await page.locator('.booking').count(), 1);
      await page.getByRole('button', { name: 'Hủy lịch demo' }).click();
      assert.equal(await page.locator('[data-empty]').count(), 1);
      assert.deepEqual(errors, []);
      await page.close();
    });
    await t.test('offline blocks confirmation and recovery preserves choices', async () => {
      const page = await browser.newPage();
      await page.goto(`${base}?screen=confirm&state=offline&service=portfolio&slot=14:30`);
      assert.equal(await page.getByRole('button', { name: 'Xác nhận lịch demo' }).isDisabled(), true);
      await page.getByRole('button', { name: 'Thử kết nối lại' }).click();
      assert.equal(new URL(page.url()).searchParams.get('slot'), '14:30');
      await page.getByRole('button', { name: 'Xác nhận lịch demo' }).click();
      assert.match(await page.locator('.booking').innerText(), /Review portfolio/);
      await page.close();
    });
    await t.test('reset and malformed local storage recover without losing navigation', async () => {
      const page = await browser.newPage();
      await page.goto(base);
      await page.evaluate(() => localStorage.setItem('uiux-mobile-appointment-demo.v1', 'invalid JSON'));
      await page.reload();
      await page.getByRole('button', { name: 'Tiếp tục · 09:00' }).click();
      await page.getByRole('button', { name: 'Xác nhận lịch demo' }).click();
      await page.getByRole('button', { name: 'Đặt lại demo' }).click();
      assert.equal(await page.evaluate(() => localStorage.getItem('uiux-mobile-appointment-demo.v1')), '[]');
      assert.equal(await page.locator('#app').getAttribute('data-screen'), 'home');
      await page.close();
    });
    for (const width of [320, 390, 1440]) {
      await t.test(`state links, assets, focus and no horizontal overflow at ${width}px`, async () => {
        const page = await browser.newPage({ viewport: { width, height: 900 } });
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
        page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
        await page.goto(`${base}?screen=confirm&service=portfolio&slot=16:00`);
        assert.match(await page.locator('.summary').innerText(), /Review portfolio/);
        assert.match(await page.locator('.summary').innerText(), /16:00/);
        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(() => document.activeElement.tagName), 'BUTTON');
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
        await page.goto(`${base}?screen=bookings&state=empty`);
        assert.equal(await page.locator('[data-empty]').count(), 1);
        await page.goto(`${base}?screen=not-a-screen&service=constructor&slot=invalid`);
        assert.equal(await page.locator('#app').getAttribute('data-screen'), 'home');
        assert.equal(await page.getByRole('button', { name: 'Tiếp tục · 09:00' }).count(), 1);
        assert.deepEqual(errors, []);
        const directory = path.resolve(process.env.QA_ARTIFACTS_DIR || 'artifacts', 'mobile-preview');
        fs.mkdirSync(directory, { recursive: true });
        await page.screenshot({ path: path.join(directory, `home-${width}.png`), fullPage: true });
        await page.close();
      });
    }
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
});
