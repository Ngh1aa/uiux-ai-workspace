// Test cho taste-check.cjs: một màn đạt và mỗi lỗi một màn cố tình sai.
//   NODE_PATH=<thư mục có playwright> node --test skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.test.cjs
'use strict';
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { execFile } = require('node:child_process');
const http = require('node:http');
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

function run(body, extraCss = '') {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'taste-'));
  fs.writeFileSync(path.join(dir, 'page.html'), `<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>t</title><style>${BASE}${extraCss}</style></head><body>${body}</body></html>`);
  const out = path.join(dir, 'out.json');
  const res = spawnSync(process.execPath, [SCRIPT, path.join(dir, 'page.html'), '--root', dir, '--width', '390', '--theme', 'light', '--json', out], { encoding: 'utf8' });
  assert.ok(fs.existsSync(out), `không có kết quả JSON:\n${res.stdout}\n${res.stderr}`);
  const data = JSON.parse(fs.readFileSync(out, 'utf8'));
  const screens = data.results.flatMap((r) => r.screens);
  return {
    code: res.status,
    rules: (name, kind) => screens.filter((s) => s.name === name).flatMap((s) => s[kind]).map((i) => i.rule),
  };
}

async function runImageCancellation(replace) {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" fill="green"/></svg>';
  const server = http.createServer((req, res) => {
    if (req.url === '/old.svg') {
      setTimeout(() => { res.writeHead(200, { 'content-type': 'image/svg+xml' }); res.end(svg); }, 1000);
    } else if (req.url === '/new.svg') {
      res.writeHead(200, { 'content-type': 'image/svg+xml' }); res.end(svg);
    } else {
      res.writeHead(200, { 'content-type': 'text/html' });
      res.end(`<!doctype html><html lang="vi"><head><title>Image fixture</title></head><body><img src="/old.svg" alt="Minh hoạ" width="64" height="64"><script>setTimeout(() => { ${replace ? 'document.querySelector("img").src="/new.svg"' : 'window.stop()'} }, 50)</script></body></html>`);
    }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'taste-image-'));
  const out = path.join(dir, 'out.json');
  try {
    const code = await new Promise(resolve => execFile(process.execPath,
      [SCRIPT, `http://127.0.0.1:${server.address().port}`, '--width', '390', '--theme', 'light', '--json', out],
      { encoding: 'utf8' }, error => resolve(error ? error.code : 0)));
    return { code, data: JSON.parse(fs.readFileSync(out, 'utf8')) };
  } finally {
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve));
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

test('ảnh đổi nguồn tải thành công không bị báo lỗi request ảnh cũ', async () => {
  const { code, data } = await runImageCancellation(true);
  assert.equal(code, 0);
  assert.ok(data.results.flatMap(r => r.screens).flatMap(s => s.warnings).some(i => i.rule === 'request-replaced'));
});

test('ảnh bị hủy mà vẫn là nguồn hiện tại phải báo lỗi', async () => {
  const { code, data } = await runImageCancellation(false);
  assert.equal(code, 1);
  assert.ok(data.results.flatMap(r => r.screens).flatMap(s => s.errors).some(i => i.rule === 'request'));
});

const GOOD = `
  <section data-screen="Tốt">
    <div class="hero"><p style="margin:0">Việc cần xử lý</p><p style="font-size:40px;line-height:44px;margin:0">35</p><p style="margin:0">12 việc hạn hôm nay</p></div>
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

test('heading xuống dòng được yêu cầu review, không bị nhận nhầm nhãn điều khiển', () => {
  const r = run('<section data-screen="Heading"><h1 style="width:8ch;font:32px/40px system-ui">Pure electric motion.</h1></section>');
  assert.ok(!r.rules('Heading', 'errors').includes('wrap'));
  assert.ok(r.rules('Heading', 'warnings').includes('wrap-review'));
});

test('tên đối tượng nhiều dòng trong rich record không bị coi là CTA ngắn', () => {
  const r = run('<section data-screen="Hồ sơ"><button style="width:150px;white-space:normal"><strong style="display:block;width:7ch">Đặng Quốc Việt</strong><span>Nhổ răng khôn, 8:30, đang khám</span></button></section>');
  assert.ok(!r.rules('Hồ sơ', 'errors').includes('wrap'));
  assert.ok(r.rules('Hồ sơ', 'warnings').includes('wrap-review'));
});

test('nút ngắn bọc icon và span vẫn bắt lỗi gãy nhãn', () => {
  const r = run('<section data-screen="Nút"><button style="width:70px"><svg width="8" height="8" aria-hidden="true"></svg><span>Điều chỉnh lớp</span></button></section>');
  assert.ok(r.rules('Nút', 'errors').includes('wrap'));
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

test('section và footer full-bleed của website không bị coi là card nổi bật', () => {
  const r = run('<main><section class="hero">Giới thiệu</section><section class="hero">Dịch vụ</section></main><footer class="hero">Liên hệ</footer>');
  assert.ok(!r.rules('t', 'errors').includes('highlight'));
});

test('website có hai card thật vẫn bị bắt dù các section nền được bỏ qua', () => {
  const r = run('<main><section class="hero">Giới thiệu</section><div class="hero card-real">A</div><div class="hero card-real">B</div></main><footer class="hero">Liên hệ</footer>', '.card-real { width: 300px; box-sizing: border-box; }');
  assert.ok(r.rules('t', 'errors').includes('highlight'));
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

function runArgs(body, args) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'taste-'));
  fs.writeFileSync(path.join(dir, 'page.html'), `<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>t</title><style>${BASE}</style></head><body>${body}</body></html>`);
  const out = path.join(dir, 'out.json');
  spawnSync(process.execPath, [SCRIPT, path.join(dir, 'page.html'), '--root', dir, '--theme', 'light', '--json', out, ...args], { encoding: 'utf8' });
  return JSON.parse(fs.readFileSync(out, 'utf8'));
}

test('bắt ảnh tải lỗi', () => {
  const data = runArgs('<section data-screen="Ảnh"><div class="card"><img src="khong-co.png" alt="Ảnh thiếu" width="40" height="40"></div></section>', ['--width', '390', '--no-axe']);
  const rules = data.results.flatMap((r) => r.screens).flatMap((s) => s.errors).map((e) => e.rule);
  assert.ok(rules.includes('request'), JSON.stringify(rules));
});

test('--reflow bắt tràn ngang ở 320 px mà 390 px không có', () => {
  const body = '<main><div style="width:360px;height:20px;background:#eee"></div><p>Nội dung</p></main>';
  const data = runArgs(body, ['--width', '390', '--reflow', '--no-axe']);
  const normal = data.results.filter((r) => !r.reflow).flatMap((r) => r.screens).flatMap((s) => s.errors).map((e) => e.rule);
  const reflow = data.results.filter((r) => r.reflow).flatMap((r) => r.screens).flatMap((s) => s.errors).map((e) => e.rule);
  assert.ok(!normal.includes('overflow'), JSON.stringify(normal));
  assert.ok(reflow.includes('reflow'), JSON.stringify(reflow));
});

test('ghi rõ axe có chạy hay không', () => {
  const data = runArgs('<main><p>A</p></main>', ['--width', '390']);
  assert.ok(['RUN', 'NOT_RUN'].includes(data.axe), data.axe);
  if (data.axe === 'RUN') {
    const bad = runArgs('<main><img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" width="10" height="10"></main>', ['--width', '390']);
    const rules = bad.results.flatMap((r) => r.screens).flatMap((s) => [...s.errors, ...s.warnings]).map((e) => e.rule);
    assert.ok(rules.includes('axe'), JSON.stringify(rules));
  }
});

function runWide(body, extra = []) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'taste-'));
  const css = `${BASE} .wide { width: 1440px; height: 900px; padding: 32px; box-sizing: border-box; display: block; }
    .wide h1 { font: 700 32px/40px system-ui; margin: 0 0 16px; } .col { width: 560px; }`;
  fs.writeFileSync(path.join(dir, 'page.html'), `<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>t</title><style>${css}</style></head><body>${body}</body></html>`);
  const out = path.join(dir, 'out.json');
  const res = spawnSync(process.execPath, [SCRIPT, path.join(dir, 'page.html'), '--root', dir, '--width', '1500', '--height', '1000', '--theme', 'light', '--no-axe', '--json', out, ...extra], { encoding: 'utf8' });
  const data = JSON.parse(fs.readFileSync(out, 'utf8'));
  const screens = data.results.flatMap((r) => r.screens);
  return { code: res.status, rules: (name, kind) => screens.filter((s) => s.name === name).flatMap((s) => s[kind]).map((i) => i.rule) };
}

const NARROW = `<section data-screen="Hẹp" class="wide"><main><h1>Đồng ý tham gia</h1>
  <div class="col card"><p style="margin:0">Mỗi mục là một lựa chọn riêng, em đọc kỹ trước khi đánh dấu.</p></div>
  <div class="col card"><button type="button">Đồng ý và tiếp tục</button></div></main></section>`;

test('màn desktop một cột hẹp bị cảnh báo trống đáy và độ phủ ngang', () => {
  const r = runWide(NARROW);
  const w = r.rules('Hẹp', 'warnings');
  assert.ok(w.includes('void'), JSON.stringify(w));
  assert.ok(w.includes('coverage'), JSON.stringify(w));
  assert.equal(r.code, 0);
});

test('--layout strict biến cảnh báo bố cục thành lỗi', () => {
  const r = runWide(NARROW, ['--layout', 'strict']);
  const e = r.rules('Hẹp', 'errors');
  assert.ok(e.includes('void') && e.includes('coverage'), JSON.stringify(e));
  assert.equal(r.code, 1);
});

test('màn desktop chia lưới đầy đủ không bị cảnh báo bố cục', () => {
  const cell = `<div class="card" style="height:340px;box-sizing:border-box"><p style="margin:0;font:700 28px system-ui">412</p>
    <p style="margin:0 0 12px">Tài khoản mới tuần này</p><div role="img" aria-label="Biểu đồ" style="height:220px;background:linear-gradient(#dfe5f5,#fff)"></div></div>`;
  const body = `<section data-screen="Đủ" class="wide" style="display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:min-content;gap:24px">
    <h1 style="grid-column:1/-1">Tổng quan</h1>${cell.repeat(6)}</section>`;
  const r = runWide(body);
  const w = r.rules('Đủ', 'warnings');
  assert.ok(!w.includes('void') && !w.includes('coverage'), JSON.stringify(w));
});

test('khoảng trống có chủ đích được đánh dấu thì không bị cảnh báo', () => {
  const r = runWide(NARROW.replace('</main>', '<div data-whitespace style="height:560px"></div></main>'));
  assert.ok(!r.rules('Hẹp', 'warnings').includes('void'));
});

test('cảnh báo thang chữ phẳng', () => {
  const p = '<p style="margin:0">Học phí tháng mười đã thu đủ cho cả lớp, còn ba bạn nộp sau.</p>';
  const r = run(`<section data-screen="Phẳng"><div class="card"><p style="margin:0;font-size:18px">Học phí</p>${p}${p}</div></section>`);
  assert.ok(r.rules('Phẳng', 'warnings').includes('flat-scale'));
});

test('cảnh báo card nổi bật chỉ có một con số', () => {
  const r = run('<section data-screen="Mỏng"><div class="hero"><p style="font-size:40px;line-height:44px;margin:0">35</p></div></section>');
  assert.ok(r.rules('Mỏng', 'warnings').includes('thin-highlight'));
});

test('data-part bỏ luật đo cả màn nhưng vẫn bắt card nổi bật mỏng', () => {
  const p = '<p style="margin:0">Học phí tháng mười đã thu đủ cho cả lớp, còn ba bạn nộp sau.</p>';
  const r = run(`<section data-part data-screen="Mẫu"><div class="card"><p style="margin:0;font-size:18px">Học phí</p>${p}${p}</div></section>`
    + '<section data-part data-screen="Mẫu mỏng"><div class="hero"><p style="font-size:40px;line-height:44px;margin:0">35</p></div></section>');
  assert.ok(!r.rules('Mẫu', 'warnings').includes('flat-scale'));
  assert.ok(r.rules('Mẫu mỏng', 'warnings').includes('thin-highlight'));
});

test('toast nền đậm không bị tính là card nổi bật', () => {
  const r = run('<section data-screen="Toast"><div class="ds-toast hero" role="status"><p style="margin:0">Đã lưu nháp</p></div></section>');
  assert.ok(!r.rules('Toast', 'warnings').includes('thin-highlight'));
  assert.ok(!r.rules('Toast', 'errors').includes('highlight'));
});

// Quy tắc của chủ repo (TASTE.md), thêm 2026-10-30 từ lỗi thật trên benchmark 2026-10-29-fresh.
test('bắt ghi chú bản mẫu hiện trên màn, bỏ qua nhãn artboard data-annotation', () => {
  const bad = run('<section data-screen="Demo"><div class="card">Ngữ cảnh mẫu lúc 9:15</div><div class="card">Bản mẫu không gửi bài cho cô.</div></section>');
  assert.ok(bad.rules('Demo', 'errors').includes('demo-note'));
  assert.equal(bad.code, 1);
  const ok = run('<section data-screen="Nhãn"><p data-annotation>Dữ liệu minh hoạ theo đề bài</p><div class="card">Lịch học tuần này</div></section>');
  assert.ok(!ok.rules('Nhãn', 'errors').includes('demo-note'));
});

test('bắt biến mẫu lộ trên màn', () => {
  const r = run('<section data-screen="Biến"><div class="card">Đã gửi nhắc cho {{count}} phụ huynh</div></section>');
  assert.ok(r.rules('Biến', 'errors').includes('template-var'));
});

test('bắt chữ dưới 12px', () => {
  const r = run('<section data-screen="Nhỏ"><div class="card"><span style="font-size:10px">Hạn thứ Năm 23/10</span></div></section>');
  assert.ok(r.rules('Nhỏ', 'errors').includes('small-text'));
  assert.ok(!run(GOOD).rules('Tốt', 'errors').includes('small-text'));
});

test('bắt thanh màu bên trái card, không bắt vạch chia mảnh 1px', () => {
  const bad = run('<section data-screen="Vạch"><div class="card" style="border-left:4px solid #c2410c">Đơn #2041 quá hạn</div></section>');
  assert.ok(bad.rules('Vạch', 'errors').includes('left-bar'));
  const pseudo = run('<section data-screen="Vạch giả"><div class="card bar">Đơn #2045 quá hạn</div></section>',
    '.bar{position:relative}.bar::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:#2563eb}');
  assert.ok(pseudo.rules('Vạch giả', 'errors').includes('left-bar'));
  const ok = run('<section data-screen="Chia"><div class="card" style="display:flex"><span>A</span><span style="border-left:1px solid #d0d3db;padding-left:8px">B</span></div></section>');
  assert.ok(!ok.rules('Chia', 'errors').includes('left-bar'));
});

test('bắt hoạ tiết ::before đè lên chữ, không bắt hoạ tiết ở góc trống', () => {
  const css = '.lines{position:relative}.lines::after{content:"";position:absolute;inset:0 0 0 40%;border-left:1px solid #fff;opacity:.3}' +
    '.corner{position:relative}.corner::before{content:"";position:absolute;right:0;bottom:0;width:24px;height:24px;background:#fff;opacity:.2}';
  const bad = run('<section data-screen="Đè"><div class="hero lines"><p style="margin:0">Lượt đặt sắp tới</p><p style="margin:0;font-size:28px;line-height:36px">Sân Phú Nhuận số 3</p><p style="margin:0">18:00 Thứ Sáu 24/10</p></div></section>', css);
  assert.ok(bad.rules('Đè', 'errors').includes('decor-overlap'));
  const ok = run('<section data-screen="Góc"><div class="hero corner"><p style="margin:0">Lượt đặt</p><p style="margin:0;font-size:28px;line-height:36px">Sân 3</p><p style="margin:0">18:00</p></div></section>', css);
  assert.ok(!ok.rules('Góc', 'errors').includes('decor-overlap'));
});

test('bắt nút bị bottom nav che khi đã cuộn hết, không bắt khi có khoảng đệm', () => {
  const frame = (pad) => `<section data-screen="Khung${pad}" style="position:relative;height:600px;padding:0;gap:0">
    <div style="overflow:auto;height:600px;padding:16px ${pad ? '16px 96px' : '16px 0'};box-sizing:border-box">
      <div class="card" style="height:520px">Bài làm</div><button type="button" style="width:100%">Nộp bài</button></div>
    <nav aria-label="Chính" style="position:absolute;left:0;right:0;bottom:0;height:72px;background:#fff">Hôm nay</nav></section>`;
  const bad = run(frame(false));
  assert.ok(bad.rules('Khungfalse', 'errors').includes('fixed-overlap'));
  const ok = run(frame(true));
  assert.ok(!ok.rules('Khungtrue', 'errors').includes('fixed-overlap'));
});

test('cảnh báo dòng giải thích phụ dưới tiêu đề, không cảnh báo dữ liệu', () => {
  const bad = run('<section data-screen="Phụ"><h2 style="font-size:24px;margin:0">Tối nay gần bạn</h2><p style="margin:0">Chọn sân còn giờ, đặt nhanh sau giờ làm.</p></section>');
  assert.ok(bad.rules('Phụ', 'warnings').includes('subtitle'));
  const ok = run('<section data-screen="Dữ liệu"><h2 style="font-size:24px;margin:0">Sân Phú Nhuận</h2><p style="margin:0">Thứ Sáu 24/10, sân số 3</p></section>');
  assert.ok(!ok.rules('Dữ liệu', 'warnings').includes('subtitle'));
});

// Dashboard và biểu đồ, thêm 2026-11-02 từ bài test thật trên Nova Home (xem
// skills_UIUX/data-visualization-and-dashboard-ux/references/nova-dashboard-case.md).
const donut = (stops, inner) => `<div role="img" aria-label="Chi tiêu tháng Mười 1.680 nghìn đồng" style="width:128px;height:128px;border-radius:50%;background:conic-gradient(${stops})">${inner || ''}</div>`;

test('bắt donut quá 3 phần, không bắt donut 3 phần', () => {
  const six = '#8ec2fb 0 37%,#f2a7c1 37% 55%,#f0d27a 55% 67%,#7fd3b6 67% 77%,#b3a6ee 77% 85%,#d7dae2 85% 100%';
  const bad = run(`<section data-screen="Sáu phần"><div class="card">${donut(six)}</div></section>`);
  assert.ok(bad.rules('Sáu phần', 'errors').includes('chart-donut'));
  assert.equal(bad.code, 1);
  const ok = run(`<section data-screen="Ba phần"><div class="card">${donut('#8ec2fb 0 50%,#7fd3b6 50% 80%,#d7dae2 80% 100%')}</div></section>`);
  assert.ok(!ok.rules('Ba phần', 'errors').includes('chart-donut'));
});

test('cảnh báo vòng tiến độ cho một con số', () => {
  const r = run(`<section data-screen="Vòng"><div class="card">${donut('#7fd3b6 0 64%,#e5e7eb 64% 100%', '<strong>64%</strong>')}</div></section>`);
  assert.ok(r.rules('Vòng', 'warnings').includes('chart-gauge'));
});

test('bắt biểu đồ SVG không có tên cho trình đọc màn hình', () => {
  const svg = (attrs) => `<svg ${attrs} width="320" height="120" viewBox="0 0 320 120"><polyline points="0,100 80,60 160,80 240,30 320,50" fill="none" stroke="#3b6fd8" stroke-width="3"/></svg>`;
  const bad = run(`<section data-screen="Không tên"><div class="card">${svg('')}</div></section>`);
  assert.ok(bad.rules('Không tên', 'errors').includes('chart-name'));
  const ok = run(`<section data-screen="Có tên"><div class="card">${svg('role="img" aria-label="Số dư thấp nhất 1.050 ngày 27/9"')}</div></section>`);
  assert.ok(!ok.rules('Có tên', 'errors').includes('chart-name'));
  const decor = run(`<section data-screen="Trang trí"><div class="card">${svg('aria-hidden="true"')}</div></section>`);
  assert.ok(!decor.rules('Trang trí', 'errors').includes('chart-name'));
});

const barChart = (labels, color) => `<div role="img" aria-label="${labels ? 'Doanh thu 6 tháng, cao nhất tháng Hai 3.480' : 'Thu và chi theo tháng'}" style="display:flex;align-items:flex-end;gap:16px;height:120px;width:320px">
  ${[60, 80, 50, 70].map((h, i) => `<span style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%">${labels ? `<b style="font-size:12px">${h * 40}</b>` : ''}<i style="display:block;width:24px;height:${h}%;background:${color || '#3b6fd8'}"></i></span>`).join('')}</div>`;

test('cảnh báo cột không có giá trị đọc được, không cảnh báo khi có nhãn số', () => {
  const bad = run(`<section data-screen="Không số"><section class="card"><h2 style="margin:0">Thu và chi</h2>${barChart(false)}</section></section>`);
  assert.ok(bad.rules('Không số', 'warnings').includes('chart-values'));
  const ok = run(`<section data-screen="Có số"><section class="card"><h2 style="margin:0">Doanh thu</h2>${barChart(true)}</section></section>`);
  assert.ok(!ok.rules('Có số', 'warnings').includes('chart-values'));
});

test('cảnh báo chú giải ô màu tách khỏi biểu đồ', () => {
  const legend = '<p style="margin:0;display:flex;gap:16px"><span><i style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#3b6fd8"></i> Thu</span><span><i style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#d98a2b"></i> Chi</span></p>';
  const r = run(`<section data-screen="Chú giải"><section class="card"><h2 style="margin:0">Thu và chi</h2>${barChart(true)}${legend}</section></section>`);
  assert.ok(r.rules('Chú giải', 'warnings').includes('chart-legend'));
});

test('cảnh báo màu series trùng màu trạng thái, không cảnh báo khi khác sắc', () => {
  const alert = '<a class="card risk" href="#x" style="display:block;background:#fdecf2;color:#a3355f">Giao dịch bất thường cần xem</a>';
  const bad = run(`<section data-screen="Trùng"><section class="card"><h2 style="margin:0">Chi</h2>${barChart(true, '#f2a7c1')}</section>${alert}</section>`);
  assert.ok(bad.rules('Trùng', 'warnings').includes('status-series'));
  const ok = run(`<section data-screen="Khác"><section class="card"><h2 style="margin:0">Chi</h2>${barChart(true, '#3b6fd8')}</section>${alert}</section>`);
  assert.ok(!ok.rules('Khác', 'warnings').includes('status-series'));
  // Chữ mực xanh đen trên dòng trạng thái không phải màu trạng thái (lỗi gặp trên Nova Home).
  const inkAlert = '<a class="card risk" href="#x" style="display:block;background:#fdecf2;color:#16232b">Giao dịch bất thường cần xem</a>';
  const ink = run(`<section data-screen="Mực"><section class="card"><h2 style="margin:0">Chi</h2>${barChart(true, '#3b6fd8')}</section>${inkAlert}</section>`);
  assert.ok(!ink.rules('Mực', 'warnings').includes('status-series'));
});

const panel = (h, extra = '') => `<section class="card" style="box-sizing:border-box;${extra}"><h2 style="margin:0 0 8px">Panel</h2><div style="height:${h}px;background:#dfe5f5"></div></section>`;

test('cảnh báo panel trống đáy do hàng lưới kéo giãn, strict thành lỗi', () => {
  const body = `<section data-screen="Kéo giãn" class="wide" style="height:auto;display:grid;grid-template-columns:2fr 1fr;gap:24px;align-items:stretch">${panel(560)}${panel(160)}</section>`;
  const r = runWide(body);
  assert.ok(r.rules('Kéo giãn', 'warnings').includes('panel-void'), JSON.stringify(r.rules('Kéo giãn', 'warnings')));
  const strict = runWide(body, ['--layout', 'strict']);
  assert.ok(strict.rules('Kéo giãn', 'errors').includes('panel-void'));
  const even = runWide(`<section data-screen="Cân" class="wide" style="height:auto;display:grid;grid-template-columns:2fr 1fr;gap:24px">${panel(560)}${panel(540)}</section>`);
  assert.ok(!even.rules('Cân', 'warnings').includes('panel-void'));
});

test('cảnh báo panel lẻ ở hàng cuối, không cảnh báo khi panel trải hết hàng', () => {
  const bad = runWide(`<section data-screen="Lẻ" class="wide" style="height:auto;display:grid;grid-template-columns:1fr 1fr;gap:24px">${panel(200)}${panel(200)}${panel(200)}</section>`);
  assert.ok(bad.rules('Lẻ', 'warnings').includes('panel-orphan'));
  const ok = runWide(`<section data-screen="Trải" class="wide" style="height:auto;display:grid;grid-template-columns:1fr 1fr;gap:24px">${panel(200)}${panel(200)}${panel(200, 'grid-column:1/-1')}</section>`);
  assert.ok(!ok.rules('Trải', 'warnings').includes('panel-orphan'));
});

test('nhận trang có query string để soát đúng màn của app nhiều màn', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'taste-'));
  fs.writeFileSync(path.join(dir, 'app.html'), `<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>App</title></head><body><main><h1 id="t">x</h1></main>
    <script>document.getElementById('t').textContent = new URLSearchParams(location.search).get('screen') === 'home' ? 'Trang chủ' : 'Màn khác · lỗi';</script></body></html>`);
  const out = path.join(dir, 'out.json');
  const res = spawnSync(process.execPath, [SCRIPT, path.join(dir, 'app.html') + '?screen=home', '--root', dir, '--width', '390', '--theme', 'light', '--no-axe', '--json', out], { encoding: 'utf8' });
  assert.equal(res.status, 0, res.stdout + res.stderr);
  const rules = JSON.parse(fs.readFileSync(out, 'utf8')).results.flatMap((r) => r.screens).flatMap((s) => s.errors).map((e) => e.rule);
  assert.ok(!rules.includes('dot'), JSON.stringify(rules));
});

test('panel cạnh panel trải hai hàng không bị coi là lẻ; chữ cỡ 0 cố ý ẩn không bị báo chữ nhỏ', () => {
  const span = runWide(`<section data-screen="Cạnh" class="wide" style="height:auto;display:grid;grid-template-columns:2fr 1fr;gap:24px">${panel(420, 'grid-row:span 2')}${panel(180)}${panel(180)}</section>`);
  assert.ok(!span.rules('Cạnh', 'warnings').includes('panel-orphan'), JSON.stringify(span.rules('Cạnh', 'warnings')));
  const hidden = run('<section data-screen="Ẩn"><div class="card"><div style="height:12px;background:#a9e5d2;font-size:0;border-radius:99px">Safe now</div></div></section>');
  assert.ok(!hidden.rules('Ẩn', 'errors').includes('small-text'));
});

test('bắt padding card không đều, nhận padding đều', () => {
  const bad = run('<section data-screen="Lệch"><div class="card" style="padding:12px 24px"><h2 style="margin:0">Số dư</h2><p style="margin:0">€1,240</p></div></section>');
  assert.ok(bad.rules('Lệch', 'errors').includes('card-padding'));
  const ok = run('<section data-screen="Đều"><div class="card" style="padding:20px"><h2 style="margin:0">Số dư</h2><p style="margin:0">€1,240</p></div></section>');
  assert.ok(!ok.rules('Đều', 'errors').includes('card-padding'));
  assert.ok(!ok.rules('Đều', 'warnings').includes('card-inset'));
});

test('cảnh báo lề trong card lệch khi lề trên khác lề trái', () => {
  const r = run('<section data-screen="Lề"><div class="card" style="padding:0"><div style="padding:40px 16px 16px"><h2 style="margin:0">Số dư</h2><p style="margin:0">€1,240</p></div></div></section>');
  assert.ok(r.rules('Lề', 'warnings').includes('card-inset'), JSON.stringify(r.rules('Lề', 'warnings')));
});

test('cảnh báo card rộng hơn nhiều so với nội dung, strict thành lỗi', () => {
  const body = '<section data-screen="Rộng" class="wide" style="height:auto"><div class="card" style="padding:24px"><h2 style="margin:0">Số dư</h2><p style="margin:0">€1,240</p></div></section>';
  assert.ok(runWide(body).rules('Rộng', 'warnings').includes('card-wide'));
  assert.ok(runWide(body, ['--layout', 'strict']).rules('Rộng', 'errors').includes('card-wide'));
  const row = runWide('<section data-screen="Ngang" class="wide" style="height:auto"><div class="card" style="padding:24px;display:flex;justify-content:space-between"><h2 style="margin:0">Số dư</h2><p style="margin:0">€1,240</p></div></section>');
  assert.ok(!row.rules('Ngang', 'warnings').includes('card-wide'));
});

test('cảnh báo dấu hiệu AI hoá: nền gradient, glow, icon cầu vồng, overline lặp; data-artwork được miễn', () => {
  const tiles = ['#5b9cf0', '#5cc3a0', '#e0a35b'].map((c) => `<span class="ico" style="display:inline-block;width:40px;height:40px;border-radius:12px;background:${c}"></span>`).join('');
  const r = run(`<section data-screen="AI"><div class="card" style="background:linear-gradient(135deg,#8f7fe0,#5b9cf0);min-height:120px;box-shadow:0 8px 32px rgba(91,156,240,.6)"><h2 style="margin:0">Tổng</h2></div>
    <div class="card"><p style="margin:0;font-size:12px">Tổng quan</p><h2 style="margin:0">Chi tiêu</h2></div><div class="card"><p style="margin:0;font-size:12px">Mục tiêu</p><h2 style="margin:0">Tiết kiệm</h2></div><div>${tiles}</div></section>`);
  const w = r.rules('AI', 'warnings');
  for (const rule of ['gradient-surface', 'glow', 'tile-rainbow', 'eyebrow']) assert.ok(w.includes(rule), `${rule}: ${JSON.stringify(w)}`);
  const art = run('<section data-screen="Thẻ"><div class="card" data-artwork style="background:linear-gradient(135deg,#8f7fe0,#5b9cf0);min-height:120px"><h2 style="margin:0">Thẻ ảo</h2></div></section>');
  assert.ok(!art.rules('Thẻ', 'warnings').includes('gradient-surface'));
});

test('bắt emoji trong chữ, không bắt mũi tên chữ', () => {
  const r = run('<section data-screen="Emoji"><div class="card"><h2 style="margin:0">Xong rồi 🎉</h2></div></section>');
  assert.ok(r.rules('Emoji', 'errors').includes('emoji'));
  const ok = run('<section data-screen="Mũi tên"><div class="card"><h2 style="margin:0">Xem thêm →</h2></div></section>');
  assert.ok(!ok.rules('Mũi tên', 'errors').includes('emoji'));
});
