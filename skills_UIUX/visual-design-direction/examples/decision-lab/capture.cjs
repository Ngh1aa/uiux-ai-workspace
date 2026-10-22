// Browser evidence for authored examples, not a beauty or user-research grader.
const { chromium, webkit } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const assert = require('node:assert/strict');
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
(async () => {
  const base = new URL(process.argv[2] || 'http://127.0.0.1:4192/');
  if (!['127.0.0.1', 'localhost', '[::1]'].includes(base.hostname)) throw Error('Use a local specimen server');
  const output = path.resolve(process.argv[3] || 'artifacts/decision-lab');
  fs.mkdirSync(output, { recursive:true });
  const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'cases.json'), 'utf8')).cases;
  const rows = [], captures = [];
  const manifest = {status:'RUNNING',evidenceClass:'AUTHORED_SYNTHETIC_BROWSER_CHECKS',humanUsability:'UNKNOWN',aestheticQuality:'UNKNOWN',rows,captures,
    sources:Object.fromEntries(['index.html','lab.css','lab.js','cases.json'].map(file=>[file,digest(fs.readFileSync(path.join(__dirname,file)))]))};
  const saveReport = () => fs.writeFileSync(path.join(output,'browser-report.json'),JSON.stringify(manifest,null,2));
  saveReport(); // A failed new run must never leave a previous PASS receipt current.
  try {
  for (const [engine, type] of Object.entries({chromium, webkit})) {
    const browser = await type.launch({headless:true});
    try {
      for (const caseKey of Object.keys(cases)) for (const variant of ['fragile','considered']) for (const width of [320,390,1280]) {
        const page = await browser.newPage({viewport:{width,height:900}});
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        try {
          const url = new URL(base); url.search = new URLSearchParams({case:caseKey,variant}).toString();
          await page.goto(url.href); await page.waitForFunction(() => window.decisionLabReady);
          assert.equal(await page.locator('#cases [aria-current]').evaluate(node => {
            const box=node.getBoundingClientRect(); return box.left>=0 && box.right<=innerWidth;
          }),true,'selected case remains visible in mobile navigation');
          assert.equal(await page.locator('.status strong').textContent(), cases[caseKey].status);
          assert.equal(await page.locator('.fact').count(), cases[caseKey].facts.length);
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'overflow');
          const edited = 'Ghi chú đã sửa — ' + caseKey;
          await page.locator('#detail').fill(edited);
          await page.locator('button[type=submit]').click();
          assert.equal(await page.locator('#review-title').evaluate(node => node === document.activeElement), true, 'review focus');
          await page.locator('#back').click();
          assert.equal(await page.locator('#detail').inputValue(), variant==='considered' ? edited : cases[caseKey].input_value);
          await page.locator('#detail').fill(''); await page.locator('button[type=submit]').click();
          assert.equal(await page.locator('#detail').getAttribute('aria-invalid'), 'true');
          await page.locator('#reset').click();
          assert.equal(await page.locator('#detail').inputValue(), cases[caseKey].input_value);
          assert.match(await page.locator('#notes').textContent(), /Đánh đổi/);
          if (cases[caseKey].help) {
            await page.locator('summary').click();
            assert.equal(await page.locator('details').getAttribute('open'), '');
            assert.match(await page.locator('details p').textContent(), /mẫu/);
          }
          if (cases[caseKey].options) {
            await page.locator('#catalog-filter').fill('không có màu này');
            await page.locator('#clear-filter').click();
            assert.equal(await page.locator('[data-option]').count(), 3);
            await page.locator('[data-option="green-m"]').click();
            assert.equal(await page.locator('[data-option="green-m"]').getAttribute('aria-pressed'), 'true');
            assert.match(await page.locator('.facts').textContent(), /Xanh lá/);
          }
          if (engine==='chromium' && (width===390 || variant==='considered' && width===1280)) {
            const file = `${engine}-${caseKey}-${variant}-${width}.png`;
            const target = path.join(output,file); await page.screenshot({path:target,fullPage:true});
            captures.push({file,caseKey,variant,width,sha256:digest(fs.readFileSync(target)),inspected:false});
          }
          await page.addStyleTag({content:'body{font-size:20px}#preview h2{font-size:36px}#preview h3{font-size:24px}input,button{font-size:20px}'});
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'enlarged-text overflow');
          assert.deepEqual(errors, []);
          rows.push({engine,caseKey,variant,width,status:'PASS',recovery:variant==='fragile'?'SEEDED_INPUT_LOSS_REPRODUCED':'INPUT_RETAINED',console:'PASS',overflow:'PASS',enlargedText:'PASS'});
        } finally { await page.close(); }
      }
      const page = await browser.newPage();
      await page.goto(new URL('?case=__proto__&variant=constructor',base).href);
      await page.waitForFunction(() => window.decisionLabReady);
      assert.deepEqual(await page.evaluate(() => ({caseKey:window.decisionLabReady.caseKey,variant:window.decisionLabReady.variant})), {caseKey:'healthcare',variant:'considered'});
      const guide = new URL(await page.locator('footer a').getAttribute('href'),page.url());
      assert.equal((await page.request.get(guide.href)).ok(),true,'practice guide link');
      await page.close();
    } finally { await browser.close(); }
  }
  manifest.status = 'PASS';
  } catch (error) {
    manifest.status = 'FAIL'; manifest.error = String(error); throw error;
  } finally { saveReport(); }
  console.log(JSON.stringify({browserCases:rows.length,captures:captures.length,output}));
})().catch(error => { console.error(error); process.exitCode = 1; });
