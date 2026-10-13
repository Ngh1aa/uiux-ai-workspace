'use strict';
// Uses the existing QA/runtime Playwright and axe packages. No install/provider calls.
const { chromium } = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');

async function capture() {
  const base = process.argv[2] || 'http://127.0.0.1:8092/';
  const output = path.resolve(process.argv[3] || 'direction-study-evidence');
  fs.mkdirSync(path.join(output,'screenshots'),{recursive:true});
  const browser = await chromium.launch({headless:true});
  try {
  const context = await browser.newContext();
  const page = await context.newPage();
  const errors = [];
  const rows = [];
  page.on('pageerror',error => errors.push(error.message));
  page.on('requestfailed',request => errors.push('Failed request: '+request.url()));
  const textByCase = new Map();
  const definitions = JSON.parse(fs.readFileSync(path.join(__dirname,'study.json'),'utf8'));
  for (const caseKey of Object.keys(definitions.cases)) {
    for (const candidate of Object.keys(definitions.directions)) {
      for (const width of [1440,1280,1024,768,480,390,360,320]) {
        const height = width <=480 ? 900 : 1000;
        await page.setViewportSize({width,height});
        await page.goto(base+'?case='+caseKey+'&direction='+candidate);
        await page.waitForFunction(() => window.studyReady);
        await page.evaluate(() => document.fonts.ready);
        const measured = await page.evaluate(() => {
          const heading = document.querySelector('h1');
          const style = getComputedStyle(heading);
          const object = document.querySelector('.object');
          return {overflow:document.documentElement.scrollWidth-innerWidth,title_px:parseFloat(style.fontSize),title_line:parseFloat(style.lineHeight)/parseFloat(style.fontSize),font:style.fontFamily,object_y:object.getBoundingClientRect().top,body_px:parseFloat(getComputedStyle(document.body).fontSize),object_padding_px:parseFloat(getComputedStyle(object).paddingTop),text:document.querySelector('main').innerText.split(/\s+/).sort().join(' ')};
        });
        if (measured.overflow > 0) errors.push(`${caseKey}/${candidate}/${width}: overflow ${measured.overflow}`);
        if (textByCase.has(caseKey) && textByCase.get(caseKey)!==measured.text) errors.push(`${caseKey}: changed words across directions or widths`);
        textByCase.set(caseKey,measured.text);
        const viewport = width <768 ? 'mobile':'desktop';
        const expected = definitions.directions[candidate][viewport+'_typography'];
        const expectedDensity = definitions.directions[candidate][viewport+'_density'];
        if (measured.title_px!==expected.title.size_px || measured.body_px!==expected.body.size_px || measured.object_padding_px!==expectedDensity.object_padding_px) errors.push(`${caseKey}/${candidate}/${width}: numeric/render drift`);
        delete measured.text;
        const row = {caseKey,candidate,width,viewport_height:height,measured};
        if ([1440,390,320].includes(width)) {
          row.file=`screenshots/${caseKey}-${candidate}-${width}.png`;
          await page.screenshot({path:path.join(output,row.file),fullPage:true});
          row.sha256=createHash('sha256').update(fs.readFileSync(path.join(output,row.file))).digest('hex');
          const accessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
          row.axe_violations=accessibility.violations.map(value=>value.id);
          if (row.axe_violations.length) errors.push(`${caseKey}/${candidate}/${width}: axe ${row.axe_violations}`);
        }
        rows.push(row);
      }
    }
  }
  await page.goto(base+'?case=constructor&direction=__proto__');
  await page.waitForFunction(()=>window.studyReady);
  if (await page.evaluate(()=>window.studyReady.caseKey!=='enterprise'||window.studyReady.candidate!=='register')) errors.push('Unsafe query fallback');
  await page.keyboard.press('Tab');
  if (await page.evaluate(()=>document.activeElement.className!=='skip')) errors.push('Skip-link focus');
  await page.keyboard.press('Enter');
  await page.keyboard.press('Tab');
  if (await page.evaluate(()=>document.activeElement.className!=='action')) errors.push('Scope action keyboard focus');
  const report={status:errors.length?'FAIL':'PASS',browser:'Chromium',checks:rows.length,rows,errors,human_preference:'UNKNOWN',aesthetic_quality:'UNKNOWN'};
  fs.writeFileSync(path.join(output,'capture-report.json'),JSON.stringify(report,null,2));
  process.stdout.write(JSON.stringify({status:report.status,checks:rows.length,errors})+'\n');
  process.exitCode=errors.length?1:0;
  } finally {
    await browser.close();
  }
}
capture().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
