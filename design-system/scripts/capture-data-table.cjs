// Local browser evidence for the table specimen and two viable teacher directions.
// NODE_PATH=<playwright-and-axe-core> node design-system/scripts/capture-data-table.cjs [output]
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../..');
const output = path.resolve(process.argv[2] || path.join(root, 'design-system/examples/data-table/review'));
const hash = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const mime = { '.html':'text/html; charset=utf-8', '.css':'text/css', '.js':'text/javascript', '.json':'application/json', '.ttf':'font/ttf', '.woff2':'font/woff2' };
let browser, server;
const report = { status:'RUNNING', evidence_class:'AUTHORED_SYNTHETIC_BROWSER_CHECKS', engine:'chromium',
  human_review:'CHƯA DUYỆT', native:'UNKNOWN', screen_reader:'UNKNOWN', rows:[], captures:[], sources:{} };
fs.mkdirSync(output, {recursive:true});
const save = () => fs.writeFileSync(path.join(output,'browser-report.json'),JSON.stringify(report,null,2)+'\n');
save();
(async () => {
  const files = ['design-system/examples/data-table/index.html','design-system/examples/data-table/table.css','design-system/examples/data-table/table.js','design-system/fonts/manifest.json',
    'skills_UIUX/visual-design-direction/examples/decision-lab/cases.json','skills_UIUX/visual-design-direction/examples/decision-lab/lab.css','skills_UIUX/visual-design-direction/examples/decision-lab/lab.js'];
  report.sources = Object.fromEntries(files.map(file => [file,hash(path.join(root,file))]));
  server = http.createServer((req,res) => {
    const file = path.resolve(root, '.' + decodeURIComponent(new URL(req.url,'http://local').pathname));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
    res.writeHead(200,{'content-type':mime[path.extname(file)] || 'application/octet-stream'}); fs.createReadStream(file).pipe(res);
  });
  await new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8');
  browser = await chromium.launch({headless:true});
  for (const width of [320,390,1280]) for (const scheme of ['light','dark']) {
    for (const specimen of ['table','schedule-first','task-first']) {
      const page = await browser.newPage({viewport:{width,height:900},colorScheme:scheme});
      const errors = [], resources = [], remote = [];
      page.on('pageerror',error => errors.push(error.message));
      page.on('console',message => { if(message.type()==='error') errors.push(message.text()); });
      page.on('requestfailed',request => resources.push(request.url()));
      page.on('response',response => {if(response.status()>=400) resources.push(response.url());});
      await page.route('**/*',route => {
        if (new URL(route.request().url()).hostname !== '127.0.0.1') { remote.push(route.request().url()); return route.abort(); }
        return route.continue();
      });
      try {
        const url = specimen === 'table' ? '/design-system/examples/data-table/index.html' : '/skills_UIUX/visual-design-direction/examples/decision-lab/index.html?case=teacher&variant='+specimen;
        await page.goto(base+url);
        if(specimen !== 'table') await page.waitForFunction(() => window.decisionLabReady);
        const loaded = await page.evaluate(async () => {
          await document.fonts.load('550 40px "Source Serif 4"', 'Nguyễn Thị Hường ₫ Ể');
          await document.fonts.load('400 16px "Manrope"', 'Nguyễn Thị Hường ₫ Ể');
          await document.fonts.ready;
          return ['550 40px "Source Serif 4"','400 16px "Manrope"'].every(font => document.fonts.check(font,'Nguyễn Thị Hường ₫ Ể'));
        });
        assert.equal(loaded,true,'bundled serif/sans loaded');
        if(specimen === 'table') {
          assert.equal(await page.locator('#rows tr').count(),3);
          const total = (await page.locator('#rows .ds-table__num').allTextContents()).reduce((sum,value)=>sum+Number(value.replaceAll('.','')),0);
          assert.equal(await page.locator('#total-value').textContent(),new Intl.NumberFormat('vi-VN').format(total),'summary equals source rows');
          await page.locator('#search').fill('SO-102');
          assert.equal(await page.locator('#rows tr').count(),1);
          await page.locator('[data-order="SO-102"]').focus(); await page.keyboard.press('Enter');
          assert.match(await page.locator('#facts').textContent(),/Trần Minh Anh/);
          assert.match(await page.locator('#facts').textContent(),/1\.200\.000 ₫/);
          await page.keyboard.press('Escape');
          assert.equal(await page.locator('[data-order="SO-102"]').evaluate(node=>node===document.activeElement),true,'dialog returns keyboard focus');
          await page.locator('#search').fill('không có đơn');
          assert.equal(await page.locator('#empty').isVisible(),true);
          await page.locator('#clear').click();
          assert.equal(await page.locator('#rows tr').count(),3);
          await page.locator('#status').selectOption('packing');
          assert.equal(await page.locator('#rows tr').count(),1);
          await page.getByRole('button',{name:'Xoá bộ lọc',exact:true}).first().click();
          await page.locator('#sort').focus(); await page.keyboard.press('Enter');
          assert.match(await page.locator('#rows tr').first().textContent(),/SO-102/);
          await page.keyboard.press('Enter');
          assert.match(await page.locator('#rows tr').first().textContent(),/SO-103/);
          await page.locator('#orders').focus();
          if(width < 780) { await page.keyboard.press('End'); await page.keyboard.press('ArrowRight'); }
        } else {
          assert.match(await page.locator('.teacher-board section').first().getAttribute('class'),specimen==='task-first'?/priorities/:/agenda/);
          assert.equal(await page.locator('.teacher-board .agenda li').count(),2);
          assert.equal(await page.locator('.teacher-board .priorities li').count(),2);
          await page.locator('#detail').fill('Giữ tranh kể chuyện và ghi chú mới');
          await page.locator('button[type=submit]').click(); await page.locator('#back').click();
          assert.equal(await page.locator('#detail').inputValue(),'Giữ tranh kể chuyện và ghi chú mới');
        }
        await page.addScriptTag({content:axeSource});
        const axe = await page.evaluate(async () => {
          const result = await window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
          return result.violations.map(item=>({id:item.id,impact:item.impact,nodes:item.nodes.length}));
        });
        assert.deepEqual(axe,[],'axe violations');
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'page reflow');
        if(width!==320) {
          if(specimen==='table') await page.locator('#orders').evaluate(node=>{node.scrollLeft=0;});
          await page.locator('body').click({position:{x:2,y:2}});
          const file = `${specimen}-${width}-${scheme}.png`;
          await page.screenshot({path:path.join(output,file),fullPage:true});
          report.captures.push({file,sha256:hash(path.join(output,file)),specimen,width,scheme,inspected:false});
        }
        await page.addStyleTag({content:'html{font-size:125%}body{font-size:20px}'});
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'enlarged text reflow');
        // Loaded local files continue working with the context offline; no external font source exists.
        await page.context().setOffline(true);
        assert.equal(await page.evaluate(()=>document.fonts.check('400 16px "Manrope"','₫ Nguyễn')),true);
        assert.deepEqual(errors,[]); assert.deepEqual(resources,[]); assert.deepEqual(remote,[]);
        report.rows.push({specimen,width,scheme,status:'PASS',console:'PASS',resources:'PASS',reflow:'PASS',enlarged_text:'PASS',axe:'PASS',fonts_offline:'PASS'});
      } finally { await page.close(); }
    }
  }
  report.status='PASS'; console.log(JSON.stringify({status:report.status,rows:report.rows.length,captures:report.captures.length}));
})().catch(error => {report.status='FAIL';report.error=String(error.stack || error);console.error(error);process.exitCode=1;})
  .finally(async () => {save();if(browser)await browser.close();if(server)server.close();});
