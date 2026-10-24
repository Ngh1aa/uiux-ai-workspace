// Test cho taste-check.cjs: một màn đạt và mỗi lỗi một màn cố tình sai.
//   NODE_PATH=<thư mục có playwright> node --test skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.test.cjs
'use strict';
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const SCRIPT = path.join(__dirname, 'taste-check.cjs');
const BASE = `
  body { margin: 0; font: 16px/24px system-ui, sans-serif; color: #17181c; background: #f4f5f9; }
  [data-screen] { width: 390px; padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px; }
  .card { background: #fff; border-radius: 24px; padding: 16px; min-height: 64px; }
  .hero { background: #253a7e; color: #fff; border-radius: 24px; padding: 20px; min-height: 120px; }
  button { min-width: 44px; min-height: 44px; border: 0; border-radius: 16px; background: #253a7e; color: #fff; font: inherit; }
`;

function run(body, extraCss = '', extraArgs = []) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'taste-'));
  fs.writeFileSync(path.join(dir, 'page.html'), `<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>t</title><style>${BASE}${extraCss}</style></head><body>${body}</body></html>`);
  const out = path.join(dir, 'out.json');
  const res = spawnSync(process.execPath, [SCRIPT, path.join(dir, 'page.html'), '--root', dir, '--theme', 'light', '--json', out, ...extraArgs], { encoding: 'utf8' });
  assert.ok(fs.existsSync(out), `không có kết quả JSON:\n${res.stdout}\n${res.stderr}`);
  const data = JSON.parse(fs.readFileSync(out, 'utf8'));
  const screens = data.results.flatMap((r) => r.screens);
  return {
    code: res.status,
    names: screens.map((s) => s.name),
    rules: (name, kind) => screens.filter((s) => s.name === name).flatMap((s) => s[kind]).map((i) => i.rule),
  };
}

const GOOD = `
  <section data-screen="Tốt">
    <div class="hero"><p>Việc cần xử lý</p><p style="font-size:40px;line-height:44px;margin:0">35</p></div>
    <div class="card"><p style="margin:0">Học phí chưa thu</p><p style="margin:0;color:#5f6370">Hạn 15/10</p></div>
    <div class="card"><button type="button">Xử lý</button></div>
  </section>`;

test('màn đúng gu thì không có lỗi nào', () => {
  const r = run(GOOD);
  assert.deepEqual(r.rules('Tốt', 'errors'), []);
  assert.deepEqual(r.rules('Tốt', 'warnings'), []);
  assert.equal(r.code, 0);
});

test('bắt dấu " · " nối cụm từ', () => {
  const r = run('<section data-screen="Dấu"><div class="card">17A0105 · Toán · Khối 5</div></section>');
  assert.ok(r.rules('Dấu', 'errors').includes('dot'));
  assert.equal(r.code, 1);
});

test('bắt chữ thiếu tương phản', () => {
  const r = run('<section data-screen="Mờ"><div class="card"><span style="color:#b8bcc6">Hạn 15/10</span></div></section>');
  assert.ok(r.rules('Mờ', 'errors').includes('contrast'));
});

test('bắt nhãn ngắn bị gãy dòng', () => {
  const r = run('<section data-screen="Gãy"><div class="card"><button type="button" style="width:60px">Điều chỉnh lớp</button></div></section>');
  assert.ok(r.rules('Gãy', 'errors').includes('wrap'));
});

test('bắt nội dung tràn ngang', () => {
  const r = run('<section data-screen="Tràn"><div class="card" style="white-space:nowrap">Một dòng chữ rất dài không được phép xuống dòng nên sẽ tràn khỏi card</div></section>');
  assert.ok(r.rules('Tràn', 'errors').includes('overflow'));
});

test('bắt hơn một card nổi bật trong một màn', () => {
  const r = run('<section data-screen="Hai hero"><div class="hero">A</div><div class="hero">B</div></section>');
  assert.ok(r.rules('Hai hero', 'errors').includes('highlight'));
});

test('thanh điều hướng nền đậm không bị tính là card nổi bật', () => {
  const r = run('<section data-screen="Có nav"><div class="hero">A</div><nav class="hero" aria-label="Chính">B</nav></section>');
  assert.ok(!r.rules('Có nav', 'errors').includes('highlight'));
});

test('cảnh báo bán kính bo góc không đồng nhất', () => {
  const r = run('<section data-screen="Bo góc"><div class="card">A</div><div class="card" style="border-radius:8px">B</div></section>');
  assert.ok(r.rules('Bo góc', 'warnings').includes('radius'));
});

test('cảnh báo quá nhiều nhóm màu', () => {
  const colors = ['#c0392b', '#1f8a4c', '#253a7e', '#b8860b', '#8e44ad'];
  const body = colors.map((c) => `<div class="card"><span style="color:${c};font-weight:700;font-size:24px">Mục</span></div>`).join('');
  const r = run(`<section data-screen="Rối màu">${body}</section>`);
  assert.ok(r.rules('Rối màu', 'warnings').includes('colors'));
});

test('cảnh báo vùng chạm nhỏ', () => {
  const r = run('<section data-screen="Nhỏ"><div class="card"><button type="button" style="min-width:0;min-height:0;width:28px;height:28px;padding:0">+</button></div></section>');
  assert.ok(r.rules('Nhỏ', 'warnings').includes('target'));
});

test('cảnh báo dòng cuối chỉ còn một chữ', () => {
  const r = run('<section data-screen="Mồ côi"><div class="card"><p style="width:30ch;margin:0;font-family:monospace">aaaa bbbb cccc dddd eeee ffff gg</p></div></section>');
  assert.ok(r.rules('Mồ côi', 'warnings').includes('widow'));
});

test('khối chỉ có đường kẻ trên không bị tính là card', () => {
  const r = run('<section data-screen="Kẻ trên"><div class="card">A</div><div style="border-top:1px solid #ccc;width:300px;min-height:80px">B</div></section>');
  assert.ok(!r.rules('Kẻ trên', 'warnings').includes('radius'));
});

test('cảnh báo chữ sát mép màn hẹp', () => {
  const r = run('<section data-screen="Sát mép" style="padding:20px 0"><p style="margin:0">Ba lớp cho người mới</p></section>');
  assert.ok(r.rules('Sát mép', 'warnings').includes('edge'));
});

test('bỏ qua phần chỉ dành cho trình đọc màn hình', () => {
  const r = run('<section data-screen="Ẩn"><div class="card"><span style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap">Một dòng chữ rất dài chỉ để trình đọc màn hình đọc · không hiện</span>A</div></section>');
  assert.deepEqual(r.rules('Ẩn', 'errors'), []);
});

test('bắt chữ bị khung cha cắt mất', () => {
  const r = run('<section data-screen="Bị cắt"><div class="card" style="overflow:hidden;width:200px"><span style="display:inline-block;white-space:nowrap;margin-left:150px">2 ngày còn lại</span></div></section>');
  assert.ok(r.rules('Bị cắt', 'errors').includes('clipped'));
});

test('hai sắc gần nhau của cùng một màu tính là một nhóm', () => {
  const body = ['#2d4592', '#263459', '#c0392b', '#1f8a4c'].map((c) => `<div class="card"><span style="color:${c};font-weight:700;font-size:24px">Mục</span></div>`).join('');
  const r = run(`<section data-screen="Cùng sắc">${body}</section>`);
  assert.ok(!r.rules('Cùng sắc', 'warnings').includes('colors'));
});

// Các mẫu hợp lệ không được báo nhầm (rút ra từ dự án app trung tâm học thêm).
const CHIPS_CSS = `
  .phone { overflow: hidden; }
  .chips { display: flex; gap: 8px; overflow-x: auto; margin: 0 -20px; padding: 0 20px; }
  .chip { flex-shrink: 0; white-space: nowrap; padding: 8px 14px; border-radius: 999px; background: #fff; }
`;

test('vùng chạm nới bằng ::after được tính vào vùng chạm', () => {
  const css = `.small { position: relative; min-width: 80px; min-height: 0; height: 36px; padding: 0 12px; }
    .small::after { content: ""; position: absolute; left: 0; right: 0; top: -4px; bottom: -4px; }`;
  const r = run('<section data-screen="Nới"><div class="card"><button type="button" class="small">Lọc</button></div></section>', css);
  assert.ok(!r.rules('Nới', 'warnings').includes('target'));
});

test('hàng chip cuộn ngang tràn sát mép không bị báo cắt chữ, sát mép hay tràn ngang', () => {
  const chips = ['Tất cả 24', 'Thiếu buổi 2', 'Lớp 4', 'Lớp 5', 'Lớp 7', 'Lớp 8', 'Lớp 9'].map((t) => `<span class="chip">${t}</span>`).join('');
  const r = run(`<section data-screen="Chip" class="phone"><div style="display:flex;flex-direction:column;gap:12px"><div class="card">Tìm</div><div class="chips">${chips}</div></div></section>`, CHIPS_CSS);
  for (const rule of ['clipped', 'overflow']) assert.ok(!r.rules('Chip', 'errors').includes(rule), rule);
  assert.ok(!r.rules('Chip', 'warnings').includes('edge'));
});

test('ô nhập cạnh card không bị tính là lệch bo góc', () => {
  const r = run('<section data-screen="Ô nhập"><div class="card">A</div><div role="textbox" aria-label="Ghi chú" style="background:#fff;border-radius:16px;min-height:96px;padding:12px">Ghi chú</div></section>');
  assert.ok(!r.rules('Ô nhập', 'warnings').includes('radius'));
});

test('data-taste-skip bỏ qua đúng quy tắc được ghi', () => {
  const r = run('<section data-screen="Bỏ qua"><div class="card">A</div><div class="card" style="border-radius:8px" data-taste-skip="radius">B</div><span style="color:#b8bcc6">mờ</span></section>');
  assert.ok(!r.rules('Bỏ qua', 'warnings').includes('radius'));
  assert.ok(r.rules('Bỏ qua', 'errors').includes('contrast'));
});

test('--screen soát từng phần tử khớp selector như một màn', () => {
  const r = run('<div class="screen" style="width:390px"><div class="card">A</div></div><div class="screen" style="width:390px"><div class="card">B · C</div></div>', '', ['--screen', '.screen']);
  assert.deepEqual(r.names, ['t #1', 't #2']);
  assert.ok(r.rules('t #2', 'errors').includes('dot'));
});
