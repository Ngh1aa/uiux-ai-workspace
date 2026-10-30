#!/usr/bin/env node
/** Soát hợp đồng luồng trong HTML nguồn, không cần trình duyệt/dependency.
 * node flow-check.cjs <page.html> [...] [--mode prototype|gallery] [--json <file>]
 * Exit 0: không có lỗi chắc chắn; 1: có lỗi; 2: không chạy được.
 * Exit 0 KHÔNG chứng minh luồng PASS: hành vi runtime luôn UNKNOWN ở lớp tĩnh.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');

// Tokenizer có trạng thái + cây cha/con, không dùng regex để suy ra đồ thị nghiệp vụ.
// Chỉ đọc HTML nguồn: không thực thi JS, sửa HTML lỗi theo chuẩn browser, hay mở shadow DOM.
const VOID = new Set('area base br col embed hr img input link meta param source track wbr'.split(' '));
const RAW = new Set(['script', 'style', 'textarea', 'title']);
function decode(text) {
  return text.replace(/&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi, (all, entity) => {
    if (entity[0] === '#') {
      const n = entity[1].toLowerCase() === 'x' ? parseInt(entity.slice(2), 16) : Number(entity.slice(1));
      return n > 0 && n <= 0x10ffff ? String.fromCodePoint(n) : all;
    }
    return ({ amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' })[entity.toLowerCase()] || all;
  });
}
function parse(html) {
  const root = { tag: '#document', attrs: {}, children: [], parent: null, line: 1 };
  const stack = [root];
  let pos = 0;
  const addText = value => stack.at(-1).children.push({ tag: '#text', value: decode(value), parent: stack.at(-1) });
  while (pos < html.length) {
    if (html.startsWith('<!--', pos)) { const end = html.indexOf('-->', pos + 4); pos = end < 0 ? html.length : end + 3; continue; }
    if (html[pos] !== '<') { const end = html.indexOf('<', pos); addText(html.slice(pos, end < 0 ? html.length : end)); pos = end < 0 ? html.length : end; continue; }
    const start = pos++;
    let quote = '';
    while (pos < html.length) {
      const c = html[pos++];
      if (quote) { if (c === quote) quote = ''; }
      else if (c === '"' || c === "'") quote = c;
      else if (c === '>') break;
    }
    const token = html.slice(start + 1, pos - 1);
    if (token.startsWith('!') || token.startsWith('?')) continue;
    const match = token.match(/^\s*(\/?)\s*([a-z][\w:-]*)/i);
    if (!match) continue;
    const tag = match[2].toLowerCase();
    if (match[1]) {
      const index = stack.findLastIndex(n => n.tag === tag);
      if (index > 0) stack.length = index;
      continue;
    }
    const attrs = {};
    const rest = token.slice(match[0].length);
    for (const m of rest.matchAll(/([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) {
      attrs[m[1].toLowerCase()] = decode(m[2] ?? m[3] ?? m[4] ?? '');
    }
    const node = { tag, attrs, children: [], parent: stack.at(-1), line: html.slice(0, start).split('\n').length };
    stack.at(-1).children.push(node);
    if (RAW.has(tag)) {
      const close = new RegExp(`</${tag}\\s*>`, 'ig'); close.lastIndex = pos;
      const end = close.exec(html);
      node.children.push({ tag: '#text', value: decode(html.slice(pos, end ? end.index : html.length)), parent: node });
      pos = end ? close.lastIndex : html.length;
    } else if (!VOID.has(tag) && !/\/\s*$/.test(token)) stack.push(node);
  }
  return root;
}
const has = (node, name) => Object.hasOwn(node.attrs || {}, name);
const walk = node => [node, ...(node.children || []).flatMap(walk)];
function text(node) {
  if (node.tag === '#text') return node.value;
  if (['script', 'style', 'template', 'svg'].includes(node.tag) || has(node, 'hidden') || node.attrs?.['aria-hidden'] === 'true') return '';
  return (node.children || []).map(text).join(' ').replace(/\s+/g, ' ').trim();
}
function ancestor(node, predicate) { for (let p = node; p; p = p.parent) if (predicate(p)) return p; return null; }
const normalize = value => value.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/đ/g, 'd');
const isDialog = node => ['dialog', 'alertdialog'].includes(node.attrs?.role) || node.tag === 'dialog' || has(node, 'data-confirm');
const risky = label => {
  const value = normalize(label);
  if (/^xoa (?:bo loc|tim kiem|lua chon)\b/.test(value)) return false;
  return /^(?:xoa\b|roi (?:lop|nhom)\b|giai tan\b|chan (?:nguoi|tai khoan)\b|khoa tai khoan\b|rut tien\b|hoan tien\b|thu (?:tien|hoc phi)\b|gui (?:cho ca|hang loat)\b|nhac tat ca\b)/.test(value);
};

function checkHtml(html, { page = '<html>', mode } = {}) {
  const tree = parse(html);
  const nodes = walk(tree).filter(n => !['#document', '#text', 'script', 'style'].includes(n.tag));
  const ids = new Map(nodes.filter(n => n.attrs.id).map(n => [n.attrs.id, n]));
  const gallery = mode === 'gallery' || nodes.some(n => n.attrs['data-flow-mode'] === 'gallery');
  const scripts = nodes.some(n => n.tag === 'script') || /<script\b/i.test(html);
  const errors = [], warnings = [], unknown = [];
  const issue = (list, rule, node, message) => list.push({ rule, status: list === errors ? 'FAIL' : list === warnings ? 'WARN' : 'UNKNOWN', line: node?.line || 1, message });
  const refs = [];
  const controls = nodes.filter(n => n.tag === 'a' || n.tag === 'button' || ['button', 'link'].includes(n.attrs.role));
  const targetId = node => {
    if (node.attrs['data-to']) return node.attrs['data-to'].replace(/^#/, '');
    const href = node.attrs.href;
    if (href?.startsWith('#') && href.length > 1) { try { return decodeURIComponent(href.slice(1)); } catch { return href.slice(1); } }
    return null;
  };
  const possibleHandler = node => scripts || Object.keys(node.attrs).some(k => /^on/.test(k)) || has(node, 'data-action');
  for (const node of controls) {
    const label = text(node) || node.attrs['aria-label'] || '';
    const href = node.attrs.href;
    const id = targetId(node);
    if (id) refs.push(id);
    const placeholder = node.tag === 'a' && href !== undefined && (href.trim() === '' || href.trim() === '#' || /^javascript:\s*(?:void\b|;|$)/i.test(href));
    if (placeholder || (id && !ids.has(id))) {
      issue(gallery || possibleHandler(node) ? unknown : errors, 'dead-link', node,
        placeholder ? `Liên kết giữ chỗ “${label}”; cần kiểm hành vi nếu được JS xử lý.` : `Đích #${id} không có trong HTML nguồn.`);
    } else if (node.tag !== 'a' && !id && !has(node, 'disabled')) {
      issue(unknown, 'dead-link', node, `“${label}”: submit, thao tác tại chỗ hoặc event handler phải kiểm trên trình duyệt; thiếu data-to không chứng minh nút chết.`);
    }
    const confirmContext = ancestor(node, isDialog);
    if (!gallery && !confirmContext && (risky(label) || node.attrs['data-risk'] === 'high')) {
      const target = ids.get(id);
      const declaredReview = node.attrs['data-review'];
      if (target && isDialog(target) || declaredReview === 'inline' || declaredReview === 'undo') {
        issue(unknown, 'no-confirm', node, 'Có khai báo bước kiểm tra/hoàn tác; cần xác minh hậu quả và hành vi thực tế.');
      } else {
        issue(node.attrs['data-risk'] === 'high' && declaredReview === 'none' ? errors : warnings, 'no-confirm', node,
          `“${label}”: kiểm tra theo hậu quả và khả năng khôi phục, không bắt buộc hai màn.`);
      }
    }
    if (!gallery && confirmContext && has(node, 'data-confirm-action')) {
      const target = ids.get(id);
      if (!target || !has(target, 'data-result')) issue(warnings, 'no-result', node, 'Chưa thấy đích kết quả; kết quả tại chỗ/live region vẫn có thể hợp lệ.');
      issue(unknown, 'no-result', node, 'Cần bấm xác nhận và kiểm tra phản hồi, dữ liệu cùng đường khôi phục.');
    }
    if ((has(node, 'disabled') || node.attrs['aria-disabled'] === 'true') && (has(node, 'data-primary') || /(?:^|\s)(?:primary|ds-button--primary)(?:\s|$)/.test(node.attrs.class || ''))) {
      const described = (node.attrs['aria-describedby'] || '').split(/\s+/).filter(Boolean).map(key => ids.get(key));
      const nearReason = node.parent?.children.some(n => has(n, 'data-reason') && text(n));
      if (!described.some(n => n && text(n)) && !nearReason) issue(warnings, 'disabled-no-reason', node, 'Nút chính bị khóa: chưa thấy lý do liên kết trong nguồn; kiểm khả năng nhìn/đọc được trên render.');
    }
    if (node.tag === 'button' && label.split(/\s+/).length > 3 && !has(node, 'data-label-context')) {
      issue(warnings, 'label-long', node, `Nhãn “${label}” dài hơn khuyến nghị 3 từ; giữ đầy đủ đối tượng khi cần hiểu hậu quả.`);
    }
  }
  const screens = nodes.filter(n => has(n, 'data-screen'));
  screens.forEach((node, index) => {
    if (!gallery && index > 0 && !has(node, 'data-entry') && !has(node, 'data-deep-link') && node.attrs.id && !refs.includes(node.attrs.id)) {
      issue(warnings, 'no-entry', node, `#${node.attrs.id} chưa có đường vào khai báo trong file này; router, deep link hoặc file khác có thể hợp lệ.`);
    }
  });
  for (const node of nodes) {
    if (['ul', 'ol'].includes(node.tag) || /(?:^|\s)app-list(?:\s|$)/.test(node.attrs.class || '')) {
      const rows = node.children.filter(n => n.tag !== '#text');
      const hints = rows.map(row => walk(row).some(n => has(n, 'data-chevron') || /chevron/.test(n.attrs?.class || '') || /chevron/.test(n.attrs?.href || '')));
      if (hints.includes(true) && hints.includes(false)) issue(warnings, 'row-mismatch', node, 'Dấu mở chi tiết khác nhau trong danh sách; kiểm mục đích, trạng thái và đúng đối tượng trước khi sửa.');
    }
    const ownText = (node.children || []).filter(n => n.tag === '#text').map(n => n.value).join(' ').trim();
    const excluded = ancestor(node, n => ['pre', 'code', 'template', 'textarea', 'script', 'style'].includes(n.tag));
    if (!excluded && /\{\{[^}]*\}\}|\bTODO\b|\bFIXME\b/.test(ownText)) {
      const deferred = ancestor(node, n => has(n, 'hidden') || n.attrs?.['aria-hidden'] === 'true') ||
        (scripts && /\{\{[^}]*\}\}/.test(ownText));
      issue(deferred ? unknown : errors, 'template-leak', node, deferred
        ? 'Template/khối ẩn cần kiểm text sau render; source chưa chứng minh biến lọt ra màn.'
        : `Biến mẫu/ghi chú nội bộ trong text nguồn: ${ownText.slice(0, 90)}`);
    }
    // Lorem/source placeholders belong to static-check, not a second flow diagnostic.
    // TASTE.md "Chữ trên màn": không dòng giải thích phụ (hướng dẫn thao tác, ghi chú kỳ/cập nhật/nguồn, ghi chú bản mẫu).
    if (/\b(?:caption|hint|note)\b/.test(node.attrs.class || '') && !excluded &&
        /^(?:bấm|chạm|nhấn|chọn để)\b|^(?:cập nhật|nguồn|đơn vị)\b|minh h(?:o[aạ]|ọa)|\bdữ liệu mẫu\b|\bbản mẫu\b/i.test(text(node))) {
      issue(warnings, 'caption', node, 'Dòng giải thích phụ trên màn (TASTE.md): bỏ, hoặc đưa đơn vị vào nhãn và ghi chú bản mẫu vào phần bàn giao.');
    }
    if (/\b\d{1,2}:\d{2}\b/.test(ownText) && !excluded) {
      const context = ancestor(node, n => has(n, 'data-screen')) || ancestor(node, n => n.tag === 'article' || n.tag === 'form') || node.parent || node;
      const contextText = text(context);
      const slot = ancestor(node, n => has(n, 'data-time-slot') || n.attrs?.role === 'status' || /(?:status.*time|clock)/.test(n.attrs?.class || ''));
      if (!slot && !ancestor(node, n => has(n, 'hidden')) && !/\b\d{1,2}[/-]\d{1,2}\b|\b\d{4}-\d{2}-\d{2}\b|thứ|hôm nay|ngày mai|tối nay|sáng nay|chiều nay/i.test(contextText) && !has(node, 'datetime')) {
        issue(warnings, 'time-no-date', node, 'Giờ chưa thấy ngày trong ngữ cảnh nguồn; kiểm bộ chọn ngày, lịch lặp hoặc đồng hồ trước khi thêm chữ.');
      }
    }
  }
  issue(unknown, 'runtime', null, gallery
    ? 'Gallery/artboard: không suy ra khả năng tương tác. Nếu bàn giao prototype, khai báo mode prototype và chạy browser scenarios.'
    : 'HTML nguồn không chứng minh luồng, Back, tổng tiền, đúng đối tượng/vai trò, khôi phục lỗi hoặc navigation động. Chạy Playwright của dự án.');
  return { page, mode: gallery ? 'gallery' : 'prototype', static_status: errors.length ? 'FAIL' : 'PASS', flow_status: 'UNKNOWN', errors, warnings, unknown };
}
function main(argv) {
  let json, mode;
  const pages = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--json') json = argv[++i];
    else if (argv[i] === '--mode') mode = argv[++i];
    else if (argv[i].startsWith('-')) throw new Error(`Tùy chọn không hợp lệ: ${argv[i]}`);
    else pages.push(argv[i]);
  }
  if (!pages.length || mode && !['prototype', 'gallery'].includes(mode)) throw new Error('Dùng: node flow-check.cjs <page.html> [...] [--mode prototype|gallery] [--json <file>]');
  const results = pages.map(page => checkHtml(fs.readFileSync(page, 'utf8'), { page, mode }));
  const report = { schema_version: 1, layer: 'source-static', errorCount: results.reduce((n, r) => n + r.errors.length, 0), warningCount: results.reduce((n, r) => n + r.warnings.length, 0), flow_status: 'UNKNOWN', results };
  for (const result of results) {
    process.stdout.write(`\n${result.page}: tĩnh ${result.static_status}, luồng UNKNOWN\n`);
    for (const issue of [...result.errors, ...result.warnings, ...result.unknown]) process.stdout.write(`  ${issue.status} [${issue.rule}] L${issue.line}: ${issue.message}\n`);
  }
  if (json) { fs.mkdirSync(path.dirname(path.resolve(json)), { recursive: true }); fs.writeFileSync(json, JSON.stringify(report, null, 2) + '\n'); }
  return report.errorCount ? 1 : 0;
}
module.exports = { parse, checkHtml, main };
if (require.main === module) {
  try { process.exitCode = main(process.argv.slice(2)); }
  catch (error) { process.stderr.write(`flow-check: ${error.message}\n`); process.exitCode = 2; }
}
