/* Chụp từng cặp Sai/Đúng thành img/<mục>.png. Cần Playwright:
 *   NODE_PATH=<thư mục có playwright> node foundations/examples/capture.cjs */
'use strict';
const {chromium}=require('playwright');
const fs=require('node:fs');const path=require('node:path');const http=require('node:http');
const root=path.resolve(__dirname,'../..');const out=path.join(__dirname,'img');fs.mkdirSync(out,{recursive:true});
const mime={'.html':'text/html; charset=utf-8','.css':'text/css','.woff2':'font/woff2','.svg':'image/svg+xml'};
const server=http.createServer((req,res)=>{const file=path.join(root,decodeURIComponent(new URL(req.url,'http://x').pathname));
  if(!file.startsWith(root)||!fs.existsSync(file)){res.writeHead(404).end();return;}
  res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1120,height:900},deviceScaleFactor:1});
  await page.goto(`http://127.0.0.1:${server.address().port}/foundations/examples/index.html`);
  await page.evaluate(()=>document.fonts.ready);
  for(const id of await page.$$eval('[data-pair]',els=>els.map(e=>e.id))){
    await page.locator('#'+id).screenshot({path:path.join(out,`${id}.png`)});
  }
  await browser.close();server.close();})();
