'use strict';
/* Test cho doctor.cjs, new-project.cjs và design-check.cjs. Không cần trình duyệt:
 * lớp render được thử bằng --skip-render, nên chạy được ở job foundation. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const doctor = require('../doctor.cjs');
const project = require('../new-project.cjs');
const gate = require('../design-check.cjs');

function tmp(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'uiux-tools-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

test('doctor: thư mục công cụ theo UIUX_TOOLS, mặc định trong thư mục nhà', () => {
  assert.equal(doctor.toolsDir({ UIUX_TOOLS: path.join(os.tmpdir(), 'x') }), path.join(os.tmpdir(), 'x'));
  assert.equal(doctor.toolsDir({}), path.join(os.homedir(), '.uiux-tools'));
});

test('doctor: so phiên bản', () => {
  assert.deepEqual(doctor.parseVersion('Python 3.12.10'), [3, 12, 10]);
  assert.equal(doctor.parseVersion('không có số'), null);
  assert.equal(doctor.atLeast([3, 12, 10], [3, 10]), true);
  assert.equal(doctor.atLeast([3, 9, 9], [3, 10]), false);
  assert.equal(doctor.atLeast([4, 0, 0], [3, 10]), true);
});

test('doctor: bỏ qua lệnh Python bị chặn hoặc quá cũ, lấy lệnh đầu tiên chạy được', () => {
  const run = (command, args) => {
    if (command === 'python3') throw new Error('bị chính sách máy chặn');
    if (command === 'python') return { status: 1, stdout: '', stderr: 'blocked' };
    if (command === 'old') return { status: 0, stdout: 'Python 3.8.1' };
    if (command === 'py') return { status: 0, stdout: '', stderr: `Python 3.12.10 ${args.join(' ')}` };
    return { status: 1 };
  };
  const found = doctor.findPython([['python3'], ['python'], ['old'], ['py', '-3']], run);
  assert.deepEqual(found, { command: ['py', '-3'], version: '3.12.10' });
  assert.equal(doctor.findPython([['python3'], ['python']], run), null);
});

test('doctor: Windows thử thêm py -3; UIUX_PYTHON đứng đầu', () => {
  const list = doctor.pythonCandidates({ UIUX_PYTHON: 'C:/py/python.exe' }, 'win32');
  assert.deepEqual(list[0], ['C:/py/python.exe']);
  assert.ok(list.some((c) => c[0] === 'py' && c[1] === '-3'));
  assert.ok(!doctor.pythonCandidates({}, 'linux').some((c) => c[0] === 'py'));
});

test('new-project: mọi loại tạo trang mà CSS đều nằm trong thư mục dự án', (t) => {
  const dir = tmp(t);
  const kinds = Object.keys(project.KINDS);
  const result = project.create(dir, kinds);
  assert.deepEqual(result.pages, kinds.map((kind) => `${kind}.html`));
  for (const page of result.pages) {
    const html = fs.readFileSync(path.join(dir, page), 'utf8');
    const hrefs = [...html.matchAll(/<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"/g)].map((m) => m[1]);
    assert.ok(hrefs.length >= 5, `${page} thiếu CSS`);
    for (const href of hrefs) {
      assert.ok(!href.startsWith('..'), `${page} còn trỏ ra ngoài: ${href}`);
      assert.ok(fs.existsSync(path.join(dir, href)), `${page} trỏ tới file không có: ${href}`);
    }
  }
  const fonts = fs.readFileSync(path.join(dir, 'ds/fonts/fonts.css'), 'utf8');
  for (const m of fonts.matchAll(/url\("\.\/([^"]+)"\)/g)) assert.ok(fs.existsSync(path.join(dir, 'ds/fonts', m[1])), m[1]);
  assert.ok(fs.existsSync(path.join(dir, 'ds/fonts/OFL.txt')), 'font phải đi kèm giấy phép OFL');
  assert.equal(JSON.parse(fs.readFileSync(path.join(dir, 'ds/SOURCE.json'), 'utf8')).repo, ROOT.split(path.sep).join('/'));
});

test('new-project: ghi chú giao lấy mẫu từ CRAFT.md và FLOW.md, brief trỏ về repo', (t) => {
  const dir = tmp(t);
  project.create(dir, ['mobile']);
  const notes = fs.readFileSync(path.join(dir, 'DESIGN-NOTES.md'), 'utf8');
  assert.ok(notes.includes(project.textBlock('CRAFT.md')));
  assert.ok(notes.includes(project.textBlock('FLOW.md')));
  assert.match(notes, /Một điểm táo bạo/);
  assert.match(notes, /Chưa kiểm:/);
  assert.match(notes, /`CHƯA DUYỆT`/);
  const brief = fs.readFileSync(path.join(dir, 'BRAND-BRIEF.md'), 'utf8');
  const links = [...brief.matchAll(/\]\(([^)#]+)(?:#[^)]*)?\)/g)].map((m) => decodeURI(m[1]));
  assert.ok(links.length > 3);
  for (const link of links) assert.ok(fs.existsSync(link), `link trong brief không tồn tại: ${link}`);
});

test('new-project: không ghi đè khi chưa có --force; báo loại không có', (t) => {
  const dir = tmp(t);
  project.create(dir, ['web']);
  fs.writeFileSync(path.join(dir, 'brand.css'), '/* của khách */');
  assert.throws(() => project.create(dir, ['web']), /đã có sẵn.*--force/);
  assert.equal(fs.readFileSync(path.join(dir, 'brand.css'), 'utf8'), '/* của khách */');
  project.create(dir, ['web'], { force: true });
  assert.notEqual(fs.readFileSync(path.join(dir, 'brand.css'), 'utf8'), '/* của khách */');
  assert.throws(() => project.parseArgs(['x', '--kind', 'tv']), /không có loại tv/);
  assert.throws(() => project.create(dir, []), /thiếu --kind/);
});

test('new-project: dừng khi starter có đường dẫn ra ngoài mà chưa được đổi', () => {
  assert.throws(() => project.rewritePage('<link rel="stylesheet" href="../moi/x.css">'), /trỏ ra ngoài/);
  assert.equal(project.rewritePage('<link href="../generated/tokens.css">'), '<link href="ds/tokens.css">');
});

test('design-check: cỡ màn theo loại sản phẩm khớp WORKFLOWS mục 4', () => {
  assert.deepEqual(gate.renderArgs('app', false), ['--width', '390', '--width', '1280']);
  assert.deepEqual(gate.renderArgs('app', true), ['--width', '390', '--width', '1280', '--layout', 'strict']);
  assert.deepEqual(gate.renderArgs('web', false), ['--width', '390', '--width', '768', '--width', '1280', '--width', '1440', '--reflow']);
  const desktop = gate.renderArgs('desktop', true);
  assert.equal(desktop.filter((a) => a === '--layout').length, 1);
  assert.ok(desktop.includes('strict') && desktop.includes('900'));
  assert.throws(() => gate.parseArgs(['a.html', '--kind', 'tv']), /--kind/);
});

test('design-check: lỗi thắng UNKNOWN, UNKNOWN chặn PASS, lớp hành vi không nâng kết luận', () => {
  const layer = (status, required = true) => ({ status, required });
  assert.equal(gate.verdict([layer('PASS'), layer('FAIL'), layer('UNKNOWN')]), 'FAIL');
  assert.equal(gate.verdict([layer('PASS'), layer('UNKNOWN')]), 'UNKNOWN');
  assert.equal(gate.verdict([layer('PASS'), layer('UNKNOWN', false)]), 'CHECKER_PASS');
  assert.equal(gate.verdict([layer('PASS'), layer('FAIL', false)]), 'CHECKER_PASS');
});

test('design-check: gốc phục vụ là thư mục hiện tại, hoặc thư mục chung khi trang nằm ngoài', () => {
  const cwd = path.resolve('/work/repo');
  assert.equal(gate.defaultRoot([path.join(cwd, 'a/x.html')], cwd), cwd);
  const out = [path.resolve('/else/p/a/x.html'), path.resolve('/else/p/b/y.html')];
  assert.equal(gate.defaultRoot(out, cwd), path.resolve('/else/p'));
});

function runGate(args) {
  return spawnSync(process.execPath, [path.join(ROOT, 'scripts/design-check.cjs'), ...args], { encoding: 'utf8' });
}

test('design-check: chưa render thì kết luận UNKNOWN, không bao giờ CHECKER_PASS', (t) => {
  const dir = tmp(t);
  project.create(dir, ['mobile']);
  fs.rmSync(path.join(dir, 'brand.css'));
  const res = runGate([path.join(dir, 'mobile.html'), '--skip-render', '--quiet']);
  assert.equal(res.status, 2, res.stdout + res.stderr);
  const report = JSON.parse(fs.readFileSync(path.join(dir, 'qa/design-check.json'), 'utf8'));
  assert.equal(report.verdict, 'UNKNOWN');
  const byName = Object.fromEntries(report.layers.map((l) => [l.name.split(' (')[0], l.status]));
  assert.equal(byName['Nguồn'], 'PASS');
  assert.equal(byName['Luồng trong nguồn'], 'PASS');
  assert.equal(byName['Render'], 'UNKNOWN');
  assert.equal(byName['Hành vi'], 'UNKNOWN');
  assert.doesNotMatch(res.stdout, /CHECKER_PASS/);
});

test('design-check: lỗi nguồn làm kết luận FAIL dù chưa render', (t) => {
  const dir = tmp(t);
  const page = path.join(dir, 'page.html');
  fs.writeFileSync(page, '<!doctype html><html lang="vi"><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Thử</title></head><body><main><h1>Lịch</h1><p>Toán · Văn · Anh</p><a href="#">Đặt lịch</a></main></body></html>');
  const res = runGate([page, '--skip-render', '--quiet']);
  assert.equal(res.status, 1, res.stdout + res.stderr);
  const report = JSON.parse(fs.readFileSync(path.join(dir, 'qa/design-check.json'), 'utf8'));
  assert.equal(report.verdict, 'FAIL');
  assert.ok(report.layers.filter((l) => l.status === 'FAIL').length >= 1);
  assert.equal(runGate([path.join(dir, 'khong-co.html')]).status, 2);
});

test('link-claude-code: skill trỏ tới file có thật, không ghi đè hay xoá skill của người khác', (t) => {
  const claude = require('../link-claude-code.cjs');
  const dir = tmp(t);
  const file = claude.link(dir);
  const text = fs.readFileSync(file, 'utf8');
  assert.match(text, /^---\nname: uiux-workspace\ndescription: .+\n---\n/);
  assert.doesNotMatch(text, /\{\{REPO\}\}/);
  const paths = [...text.matchAll(/`(?:node )?([^`\s]+\.(?:md|cjs))/g)].map((m) => m[1]).filter((p) => path.isAbsolute(p));
  assert.ok(paths.length >= 5);
  for (const p of paths) assert.ok(fs.existsSync(p), `skill trỏ tới file không có: ${p}`);
  claude.link(dir);
  fs.writeFileSync(file, '---\nname: uiux-workspace\n---\ncủa người khác');
  assert.throws(() => claude.link(dir), /không do lệnh này sinh ra/);
  assert.throws(() => claude.remove(dir), /không do lệnh này sinh ra/);
  fs.writeFileSync(file, claude.render());
  assert.equal(claude.remove(dir), file);
  assert.equal(fs.existsSync(path.dirname(file)), false);
  assert.equal(claude.remove(dir), '');
});
