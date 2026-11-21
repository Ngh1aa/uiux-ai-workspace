#!/usr/bin/env node
/**
 * Kiểm máy trước khi thiết kế: Node, Python, Playwright, Chromium, axe-core, git.
 * In đúng lệnh dùng được trên máy này, để checker không rơi về UNKNOWN chỉ vì thiếu công cụ.
 *
 * Dùng:
 *   node scripts/doctor.cjs              kiểm và in cách sửa
 *   node scripts/doctor.cjs --install    cài Playwright, Chromium và axe-core vào thư mục công cụ
 *   node scripts/doctor.cjs --json <file>
 *
 * Thư mục công cụ nằm ngoài repo: biến UIUX_TOOLS, mặc định ~/.uiux-tools. taste-check và
 * design-check tự tìm ở đó, không cần đặt NODE_PATH.
 *
 * Thoát 0: soát render chạy được. Thoát 1: thiếu thứ bắt buộc (Node đủ mới, Playwright, Chromium).
 * Python, axe-core và git thiếu chỉ là cảnh báo: phần việc dùng tới chúng phải ghi UNKNOWN khi giao.
 */
'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const MIN_NODE = 20;
const MIN_PYTHON = [3, 10];

function toolsDir(env = process.env) {
  return path.resolve(env.UIUX_TOOLS || path.join(os.homedir(), '.uiux-tools'));
}

/** Thư mục node_modules để tìm Playwright và axe-core, theo thứ tự ưu tiên. */
function moduleRoots(env = process.env) {
  const roots = [path.join(toolsDir(env), 'node_modules')];
  for (const entry of (env.NODE_PATH || '').split(path.delimiter)) if (entry) roots.push(path.resolve(entry));
  try {
    const res = spawnSync('npm root -g', { encoding: 'utf8', shell: true });
    if (res.status === 0 && res.stdout.trim()) roots.push(res.stdout.trim());
  } catch { /* không có npm */ }
  return [...new Set(roots)];
}

function findModule(name, roots = moduleRoots()) {
  for (const candidate of [name, ...roots.map((root) => path.join(root, name))]) {
    try { return require.resolve(candidate); } catch { /* thử tiếp */ }
  }
  return '';
}

function parseVersion(text) {
  const match = /(\d+)\.(\d+)(?:\.(\d+))?/.exec(text || '');
  return match ? [Number(match[1]), Number(match[2]), Number(match[3] || 0)] : null;
}

function atLeast(version, min) {
  for (let i = 0; i < min.length; i += 1) {
    if ((version[i] || 0) > min[i]) return true;
    if ((version[i] || 0) < min[i]) return false;
  }
  return true;
}

/** Các lệnh Python đáng thử. Windows hay chặn bản trong PATH, nên thử cả `py -3` và bản cài riêng. */
function pythonCandidates(env = process.env, platform = process.platform) {
  const list = [];
  if (env.UIUX_PYTHON) list.push([env.UIUX_PYTHON]);
  list.push(['python3'], ['python']);
  if (platform === 'win32') {
    list.push(['py', '-3']);
    const base = env.LOCALAPPDATA && path.join(env.LOCALAPPDATA, 'Programs', 'Python');
    if (base && fs.existsSync(base)) {
      for (const dir of fs.readdirSync(base).sort().reverse()) list.push([path.join(base, dir, 'python.exe')]);
    }
  }
  return list;
}

/** Lệnh Python đầu tiên thật sự chạy được và đủ mới; null khi không có. */
function findPython(candidates = pythonCandidates(), run = spawnSync) {
  for (const command of candidates) {
    let res;
    try { res = run(command[0], [...command.slice(1), '--version'], { encoding: 'utf8', timeout: 15000 }); } catch { continue; }
    if (!res || res.status !== 0) continue;
    const version = parseVersion(`${res.stdout || ''} ${res.stderr || ''}`);
    if (version && atLeast(version, MIN_PYTHON)) return { command, version: version.join('.') };
  }
  return null;
}

function quote(part) {
  return /[\s"]/.test(part) ? `"${part}"` : part;
}

function chromiumPath(playwrightEntry) {
  try {
    const file = require(playwrightEntry).chromium.executablePath();
    return file && fs.existsSync(file) ? file : '';
  } catch { return ''; }
}

function inspect() {
  const dir = toolsDir();
  const roots = moduleRoots();
  const node = parseVersion(process.version);
  const playwright = findModule('playwright', roots) || findModule('playwright-core', roots);
  const chromium = playwright ? chromiumPath(playwright) : '';
  const axe = findModule('axe-core/axe.min.js', roots);
  const python = findPython();
  const git = spawnSync('git', ['--version'], { encoding: 'utf8' });
  const install = 'node scripts/doctor.cjs --install';
  const checks = [
    { name: 'Node', required: true, ok: atLeast(node, [MIN_NODE]), detail: process.version, fix: `Cài Node ${MIN_NODE} trở lên.` },
    { name: 'Playwright', required: true, ok: Boolean(playwright), detail: playwright || 'không thấy', fix: install },
    { name: 'Chromium', required: true, ok: Boolean(chromium), detail: chromium || 'không thấy', fix: install },
    { name: 'axe-core', required: false, ok: Boolean(axe), detail: axe || 'không thấy', fix: install,
      without: 'taste-check ghi "axe: chưa chạy"; khả năng tiếp cận chưa được soát tự động.' },
    { name: 'Python', required: false, ok: Boolean(python),
      detail: python ? `${python.command.map(quote).join(' ')} (${python.version})` : 'không lệnh nào chạy được',
      fix: `Cài Python ${MIN_PYTHON.join('.')} trở lên, hoặc đặt UIUX_PYTHON trỏ tới python chạy được.`,
      without: 'check-brand, inline-icons, review-packet, overlay-check và validate không chạy; ghi UNKNOWN.' },
    { name: 'git', required: false, ok: git.status === 0, detail: (git.stdout || '').trim() || 'không thấy', fix: 'Cài git.',
      without: 'overlay-check và ghi nguồn design system khi tạo dự án không chạy.' },
  ];
  return {
    tools_dir: dir,
    python: python ? python.command : null,
    python_prefix: python ? `${python.command.map(quote).join(' ')} -X utf8` : null,
    checks,
    render_ready: checks.filter((c) => c.required).every((c) => c.ok),
  };
}

function install() {
  const dir = toolsDir();
  fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(path.join(dir, 'package.json'))) {
    fs.writeFileSync(path.join(dir, 'package.json'), `${JSON.stringify({ name: 'uiux-tools', private: true }, null, 2)}\n`);
  }
  const steps = ['npm install --no-audit --no-fund playwright@1 axe-core@4', 'npx playwright install chromium'];
  for (const step of steps) {
    process.stdout.write(`\n> ${step}   (trong ${dir})\n`);
    const res = spawnSync(step, { cwd: dir, stdio: 'inherit', shell: true });
    if (res.status !== 0) {
      process.stderr.write(`doctor: lệnh trên thất bại (mã ${res.status}). Mạng chặn thì theo mục "Khi không chạy được taste-check" trong README công cụ QA.\n`);
      return false;
    }
  }
  return true;
}

function print(report) {
  process.stdout.write(`Thư mục công cụ: ${report.tools_dir}\n\n`);
  for (const check of report.checks) {
    const status = check.ok ? 'CÓ   ' : check.required ? 'THIẾU' : 'KHÔNG';
    process.stdout.write(`  ${status}  ${check.name.padEnd(11)} ${check.detail}\n`);
    if (!check.ok) {
      process.stdout.write(`         sửa: ${check.fix}\n`);
      if (check.without) process.stdout.write(`         chưa sửa thì: ${check.without}\n`);
    }
  }
  if (report.python_prefix) {
    process.stdout.write(`\nLệnh Python của máy này (thay cho "python3" trong tài liệu):\n  ${report.python_prefix} <script.py>\n`);
    process.stdout.write('Chạy bộ test Python thì đặt thêm biến PYTHONUTF8=1: -X utf8 không truyền sang tiến trình con.\n');
  }
  process.stdout.write(report.render_ready
    ? '\nSoát render chạy được: node scripts/design-check.cjs <trang.html>\n'
    : '\nChưa soát render được. Chạy: node scripts/doctor.cjs --install\n');
}

function main(argv) {
  let json = '';
  let doInstall = false;
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--install') doInstall = true;
    else if (argv[i] === '--json') json = argv[++i] || '';
    else if (argv[i] === '-h' || argv[i] === '--help') {
      process.stdout.write(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace(/^#!.*\n\/\*\*?/, '').replace(/^ \* ?/gm, ''));
      return 0;
    } else throw new Error(`không hiểu tuỳ chọn ${argv[i]}`);
  }
  if (doInstall && !install()) return 1;
  const report = inspect();
  print(report);
  if (json) {
    fs.mkdirSync(path.dirname(path.resolve(json)), { recursive: true });
    fs.writeFileSync(json, `${JSON.stringify(report, null, 2)}\n`);
  }
  return report.render_ready ? 0 : 1;
}

module.exports = { toolsDir, moduleRoots, findModule, parseVersion, atLeast, pythonCandidates, findPython, inspect };
if (require.main === module) {
  try { process.exitCode = main(process.argv.slice(2)); } catch (err) {
    process.stderr.write(`doctor: ${err.message}\n`);
    process.exitCode = 2;
  }
}
