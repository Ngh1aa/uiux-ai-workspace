#!/usr/bin/env node
/**
 * Soát tĩnh một trang HTML khi không chạy được taste-check (không có Playwright, mạng chặn).
 * Chỉ dùng Node, không cần cài gì. Đọc mã nguồn trang và các file CSS cục bộ nó nạp.
 *
 * Dùng:
 *   node static-check.cjs <trang.html> [...] [--json <file>]
 *
 * LỖI (thoát với mã 1):
 *   - dấu " · " hoặc " • " nối cụm từ trong chữ hiển thị
 *   - thiếu <html lang>, thẻ viewport hoặc <title>
 *   - viewport chặn phóng to (user-scalable=no, maximum-scale=1)
 *   - ảnh thiếu alt; nút hoặc liên kết không có chữ và không có aria-label
 *   - aria-label của nút/liên kết không chứa chữ đang hiện trên nút (WCAG 2.5.3)
 *   - div/span/p có aria-label mà không có role (ARIA cấm, trình đọc màn hình bỏ qua)
 *   - chữ giữ chỗ kiểu "Lorem ipsum", "John Doe", "Acme"
 *   - TASTE.md: ghi chú bản mẫu trên màn (demo-note), biến mẫu {{…}} (template-var), cỡ chữ dưới 12px (small)
 *     Chữ trong phần tử có data-annotation (nhãn artboard, gallery) được bỏ qua.
 * CẢNH BÁO:
 *   - mã màu viết cứng ngoài phần khai báo token (--tên: giá trị)
 *   - transition: all; outline: none mà không có :focus-visible
 *   - emoji dùng như icon
 *   - mặc định kiểu AI generic (CRAFT.md mục 2): font duy nhất là Inter/Roboto/Arial/Open Sans/
 *     Lato/hệ thống; gradient tím–xanh; nhãn IN HOA lặp từ 3 chỗ; mũi tên "→" sau nhiều liên kết
 *
 * Không thay được việc render và nhìn ảnh: không đo được tương phản thật, tràn chữ, gãy dòng.
 * Khi giao, ghi rõ trang chỉ mới được soát tĩnh.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');

const DOT = /\S\s[·•]\s\S/;
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u;
// Cùng mẫu với taste-check.cjs (demo-note).
const DEMO = /\b(?:dữ liệu|số liệu|lời|lịch|ngữ cảnh|nội dung|mẫu tương tác)\s+(?:mẫu|minh ho[aạ]|minh họa|từ đề|theo đề)|\b(?:bản|là) minh (?:ho[aạ]|họa)\b|\bminh (?:ho[aạ]|họa) theo\b|\bbản mẫu (?:này|không|chưa)|\btrong bản mẫu\b|\bbrowser preview\b|\bdữ liệu (?:từ |theo )?đề bài\b|\bmô phỏng quyền\b|\btheo brief\b|\bbackend\b/i;

function visibleText(html) {
  return html
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<([a-z][\w-]*)\b[^>]*\bdata-annotation\b[^>]*>[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<(script|style|svg|template)\b[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]+>/g, '\n')
    .replace(/&nbsp;/g, ' ')
    .split('\n').map((l) => l.replace(/\s+/g, ' ').trim()).filter(Boolean);
}

function localCss(html, file, pageOnly = false) {
  const parts = [];
  for (const m of html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)) parts.push(m[1]);
  for (const m of html.matchAll(/<link\b[^>]*rel=["']?stylesheet[^>]*>/gi)) {
    const href = (m[0].match(/href=["']([^"']+)["']/i) || [])[1];
    if (!href || /^(https?:)?\/\//.test(href)) continue;
    const target = path.resolve(path.dirname(file), href.split(/[?#]/)[0]);
    if (pageOnly && /design-system[\\/](generated|components|fonts)[\\/]/.test(target)) continue;
    if (fs.existsSync(target)) parts.push(fs.readFileSync(target, 'utf8'));
  }
  for (const m of html.matchAll(/\sstyle=["']([^"']*)["']/gi)) parts.push(m[1]);
  return parts.join('\n').replace(/\/\*[\s\S]*?\*\//g, '');
}

function check(file) {
  const html = fs.readFileSync(file, 'utf8');
  const errors = [];
  const warnings = [];
  const err = (rule, message) => errors.push({ rule, message });
  const warn = (rule, message) => warnings.push({ rule, message });

  if (!/<html\b[^>]*\blang=["']?[a-z]/i.test(html)) err('lang', 'thiếu <html lang="..."> (tiếng Việt: lang="vi")');
  const viewport = (html.match(/<meta\b[^>]*name=["']?viewport[^>]*>/i) || [])[0];
  if (!viewport) err('viewport', 'thiếu <meta name="viewport" content="width=device-width, initial-scale=1">');
  else if (/user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b/i.test(viewport)) err('zoom', 'viewport đang chặn người dùng phóng to');
  if (!/<title>[^<]*\S[^<]*<\/title>/i.test(html)) err('title', 'thiếu <title>');

  for (const line of visibleText(html)) {
    if (DOT.test(line)) err('dot', `nối cụm từ bằng dấu chấm giữa: "${line.slice(0, 80)}"`);
    if (/lorem ipsum|john doe|\bacme\b/i.test(line)) err('placeholder', `chữ giữ chỗ: "${line.slice(0, 60)}"`);
    if (DEMO.test(line)) err('demo-note', `ghi chú bản mẫu trên màn: "${line.slice(0, 60)}" (chuyển vào phần bàn giao)`);
    if (/\{\{|\}\}/.test(line)) err('template-var', `lộ biến mẫu: "${line.slice(0, 60)}"`);
    if (EMOJI.test(line) && line.length <= 3) warn('emoji', `emoji dùng như icon: "${line}" (dùng icon SVG)`);
  }
  for (const m of html.matchAll(/<img\b[^>]*>/gi)) {
    if (!/\balt=/i.test(m[0])) err('alt', `ảnh thiếu alt: ${m[0].slice(0, 80)}`);
  }
  for (const m of html.matchAll(/<(div|span|p)\b([^>]*)>/gi)) {
    if (/\saria-label(ledby)?=/i.test(m[2]) && !/\srole=/i.test(m[2])) {
      err('aria-prohibited', `<${m[1]}> có aria-label nhưng không có role: thêm role (group, region, status...) hoặc bỏ aria-label`);
    }
  }
  for (const m of html.matchAll(/<(button|a)\b([^>]*)>([\s\S]*?)<\/\1>/gi)) {
    const text = m[3].replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim();
    if (!text && !/aria-label(ledby)?=/i.test(m[2]) && !/<title>|aria-label=|<img\b[^>]*alt=["'][^"']+/i.test(m[3])) {
      err('name', `<${m[1]}> không có chữ và không có aria-label`);
    }
    const label = (m[2].match(/aria-label=["']([^"']*)["']/i) || [])[1];
    const shown = m[3].replace(/<([a-z]+)\b[^>]*aria-hidden=["']true["'][^>]*>[\s\S]*?<\/\1>/gi, '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
    if (label && shown && !label.toLowerCase().includes(shown.toLowerCase())) {
      err('name-mismatch', `<${m[1]}> hiện "${shown.slice(0, 40)}" nhưng aria-label là "${label.slice(0, 40)}" (WCAG 2.5.3: tên phải chứa chữ đang hiện)`);
    }
  }
  // Liên kết và hành vi thuộc flow-check; không báo trùng ở checker giao diện tĩnh.

  const css = localCss(html, file);
  const pageCss = localCss(html, file, true);
  const hardcoded = new Set();
  for (const decl of css.split(/[;{}]/)) {
    const d = decl.trim();
    if (!d || d.startsWith('--') || d.startsWith('@')) continue;
    for (const c of d.match(/#[0-9a-f]{3,8}\b|\brgba?\([^)]*\)/gi) || []) hardcoded.add(c.toLowerCase());
    const size = d.match(/^font-size\s*:\s*(\d+(?:\.\d+)?)px/i);
    if (size && Number(size[1]) < 12) err('small', `cỡ chữ ${size[1]}px dưới 12px (TASTE: chữ phụ ≥ 12px)`);
  }
  if (hardcoded.size) warn('hex', `${hardcoded.size} màu viết cứng ngoài token: ${[...hardcoded].slice(0, 6).join(', ')}`);
  // Mặc định kiểu AI generic (CRAFT.md mục 2)
  const GENERIC = /^(inter|roboto|arial|helvetica( neue)?|open sans|lato|system-ui|-apple-system|blinkmacsystemfont|segoe ui|sans-serif)$/i;
  const firsts = new Set();
  for (const m of css.matchAll(/font-family\s*:\s*([^;}]+)/gi)) {
    const first = m[1].split(',')[0].trim().replace(/^["']|["']$/g, '');
    if (first && !first.startsWith('var(') && !/^(inherit|initial|unset)$/i.test(first)) firsts.add(first);
  }
  if (firsts.size && [...firsts].every((f) => GENERIC.test(f))) {
    warn('generic-font', `font duy nhất là font mặc định (${[...firsts].join(', ')}); chọn font theo thương hiệu`);
  }
  const hue = (hex) => {
    let h = hex.replace('#', '');
    if (h.length === 3) h = h.split('').map((c) => c + c).join('');
    const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
    const max = Math.max(r, g, b); const min = Math.min(r, g, b); const d = max - min;
    if (d < 0.25) return null;
    let x = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return (x * 60 + 360) % 360;
  };
  for (const m of pageCss.matchAll(/(?:linear|radial|conic)-gradient\(([^;]*?)\)\s*[;}]/gi)) {
    const hues = (m[1].match(/#[0-9a-f]{6}\b|#[0-9a-f]{3}\b/gi) || []).map(hue).filter((h) => h !== null);
    if (hues.some((h) => h >= 250 && h <= 300)) { warn('purple-gradient', 'gradient tím–xanh: kiểm lại có đến từ brand brief không'); break; }
  }
  const eyebrows = (pageCss.match(/text-transform\s*:\s*uppercase/gi) || []).length
    + (html.match(/class=["'][^"']*\bds-text-label-sm\b/g) || []).length;
  if (eyebrows >= 3) warn('eyebrow', `${eyebrows} chỗ chữ IN HOA nhỏ; nhãn eyebrow lặp lại là dấu hiệu template`);
  const arrows = (html.match(/→\s*<\/a>|→<\/a>/g) || []).length;
  if (arrows >= 3) warn('arrow', `${arrows} liên kết kết thúc bằng "→"`);
  if (/transition\s*:\s*all\b/i.test(css)) warn('transition', 'transition: all (liệt kê thuộc tính cụ thể)');
  if (/outline\s*:\s*(none|0)\b/i.test(css) && !/:focus-visible/.test(css)) warn('focus', 'bỏ outline mà không có kiểu :focus-visible thay thế');

  const dedupe = (list) => [...new Map(list.map((i) => [i.rule + i.message, i])).values()];
  return { page: file, errors: dedupe(errors), warnings: dedupe(warnings) };
}

function main(argv) {
  const pages = [];
  let json = '';
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--json') json = argv[++i] || '';
    else if (argv[i] === '-h' || argv[i] === '--help') pages.length = 0, (argv.length = 0);
    else pages.push(argv[i]);
  }
  if (!pages.length) {
    process.stdout.write(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace(/^#!.*\n\/\*\*?/, '').replace(/^ \* ?/gm, ''));
    return 2;
  }
  let errorCount = 0;
  const results = [];
  for (const page of pages) {
    if (!fs.existsSync(page)) {
      process.stderr.write(`static-check: không có file ${page}\n`);
      return 2;
    }
    const r = check(page);
    results.push(r);
    errorCount += r.errors.length;
    process.stdout.write(`\n${page}: ${r.errors.length ? 'LỖI' : r.warnings.length ? 'CẢNH BÁO' : 'ĐẠT'}\n`);
    for (const i of r.errors) process.stdout.write(`  lỗi       ${i.message}\n`);
    for (const i of r.warnings) process.stdout.write(`  cảnh báo  ${i.message}\n`);
  }
  process.stdout.write(`\nTổng: ${errorCount} lỗi. Soát tĩnh không thay việc render và nhìn ảnh chụp.\n`);
  if (json) fs.writeFileSync(json, `${JSON.stringify({ errorCount, results }, null, 2)}\n`);
  return errorCount ? 1 : 0;
}

process.exitCode = main(process.argv.slice(2));
