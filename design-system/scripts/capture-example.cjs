// Browser checks + screenshots for examples/appointment-app.
//   NODE_PATH=<dir with playwright and axe-core> node design-system/scripts/capture-example.cjs <out-dir> [engines] [--allow-partial]
// All requested engines and axe-core are required by default. --allow-partial is local-only;
// its incomplete results are PARTIAL, never PASS. CI always requires the full matrix.
// Checks per engine x viewport: no horizontal overflow, filter/search/empty/reset, invalid input
// recovery, back retains input, feedback toast, no page errors, enlarged-text stress, and (when
// axe-core is resolvable) WCAG 2.2 A/AA automated rules in light and dark themes.
// Automated checks are necessary, not sufficient: they do not replace a screen-reader session.
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

const DS_ROOT = path.resolve(__dirname, '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.json': 'application/json' };
// Static server: axe-core fetches stylesheets, which browsers block on file:// URLs.
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
let browser;
let server;
let report;
let out;
function saveReport() {
  if (report && out) fs.writeFileSync(path.join(out, 'browser-report.json'), JSON.stringify(report, null, 2) + '\n');
}

(async () => {
  const args = process.argv.slice(2).filter(arg => arg !== '--allow-partial');
  out = path.resolve(args[0] || 'artifacts/appointment-app');
  const wanted = [...new Set((args[1] || 'chromium,webkit,firefox').split(',').map(engine => engine.trim()).filter(Boolean))];
  const strict = process.env.CI === 'true' || !process.argv.includes('--allow-partial');
  fs.mkdirSync(out, { recursive: true });
  report = { status: 'RUNNING', strict, requested_engines: wanted, expected_runs: wanted.length * 12,
    pages: ['examples/appointment-app/index.html', 'docs/index.html'], axe: 'NOT_RUN', engines_skipped: [], runs: [] };
  saveReport();
  if (!wanted.length || wanted.some(engine => !['chromium', 'webkit', 'firefox'].includes(engine))) {
    throw new Error('engines must name chromium, webkit or firefox');
  }
  if (process.env.CI === 'true' && wanted.length !== 3) {
    throw new Error('CI requires the complete chromium, webkit, firefox engine matrix');
  }
  const playwright = require('playwright');
  let axeSource = null;
  try {
    axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
    if (!axeSource.trim()) throw new Error('axe-core source is empty');
    report.axe = 'RUN';
  }
  catch (e) { if (strict) throw new Error('axe-core is required for a complete browser review'); }
  server = await serve();
  const base = `http://127.0.0.1:${server.address().port}`;
  const pages = [
    { name: 'app', path: '/examples/appointment-app/index.html', tasks: true },
    { name: 'docs', path: '/docs/index.html', tasks: false },
  ];
  for (const engine of wanted) {
    try { browser = await playwright[engine].launch({ headless: true }); }
    catch (e) { report.engines_skipped.push({ engine, reason: String(e.message).split('\n')[0] }); continue; }
    for (const target of pages) {
    const url = base + target.path;
    for (const width of [320, 390, 1280]) {
      for (const scheme of ['light', 'dark']) {
        const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
        page.setDefaultTimeout(15000);
        const errors = [];
        const log = msg => { if (process.env.CAPTURE_DEBUG) console.error(`[${engine}/${width}/${scheme}] ${msg}`); };
        page.on('pageerror', e => errors.push(e.message));
        page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
        await page.goto(url);
        await page.evaluate(() => document.fonts.ready);
        const run = { page: target.name, engine, width, scheme };
        const fail = msg => { throw new Error(`${target.name}/${engine}/${width}/${scheme}: ${msg}`); };

        if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) fail('horizontal overflow');
        const theme = await page.evaluate(() => document.documentElement.dataset.theme);
        if (theme !== scheme) fail(`theme init ${theme}`);
        if (!(await page.evaluate(() => document.fonts.check('600 16px "Be Vietnam Pro"', 'Đặt lịch')))) fail('Be Vietnam Pro not loaded');

        if (scheme === 'light' && target.tasks) {
          await page.getByRole('button', { name: /Đã hủy/ }).click();
          await page.getByRole('heading', { name: 'Chưa có lịch phù hợp' }).waitFor();
          await page.getByRole('button', { name: 'Xóa bộ lọc' }).click();
          if (await page.locator('.appointment').count() !== 2) fail('reset failed');
          await page.locator('#search').fill('mắt');
          if (await page.locator('.appointment').count() !== 1) fail('search failed');
          await page.locator('#search').fill('');
          await page.locator('#next').click();
          await page.locator('#phone[aria-invalid=true]').waitFor();
          if (!(await page.locator('#phone-error').isVisible())) fail('error not shown');
          if (!(await page.evaluate(() => document.activeElement.id === 'phone'))) fail('focus not moved to invalid field');
          await page.locator('#phone').fill('0901234567');
          await page.locator('#next').click();
          await page.locator('#confirmation').waitFor({ state: 'visible' });
          if (await page.locator('form').isVisible()) fail('form still visible');
          await page.locator('#back').click();
          if (await page.locator('#phone').inputValue() !== '0901234567') fail('lost input on back');
          await page.locator('#overview .primary').click();
          if (!(await page.locator('#overview .message').textContent()).includes('CF-0001')) fail('no feedback');
          run.task_recovery = 'PASS';
          // reset visual state for the screenshot
          await page.reload();
          await page.evaluate(() => document.fonts.ready);
        }

        log('axe');
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
        log('screenshot');
        await page.screenshot({ path: path.join(out, `${target.name}-${engine}-${width}-${scheme}.png`), fullPage: true });
        await page.addStyleTag({ content: 'html{font-size:125%}' });
        if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) fail('overflow at 125% root font size');
        run.enlarged_text = 'PASS';
        if (errors.length) fail('console/page errors: ' + errors.join(' | '));
        run.console = 'PASS';
        run.overflow = 'PASS';
        report.runs.push(run);
        log('close');
        await page.close();
      }
    }
    }
    await browser.close();
    browser = null;
  }
  if (!report.runs.length) throw new Error('no browser engine could be launched');
  if (strict && (report.engines_skipped.length || report.runs.length !== report.expected_runs)) {
    throw new Error('incomplete browser matrix: ' + report.engines_skipped.map(s => s.engine).join(', '));
  }
  report.status = report.engines_skipped.length || !axeSource ? 'PARTIAL' : 'PASS';
  saveReport();
  console.log(JSON.stringify({ status: report.status, runs: report.runs.length, skipped: report.engines_skipped.map(s => s.engine), axe: report.axe }));
})().catch(e => {
  if (report) { report.status = 'FAIL'; report.error = String(e.message); saveReport(); }
  console.error(e); process.exitCode = 1;
})
  .finally(async () => { if (browser) await browser.close().catch(() => {}); if (server) server.close(); });
