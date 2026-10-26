// Data must agree from selection through confirmation, including editing and browser back.
// Run with the same NODE_PATH/Playwright installation as taste-check.test.cjs.
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { test } = require('node:test');
const { chromium } = require('playwright');

const url = pathToFileURL(path.join(__dirname, '../examples/gom-moc/app.html')).href;

for (const width of [390, 1280]) for (const colorScheme of ['light', 'dark']) {
  test(`booking data survives confirm, edit and back: ${width}px ${colorScheme}`, async () => {
    const browser = await chromium.launch({ headless: true });
    try {
      const page = await browser.newPage({ viewport: { width, height: 844 }, colorScheme });
      const pageErrors = [];
      page.on('pageerror', error => pageErrors.push(error.message));
      await page.goto(url);
      await page.locator('[href="#chi-tiet"]').first().click();
      await page.locator('[name="exp"]').last().check();
      await page.locator('input[type="checkbox"]').uncheck();

      // Upper and lower limits must both preserve the selected count.
      assert.equal(await page.locator('[data-step="1"]').getAttribute('aria-disabled'), 'true');
      await page.locator('[data-step="1"]').click({ force: true });
      assert.equal(await page.locator('[data-people]').innerText(), '2');
      await page.locator('[data-step="-1"]').click();
      assert.equal(await page.locator('[data-step="-1"]').getAttribute('aria-disabled'), 'true');
      await page.locator('[data-step="-1"]').click({ force: true });
      assert.equal(await page.locator('[data-people]').innerText(), '1');
      assert.match(await page.locator('[data-pay]').innerText(), /Giữ 1 chỗ, 450\.000\s₫/);
      await page.locator('[data-pay]').click();
      assert.equal(await page.locator('[data-confirm-title]').innerText(), 'Đã giữ 1 chỗ');
      assert.equal(await page.locator('[data-confirm-people]').innerText(), '1');
      assert.match(await page.locator('[data-confirm-total]').innerText(), /450\.000\s₫/);

      await page.goBack();
      assert.equal(await page.locator('[data-people]').innerText(), '1');
      assert.equal(await page.locator('[name="exp"]').last().isChecked(), true);
      assert.equal(await page.locator('input[type="checkbox"]').isChecked(), false);
      await page.locator('[data-pay]').click();
      await page.locator('[data-edit-booking]').click();
      await page.locator('[data-step="1"]').click();
      await page.locator('[data-pay]').click();
      assert.equal(await page.locator('[data-confirm-title]').innerText(), 'Đã giữ 2 chỗ');
      assert.equal(await page.locator('[data-confirm-people]').innerText(), '2');
      assert.match(await page.locator('[data-confirm-total]').innerText(), /900\.000\s₫/);
      assert.deepEqual(pageErrors, []);
    } finally {
      await browser.close();
    }
  });
}
