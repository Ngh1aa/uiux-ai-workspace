/* taste-check: hàm dùng chung (màu, hình học, bề mặt).
 * Chạy trong trang (Playwright evaluate), không phải module Node. taste-check.cjs ghép các file trong
 * thư mục này theo thứ tự shared, text, card, layout, chart, audit vào một hàm rồi chạy một lần mỗi trang.
 * Mỗi luật nhận ctx = { root, all, isPart, rootRect, rootBg, errors, warnings, massOf, highlights }. */
const canvas = document.createElement('canvas');
canvas.width = 1;
canvas.height = 1;
const canvasCtx = canvas.getContext('2d', { willReadFrequently: true });
const colorCache = new Map();
const toRgba = (value) => {
  if (!value || value === 'transparent') return [0, 0, 0, 0];
  if (colorCache.has(value)) return colorCache.get(value);
  canvasCtx.clearRect(0, 0, 1, 1);
  canvasCtx.fillStyle = '#000';
  canvasCtx.fillStyle = value;
  canvasCtx.fillRect(0, 0, 1, 1);
  const d = canvasCtx.getImageData(0, 0, 1, 1).data;
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

// Bề mặt của một khối: nền, viền đủ bốn cạnh, bóng.
const surfaceOf = (el) => {
  const st = getComputedStyle(el);
  const own = toRgba(st.backgroundColor);
  const hasBg = own[3] > 0.05 || (st.backgroundImage && st.backgroundImage !== 'none');
  const hasEdge = ['Top', 'Right', 'Bottom', 'Left'].every((side) => parseFloat(st[`border${side}Width`]) > 0) && toRgba(st.borderTopColor)[3] > 0.05;
  const hasShadow = st.boxShadow && st.boxShadow !== 'none';
  return { st, own, hasBg, hasEdge, hasShadow };
};
// Phần tử hình hoặc ô nhập: tính cả khối là nội dung.
const MEDIA = 'img, svg, video, canvas, iframe, input, select, textarea, button, progress, meter, [role="img"]';
// Hộp chữ lấy theo dòng chữ thật (không theo khối), để đoạn ngắn trong cột rộng vẫn lộ khoảng trống.
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
// Khối có "khối lượng" nhìn thấy được (ảnh nền, nền đậm, khối hình không chữ) của một màn.
const makeMassOf = (root, rootBg) => (el) => {
  if (el === root) return false;
  if (el.hasAttribute('data-whitespace')) return true;
  const st = getComputedStyle(el);
  if (st.backgroundImage && st.backgroundImage !== 'none') return true;
  const own = toRgba(st.backgroundColor);
  if (own[3] >= 0.9 && ratio(own, rootBg) >= 1.5) return true;
  // Khối hình không chữ (thanh tiến độ, dòng khung xương, vạch biểu đồ) là nội dung nhìn thấy được.
  return own[3] > 0.05 && !el.children.length && !el.textContent.trim();
};
// Nhãn artboard/gallery nằm ngoài màn đánh dấu data-annotation để không bị soát như chữ trên màn.
const annotated = (el) => !!el.closest('[data-annotation]');
const saturated = (c) => c[3] > 0.3 && hsl(c)[1] >= 0.2 && hsl(c)[2] < 0.97;
const hueGap = (a, b) => { const d = Math.abs(hsl(a)[0] - hsl(b)[0]); return Math.min(d, 360 - d); };
const gradientColors = (value) => [...new Set((value.match(/rgba?\([^)]*\)|#[0-9a-f]{3,8}\b/gi) || []).map((v) => hex(toRgba(v))))];
