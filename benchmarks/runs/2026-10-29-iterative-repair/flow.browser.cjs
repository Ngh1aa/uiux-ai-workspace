'use strict';
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../../..');
const output=process.argv.includes('--json')?process.argv[process.argv.indexOf('--json')+1]:path.join(__dirname,'flow-results.json');
const report={evidence_type:'actual_playwright_assertions',native_status:'UNKNOWN',briefs:{}};
const server=http.createServer((req,res)=>{let file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');fs.readFile(file,(error,data)=>{if(error){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html; charset=utf8','.css':'text/css; charset=utf8','.js':'application/javascript','.svg':'image/svg+xml','.woff2':'font/woff2','.ttf':'font/ttf'})[path.extname(file)]||'application/octet-stream');res.end(data);});});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const base=`http://127.0.0.1:${server.address().port}/benchmarks/runs/${path.basename(__dirname)}/`;
 const browser=await chromium.launch({headless:true});
 for(const brief of ['01-landing','02-app','03-dashboard','04-multi-role','05-native']){
  const result=report.briefs[brief]={status:'UNKNOWN',scenarios:[]};
  const modulePath=path.join(__dirname,brief,'flow.cjs');
  if(!fs.existsSync(modulePath)){result.reason='Chưa có scenario thực thi';continue;}
  for(const width of [390,1280])for(const colorScheme of ['light','dark']){
   const context=await browser.newContext({locale:'vi-VN',viewport:{width,height:width===390?844:900},colorScheme});
   const page=await context.newPage(),errors=[],failed=[];
   page.on('pageerror',e=>errors.push(e.message));
   page.on('requestfailed',request=>failed.push(request.url()));
   page.on('response',response=>{if(response.status()>=400)failed.push(response.url());});
   const dir=process.env.BENCHMARK_SHOTS||path.join(__dirname,'shots','behavior');fs.mkdirSync(dir,{recursive:true});
   const snap=async(p,name)=>{await p.screenshot({path:path.join(dir,`${brief}-${width}-${colorScheme}-${name}.png`),fullPage:true});};
   try{
    await page.goto(base+brief+'/index.html');await page.evaluate(()=>document.fonts.ready);
    const scenarios=await require(modulePath)(page,assert,{base,snap});
    assert.ok(scenarios.length,'Không có assertion scenario');
    assert.equal(errors.length,0,errors.join('\n'));assert.equal(failed.length,0,failed.join('\n'));
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow');
    await snap(page,'result');
    result.scenarios.push(...scenarios.map(s=>({...s,name:`${width}/${colorScheme}: ${s.name}`})),{name:`${width}/${colorScheme}: console resources reflow`,status:'PASS'});
   }catch(error){result.scenarios.push({name:`${width}/${colorScheme}: assertion`,status:'FAIL',details:error.stack});await snap(page,'failure');}
   await context.close();
  }
  result.status=result.scenarios.some(s=>s.status==='FAIL')?'FAIL':result.scenarios.length?'PASS':'UNKNOWN';
  if(brief==='05-native')result.native_status='UNKNOWN';
 }
 await browser.close();await new Promise(resolve=>server.close(resolve));
 fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(Object.fromEntries(Object.entries(report.briefs).map(([key,value])=>[key,value.status]))));
 if(Object.values(report.briefs).some(x=>x.status==='FAIL'))process.exitCode=1;
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
