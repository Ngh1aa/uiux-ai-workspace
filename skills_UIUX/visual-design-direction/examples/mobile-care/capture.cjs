const { chromium, webkit } = require('playwright');
const { pathToFileURL } = require('node:url');
const fs = require('node:fs');
const path = require('node:path');
(async()=>{
 const out=path.resolve(process.argv[2] || 'artifacts/mobile-care');fs.mkdirSync(out,{recursive:true});
 const url=pathToFileURL(path.join(__dirname,'index.html')).href;
 const report=[];
 for(const [engine,browserType] of Object.entries({chromium,webkit})){
  const browser=await browserType.launch({headless:true});
  for(const width of [320,390,1280]){
   const page=await browser.newPage({viewport:{width,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(url);
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error(`${engine}/${width}: overflow`);
   await page.getByRole('button',{name:'Đã hủy',exact:true}).click();
   await page.getByRole('heading',{name:'Chưa có lịch phù hợp'}).waitFor();
   await page.getByRole('button',{name:'Xóa bộ lọc'}).click();
   if(await page.locator('.appointment').count()!==2)throw Error('reset failed');
   await page.locator('#search').fill('khám mắt');if(await page.locator('.appointment').count()!==1)throw Error('search failed');
   await page.locator('#search').fill('');
   await page.locator('#next').click();await page.locator('#phone[aria-invalid=true]').waitFor();
   await page.locator('#phone').fill('0901234567');await page.locator('#next').click();
   await page.locator('#confirmation').waitFor({state:'visible'});
   if(await page.locator('form').isVisible())throw Error('hidden form still visible');
   await page.locator('#back').click();if(await page.locator('#phone').inputValue()!=='0901234567')throw Error('lost input');
   await page.locator('#overview .primary').click();if(!(await page.locator('#overview .message').textContent()).includes('CF-0001'))throw Error('no feedback');
   await page.screenshot({path:path.join(out,`${engine}-${width}.png`),fullPage:true});
   await page.addStyleTag({content:'body{font-size:20px}h2{font-size:28px}small{font-size:16px}button,input,select{font-size:20px}'});
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error(`${engine}/${width}: enlarged text overflow`);
   if(errors.length)throw Error(errors.join('\n'));
   report.push({engine,width,task_recovery:'PASS',overflow:'PASS',enlarged_text:'PASS',console:'PASS'});await page.close();
  }
  await browser.close();
 }
 fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1});
