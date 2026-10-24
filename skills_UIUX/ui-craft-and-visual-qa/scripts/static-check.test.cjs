'use strict';
// Chạy: node --test skills_UIUX/ui-craft-and-visual-qa/scripts/static-check.test.cjs (không cần cài gì)
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const SCRIPT = path.join(__dirname, 'static-check.cjs');

function run(body, head = '<meta name="viewport" content="width=device-width, initial-scale=1"><title>t</title>', lang = ' lang="vi"') {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'static-'));
  const page = path.join(dir, 'page.html');
  fs.writeFileSync(page, `<!doctype html><html${lang}><head><meta charset="utf-8">${head}</head><body>${body}</body></html>`);
  const out = path.join(dir, 'out.json');
  const res = spawnSync(process.execPath, [SCRIPT, page, '--json', out], { encoding: 'utf8' });
  const data = JSON.parse(fs.readFileSync(out, 'utf8'));
  const r = data.results[0];
  return { code: res.status, errors: r.errors.map((i) => i.rule), warnings: r.warnings.map((i) => i.rule) };
}

test('trang sạch thì đạt', () => {
  const r = run('<main><h1>Lịch hẹn</h1><p>Hôm nay có 3 lịch</p><button type="button">Đặt lịch</button></main>');
  assert.deepEqual(r.errors, []);
  assert.equal(r.code, 0);
});

test('bắt dấu chấm giữa nối cụm từ', () => {
  const r = run('<p>Ăn uống · 08:12</p>');
  assert.ok(r.errors.includes('dot'));
  assert.equal(r.code, 1);
});

test('bắt thiếu lang, viewport, title', () => {
  const r = run('<p>A</p>', '', '');
  for (const rule of ['lang', 'viewport', 'title']) assert.ok(r.errors.includes(rule), rule);
});

test('bắt viewport chặn phóng to', () => {
  const r = run('<p>A</p>', '<meta name="viewport" content="width=device-width, maximum-scale=1"><title>t</title>');
  assert.ok(r.errors.includes('zoom'));
});

test('bắt ảnh thiếu alt và nút không tên', () => {
  const r = run('<img src="a.png"><button type="button"><svg></svg></button><button aria-label="Đóng"><svg></svg></button>');
  assert.ok(r.errors.includes('alt'));
  assert.equal(r.errors.filter((x) => x === 'name').length, 1);
});

test('cảnh báo màu viết cứng nhưng bỏ qua khai báo token', () => {
  const ok = run('<style>:root{--ds-brand:#123456}</style><p>A</p>');
  assert.ok(!ok.warnings.includes('hex'));
  const bad = run('<style>p{color:#123456}</style><p>A</p>');
  assert.ok(bad.warnings.includes('hex'));
});
