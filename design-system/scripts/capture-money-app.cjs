// Browser checks + screenshots for examples/money-app.
//   NODE_PATH=<dir with playwright and axe-core> node design-system/scripts/capture-money-app.cjs <out-dir> [engines] [--allow-partial]
// Same evidence contract as capture-example.cjs: every requested engine and axe-core are required
// unless --allow-partial is passed locally, and partial results are labelled PARTIAL, never PASS.
// Checks per engine x viewport x theme: no horizontal overflow, theme init, bundled font, task
// flows (segmented filter, search empty state and reset, hide balance, transfer validation and
// recovery, quick amounts), axe-core WCAG 2.2 A/AA rules, enlarged-text stress, no console errors.
// Automated checks are necessary, not sufficient: they do not replace a screen-reader session.
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

const DS_ROOT = path.resolve(__dirname, '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.json': 'application/json' };
function serve() {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    const file = path.resolve(DS_ROOT, '.' + rel);
    if (!file.startsWith(DS_ROOT + path.sep) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

let browser; let server; let report; let out;
const saveReport = () => { if (report && out) fs.writeFileSync(path.join(out, 'browser-report.json'), JSON.stringify(report, null, 2) + '\n'); };

async function tasks(page, fail) {
  const rows = () => page.locator('#tx-list .mx-row').count();
  if (await rows() !== 6) fail('expected 6 transactions');
  await page.getByRole('button', { name: 'Thu nhập' }).click();
  if (await rows() !== 1) fail('segmented filter failed');
  await page.getByRole('button', { name: 'Tất cả' }).click();
  await page.locator('#tx-search').fill('không có gì');
  await page.getByRole('heading', { name: 'Không tìm thấy giao dịch' }).waitFor();
  await page.getByRole('button', { name: 'Xóa tìm kiếm' }).click();
  if (await rows() !== 6) fail('reset failed');
  if (!(await page.evaluate(() => document.activeElement.id === 'tx-search'))) fail('focus not returned to search');

  await page.locator('#toggle-balance').click();
  if ((await page.locator('#balance .mx-amount__value').textContent()).includes('48')) fail('balance not hidden');
  await page.locator('#toggle-balance').click();
  if (!(await page.locator('#balance .mx-amount__value').textContent()).includes('48.250.000')) fail('balance not restored');

  await page.locator('#amount').fill('99000000');
  await page.locator('#send').click();
  if (!(await page.locator('#amount-error').isVisible())) fail('over-balance error not shown');
  if (!(await page.evaluate(() => document.activeElement.id === 'amount'))) fail('focus not moved to amount');
  await page.getByRole('button', { name: '1.000.000' }).click();
  if (await page.locator('#amount-error').isVisible()) fail('error not cleared after valid amount');
  if ((await page.locator('#send').textContent()).trim() !== 'Chuyển 1.000.000 ₫') fail('button label does not follow amount');
  await page.locator('#send').click();
  await page.locator('#sent').waitFor({ state: 'visible' });
  await page.locator('#sheet-cancel').click();
  if ((await page.locator('#amount').inputValue()) !== '500.000') fail('cancel did not restore draft');
}

(async () => {
  const args = process.argv.slice(2).filter(arg => arg !== '--allow-partial');
  out = path.resolve(args[0] || 'artifacts/money-app');
  const wanted = [...new Set((args[1] || 'chromium,webkit,firefox').split(',').map(e => e.trim()).filter(Boolean))];
  const strict = process.env.CI === 'true' || !process.argv.includes('--allow-partial');
  fs.mkdirSync(out, { recursive: true });
  const widths = [320, 390, 1280];
  report = { status: 'RUNNING', strict, requested_engines: wanted, expected_runs: wanted.length * widths.length * 2,
    pages: ['examples/money-app/index.html'], axe: 'NOT_RUN', engines_skipped: [], runs: [] };
  saveReport();
  if (!wanted.length || wanted.some(e => !['chromium', 'webkit', 'firefox'].includes(e))) throw new Error('engines must name chromium, webkit or firefox');
  if (process.env.CI === 'true' && wanted.length !== 3) throw new Error('CI requires the complete chromium, webkit, firefox engine matrix');
  const playwright = require('playwright');
  let axeSource = null;
  try {
    axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
    if (!axeSource.trim()) throw new Error('axe-core source is empty');
    report.axe = 'RUN';
  } catch (e) { if (strict) throw new Error('axe-core is required for a complete browser review'); }
  server = await serve();
  const url = `http://127.0.0.1:${server.address().port}/examples/money-app/index.html`;
  for (const engine of wanted) {
    try { browser = await playwright[engine].launch({ headless: true }); }
    catch (e) { report.engines_skipped.push({ engine, reason: String(e.message).split('\n')[0] }); continue; }
    for (const width of widths) {
      for (const scheme of ['light', 'dark']) {
        const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
        page.setDefaultTimeout(15000);
        const errors = [];
        page.on('pageerror', e => errors.push(e.message));
        page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
        await page.goto(url);
        await page.evaluate(() => document.fonts.ready);
        const run = { page: 'money-app', engine, width, scheme };
        const fail = msg => { throw new Error(`money-app/${engine}/${width}/${scheme}: ${msg}`); };
        if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) fail('horizontal overflow');
        if ((await page.evaluate(() => document.documentElement.dataset.theme)) !== scheme) fail('theme init');
        if (!(await page.evaluate(() => document.fonts.check('600 16px "Be Vietnam Pro"', 'Chuyển tiền')))) fail('Be Vietnam Pro not loaded');
        if (scheme === 'light') {
          await tasks(page, fail);
          run.task_recovery = 'PASS';
          await page.reload();
          await page.evaluate(() => document.fonts.ready);
        }
        if (axeSource) {
          await page.addScriptTag({ content: axeSource });
          const res = await page.evaluate(async () => {
            const r = await window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } });
            return { violations: r.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help })), passes: r.passes.length, incomplete: r.incomplete.map(v => v.id) };
          });
          run.axe = res;
          if (res.violations.length) fail('axe violations: ' + JSON.stringify(res.violations));
        }
        await page.mouse.move(0, 0);
        await page.screenshot({ path: path.join(out, `money-${engine}-${width}-${scheme}.png`), fullPage: true });
        await page.addStyleTag({ content: 'html{font-size:125%}' });
        if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) fail('overflow at 125% root font size');
        run.enlarged_text = 'PASS';
        if (errors.length) fail('console/page errors: ' + errors.join(' | '));
        run.console = 'PASS';
        run.overflow = 'PASS';
        report.runs.push(run);
        await page.close();
      }
    }
    await browser.close();
    browser = null;
  }
  if (!report.runs.length) throw new Error('no browser engine could be launched');
  if (strict && (report.engines_skipped.length || report.runs.length !== report.expected_runs)) {
    throw new Error('incomplete browser matrix: ' + report.engines_skipped.map(s => s.engine).join(', '));
  }
  report.status = report.engines_skipped.length || !axeSource || report.runs.length !== report.expected_runs ? 'PARTIAL' : 'PASS';
  saveReport();
  console.log(JSON.stringify({ status: report.status, runs: report.runs.length, skipped: report.engines_skipped.map(s => s.engine), axe: report.axe }));
})().catch(e => {
  if (report) { report.status = 'FAIL'; report.error = String(e.message); saveReport(); }
  console.error(e); process.exitCode = 1;
}).finally(async () => { if (browser) await browser.close().catch(() => {}); if (server) server.close(); });
