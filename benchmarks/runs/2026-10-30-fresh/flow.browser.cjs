/* Kiểm hành vi thật bằng Playwright cho lượt 2026-10-30-fresh.
 * Mỗi đề có <đề>/scenarios.cjs xuất async (page, pass, expect) => {...}; pass(tên) ghi một kịch bản PASS
 * sau khi các assert trước nó đã qua. Không đọc lượt cũ. */
'use strict';
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const http=require('node:http');
const run=__dirname,root=path.resolve(run,'../../..');
const argv=process.argv;
const output=argv.includes('--json')?path.resolve(argv[argv.indexOf('--json')+1]):path.join(run,'flow-results.json');
const shots=process.env.BENCHMARK_SHOTS?path.resolve(process.env.BENCHMARK_SHOTS):path.join(run,'shots','behavior');
fs.mkdirSync(shots,{recursive:true});
const report={schema_version:1,evidence_type:'actual_playwright_browser_assertions',native_status:'UNKNOWN',independent_review:false,briefs:{}};
const prefix='/benchmarks/runs/2026-10-30-fresh/';
const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.svg':'image/svg+xml','.woff2':'font/woff2','.json':'application/json'};
const server=http.createServer((req,res)=>{let file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');fs.readFile(file,(e,data)=>{if(e){res.writeHead(404).end('Not found');return;}res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');res.end(data);});});
const VIEW={'01-landing':[390,844],'02-app':[390,844],'03-dashboard':[1280,900],'04-multi-role':[1280,800],'05-native':[390,844]};
(async()=>{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const base=`http://127.0.0.1:${server.address().port}${prefix}`;
  const browser=await chromium.launch({headless:true});
  for(const id of Object.keys(VIEW)){
    const file=path.join(run,id,'scenarios.cjs');
    const result=report.briefs[id]={status:'UNKNOWN',browser_status:'UNKNOWN',scenarios:[],console_errors:[]};
    if(id==='05-native')result.native_status='UNKNOWN';
    if(!fs.existsSync(file)){result.reason='Chưa có scenarios.cjs';continue;}
    const [w,h]=VIEW[id];
    const context=await browser.newContext({locale:'vi-VN',viewport:{width:w,height:h},colorScheme:'light',reducedMotion:'reduce'});
    const page=await context.newPage();
    page.on('pageerror',e=>result.console_errors.push(e.message));
    const pass=(name)=>result.scenarios.push({name,status:'PASS'});
    try{
      await page.goto(base+id+'/index.html');
      await page.evaluate(()=>document.fonts.ready);
      await require(file)(page,pass,assert);
      assert.equal(result.console_errors.length,0,result.console_errors.join('\n'));
      pass('Không có lỗi JavaScript trên các luồng đã thực thi');
      await page.screenshot({path:path.join(shots,`${id}-end.png`)});
      result.status='PASS';result.browser_status='PASS';
    }catch(e){result.status='FAIL';result.browser_status='FAIL';result.failure=String(e.message||e).slice(0,600);result.scenarios.push({name:'Kịch bản lỗi',status:'FAIL'});}
    await context.close();
  }
  await browser.close();server.close();
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  process.exitCode=Object.values(report.briefs).every(b=>b.status==='PASS')?0:1;
})().catch(e=>{process.stderr.write(String(e.stack||e)+'\n');process.exitCode=2;});
