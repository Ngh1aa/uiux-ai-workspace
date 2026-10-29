'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { checkHtml, parse } = require('./flow-check.cjs');
const check = (html, opts) => checkHtml(html, opts);
const has = (result, rule, level = 'warnings') => result[level].some(item => item.rule === rule);

test('dead-link: placeholder/missing fragment fail only when absence is certain', () => {
  assert.ok(has(check('<a href="#">Đặt lịch</a>'), 'dead-link', 'errors'));
  assert.ok(has(check('<a href="#missing">Mở</a>'), 'dead-link', 'errors'));
  assert.ok(!has(check('<a href="#detail">Mở</a><section id="detail"></section>'), 'dead-link', 'errors'));
  assert.ok(!has(check('<a href="https://example.com">Mở</a>'), 'dead-link', 'errors'));
});
test('submit, in-place and delegated controls do not require data-to/onclick', () => {
  for (const html of [
    '<form action="/booking"><button type="submit">Lưu</button></form>',
    '<form id="f"></form><button form="f">Gửi</button>',
    '<button type="button" data-step="1">2</button>',
    '<button type="button">Back</button>',
    '<a href="#" data-action="sheet">Mở sheet</a><script>document.addEventListener("click", handler)</script>',
  ]) {
    const result = check(html);
    assert.deepEqual(result.errors, []);
    assert.equal(result.flow_status, 'UNKNOWN');
    assert.ok(has(result, 'dead-link', 'unknown'));
  }
});
test('no-entry: root/deep link/explicit entry/gallery exemptions', () => {
  const root = '<section id="root" data-screen="Gốc"></section>';
  assert.ok(has(check(root + '<section id="orphan" data-screen="Khác"></section>'), 'no-entry'));
  for (const entry of ['data-entry', 'data-deep-link']) assert.ok(!has(check(root + `<section id="orphan" data-screen="Khác" ${entry}></section>`), 'no-entry'));
  assert.ok(!has(check(root + '<a href="#detail">Mở</a><section id="detail" data-screen="Chi tiết"></section>'), 'no-entry'));
  assert.ok(!has(check(root + '<section id="orphan" data-screen="Khác"></section>', { mode: 'gallery' }), 'no-entry'));
});
test('no-confirm: infer risk for review, never infer transaction from Thu gọn', () => {
  assert.ok(has(check('<button>Xóa tài khoản</button>'), 'no-confirm'));
  assert.ok(has(check('<button data-risk="high" data-review="none">Chuyển tiền</button>'), 'no-confirm', 'errors'));
  assert.ok(!has(check('<button>Thu gọn</button>'), 'no-confirm'));
  assert.ok(!has(check('<button>Thuộc tính</button>'), 'no-confirm'));
  assert.ok(!has(check('<button>Xóa bộ lọc</button>'), 'no-confirm'));
  assert.ok(!has(check('<button data-review="undo">Xóa bản nháp</button>'), 'no-confirm'));
  assert.ok(!has(check('<button data-review="inline">Thu học phí</button>'), 'no-confirm'));
  for (const role of ['dialog', 'alertdialog']) {
    assert.ok(!has(check(`<button data-to="confirm">Xóa hồ sơ</button><section id="confirm" role="${role}"><button>Hủy</button><button>Xóa hồ sơ</button></section>`), 'no-confirm'));
  }
});
test('no-result: accepts declared result and requires runtime feedback verification', () => {
  assert.ok(has(check('<section role="alertdialog"><button data-confirm-action>Xóa</button></section>'), 'no-result'));
  const result = check('<section role="dialog"><button data-confirm-action data-to="done">Xóa</button></section><p id="done" data-result role="status">Đã xóa</p>');
  assert.ok(!has(result, 'no-result'));
  assert.ok(has(result, 'no-result', 'unknown'));
});
test('disabled-no-reason: linked or nearby useful reason accepted', () => {
  assert.ok(has(check('<button data-primary disabled>Gửi</button>'), 'disabled-no-reason'));
  assert.ok(has(check('<button data-primary disabled aria-describedby="empty">Gửi</button><p id="empty"></p>'), 'disabled-no-reason'));
  assert.ok(!has(check('<button data-primary disabled aria-describedby="reason">Gửi</button><p id="reason">Chọn người nhận</p>'), 'disabled-no-reason'));
  assert.ok(!has(check('<div><button data-primary disabled>Gửi</button><p data-reason>Chọn người nhận</p></div>'), 'disabled-no-reason'));
  assert.ok(!has(check('<button disabled>Gửi</button>'), 'disabled-no-reason'));
});
test('row-mismatch: review inconsistent affordances without rejecting purposeful rows', () => {
  assert.ok(has(check('<ul><li><a href="/1" data-chevron>A</a></li><li>B</li></ul>'), 'row-mismatch'));
  assert.ok(!has(check('<ul><li><a href="/1" data-chevron>A</a></li><li><a href="/2" data-chevron>B</a></li></ul>'), 'row-mismatch'));
  assert.ok(!has(check('<ul><li>A</li><li>B</li></ul>'), 'row-mismatch'));
});
test('label-long: recommendation, permits numbers, time slots and necessary context', () => {
  assert.ok(has(check('<button>Gửi báo cáo cho lớp</button>'), 'label-long'));
  for (const html of ['<button>2</button>', '<button>09:30</button>', '<button>Chọn 2 người</button>', '<button data-label-context="consequence">Xóa vĩnh viễn hồ sơ</button>']) assert.ok(!has(check(html), 'label-long'));
});
test('time-no-date: date in screen context, time slot, semantic datetime and status clock valid', () => {
  assert.ok(has(check('<article><p>09:30</p></article>'), 'time-no-date'));
  for (const html of [
    '<section data-screen="Lịch"><h1>Thứ Năm 29/10</h1><p>09:30</p></section>',
    '<button data-time-slot>09:30</button>',
    '<time datetime="2026-10-29T09:30">09:30</time>',
    '<span class="app-status__time">9:41</span>',
    '<section data-screen="Tối nay"><h1>Tối nay</h1><p>19:00</p></section>',
    '<div hidden><p>19:00</p></div>',
  ]) assert.ok(!has(check(html), 'time-no-date'), html);
});
test('template-leak: visible interpolation/internal notes fail, sample code and scripts exempt', () => {
  assert.ok(has(check('<p>{{count}} người</p>'), 'template-leak', 'errors'));
  assert.ok(has(check('<p>TODO sửa bản nháp</p>'), 'template-leak', 'errors'));
  for (const html of ['<p>2 người</p>', '<code>{{count}}</code>', '<template>{{count}}</template>', '<script>const a="{{count}}";</script>', '<!-- TODO -->']) assert.ok(!has(check(html), 'template-leak', 'errors'));
});
test('caption: review redundant instruction, preserve units/source/update/synthetic label', () => {
  assert.ok(has(check('<p class="hint">Bấm để mở lớp</p>'), 'caption'));
  for (const html of ['<p class="caption">Nghìn đồng, tháng 10</p>', '<p class="note">Cập nhật 7:45</p>', '<p class="note">Dữ liệu minh họa</p>', '<p class="caption">Nguồn: sổ thu</p>']) assert.ok(!has(check(html), 'caption'));
});

test('template binding and hidden content require render before claiming a leak', () => {
  for (const html of ['<p hidden>{{count}}</p>', '<section aria-hidden="true"><p>TODO</p></section>', '<p>{{count}}</p><script src="app.js"></script>']) {
    const result = check(html);
    assert.ok(!has(result, 'template-leak', 'errors'));
    assert.ok(has(result, 'template-leak', 'unknown'));
  }
});
test('source tree handles nested buttons, quoted >, comments and raw scripts', () => {
  const source = '<!-- <a href="#"> --> <section id="detail"><button aria-label="X > Y"><span>Thu gọn</span></button></section><script>if (a < b) { const s="<a href=\'#\'>"; }</script>';
  assert.equal(parse(source).children.filter(n => n.tag === 'section').length, 1);
  assert.deepEqual(check(source).errors, []);
});
test('gallery does not claim prototype completeness or reject noninteractive artboards', () => {
  const r = check('<main data-flow-mode="gallery"><a href="#">Mẫu nút</a></main>');
  assert.equal(r.mode, 'gallery'); assert.equal(r.flow_status, 'UNKNOWN'); assert.deepEqual(r.errors, []);
  assert.ok(has(r, 'dead-link', 'unknown'));
});
test('CLI persists UTF-8 JSON and human statuses; exit zero remains flow UNKNOWN', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'flow-check-'));
  try {
    const page = path.join(dir, 'page.html'), out = path.join(dir, 'result.json');
    fs.writeFileSync(page, '<button>Đặt lịch</button>');
    const r = spawnSync(process.execPath, [path.join(__dirname, 'flow-check.cjs'), page, '--json', out], { encoding: 'utf8' });
    assert.equal(r.status, 0); assert.match(r.stdout, /luồng UNKNOWN/);
    assert.equal(JSON.parse(fs.readFileSync(out, 'utf8')).flow_status, 'UNKNOWN');
    fs.writeFileSync(page, '<a href="#">Đặt lịch</a>');
    assert.equal(spawnSync(process.execPath, [path.join(__dirname, 'flow-check.cjs'), page]).status, 1);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});
