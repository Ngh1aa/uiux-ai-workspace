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
      await page.locator('[data-confirm-action]').click();
      assert.equal(await page.locator('[data-confirm-title]').innerText(), 'Đã giữ 1 chỗ');
      assert.equal(await page.locator('[data-confirm-people]').innerText(), '1');
      assert.match(await page.locator('[data-confirm-total]').innerText(), /450\.000\s₫/);

      await page.goBack();
      assert.equal(await page.locator('[data-people]').innerText(), '1');
      assert.equal(await page.locator('[name="exp"]').last().isChecked(), true);
      assert.equal(await page.locator('input[type="checkbox"]').isChecked(), false);
      await page.locator('[data-pay]').click();
      await page.locator('[data-confirm-action]').click();
      await page.locator('[data-edit-booking]').click();
      await page.locator('[data-step="1"]').click();
      await page.locator('[data-pay]').click();
      await page.locator('[data-confirm-action]').click();
      assert.equal(await page.locator('[data-confirm-title]').innerText(), 'Đã giữ 2 chỗ');
      assert.equal(await page.locator('[data-confirm-people]').innerText(), '2');
      assert.match(await page.locator('[data-confirm-total]').innerText(), /900\.000\s₫/);
      // Same semantic session and customer role must be retained across every state.
      assert.equal(await page.locator('main').getAttribute('data-role'), 'customer');
      assert.equal(await page.locator('[data-confirm-name]').innerText(), 'Bát ăn cơm đầu tiên');
      assert.match(await page.locator('[data-confirm-session]').innerText(), /7\/11/);
      assert.equal(await page.locator('[data-shipping-step]').isVisible(), false);
      assert.deepEqual(pageErrors, []);
    } finally {
      await browser.close();
    }
  });
}

for (const width of [390, 1280]) for (const colorScheme of ['light', 'dark']) {
  test(`booking correct object, review, capacity recovery and calendar: ${width}px ${colorScheme}`, async () => {
    const browser = await chromium.launch({ headless: true });
    try {
      const page = await browser.newPage({ viewport: { width, height: 844 }, colorScheme });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
      await page.goto(url);
      await page.locator('[data-session="cup"]').click();
      assert.equal(await page.locator('[data-session-title]').innerText(), 'Cốc có quai');
      assert.match(await page.locator('[data-session-date]').innerText(), /8\/11/);
      await page.locator('[data-step="1"]').click();
      assert.equal(await page.locator('[data-people]').innerText(), '3');
      await page.locator('[data-pay]').click();
      assert.equal(await page.locator('#booking-review').isVisible(), true);
      assert.match(await page.locator('[data-review-summary]').innerText(), /Cốc có quai.*8\/11.*3 người, 1\.350\.000\s₫/);
      assert.equal(await page.evaluate(() => location.hash), '#chi-tiet');
      // Review is a real modal; cancel returns focus and preserves all choices.
      await page.locator('[data-review-back]').click();
      assert.equal(await page.locator('#booking-review').isVisible(), false);
      assert.equal(await page.locator('[data-people]').innerText(), '3');
      assert.equal(await page.locator('[data-pay]').evaluate(node => node === document.activeElement), true);
      await page.locator('[data-step="-1"]').click();
      await page.locator('[data-pay]').click();
      await page.locator('[data-confirm-action]').click();
      assert.equal(await page.locator('[data-confirm-name]').innerText(), 'Cốc có quai');
      assert.match(await page.locator('[data-confirm-session]').innerText(), /8\/11/);
      assert.equal(await page.locator('[data-confirm-people]').innerText(), '2');
      assert.match(await page.locator('[data-confirm-total]').innerText(), /900\.000\s₫/);
      const downloadPromise = page.waitForEvent('download');
      await page.locator('[data-calendar]').click();
      const download = await downloadPromise;
      assert.equal(download.suggestedFilename(), 'lich-gom-cup.ics');
      const calendar = require('node:fs').readFileSync(await download.path(), 'utf8');
      assert.match(calendar, /DTSTART:20261108T090000/);
      assert.match(calendar, /SUMMARY:Cốc có quai/);
      assert.match(await page.locator('[data-calendar-status]').innerText(), /Đã tạo tệp/);
      // Closed session is a genuine fixture: payment cannot proceed and recovery is available.
      await page.locator('[href="#chon-buoi"]').last().click();
      await page.locator('[data-session="full"]').click();
      assert.match(await page.locator('[data-session-date]').innerText(), /14\/11/);
      assert.equal(await page.locator('[data-unavailable]').isVisible(), true);
      assert.equal(await page.locator('[data-pay]').getAttribute('aria-disabled'), 'true');
      assert.match(await page.locator('#booking-reason').innerText(), /đã kín/);
      // Deliberately bypass Playwright's disabled guard to test the application's guard too.
      await page.locator('[data-pay]').click({ force: true });
      assert.equal(await page.locator('#booking-review').isVisible(), false);
      await page.locator('[data-recover]').click();
      assert.equal(await page.locator('[data-pay]').getAttribute('aria-disabled'), 'false');
      assert.equal(await page.locator('[data-session-title]').innerText(), 'Bát ăn cơm đầu tiên');
      assert.match(await page.locator('[data-session-date]').innerText(), /7\/11/);
      await page.locator('[data-pay]').click();
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('#booking-review').isVisible(), false);
      assert.deepEqual(errors, []);
    } finally { await browser.close(); }
  });
}
