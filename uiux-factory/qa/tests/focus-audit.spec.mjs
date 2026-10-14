import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

test('rendered focus rejects selector/cascade failures and preserves valid indicators', async () => {
  const browser = await chromium.launch({ headless: true, chromiumSandbox: true,
    ...(process.env.QA_CHROME_EXECUTABLE ? { executablePath: process.env.QA_CHROME_EXECUTABLE } : {}) });
  try {
    const page = await browser.newPage();
    const cases = [
      ['button{outline:none}.absent:focus-visible{outline:2px solid blue}', 'FAIL'],
      ['button{outline:none!important}button:focus-visible{outline:2px solid blue}', 'FAIL'],
      ['button{outline:2px solid blue}', 'FAIL'],
      ['button:focus-visible{outline:none;box-shadow:0 0 0 0 blue}', 'FAIL'],
      ['button:focus-visible{outline:2px solid blue}', 'PASS'],
      [':root{--ring:2px solid blue}button:focus-visible{outline:var(--ring)}', 'PASS'],
      ['button:focus-visible{outline-style:solid;outline-width:2px;outline-color:blue}', 'PASS'],
      ['button:focus-visible{outline:none;box-shadow:0 0 0 3px blue}', 'PASS'],
      ['button{outline:none}button:focus-visible{background:yellow}', 'NEEDS_REVIEW'],
      ['button:focus-visible{outline:2px solid blue;opacity:0}', 'FAIL'],
      ['button:focus-visible{outline:2px solid blue;position:absolute;clip:rect(0,0,0,0)}', 'FAIL'],
      ['button{pointer-events:none}button:focus-visible{outline:2px solid blue}', 'NEEDS_REVIEW'],
      ['button{pointer-events:none}button:focus-visible{outline:2px solid blue;opacity:0}', 'FAIL'],
      ['button{outline:0 solid blue;transition:outline-width .1s}button:focus-visible{outline-width:3px}', 'PASS'],
      ['button{transition:opacity .1s}button:focus-visible{outline:3px solid blue;opacity:0}', 'FAIL'],
      ['@keyframes pulse{to{outline-width:6px}}button:focus-visible{outline:3px solid blue;animation:pulse .2s infinite alternate}', 'NEEDS_REVIEW'],
      ['button:focus-visible{outline:none;box-shadow:0 0 0 3px transparent,0 0 0 0 blue}', 'FAIL'],
      ['button:focus-visible{outline:none;box-shadow:0 0 0 3px blue,0 0 0 0 transparent}', 'PASS'],
    ];
    for (const [css, expected] of cases) {
      await page.setContent(`<style>${css}</style><button>Submit</button>`);
      await page.keyboard.press('Tab');
      const result = await page.evaluate(fs.readFileSync(new URL('../scripts/focus-audit.js', import.meta.url), 'utf8'));
      assert.equal(result.status, expected, JSON.stringify({css,result}));
      assert.equal(result.total, 1);
    }
  } finally { await browser.close(); }
});
