'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {main,requiredBriefs,isCurrentCapture}=require('./run.cjs');
const fs=require('node:fs');
const os=require('node:os');
test('later briefs required from actual addition date',()=>{
 assert.deepEqual(requiredBriefs('2026-10-24'),['01-landing','02-app','03-dashboard']);
 assert.equal(requiredBriefs('2026-10-29').length,5);
});
test('historical evaluations cannot be overwritten',()=>{
 for(const run of ['2026-10-24-v1','2026-10-24-v2'])assert.throws(()=>main([path.join(__dirname,'runs',run),'--refresh']),/lịch sử/);
});
test('output cannot escape the runs directory',()=>assert.throws(()=>main([path.dirname(__dirname)]),/thư mục con/));
test('stale screenshots are never attributed to a new evaluation',()=>{
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'benchmark-capture-'));
 const file=path.join(directory,'old.png');fs.writeFileSync(file,'image');
 const checkedAt=new Date().toISOString();
 fs.utimesSync(file,new Date('2020-01-01'),new Date('2020-01-01'));
 assert.equal(isCurrentCapture(file,checkedAt),false);
 fs.utimesSync(file,new Date(),new Date(Date.now()+1000));
 assert.equal(isCurrentCapture(file,checkedAt),true);
 fs.unlinkSync(file);fs.rmdirSync(directory);
});
