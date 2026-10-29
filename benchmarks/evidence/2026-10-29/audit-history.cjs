'use strict';
// Read-only audit: never writes into historical run folders.
const fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../../..');
(async()=>{
 const file=path.join(root,'benchmarks/runs/2026-10-24-v2/02-app/index.html');
 const text=fs.readFileSync(file,'utf8');
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:390,height:844}});
 await page.goto(pathToFileURL(file).href);await page.evaluate(()=>document.fonts.ready);
 const state=()=>page.evaluate(()=>({screenNames:[...document.querySelectorAll('[data-screen]')].filter(el=>el.getBoundingClientRect().height>0).map(el=>el.dataset.screen),resultCount:document.querySelectorAll('[data-result]').length,text:document.body.innerText}));
 const before=await state();
 await page.locator('[data-screen="Danh sách sân"] [data-checkout-go]').click();
 const after=await state();
 const result={baseline:'d7000758c2e2aa273785455ae91d255fe3be04e0',source:'benchmarks/runs/2026-10-24-v2/02-app/index.html',placeholder_anchors:[...text.matchAll(/<a\b[^>]*href="#"/g)].length,
  action:'Danh sách sân: Đặt sân này',visible_screens_before:before.screenNames,visible_screens_after:after.screenNames,
  result_elements:after.resultCount,visible_text_changed:before.text!==after.text,
  observation:'Action changes no task state/result; historical sample is an artboard gallery with partial selection handlers, not proof of a complete clickable prototype.',
  backend:'UNKNOWN',historical_scores:'Preserved; not rerated'};
 await browser.close();fs.writeFileSync(path.join(__dirname,'history-audit.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
