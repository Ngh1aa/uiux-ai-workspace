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
 *   --layout strict       coi các cảnh báo bố cục (void, coverage, flat-scale, thin-highlight) là lỗi;
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
 *
 * axe-core là tuỳ chọn: cài cùng chỗ với Playwright (npm install axe-core@4). Không có thì kết
 * quả ghi "axe: chưa chạy"; khi giao phải nói rõ phần khả năng tiếp cận chưa được soát tự động.
 *
 * Đây là tín hiệu tự động, không thay việc nhìn ảnh chụp và không phải bằng chứng đạt WCAG.
 * Cần Playwright. Script tự tìm: NODE_PATH, node_modules gần đó, rồi thư mục npm toàn cục.
 * Không có thì xem mục "Khi không chạy được taste-check" trong START-HERE.md.
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

/* Runs inside the page. Returns one entry per screen. */
function auditInPage() {
  const canvas = document.createElement('canvas');
  canvas.width = 1;
  canvas.height = 1;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const colorCache = new Map();
  const toRgba = (value) => {
    if (!value || value === 'transparent') return [0, 0, 0, 0];
    if (colorCache.has(value)) return colorCache.get(value);
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = '#000';
    ctx.fillStyle = value;
    ctx.fillRect(0, 0, 1, 1);
    const d = ctx.getImageData(0, 0, 1, 1).data;
    const rgba = [d[0], d[1], d[2], d[3] / 255];
    colorCache.set(value, rgba);
    return rgba;
  };
  const hex = ([r, g, b]) => `#${[r, g, b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('')}`;
  const over = (top, bottom) => {
    const a = top[3];
    return [0, 1, 2].map((i) => top[i] * a + bottom[i] * (1 - a)).concat(1);
  };
  const lum = ([r, g, b]) => {
    const f = (v) => {
      const c = v / 255;
      return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => {
    const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
    return (hi + 0.05) / (lo + 0.05);
  };
  const hsl = ([r, g, b]) => {
    const [R, G, B] = [r / 255, g / 255, b / 255];
    const max = Math.max(R, G, B);
    const min = Math.min(R, G, B);
    const l = (max + min) / 2;
    if (max === min) return [0, 0, l];
    const d = max - min;
    const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    let h;
    if (max === R) h = (G - B) / d + (G < B ? 6 : 0);
    else if (max === G) h = (B - R) / d + 2;
    else h = (R - G) / d + 4;
    return [h * 60, s, l];
  };
  const visible = (el) => {
    if (el.closest('[hidden]')) return false;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || st.visibility === 'collapse') return false;
    const r = el.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return false;
    // Phần chỉ dành cho trình đọc màn hình (khung 1px, cắt bỏ phần thừa) không được soát bằng mắt.
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const ns = getComputedStyle(n);
      const nr = n.getBoundingClientRect();
      if ((ns.overflow === 'hidden' || ns.clip !== 'auto' || ns.clipPath !== 'none') && (nr.width <= 1 || nr.height <= 1)) return false;
    }
    return true;
  };
  const opacityChain = (el) => {
    let o = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) o *= Number(getComputedStyle(n).opacity || 1);
    return o;
  };
  const backdrop = (el) => {
    const layers = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const st = getComputedStyle(n);
      if (st.backgroundImage && st.backgroundImage !== 'none') return null;
      const c = toRgba(st.backgroundColor);
      if (c[3] > 0) {
        layers.push(c);
        if (c[3] >= 0.999) break;
      }
    }
    let base = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i -= 1) base = over(layers[i], base);
    return base;
  };
  const describe = (el) => {
    const cls = typeof el.className === 'string' && el.className.trim() ? `.${el.className.trim().split(/\s+/)[0]}` : '';
    const text = (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40);
    return `${el.tagName.toLowerCase()}${cls}${text ? ` "${text}"` : ''}`;
  };
  const ownText = (el) => [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join('').replace(/\s+/g, ' ').trim();
  const lineBoxes = (el) => {
    const lines = [];
    for (const node of el.childNodes) {
      if (node.nodeType !== 3 || !node.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const rect of range.getClientRects()) {
        if (rect.width < 1) continue;
        const line = lines.find((l) => Math.abs(l.top - rect.top) < 3);
        if (line) { line.left = Math.min(line.left, rect.left); line.right = Math.max(line.right, rect.right); }
        else lines.push({ top: rect.top, left: rect.left, right: rect.right });
      }
    }
    return lines.sort((a, b) => a.top - b.top);
  };
  const lineCount = (el) => {
    const tops = [];
    for (const node of el.childNodes) {
      if (node.nodeType !== 3 || !node.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const rect of range.getClientRects()) {
        if (rect.width < 1) continue;
        if (!tops.some((t) => Math.abs(t - rect.top) < 3)) tops.push(rect.top);
      }
    }
    return tops.length;
  };
  const INTERACTIVE = 'a[href], button, input:not([type="hidden"]), select, textarea, summary, [role="button"], [role="tab"], [role="switch"], [role="checkbox"], [role="radio"], [role="link"]';
  const CONTROL = 'button, input, select, textarea, a.ds-button, [role="button"], [role="switch"], [role="tab"]';

  const roots = [...document.querySelectorAll('[data-screen]')].filter(visible);
  const screens = roots.length ? roots : [document.body];

  return screens.map((root) => {
    const name = root === document.body ? (document.title || 'Trang') : root.getAttribute('data-screen');
    const errors = [];
    const warnings = [];
    const all = [root, ...root.querySelectorAll('*')].filter(visible);
    // data-part: khối mẫu trong thư viện pattern, không phải màn đầy đủ; bỏ các luật đo cả màn.
    const isPart = root.hasAttribute('data-part');
    const rootRect = root.getBoundingClientRect();
    const rootBg = backdrop(root) || [255, 255, 255, 1];

    // 1. Dấu chấm giữa nối cụm từ
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const parent = node.parentElement;
      if (!parent || !visible(parent) || parent.closest('script, style')) continue;
      const m = node.textContent.match(/\S[^\n]{0,24}\s[·•]\s[^\n]{0,24}\S/);
      if (m || /(^|\s)[·•](\s|$)/.test(node.textContent)) {
        errors.push({ rule: 'dot', message: `Dấu " · " nối cụm từ: "${(m ? m[0] : node.textContent).trim().slice(0, 60)}"` });
      }
    }

    for (const el of all) {
      const st = getComputedStyle(el);
      const text = ownText(el);

      if (text && !el.closest('[aria-disabled="true"], :disabled')) {
        // 2. Tương phản
        const bg = backdrop(el);
        if (bg) {
          const fg = toRgba(st.color);
          const alpha = fg[3] * opacityChain(el);
          const shown = over([fg[0], fg[1], fg[2], alpha], bg);
          const size = parseFloat(st.fontSize);
          const large = size >= 24 || (size >= 18.66 && Number(st.fontWeight) >= 700);
          const need = large ? 3 : 4.5;
          const got = ratio(shown, bg);
          if (got + 0.005 < need) {
            errors.push({ rule: 'contrast', message: `Tương phản ${got.toFixed(2)}:1 < ${need}:1 ở ${describe(el)} (${hex(shown)} trên ${hex(bg)})` });
          }
        }
        // 3. Nhãn ngắn bị gãy dòng
        const full = (el.textContent || '').replace(/\s+/g, ' ').trim();
        if (full.length <= 24 && text.length >= 2 && lineCount(el) > 1) {
          const label = el.matches(INTERACTIVE) || el.closest('label, button, [role="button"], [role="tab"]');
          if (label) errors.push({ rule: 'wrap', message: `Nhãn điều khiển ngắn bị gãy dòng: ${describe(el)}` });
          else warnings.push({ rule: 'wrap-review', message: `Nội dung ngắn xuống dòng; kiểm tra chủ đích theo brief: ${describe(el)}` });
        }
        // Dòng cuối chỉ còn một chữ
        if (full.length > 24 && el.children.length === 0) {
          const lines = lineBoxes(el);
          const last = lines[lines.length - 1];
          const words = text.split(' ');
          if (lines.length > 1 && last && (last.right - last.left) < (lines[0].right - lines[0].left) * 0.2 && words[words.length - 1].length <= 8) {
            // Chỉ là "một chữ" khi dòng cuối không rộng hơn chữ cuối cùng (tiếng Việt: một âm tiết).
            let lastWordWidth = Infinity;
            const node = [...el.childNodes].reverse().find((n) => n.nodeType === 3 && n.textContent.trim());
            if (node) {
              const raw = node.textContent.replace(/\s+$/, '');
              const start = Math.max(raw.search(/\S+$/), 0);
              const range = document.createRange();
              range.setStart(node, start); range.setEnd(node, raw.length);
              lastWordWidth = range.getBoundingClientRect().width;
            }
            if ((last.right - last.left) <= lastWordWidth + 2) {
              warnings.push({ rule: 'widow', message: `Dòng cuối chỉ còn một chữ: ${describe(el)}` });
            }
          }
        }
        // Chữ bị khung cha (overflow hidden/clip) cắt mất mà không có dấu …
        if (st.textOverflow !== 'ellipsis') {
          const box = el.getBoundingClientRect();
          for (let n = el.parentElement; n && n !== root.parentElement; n = n.parentElement) {
            const ns = getComputedStyle(n);
            // Khung cuộn ngang (bảng rộng trên màn hẹp) cho người dùng cuộn tới phần còn lại: không phải bị cắt.
            if (['auto', 'scroll'].includes(ns.overflowX)) break;
            if (!['hidden', 'clip'].includes(ns.overflowX)) continue;
            const nr = n.getBoundingClientRect();
            if (nr.width <= 1) break;
            const cut = Math.max(box.right - nr.right, nr.left - box.left);
            if (cut > 1) errors.push({ rule: 'clipped', message: `Chữ bị cắt mất ${Math.round(cut)}px bởi khung ${describe(n).split(' ')[0]}: ${describe(el)}` });
            break;
          }
        }
        // Chữ sát mép màn
        const tr = el.getBoundingClientRect();
        const edge = Math.min(tr.left - rootRect.left, rootRect.right - tr.right);
        if (rootRect.width <= 600 && edge < 12 && !el.closest('nav, [role="tablist"]') && getComputedStyle(el).position !== 'fixed') {
          warnings.push({ rule: 'edge', message: `Chữ cách mép màn ${Math.max(0, Math.round(edge))}px (nên ≥ 16px): ${describe(el)}` });
        }
        // Chữ bị cắt bằng dấu …
        if (st.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1) {
          warnings.push({ rule: 'ellipsis', message: `Chữ bị cắt bằng "…": ${describe(el)}` });
        }
      }

      // 4. Tràn ngang
      const clips = ['visible', 'clip'].includes(st.overflowX);
      if (clips && !(el instanceof SVGElement) && el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0 && el.textContent.trim()) {
        const inner = [...el.children].some((c) => c.scrollWidth > c.clientWidth + 1 && getComputedStyle(c).overflowX === st.overflowX);
        if (!inner) errors.push({ rule: 'overflow', message: `Nội dung tràn ngang ${el.scrollWidth - el.clientWidth}px: ${describe(el)}` });
      }

      // Vùng chạm
      if (el.matches(INTERACTIVE)) {
        const host = el.matches('input, select, textarea') && el.closest('label');
        const r = (host || el).getBoundingClientRect();
        const inlineLink = el.tagName === 'A' && el.closest('p, li') && st.display === 'inline';
        if (!inlineLink && (r.width < 43.5 || r.height < 43.5)) {
          warnings.push({ rule: 'target', message: `Vùng chạm ${Math.round(r.width)}×${Math.round(r.height)}px < 44×44: ${describe(el)}` });
        }
      }
    }
    if (root !== document.body && root.scrollWidth > root.clientWidth + 1 && getComputedStyle(root).overflowX !== 'hidden') {
      errors.push({ rule: 'overflow', message: `Màn tràn ngang ${root.scrollWidth - root.clientWidth}px` });
    }

    // 5. Card nổi bật và 6. bo góc
    const surfaceOf = (el) => {
      const st = getComputedStyle(el);
      const own = toRgba(st.backgroundColor);
      const hasBg = own[3] > 0.05 || (st.backgroundImage && st.backgroundImage !== 'none');
      const hasEdge = ['Top', 'Right', 'Bottom', 'Left'].every((side) => parseFloat(st[`border${side}Width`]) > 0) && toRgba(st.borderTopColor)[3] > 0.05;
      const hasShadow = st.boxShadow && st.boxShadow !== 'none';
      return { st, own, hasBg, hasEdge, hasShadow };
    };
    const highlights = [];
    const cards = [];
    for (const el of all) {
      if (el === root || el.matches(CONTROL) || el.closest('nav, [role="tablist"], [role="navigation"], [role="dialog"], [role="alertdialog"], [role="status"], [role="alert"], .ds-toast')) continue;
      const r = el.getBoundingClientRect();
      if (r.width < rootRect.width * 0.6 || r.height < 56) continue;
      const fullBleed = r.width >= rootRect.width - 2;
      // A whole website may alternate section backgrounds. Those are layout regions,
      // not competing highlight cards. Explicit data-screen canvases retain their card checks.
      if (root === document.body && fullBleed && el.matches('header, footer, main, section, [role="banner"], [role="contentinfo"]')) continue;
      const { st, own, hasBg, hasEdge, hasShadow } = surfaceOf(el);
      if (own[3] >= 0.9 && ratio(own, rootBg) >= 3 && !highlights.some((h) => h.contains(el))) highlights.push(el);
      if ((hasBg || hasEdge || hasShadow) && !(own[3] >= 0.999 && ratio(own, backdrop(el.parentElement) || rootBg) < 1.02 && !hasEdge && !hasShadow)) {
        const radius = parseFloat(st.borderTopLeftRadius) || 0;
        if (!fullBleed && radius < Math.min(r.width, r.height) / 2 - 1) cards.push({ el, radius: Math.round(radius) });
      }
    }
    if (highlights.length > 1) {
      errors.push({ rule: 'highlight', message: `${highlights.length} card nổi bật trong một màn (tối đa 1): ${highlights.map(describe).join('; ')}` });
    }
    const topCards = cards.filter((c) => !cards.some((o) => o !== c && o.el.contains(c.el)));
    const radii = [...new Set(topCards.map((c) => c.radius))];
    if (radii.length > 1) {
      const sample = radii.map((rad) => `${rad}px (${describe(topCards.find((c) => c.radius === rad).el)})`);
      warnings.push({ rule: 'radius', message: `Card có ${radii.length} bán kính bo góc khác nhau: ${sample.join('; ')}` });
    }

    // 8. Bố cục: khoảng trống thừa, độ phủ ngang, thang chữ phẳng, card nổi bật quá mỏng.
    // Hộp chữ lấy theo dòng chữ thật (không theo khối), để đoạn ngắn trong cột rộng vẫn lộ khoảng trống.
    const MEDIA = 'img, svg, video, canvas, iframe, input, select, textarea, button, progress, meter, [role="img"]';
    const textRects = (el) => {
      const rects = [];
      for (const node of el.childNodes) {
        if (node.nodeType !== 3 || !node.textContent.trim()) continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        for (const rect of range.getClientRects()) if (rect.width >= 1 && rect.height >= 1) rects.push(rect);
      }
      return rects;
    };
    const massOf = (el) => {
      if (el === root) return false;
      if (el.hasAttribute('data-whitespace')) return true;
      const st = getComputedStyle(el);
      if (st.backgroundImage && st.backgroundImage !== 'none') return true;
      const own = toRgba(st.backgroundColor);
      if (own[3] >= 0.9 && ratio(own, rootBg) >= 1.5) return true;
      // Khối hình không chữ (thanh tiến độ, dòng khung xương, vạch biểu đồ) là nội dung nhìn thấy được.
      return own[3] > 0.05 && !el.children.length && !el.textContent.trim();
    };
    const content = [];
    for (const el of all) {
      if (el === root) continue;
      const svgChild = el.closest('svg') && el.closest('svg') !== el;
      if (svgChild) continue;
      if (el.matches(MEDIA) || massOf(el)) content.push(el.getBoundingClientRect());
      else if (ownText(el)) content.push(...textRects(el));
    }
    const rootStyle = getComputedStyle(root);
    const inner = {
      top: rootRect.top + parseFloat(rootStyle.paddingTop || 0),
      bottom: rootRect.bottom - parseFloat(rootStyle.paddingBottom || 0),
    };
    if (content.length) {
      // Khoảng trống dọc lớn nhất giữa các vùng có nội dung, tính cả phần đáy màn.
      const spans = content
        .map((r) => [Math.max(r.top, inner.top), Math.min(r.bottom, inner.bottom)])
        .filter(([a, b]) => b > a)
        .sort((a, b) => a[0] - b[0]);
      let reach = spans.length ? spans[0][0] : inner.top;
      let gap = { size: 0, at: 0 };
      for (const [a, b] of spans) {
        if (a - reach > gap.size) gap = { size: a - reach, at: reach };
        reach = Math.max(reach, b);
      }
      if (inner.bottom - reach > gap.size) gap = { size: inner.bottom - reach, at: reach, bottom: true };
      const isScreen = root !== document.body;
      const limit = isScreen ? Math.max(160, rootRect.height * 0.18) : Math.max(320, window.innerHeight * 0.5);
      if (gap.size > limit) {
        const where = gap.bottom ? 'ở đáy màn' : `cách đầu màn ${Math.round(gap.at - rootRect.top)}px`;
        warnings.push({ rule: 'void', message: `Khoảng trống ${Math.round(gap.size)}px ${where} (ngưỡng ${Math.round(limit)}px). Lấp bằng nội dung có ích, chia lại cột, hoặc thu khung; trống có chủ đích thì đánh dấu data-whitespace` });
      }

      // Độ phủ ngang trên màn rộng: nội dung dồn một bên, bên kia bỏ trống.
      const region = root.querySelector('main, [role="main"]');
      const area = region && visible(region) ? region : root;
      const ar = area.getBoundingClientRect();
      if (!isPart && (ar.width >= 1024 - 1 || (area === root && rootRect.width >= 1024 - 1))) {
        const ast = getComputedStyle(area);
        const left = ar.left + parseFloat(ast.paddingLeft || 0);
        const right = ar.right - parseFloat(ast.paddingRight || 0);
        const inside = content.filter((r) => r.right > left && r.left < right && r.width < (right - left) + 2);
        if (inside.length) {
          const minLeft = Math.min(...inside.map((r) => r.left));
          const maxRight = Math.max(...inside.map((r) => r.right));
          const width = right - left;
          const rightGap = right - maxRight;
          const leftGap = minLeft - left;
          if (rightGap > width * 0.28 && rightGap > 280 && rightGap > leftGap * 2 + 120) {
            warnings.push({ rule: 'coverage', message: `Nội dung chỉ phủ ${Math.round(((maxRight - minLeft) / width) * 100)}% bề ngang, bỏ trống ${Math.round(rightGap)}px bên phải. Dùng lưới nhiều cột hoặc thêm cột phụ` });
          }
        }
      }
    }

    // Thang chữ phẳng: chữ lớn nhất không đủ khác chữ thân.
    const sizes = new Map();
    let largest = 0;
    for (const el of all) {
      const text = ownText(el);
      if (!text) continue;
      const size = Math.round(parseFloat(getComputedStyle(el).fontSize));
      sizes.set(size, (sizes.get(size) || 0) + text.length);
      largest = Math.max(largest, size);
    }
    const totalChars = [...sizes.values()].reduce((a, b) => a + b, 0);
    if (totalChars >= 80 && !isPart) {
      const body = [...sizes.entries()].sort((a, b) => b[1] - a[1])[0][0];
      const need = rootRect.width < 600 ? 1.3 : 1.5;
      if (largest / body < need) {
        warnings.push({ rule: 'flat-scale', message: `Thang chữ phẳng: chữ lớn nhất ${largest}px chỉ gấp ${(largest / body).toFixed(2)} lần chữ thân ${body}px (nên ≥ ${String(need).replace('.', ',')}). Tạo một điểm nhìn bằng cỡ chữ` });
      }
    }

    // Card nổi bật quá mỏng: cần ít nhất 3 dòng thông tin ở 2 cỡ chữ, và nội dung phủ phần lớn card.
    for (const card of highlights) {
      const texts = [card, ...card.querySelectorAll('*')].filter((el) => visible(el) && ownText(el));
      const levels = new Set(texts.map((el) => Math.round(parseFloat(getComputedStyle(el).fontSize))));
      const cr = card.getBoundingClientRect();
      const cs = getComputedStyle(card);
      const innerH = cr.height - parseFloat(cs.paddingTop || 0) - parseFloat(cs.paddingBottom || 0);
      const parts = [...card.querySelectorAll('*')].filter((el) => visible(el) && (ownText(el) || el.matches(MEDIA)));
      const rects = parts.flatMap((el) => (el.matches(MEDIA) ? [el.getBoundingClientRect()] : textRects(el)));
      const top = rects.length ? Math.min(...rects.map((r) => r.top)) : cr.top;
      const bottom = rects.length ? Math.max(...rects.map((r) => r.bottom)) : cr.top;
      const fill = innerH > 0 ? (bottom - top) / innerH : 1;
      if (texts.length < 3 || levels.size < 2) {
        warnings.push({ rule: 'thin-highlight', message: `Card nổi bật chỉ có ${texts.length} dòng chữ ở ${levels.size} cỡ: ${describe(card)}. Thêm tầng ngữ cảnh (so sánh, tiến độ, hạn) theo patterns/` });
      } else if (fill < 0.5 && cr.height > 160) {
        warnings.push({ rule: 'thin-highlight', message: `Nội dung chỉ phủ ${Math.round(fill * 100)}% chiều cao card nổi bật: ${describe(card)}` });
      }
    }

    // 7. Số nhóm màu
    const hues = new Map();
    const addColor = (value, el) => {
      const c = toRgba(value);
      if (c[3] < 0.3) return;
      const [h, s, l] = hsl(c);
      if (s < 0.25 || l < 0.12 || l > 0.92) return;
      // Gom các màu có sắc độ cách nhau dưới 20° vào cùng một nhóm.
      const near = [...hues.keys()].find((k) => Math.min(Math.abs(k - h), 360 - Math.abs(k - h)) < 20);
      if (near === undefined) hues.set(h, `${hex(c)} ở ${describe(el)}`);
    };
    for (const el of all) {
      const st = getComputedStyle(el);
      if (ownText(el)) addColor(st.color, el);
      addColor(st.backgroundColor, el);
      if (parseFloat(st.borderTopWidth) > 0) addColor(st.borderTopColor, el);
      if (el instanceof SVGElement) {
        if (st.stroke && st.stroke !== 'none') addColor(st.stroke, el);
        if (st.fill && st.fill !== 'none') addColor(st.fill, el);
      }
    }
    if (hues.size > 3) {
      warnings.push({ rule: 'colors', message: `${hues.size} nhóm màu trong một màn (nên ≤ 3): ${[...hues.values()].join('; ')}` });
    }

    const dedupe = (items) => {
      const seen = new Set();
      return items.filter((item) => (seen.has(item.message) ? false : seen.add(item.message)));
    };
    return { name, errors: dedupe(errors), warnings: dedupe(warnings) };
  });
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
  const server = await serve(opts.root);
  const base = `http://127.0.0.1:${server.address().port}`;
  const themes = opts.theme === 'both' ? ['light', 'dark'] : [opts.theme];
  const browser = await playwright.chromium.launch({ headless: true });
  const results = [];
  try {
    for (const page of opts.pages) {
      let url = page;
      if (!/^https?:\/\//.test(page)) {
        const file = path.resolve(page);
        if (!file.startsWith(opts.root + path.sep)) throw new Error(`${page} nằm ngoài --root ${opts.root}`);
        if (!fs.existsSync(file)) throw new Error(`không có file ${page}`);
        url = `${base}/${path.relative(opts.root, file).split(path.sep).map(encodeURIComponent).join('/')}`;
      }
      const passes = [];
      for (const width of opts.widths) for (const theme of themes) passes.push({ width, theme, reflow: false });
      if (opts.reflow) passes.push({ width: 320, theme: 'light', reflow: true });
      for (const { width, theme, reflow } of passes) {
        {
          const context = await browser.newContext({ viewport: { width, height: opts.height }, colorScheme: theme, reducedMotion: 'reduce' });
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
          let screens = await tab.evaluate(auditInPage);
          if (opts.layout === 'strict') {
            const LAYOUT = ['void', 'coverage', 'flat-scale', 'thin-highlight'];
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
