#!/usr/bin/env node
/**
 * Tự soát giao diện theo TASTE.md trên trang đã render thật (Chromium qua Playwright).
 *
 * Dùng:
 *   node taste-check.cjs <trang.html | URL> [...] [tuỳ chọn]
 *
 * Tuỳ chọn:
 *   --root <thư mục>      thư mục gốc để phục vụ file cục bộ qua HTTP (mặc định: thư mục hiện tại)
 *   --width <px>          bề rộng khung nhìn (mặc định 390 và 1280: điện thoại và máy tính);
 *                         ghi --width là thay mặc định, dùng nhiều lần: --width 390 --width 768 --width 1440
 *   --height <px>         chiều cao khung nhìn (mặc định 844)
 *   --theme light|dark|both   chế độ màu (mặc định both)
 *   --screenshot <thư mục>    lưu ảnh chụp toàn trang
 *   --format png|jpeg     định dạng ảnh chụp (mặc định png; jpeg nhẹ hơn để lưu vào repo)
 *   --name <tên>          tên gốc của file ảnh (mặc định theo tên file trang)
 *   --json <file>         ghi kết quả dạng JSON
 *   --reflow              soát thêm ở 320 px (tương đương phóng to 400% trên 1280 px, WCAG 1.4.10):
 *                         chỉ bắt tràn ngang. Dùng cho website, không dùng cho trang có khung điện thoại cố định
 *   --no-axe              bỏ axe-core dù có cài
 *   --layout strict       coi các cảnh báo bố cục (void, coverage, flat-scale, thin-highlight,
 *                         panel-void, panel-orphan, card-inset, card-wide, table-scroll) là lỗi;
 *                         dùng cho màn desktop và artboard canvas trước khi giao
 *
 * Mỗi phần tử có thuộc tính data-screen="Tên màn" được soát như một màn riêng; trang không có
 * data-screen thì cả trang là một màn. Thêm data-part khi khối chỉ là một pattern mẫu (thư viện
 * pattern), không phải màn đầy đủ: bỏ qua flat-scale và coverage, các luật khác giữ nguyên.
 *
 * LỖI (thoát với mã 1):
 *   - dấu " · " hoặc " • " nối cụm từ
 *   - chữ dưới ngưỡng tương phản WCAG AA (4.5:1, chữ lớn 3:1)
 *   - nhãn điều khiển ngắn (≤ 24 ký tự) bị gãy dòng; heading/nội dung xuống dòng là cảnh báo để review
 *   - nội dung tràn ngang, hoặc chữ bị khung cha cắt mất
 *   - hơn một card nổi bật (khối nền đậm, rộng) trong một màn
 *   - ảnh, font, CSS, script tải lỗi (mã HTTP ≥ 400 hoặc không tải được)
 *   - axe-core (nếu có cài): vi phạm WCAG mức serious hoặc critical
 *   - --reflow: tràn ngang ở 320 px
 *   - quy tắc chủ repo trong TASTE.md:
 *     demo-note      ghi chú bản mẫu trên màn ("dữ liệu mẫu", "bản mẫu không…", "ngữ cảnh mẫu")
 *     template-var   lộ biến mẫu {{…}}
 *     small-text     chữ dưới 12 px
 *     left-bar       thanh màu bên trái card hay dòng (viền trái ≥ 3 px có màu, hoặc vạch ::before)
 *     decor-overlap  hoạ tiết ::before/::after chạy qua dòng chữ (vân nền phủ kín khối thì bỏ qua)
 *     fixed-overlap  nội dung bị thanh cố định ở đáy che khi đã cuộn hết
 *     Chữ trong phần tử có data-annotation (nhãn artboard, gallery) không bị soát các luật chữ trên.
 *   - dashboard và biểu đồ (skill data-visualization-and-dashboard-ux):
 *     chart-donut    donut/pie quá 3 phần (conic-gradient hoặc vòng SVG stroke-dasharray)
 *     chart-name     biểu đồ (canvas, SVG có đường/cột, [role="img"] có vạch, [data-chart]) không có tên
 *                    cho trình đọc màn hình; SVG aria-hidden được coi là trang trí
 *   - card (khối có nền, viền hoặc bóng, bo ≥ 8 px, cao ≥ 72 px; không phải nút, nav, figure, landmark):
 *     card-padding   padding bốn cạnh lệch nhau quá 2 px (padding 0 để khối con lo lề thì bỏ qua)
 *     emoji          emoji trong chữ
 * CẢNH BÁO:
 *   - card ngang hàng có bán kính bo góc khác nhau
 *   - hơn 3 nhóm màu sắc trong một màn
 *   - vùng chạm nhỏ hơn 44 × 44 px
 *   - chữ bị cắt bằng dấu "…"
 *   - dòng cuối của một đoạn chỉ còn một chữ
 *   - chữ cách mép màn dưới 12 px trên màn hẹp (≤ 600 px)
 *   - axe-core: vi phạm mức moderate hoặc minor
 *   - void: khoảng trống dọc lớn (màn: > 160 px hoặc 18% chiều cao; trang: > 320 px hoặc nửa khung nhìn).
 *     Phần tử có data-whitespace được coi là khoảng trống có chủ đích
 *   - coverage: màn rộng ≥ 1024 px mà nội dung dồn một bên, bỏ trống > 28% bề ngang bên phải
 *   - flat-scale: chữ lớn nhất chưa gấp 1,5 lần chữ thân (màn hẹp dưới 600 px: 1,3 lần)
 *   - thin-highlight: card nổi bật dưới 3 dòng chữ hoặc chỉ một cỡ chữ, hoặc nội dung phủ dưới nửa card
 *   - subtitle: dòng giải thích phụ ngay dưới tiêu đề (câu có dấu chấm, hoặc mở đầu "chọn", "bấm", "để"…)
 *   - chart-gauge: vòng tiến độ chỉ để hiện một con số %; dùng số lớn kèm thanh ngang
 *   - chart-values: từ 3 cột trở lên mà không có giá trị đọc được (nhãn số, số trong tên biểu đồ, hay bảng)
 *   - chart-legend: chú giải ô màu tách khỏi biểu đồ; ghi nhãn trực tiếp
 *   - status-series: màu dữ liệu cùng sắc với màu trạng thái (lớp risk, danger, error, alert, warning,
 *     overdue, unusual… hoặc role="alert", data-status) trên cùng màn
 *   - panel-void (bố cục): panel trong lưới trống đáy > 96 px và > 25% chiều cao vì hàng bị kéo giãn
 *   - panel-orphan (bố cục): panel lẻ một mình ở hàng cuối, rộng chưa tới 60% lưới
 *   - card-inset (bố cục): khoảng từ mép card tới nội dung, trên và trái, lệch quá 8 px
 *   - card-wide (bố cục): card ≥ 360 px mà nội dung chỉ chiếm dưới 55% bề ngang trong
 *   - dấu hiệu "AI hoá": gradient-surface (nền hay chữ gradient có màu; data-artwork để miễn cho ảnh, mặt thẻ),
 *     glow (bóng màu phát sáng), tile-rainbow (≥ 3 ô cùng loại tô ≥ 3 sắc), eyebrow (≥ 2 tiêu đề có nhãn nhỏ phía trên)
 *
 * Trang có thể kèm query hoặc hash để chọn màn của app nhiều màn: app.html?screen=home.
 *
 * axe-core là tuỳ chọn: cài cùng chỗ với Playwright (npm install axe-core@4). Không có thì kết
 * quả ghi "axe: chưa chạy"; khi giao phải nói rõ phần khả năng tiếp cận chưa được soát tự động.
 *
 * Đây là tín hiệu tự động, không thay việc nhìn ảnh chụp và không phải bằng chứng đạt WCAG.
 * Cần Playwright. Script tự tìm: NODE_PATH, node_modules gần đó, rồi thư mục npm toàn cục.
 * Không có thì xem mục "Khi không chạy được taste-check" trong scripts/README.md.
 */
'use strict';
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.cjs': 'text/javascript',
  '.mjs': 'text/javascript', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
};

function parseArgs(argv) {
  const opts = { pages: [], root: process.cwd(), widths: [], height: 844, theme: 'both', screenshot: '', json: '', format: 'png', name: '', reflow: false, axe: true, layout: 'warn' };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      if (i + 1 >= argv.length) throw new Error(`thiếu giá trị cho ${arg}`);
      i += 1;
      return argv[i];
    };
    if (arg === '--root') opts.root = path.resolve(next());
    else if (arg === '--width') opts.widths.push(Number(next()));
    else if (arg === '--reflow') opts.reflow = true;
    else if (arg === '--no-axe') opts.axe = false;
    else if (arg === '--layout') opts.layout = next();
    else if (arg === '--height') opts.height = Number(next());
    else if (arg === '--theme') opts.theme = next();
    else if (arg === '--locale') opts.locale = next();
    else if (arg === '--screenshot') opts.screenshot = path.resolve(next());
    else if (arg === '--json') opts.json = path.resolve(next());
    else if (arg === '--format') opts.format = next();
    else if (arg === '--name') opts.name = next();
    else if (arg === '-h' || arg === '--help') opts.help = true;
    else if (arg.startsWith('--')) throw new Error(`không hiểu tuỳ chọn ${arg}`);
    else opts.pages.push(arg);
  }
  if (!opts.widths.length) opts.widths = [390, 1280];
  if (opts.widths.some((w) => !Number.isFinite(w) || w < 200)) throw new Error('--width phải là số ≥ 200');
  if (!['png', 'jpeg'].includes(opts.format)) throw new Error('--format phải là png hoặc jpeg');
  if (!['warn', 'strict'].includes(opts.layout)) throw new Error('--layout phải là warn hoặc strict');
  if (!['light', 'dark', 'both'].includes(opts.theme)) throw new Error('--theme phải là light, dark hoặc both');
  if (opts.locale) {
    try { new Intl.Locale(opts.locale); } catch { throw new Error('--locale phải là BCP 47 hợp lệ, ví dụ vi-VN'); }
  }
  return opts;
}

function serve(root) {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    const file = path.resolve(root, `.${rel}`);
    if ((file !== root && !file.startsWith(root + path.sep)) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404);
      res.end();
      return;
    }
    res.writeHead(200, { 'content-type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

/* Kiểm tra trong trang nằm ở thư mục taste-check/, chia theo nhóm luật. Ghép thành một biểu thức
 * để Playwright chạy trong trang; giữ đúng thứ tự file vì các file dùng chung phạm vi. */
const PAGE_FILES = ['shared.js', 'text.js', 'card.js', 'layout.js', 'chart.js', 'audit.js'];
function pageAuditSource() {
  const dir = path.join(__dirname, 'taste-check');
  const body = PAGE_FILES.map((file) => fs.readFileSync(path.join(dir, file), 'utf8')).join('\n');
  return `(() => {\n${body}\nreturn auditScreens();\n})()`;
}

function searchRoots() {
  const roots = [];
  try {
    const { execSync } = require('node:child_process');
    const globalRoot = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    if (globalRoot) roots.push(globalRoot);
  } catch { /* không có npm */ }
  return roots;
}

function loadAxeSource() {
  const names = ['axe-core/axe.min.js', ...searchRoots().map((r) => path.join(r, 'axe-core', 'axe.min.js'))];
  for (const name of names) {
    try { return fs.readFileSync(require.resolve(name), 'utf8'); } catch { /* thử tiếp */ }
  }
  return '';
}

async function runAxe(tab, source) {
  await tab.addScriptTag({ content: source });
  const result = await tab.evaluate(async () => window.axe.run(document, {
    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] },
    rules: { 'color-contrast': { enabled: false } },
  }));
  const errors = []; const warnings = [];
  for (const v of result.violations) {
    const where = v.nodes.slice(0, 3).map((n) => n.target.join(' ')).join(', ');
    const item = { rule: 'axe', message: `${v.id}: ${v.help} (${v.nodes.length} chỗ: ${where})` };
    (['serious', 'critical'].includes(v.impact) ? errors : warnings).push(item);
  }
  return { name: 'axe-core', errors, warnings };
}

function loadPlaywright() {
  const tries = ['playwright', 'playwright-core'];
  try {
    const { execSync } = require('node:child_process');
    const globalRoot = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    if (globalRoot) tries.push(path.join(globalRoot, 'playwright'), path.join(globalRoot, 'playwright-core'));
  } catch { /* không có npm */ }
  for (const name of tries) {
    try {
      const mod = require(name);
      if (mod && mod.chromium) return mod;
    } catch { /* thử tiếp */ }
  }
  return null;
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || !opts.pages.length) {
    process.stdout.write(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace(/^#!.*\n\/\*\*?/, '').replace(/^ \* ?/gm, ''));
    return opts.help ? 0 : 2;
  }
  const playwright = loadPlaywright();
  if (!playwright) {
    process.stderr.write([
      'Không tìm thấy Playwright, nên chưa soát được trang đã render.',
      'Thử lần lượt:',
      '  1. Cài ngoài repo: npm install --prefix /tmp/pw playwright@1 && npx --prefix /tmp/pw playwright install chromium,',
      '     rồi chạy lại với NODE_PATH=/tmp/pw/node_modules',
      '  2. Không cài được (mạng chặn): mở trang bằng trình duyệt có sẵn, chụp 390 px và 1280 px, sáng và tối,',
      '     rồi soát bằng mắt theo checklist trong TASTE.md',
      '  3. Luôn chạy được: node skills_UIUX/ui-craft-and-visual-qa/scripts/static-check.cjs <trang.html>',
      'Khi giao, ghi rõ đã dùng cách nào và phần nào chưa soát được.',
      '',
    ].join('\n'));
    return 2;
  }
  const axeSource = opts.axe ? loadAxeSource() : '';
  const auditSource = pageAuditSource();
  const server = await serve(opts.root);
  const base = `http://127.0.0.1:${server.address().port}`;
  const themes = opts.theme === 'both' ? ['light', 'dark'] : [opts.theme];
  const browser = await playwright.chromium.launch({ headless: true });
  const results = [];
  try {
    for (const page of opts.pages) {
      let url = page;
      if (!/^https?:\/\//.test(page)) {
        // App nhiều màn chọn màn bằng query hoặc hash (app.html?screen=home): phục vụ file, giữ phần sau.
        const cut = page.search(/[?#]/);
        const filePart = cut >= 0 ? page.slice(0, cut) : page;
        const suffix = cut >= 0 ? page.slice(cut) : '';
        const file = path.resolve(filePart);
        if (!file.startsWith(opts.root + path.sep)) throw new Error(`${page} nằm ngoài --root ${opts.root}`);
        if (!fs.existsSync(file)) throw new Error(`không có file ${filePart}`);
        url = `${base}/${path.relative(opts.root, file).split(path.sep).map(encodeURIComponent).join('/')}${suffix}`;
      }
      const passes = [];
      for (const width of opts.widths) for (const theme of themes) passes.push({ width, theme, reflow: false });
      if (opts.reflow) passes.push({ width: 320, theme: 'light', reflow: true });
      for (const { width, theme, reflow } of passes) {
        {
          const context = await browser.newContext({ viewport: { width, height: opts.height }, colorScheme: theme, reducedMotion: 'reduce', ...(opts.locale ? {locale:opts.locale} : {}) });
          const tab = await context.newPage();
          const consoleErrors = [];
          tab.on('pageerror', (err) => consoleErrors.push(String(err.message || err)));
          const failedRequests = [];
          const cancelledImages = [];
          tab.on('requestfailed', (req) => {
            if (/^data:/.test(req.url())) return;
            const error = req.failure() ? req.failure().errorText : 'lỗi';
            if (req.resourceType() === 'image' && /ERR_ABORTED|NS_BINDING_ABORTED/.test(error)) cancelledImages.push(req.url());
            else failedRequests.push(`${req.url()} (${error})`);
          });
          tab.on('response', (res) => { if (res.status() >= 400) failedRequests.push(`${res.url()} (HTTP ${res.status()})`); });
          await tab.goto(url, { waitUntil: 'networkidle' });
          await tab.evaluate(() => document.fonts && document.fonts.ready);
          let screens = await tab.evaluate(auditSource);
          if (opts.layout === 'strict') {
            const LAYOUT = ['void', 'coverage', 'flat-scale', 'thin-highlight', 'panel-void', 'panel-orphan', 'card-inset', 'card-wide', 'table-scroll'];
            screens = screens.map((sc) => ({
              ...sc,
              errors: [...sc.errors, ...sc.warnings.filter((w) => LAYOUT.includes(w.rule))],
              warnings: sc.warnings.filter((w) => !LAYOUT.includes(w.rule)),
            }));
          }
          // Runtime may replace an image's src. An aborted old request is not a broken
          // final image; keep it visible as a diagnostic, and still fail unresolved images.
          for (const imageUrl of new Set(cancelledImages)) {
            const unresolved = await tab.evaluate((url) => [...document.images].some((img) =>
              (img.currentSrc === url || img.src === url) && (!img.complete || img.naturalWidth === 0)), imageUrl);
            if (unresolved) failedRequests.push(`${imageUrl} (ảnh hiện tại bị hủy tải)`);
            else screens.push({ name: 'Ảnh đổi nguồn', errors: [], warnings: [{ rule: 'request-replaced', message: `Request ảnh cũ bị hủy; không còn ảnh lỗi dùng nguồn này: ${imageUrl}` }] });
          }
          if (reflow) {
            screens = screens.map((sc) => ({ name: `${sc.name} (reflow 320 px)`, errors: sc.errors.filter((e) => e.rule === 'overflow').map((e) => ({ ...e, rule: 'reflow' })), warnings: [] }));
          }
          if (opts.screenshot && !reflow) {
            fs.mkdirSync(opts.screenshot, { recursive: true });
            const stem = opts.name || path.basename(page).replace(/\.[a-z]+$/i, '').replace(/[^\w-]+/g, '-');
            const ext = opts.format === 'jpeg' ? 'jpg' : 'png';
            const shot = { path: path.join(opts.screenshot, `${stem}-${width}-${theme}.${ext}`), fullPage: true, type: opts.format };
            if (opts.format === 'jpeg') shot.quality = 78;
            await tab.screenshot(shot);
          }
          for (const message of consoleErrors) screens.push({ name: 'Lỗi JavaScript', errors: [{ rule: 'script', message }], warnings: [] });
          if (failedRequests.length) screens.push({ name: 'Tài nguyên tải lỗi', errors: [...new Set(failedRequests)].map((message) => ({ rule: 'request', message })), warnings: [] });
          if (axeSource && !reflow) screens.push(await runAxe(tab, axeSource));
          results.push({ page, width, theme, reflow, screens });
          await context.close();
        }
      }
    }
  } finally {
    await browser.close();
    server.close();
  }

  let errorCount = 0;
  let warningCount = 0;
  const label = { light: 'sáng', dark: 'tối' };
  for (const run of results) {
    process.stdout.write(`\n${run.page}  ${run.width}px  ${run.reflow ? 'reflow' : label[run.theme]}\n`);
    for (const screen of run.screens) {
      errorCount += screen.errors.length;
      warningCount += screen.warnings.length;
      const status = screen.errors.length ? 'LỖI' : screen.warnings.length ? 'CẢNH BÁO' : 'ĐẠT';
      process.stdout.write(`  ${status.padEnd(8)} ${screen.name}\n`);
      for (const item of screen.errors) {
        process.stdout.write(`           lỗi       ${item.message}\n`);
        // Trên GitHub Actions: hiện lỗi thành chú thích trên pull request
        if (process.env.GITHUB_ACTIONS) process.stdout.write(`::error title=taste-check ${run.page} ${run.width}px::${screen.name}: ${item.message.replace(/[\r\n]+/g, ' ')}\n`);
      }
      for (const item of screen.warnings) process.stdout.write(`           cảnh báo  ${item.message}\n`);
    }
  }
  const axeStatus = !opts.axe ? 'tắt (--no-axe)' : axeSource ? 'đã chạy' : 'chưa chạy (không có axe-core; npm install axe-core@4 cùng chỗ với Playwright)';
  process.stdout.write(`\naxe: ${axeStatus}\nTổng: ${errorCount} lỗi, ${warningCount} cảnh báo. Vẫn phải nhìn ảnh chụp trước khi giao.\n`);
  if (opts.json) fs.writeFileSync(opts.json, `${JSON.stringify({ errorCount, warningCount, axe: !opts.axe ? 'OFF' : axeSource ? 'RUN' : 'NOT_RUN', results }, null, 2)}\n`);
  return errorCount ? 1 : 0;
}

main().then((code) => { process.exitCode = code; }, (err) => {
  process.stderr.write(`taste-check: ${err.message}\n`);
  process.exitCode = 2;
});
