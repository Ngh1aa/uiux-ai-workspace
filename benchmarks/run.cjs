'use strict';
const fs=require('node:fs');
const path=require('node:path');
const {spawnSync}=require('node:child_process');
const {hash,snapshot}=require('./provenance.cjs');
const REPO=path.resolve(__dirname,'..');
const QA=path.join(REPO,'skills_UIUX/ui-craft-and-visual-qa/scripts');
const CHECKERS={render:path.join(QA,'taste-check.cjs'),flow:path.join(QA,'flow-check.cjs'),static:path.join(QA,'static-check.cjs')};
const BRIEFS=fs.readdirSync(path.join(__dirname,'briefs')).filter(f=>f.endsWith('.md')).map(f=>f.slice(0,-3)).sort();
function requiredBriefs(day) {
  return BRIEFS.filter(b=>{
    const text=fs.readFileSync(path.join(__dirname,'briefs',b+'.md'),'utf8');
    return (text.match(/\*\*Thêm vào:\*\*\s*(\d{4}-\d{2}-\d{2})/)?.[1]||'0000-00-00')<=day;
  });
}
function runJson(script,args,json) {
  if(fs.existsSync(json)) fs.unlinkSync(json);
  const res=spawnSync(process.execPath,[script,...args,'--json',json],{encoding:'utf8',maxBuffer:32*1024*1024});
  if(res.stdout)process.stdout.write(res.stdout);
  if(res.stderr)process.stderr.write(res.stderr);
  let data=null;
  try{data=JSON.parse(fs.readFileSync(json,'utf8'));}catch{ /* UNKNOWN, never stale PASS */ }
  return {exit_code:res.status,data};
}
function isCurrentCapture(file, checkedAt) {
  return fs.statSync(file).mtimeMs >= Date.parse(checkedAt);
}
function main(argv=process.argv.slice(2)) {
  const runArg=argv.find(a=>!a.startsWith('--'));
  if(!runArg){process.stderr.write('node benchmarks/run.cjs benchmarks/runs/YYYY-MM-DD-name [--refresh]\n');return 2;}
  const runDir=path.resolve(runArg);
  if(!fs.existsSync(runDir))throw new Error('Không có thư mục lượt chạy');
  const relative=path.relative(path.join(__dirname,'runs'),runDir);
  if(relative.startsWith('..')||path.isAbsolute(relative)||!relative)throw new Error('Run phải là thư mục con benchmarks/runs');
  const name=path.basename(runDir);
  if(['2026-10-24-v1','2026-10-24-v2'].includes(name))throw new Error('Lượt lịch sử bất biến; tạo lượt mới');
  const target=path.join(runDir,'checks.json');
  if(fs.existsSync(target)&&!argv.includes('--refresh'))throw new Error('Đã có kết quả; tạo lượt mới hoặc --refresh riêng lượt local chưa review');
  if(fs.existsSync(path.join(runDir,'reviews')))throw new Error('Đã có review packet: tạo lượt mới để không ghi đè bằng chứng đã review');
  const shots=path.join(runDir,'shots');fs.mkdirSync(shots,{recursive:true});
  const summary={version:2,run:name,checked_at:new Date().toISOString(),source:snapshot(REPO,runDir,CHECKERS),briefs:{}};
  const runtimeFile=path.join(runDir,'flow-results.json'),runtimeScript=path.join(runDir,'flow.browser.cjs');
  const runtime=fs.existsSync(runtimeScript)?runJson(runtimeScript,[],runtimeFile):{exit_code:null,data:null};
  for(const brief of requiredBriefs(name.slice(0,10))) {
    const page=path.join(runDir,brief,'index.html');
    if(!fs.existsSync(page)){summary.briefs[brief]={status:'MISSING'};continue;}
    const render=runJson(CHECKERS.render,[page,'--root',REPO,'--locale','vi-VN','--width','390','--width','1024','--width','1280','--width','1440','--height','900',...(brief==='04-multi-role'?['--layout','strict']:[]),'--reflow','--screenshot',shots,'--format','jpeg','--name',brief],path.join(runDir,`${brief}.render.json`));
    const flow=runJson(CHECKERS.flow,[page],path.join(runDir,`${brief}.flow-static.json`));
    const data=render.data;
    const renderStatus=!data?'UNKNOWN':render.exit_code===0&&data.errorCount===0?'PASS':'FAIL';
    const staticStatus=!flow.data?'UNKNOWN':flow.exit_code===0?'PASS':'FAIL';
    const browser=runtime.data?.briefs?.[brief]||{status:'UNKNOWN',reason:'Chưa kiểm hành vi trình duyệt đề này'};
    let behaviorStatus=['PASS','FAIL','UNKNOWN'].includes(browser.status)?browser.status:'UNKNOWN';
    if(behaviorStatus==='PASS'&&(!Array.isArray(browser.scenarios)||!browser.scenarios.length||browser.scenarios.some(s=>s.status!=='PASS')))behaviorStatus='UNKNOWN';
    // Exit 1 can mean another brief failed. Preserve an executed PASS for this
    // brief; crashes/launch errors without a normal result remain UNKNOWN.
    if(![0,1].includes(runtime.exit_code)&&behaviorStatus==='PASS')behaviorStatus='UNKNOWN';
    const flowStatus=staticStatus==='FAIL'||behaviorStatus==='FAIL'?'FAIL':staticStatus==='PASS'&&behaviorStatus==='PASS'?'PASS':'UNKNOWN';
    const status=renderStatus==='FAIL'||flowStatus==='FAIL'?'FAIL':renderStatus==='PASS'&&flowStatus==='PASS'?'PASS':'UNKNOWN';
    const sampleFiles={};
    const collect=dir=>{for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const full=path.join(dir,ent.name);if(ent.isDirectory())collect(full);else sampleFiles[path.relative(runDir,full).replaceAll('\\','/')]=hash(fs.readFileSync(full));}};
    collect(path.dirname(page));
    const sources=path.join(runDir,'sample-sources.json');
    summary.briefs[brief]={status,checker_exit_code:render.exit_code,errors:data?.errorCount??0,warnings:data?.warningCount??0,axe:data?.axe??'UNKNOWN',
      sample:{source:fs.existsSync(sources)?JSON.parse(fs.readFileSync(sources,'utf8'))[brief]:'local-original; see NOTES.md',files:sampleFiles},
      render:{status:renderStatus,evidence:`${brief}.render.json`,sha256:fs.existsSync(path.join(runDir,`${brief}.render.json`))?hash(fs.readFileSync(path.join(runDir,`${brief}.render.json`))):null},
      flow:{status:flowStatus,static:{status:staticStatus,errors:flow.data?.errorCount??null,evidence:`${brief}.flow-static.json`,sha256:fs.existsSync(path.join(runDir,`${brief}.flow-static.json`))?hash(fs.readFileSync(path.join(runDir,`${brief}.flow-static.json`))):null},browser:{...browser,status:behaviorStatus,evidence:'flow-results.json',sha256:fs.existsSync(runtimeFile)?hash(fs.readFileSync(runtimeFile)):null},native_status:brief==='05-native'?'UNKNOWN':undefined},
      issues:data?.results?.flatMap(r=>r.screens.flatMap(s=>[...s.errors.map(x=>({...x,level:'error'})),...s.warnings.map(x=>({...x,level:'warning'}))].map(x=>({...x,screen:s.name,width:r.width,theme:r.theme}))))??[]};
  }
  summary.source.browser_test_sha256=fs.existsSync(runtimeScript)?hash(fs.readFileSync(runtimeScript)):null;
  summary.source.browser_exit_code=runtime.exit_code;
  const inputFiles={},images={};
  const scan=(dir)=>{for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
    if(['provenance','reviews'].includes(entry.name))continue;
    const file=path.join(dir,entry.name),relative=path.relative(runDir,file).replaceAll('\\','/');
    if(entry.isDirectory())scan(file);
    else if(/\.(?:html|css|cjs|js|svg|ttf|woff2)$/.test(entry.name))inputFiles[relative]=hash(fs.readFileSync(file));
    else if(relative.startsWith('shots/')&&/\.(?:png|jpe?g|webp)$/.test(entry.name)&&isCurrentCapture(file,summary.checked_at))images[relative]=hash(fs.readFileSync(file));
  }};
  scan(runDir);summary.source.run_files=inputFiles;summary.source.images=images;
  fs.writeFileSync(target,JSON.stringify(summary,null,2)+'\n');
  process.stdout.write(`Đã ghi ${path.relative(REPO,target)}\n`);
  return Object.values(summary.briefs).every(b=>b.status==='PASS')?0:1;
}
module.exports={main,requiredBriefs,isCurrentCapture};
if(require.main===module){try{process.exitCode=main();}catch(err){process.stderr.write(err.message+'\n');process.exitCode=2;}}
