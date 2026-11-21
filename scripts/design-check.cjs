#!/usr/bin/env node
/**
 * Cổng soát một lệnh: chạy static-check, flow-check, taste-check và check-brand với đúng cỡ màn
 * của loại sản phẩm, rồi ghi kết luận từng lớp là PASS, FAIL hoặc UNKNOWN.
 *
 * Dùng:
 *   node scripts/design-check.cjs <trang.html> [...] [tuỳ chọn]
 *
 * Tuỳ chọn:
 *   --kind app|web|desktop   app (mặc định): 390 và 1280 px
 *                            web: 390, 768, 1280, 1440 px và reflow 320 px
 *                            desktop: 1024, 1280, 1440 px, cao 900, bố cục strict
 *   --strict                 coi cảnh báo bố cục là lỗi (desktop đã bật sẵn; dùng cho artboard)
 *   --brand <brand.css>      mặc định: brand.css nằm cạnh trang đầu tiên, nếu có
 *   --mode prototype|gallery chuyển cho flow-check
 *   --root <thư mục>         gốc phục vụ file cho taste-check (mặc định: thư mục hiện tại, hoặc thư
 *                            mục chứa các trang khi chúng nằm ngoài thư mục hiện tại)
 *   --out <thư mục>          nơi ghi ảnh và JSON (mặc định qa/ cạnh trang đầu tiên)
 *   --skip-render            không chạy taste-check; lớp render ghi UNKNOWN
 *   --quiet                  chỉ in bảng kết luận; chi tiết nằm trong các file JSON
 *
 * Kết luận:
 *   FAIL          có lớp báo lỗi. Thoát 1.
 *   UNKNOWN       không lỗi, nhưng có lớp bắt buộc chưa chạy được (render, brand). Thoát 2.
 *   CHECKER_PASS  các lớp tự động không còn lỗi. Thoát 0.
 *
 * CHECKER_PASS chưa phải "Đạt". Còn ba việc lệnh này không làm thay: mở từng ảnh ra nhìn và đối chiếu
 * TASTE.md, bấm thử luồng theo FLOW.md (lớp hành vi ở đây luôn UNKNOWN), chấm rubric theo cỡ việc.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { findPython } = require('./doctor.cjs');

const REPO = path.resolve(__dirname, '..');
const QA = path.join(REPO, 'skills_UIUX', 'ui-craft-and-visual-qa', 'scripts');
const KINDS = {
  app: { widths: [390, 1280], args: [] },
  web: { widths: [390, 768, 1280, 1440], args: ['--reflow'] },
  desktop: { widths: [1024, 1280, 1440], args: ['--height', '900', '--layout', 'strict'] },
};

function parseArgs(argv) {
  const opts = { pages: [], kind: 'app', strict: false, brand: '', mode: '', root: '', out: '', skipRender: false, quiet: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      if (i + 1 >= argv.length) throw new Error(`thiếu giá trị cho ${arg}`);
      i += 1;
      return argv[i];
    };
    if (arg === '--kind') opts.kind = next();
    else if (arg === '--strict') opts.strict = true;
    else if (arg === '--brand') opts.brand = next();
    else if (arg === '--mode') opts.mode = next();
    else if (arg === '--root') opts.root = next();
    else if (arg === '--out') opts.out = next();
    else if (arg === '--skip-render') opts.skipRender = true;
    else if (arg === '--quiet') opts.quiet = true;
    else if (arg === '-h' || arg === '--help') opts.help = true;
    else if (arg.startsWith('--')) throw new Error(`không hiểu tuỳ chọn ${arg}`);
    else opts.pages.push(arg);
  }
  if (!KINDS[opts.kind]) throw new Error(`--kind phải là ${Object.keys(KINDS).join(', ')}`);
  if (opts.mode && !['prototype', 'gallery'].includes(opts.mode)) throw new Error('--mode phải là prototype hoặc gallery');
  return opts;
}

/** Tham số taste-check cho một loại sản phẩm. */
function renderArgs(kind, strict) {
  const spec = KINDS[kind];
  const args = spec.widths.flatMap((width) => ['--width', String(width)]).concat(spec.args);
  if (strict && !args.includes('--layout')) args.push('--layout', 'strict');
  return args;
}

function filePart(page) {
  const cut = page.search(/[?#]/);
  return path.resolve(cut >= 0 ? page.slice(0, cut) : page);
}

function inside(dir, file) {
  const rel = path.relative(dir, file);
  return !rel.startsWith('..') && !path.isAbsolute(rel);
}

/** Gốc phục vụ file: thư mục hiện tại khi chứa mọi trang, không thì thư mục chung của các trang. */
function defaultRoot(files, cwd = process.cwd()) {
  if (files.every((file) => inside(cwd, file))) return cwd;
  let root = path.dirname(files[0]);
  while (!files.every((file) => inside(root, file))) {
    const parent = path.dirname(root);
    if (parent === root) break;
    root = parent;
  }
  return root;
}

/**
 * Kết luận chung từ các lớp. Lớp hành vi luôn UNKNOWN ở công cụ này nên không tính vào đây;
 * nó được in riêng để không ai đọc CHECKER_PASS thành "luồng đã đạt".
 */
function verdict(layers) {
  const required = layers.filter((layer) => layer.required);
  if (required.some((layer) => layer.status === 'FAIL')) return 'FAIL';
  if (required.some((layer) => layer.status === 'UNKNOWN')) return 'UNKNOWN';
  return 'CHECKER_PASS';
}

function run(command, args, quiet) {
  const res = spawnSync(command, args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, env: { ...process.env, PYTHONUTF8: '1' } });
  if (!quiet) {
    if (res.stdout) process.stdout.write(res.stdout);
    if (res.stderr) process.stderr.write(res.stderr);
  }
  return res;
}

function readJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

function count(items, key) {
  return (items || []).reduce((total, item) => total + ((item[key] || []).length), 0);
}

function check(opts) {
  const files = opts.pages.map(filePart);
  const missing = files.filter((file) => !fs.existsSync(file));
  if (missing.length) throw new Error(`không có file ${missing.join(', ')}`);
  const out = path.resolve(opts.out || path.join(path.dirname(files[0]), 'qa'));
  const root = path.resolve(opts.root || defaultRoot(files));
  fs.mkdirSync(out, { recursive: true });
  const section = (title) => { if (!opts.quiet) process.stdout.write(`\n=== ${title} ===\n`); };
  const layers = [];

  section('static-check (nguồn HTML/CSS)');
  const staticJson = path.join(out, 'static.json');
  fs.rmSync(staticJson, { force: true });
  const staticRun = run(process.execPath, [path.join(QA, 'static-check.cjs'), ...files, '--json', staticJson], opts.quiet);
  const staticData = readJson(staticJson);
  layers.push({ name: 'Nguồn (static-check)', required: true, evidence: staticJson,
    status: !staticData ? 'UNKNOWN' : staticRun.status === 0 ? 'PASS' : 'FAIL',
    errors: staticData ? staticData.errorCount : null, warnings: staticData ? count(staticData.results, 'warnings') : null });

  section('flow-check (hợp đồng luồng trong nguồn)');
  const flowJson = path.join(out, 'flow-source.json');
  fs.rmSync(flowJson, { force: true });
  const flowRun = run(process.execPath, [path.join(QA, 'flow-check.cjs'), ...files, ...(opts.mode ? ['--mode', opts.mode] : []), '--json', flowJson], opts.quiet);
  const flowData = readJson(flowJson);
  layers.push({ name: 'Luồng trong nguồn (flow-check)', required: true, evidence: flowJson,
    status: !flowData ? 'UNKNOWN' : flowRun.status === 0 ? 'PASS' : 'FAIL',
    errors: flowData ? flowData.errorCount : null, warnings: flowData ? flowData.warningCount : null });

  const renderJson = path.join(out, 'render.json');
  fs.rmSync(renderJson, { force: true });
  let shots = [];
  if (opts.skipRender) {
    layers.push({ name: 'Render (taste-check)', required: true, status: 'UNKNOWN', errors: null, warnings: null, note: 'bỏ qua theo --skip-render' });
  } else {
    section(`taste-check (render, loại ${opts.kind})`);
    const started = Date.now();
    const renderRun = run(process.execPath, [path.join(QA, 'taste-check.cjs'), ...opts.pages, '--root', root,
      ...renderArgs(opts.kind, opts.strict), '--screenshot', out, '--json', renderJson], opts.quiet);
    const renderData = readJson(renderJson);
    // Ảnh của lượt này, không lấy ảnh cũ còn sót trong thư mục làm bằng chứng.
    shots = fs.readdirSync(out).filter((name) => /\.(png|jpe?g)$/i.test(name) && fs.statSync(path.join(out, name)).mtimeMs >= started - 1000).sort();
    layers.push({ name: 'Render (taste-check)', required: true, evidence: renderJson,
      status: !renderData || ![0, 1].includes(renderRun.status) ? 'UNKNOWN' : renderRun.status === 0 ? 'PASS' : 'FAIL',
      errors: renderData ? renderData.errorCount : null, warnings: renderData ? renderData.warningCount : null,
      note: !renderData ? 'không chạy được; xem node scripts/doctor.cjs' : renderData.axe === 'RUN' ? 'axe đã chạy' : 'axe chưa chạy: khả năng tiếp cận chưa soát tự động' });
  }

  const brand = opts.brand ? path.resolve(opts.brand) : path.join(path.dirname(files[0]), 'brand.css');
  if (fs.existsSync(brand)) {
    section('check-brand (lớp thương hiệu)');
    const python = findPython();
    if (!python) {
      layers.push({ name: 'Thương hiệu (check-brand)', required: true, status: 'UNKNOWN', errors: null, warnings: null, note: 'không có Python chạy được; xem node scripts/doctor.cjs' });
    } else {
      const res = run(python.command[0], [...python.command.slice(1), '-X', 'utf8', path.join(REPO, 'design-system', 'scripts', 'check-brand.py'), brand], opts.quiet);
      const text = res.stdout || '';
      layers.push({ name: 'Thương hiệu (check-brand)', required: true, evidence: brand,
        status: res.status === 0 ? 'PASS' : res.status === 1 ? 'FAIL' : 'UNKNOWN',
        errors: (text.match(/^ {2}lỗi /gm) || []).length, warnings: (text.match(/^ {2}cảnh báo /gm) || []).length });
    }
  } else if (opts.brand) {
    throw new Error(`không có file ${opts.brand}`);
  }

  layers.push({ name: 'Hành vi (bấm thử theo FLOW.md)', required: false, status: 'UNKNOWN', errors: null, warnings: null,
    note: 'công cụ này không bấm luồng; ghi PASS/FAIL sau khi chạy kịch bản trình duyệt' });

  const report = { schema_version: 1, kind: opts.kind, pages: opts.pages, root, out, verdict: verdict(layers), layers,
    screenshots: shots, checked_at: new Date().toISOString() };
  fs.writeFileSync(path.join(out, 'design-check.json'), `${JSON.stringify(report, null, 2)}\n`);
  return report;
}

function print(report) {
  process.stdout.write('\n=== Kết luận design-check ===\n');
  for (const layer of report.layers) {
    const counts = layer.errors === null ? '' : `${layer.errors} lỗi, ${layer.warnings} cảnh báo`;
    process.stdout.write(`  ${layer.status.padEnd(8)} ${layer.name.padEnd(34)} ${[counts, layer.note].filter(Boolean).join('; ')}\n`);
  }
  const rel = (file) => {
    const text = path.relative(process.cwd(), file) || '.';
    return (text.startsWith('..') ? file : text).split(path.sep).join('/');
  };
  process.stdout.write(`\n${report.verdict}  (chi tiết: ${rel(path.join(report.out, 'design-check.json'))})\n`);
  if (report.verdict === 'FAIL') process.stdout.write('Sửa lỗi ở đúng tầng gây lỗi rồi chạy lại.\n');
  if (report.verdict === 'UNKNOWN') process.stdout.write('Có lớp chưa chạy được: không kết luận Đạt. Chạy node scripts/doctor.cjs.\n');
  if (report.verdict === 'CHECKER_PASS') {
    process.stdout.write('Checker không còn lỗi. Chưa phải "Đạt", còn:\n');
    process.stdout.write(`  1. Mở ${report.screenshots.length} ảnh trong ${rel(report.out)} và đối chiếu TASTE.md; từng cảnh báo đã sửa hoặc có lý do giữ.\n`);
    process.stdout.write('  2. Bấm thử luồng theo FLOW.md, ghi PASS/FAIL/UNKNOWN từng điều.\n');
    process.stdout.write('  3. Chấm rubric theo cỡ việc; M trở lên có duyệt độc lập.\n');
  }
}

function main(argv) {
  const opts = parseArgs(argv);
  if (opts.help || !opts.pages.length) {
    process.stdout.write(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace(/^#!.*\n\/\*\*?/, '').replace(/^ \* ?/gm, ''));
    return opts.help ? 0 : 2;
  }
  const report = check(opts);
  print(report);
  return { FAIL: 1, UNKNOWN: 2, CHECKER_PASS: 0 }[report.verdict];
}

module.exports = { KINDS, parseArgs, renderArgs, defaultRoot, verdict, check };
if (require.main === module) {
  try { process.exitCode = main(process.argv.slice(2)); } catch (err) {
    process.stderr.write(`design-check: ${err.message}\n`);
    process.exitCode = 2;
  }
}
