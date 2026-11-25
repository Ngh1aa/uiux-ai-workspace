/* taste-check: luật chữ (dot, contrast, wrap, wrap-room, widow, clipped, edge, ellipsis, small-text, subtitle, template-var, demo-note, emoji, font-mix).
 * Chạy trong trang (Playwright evaluate), không phải module Node. taste-check.cjs ghép các file trong
 * thư mục này theo thứ tự shared, text, card, layout, chart, audit vào một hàm rồi chạy một lần mỗi trang.
 * Mỗi luật nhận ctx = { root, all, isPart, rootRect, rootBg, errors, warnings, massOf, highlights }. */
const DEMO = /\b(?:dữ liệu|số liệu|lời|lịch|ngữ cảnh|nội dung|mẫu tương tác)\s+(?:mẫu|minh ho[aạ]|minh họa|từ đề|theo đề)|\b(?:bản|là) minh (?:ho[aạ]|họa)(?![\p{L}])|\bminh (?:ho[aạ]|họa) theo\b|\bbản mẫu (?:này|không|chưa)|\btrong bản mẫu\b|\bbrowser preview\b|\bdữ liệu (?:từ |theo )?đề bài\b|\bmô phỏng quyền\b|\btheo brief\b|\bbackend\b/iu;
const SUBTITLE = /[.?…]$|^(?:bấm|chạm|chọn|xem|nhấn|kéo|để|giúp|theo|mỗi|đây là|tất cả)\b/i;
const EMOJI = /\p{Emoji_Presentation}|\p{Extended_Pictographic}️/u;
// Chữ xuống dòng dù còn chỗ: bề rộng một dòng (đo trên bản sao không xuống dòng) vừa phần khung cha
// còn trống trên hàng của nó (trừ padding cha và khối anh em cùng hàng). Khối inline nằm giữa đoạn văn,
// có <br>, white-space pre hoặc định vị tuyệt đối thì bỏ qua. Trả về null nếu không còn chỗ thật.
const wrapRoom = (el, st) => {
  const parent = el.parentElement;
  if (!parent || st.display === 'inline' || /^(absolute|fixed)$/.test(st.position) || /^pre/.test(st.whiteSpace) ||
      el.querySelector('br') || el.matches('td, th')) return null;
  const ps = getComputedStyle(parent);
  const pr = parent.getBoundingClientRect();
  const er = el.getBoundingClientRect();
  const gap = /flex|grid/.test(ps.display) ? (parseFloat(ps.columnGap) || 0) : 0;
  let left = pr.left + parseFloat(ps.borderLeftWidth) + parseFloat(ps.paddingLeft);
  let right = pr.right - parseFloat(ps.borderRightWidth) - parseFloat(ps.paddingRight);
  for (const sib of parent.children) {
    if (sib === el || !visible(sib) || /^(absolute|fixed)$/.test(getComputedStyle(sib).position)) continue;
    const sr = sib.getBoundingClientRect();
    if (sr.bottom <= er.top + 1 || sr.top >= er.bottom - 1) continue;
    if (sr.left >= er.right - 1) right = Math.min(right, sr.left - gap);
    else if (sr.right <= er.left + 1) left = Math.max(left, sr.right + gap);
  }
  const free = right - left - (parseFloat(st.marginLeft) || 0) - (parseFloat(st.marginRight) || 0);
  const clone = el.cloneNode(true);
  clone.removeAttribute('id');
  clone.setAttribute('aria-hidden', 'true');
  Object.assign(clone.style, { position: 'absolute', visibility: 'hidden', left: '0', top: '0', whiteSpace: 'nowrap',
    width: 'max-content', minWidth: '0', maxWidth: 'none', flex: 'none' });
  parent.appendChild(clone);
  const need = clone.getBoundingClientRect().width;
  clone.remove();
  return need > 0 && need <= free - 1 ? { need: Math.ceil(need), free: Math.floor(free) } : null;
};
const textRules = {
  // 1. Dấu chấm giữa nối cụm từ
  dots(ctx) {
    const { root, errors } = ctx;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const parent = node.parentElement;
      if (!parent || !visible(parent) || parent.closest('script, style')) continue;
      const m = node.textContent.match(/\S[^\n]{0,24}\s[·•]\s[^\n]{0,24}\S/);
      if (m || /(^|\s)[·•](\s|$)/.test(node.textContent)) {
        errors.push({ rule: 'dot', message: `Dấu " · " nối cụm từ: "${(m ? m[0] : node.textContent).trim().slice(0, 60)}"` });
      }
    }
  },

  // Theo từng phần tử có chữ: tương phản, nhãn gãy dòng, dòng cuối một chữ, chữ bị cắt, sát mép, dấu …
  element(ctx, el, st) {
    const { root, rootRect, errors, warnings } = ctx;
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
      // 3. Nhãn ngắn bị gãy dòng; chữ ngắn (≤ 60 ký tự) xuống dòng dù khung cha còn đủ chỗ (TASTE "Chữ trên màn")
      const full = (el.textContent || '').replace(/\s+/g, ' ').trim();
      const wraps = text.length >= 2 && lineCount(el) > 1;
      let shortLabel = false;
      if (full.length <= 24 && wraps) {
        const label = el.matches(INTERACTIVE) || el.closest('label, button, [role="button"], [role="tab"]');
        const control = el.closest('button, [role="button"], [role="tab"]');
        // A rich record button can contain a wrapping patient/object name plus
        // separate time/status fields. That content is not a short CTA label.
        const richRecord = control && control !== el && control.children.length > 1 &&
          control.textContent.replace(/\s+/g, ' ').trim().length > 24;
        shortLabel = label && !richRecord;
        if (shortLabel) errors.push({ rule: 'wrap', message: `Nhãn điều khiển ngắn bị gãy dòng: ${describe(el)}` });
      }
      const room = wraps && !shortLabel && full.length <= 60 ? wrapRoom(el, st) : null;
      if (room) {
        warnings.push({ rule: 'wrap-room', message: `Xuống dòng dù còn chỗ: một dòng cần ${room.need}px, khung còn ${room.free}px: ${describe(el)}. Bỏ giới hạn bề rộng hoặc cho khối rộng ra` });
      } else if (full.length <= 24 && wraps && !shortLabel) {
        warnings.push({ rule: 'wrap-review', message: `Nội dung ngắn xuống dòng; kiểm tra chủ đích theo brief: ${describe(el)}` });
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
  },

  // Lộ biến mẫu {{…}} và ghi chú bản mẫu trên màn
  markers(ctx) {
    const { root, errors } = ctx;
    const textWalker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = textWalker.nextNode(); node; node = textWalker.nextNode()) {
      const parent = node.parentElement;
      if (!parent || !visible(parent) || parent.closest('script, style, template') || annotated(parent)) continue;
      const t = node.textContent.replace(/\s+/g, ' ').trim();
      if (!t) continue;
      if (/\{\{|\}\}/.test(t)) errors.push({ rule: 'template-var', message: `Lộ biến mẫu trên màn: "${t.slice(0, 60)}"` });
      if (DEMO.test(t)) errors.push({ rule: 'demo-note', message: `Ghi chú bản mẫu hiện trên màn: "${t.slice(0, 60)}". Chuyển vào phần bàn giao` });
    }
  },

  // Chữ dưới 12 px và dòng giải thích phụ dưới tiêu đề
  markup(ctx, el, st) {
    const { errors, warnings } = ctx;
    const text = ownText(el);
    // Chữ phụ dưới 12 px (làm tròn 11,5 để chừa sai số render).
    // Cỡ 0 là chữ ẩn có chủ đích (nhãn cho trình đọc màn hình trên vạch màu), không phải chữ nhỏ nhìn thấy.
    if (text && parseFloat(st.fontSize) < 11.5 && parseFloat(st.fontSize) >= 1) {
      errors.push({ rule: 'small-text', message: `Chữ ${parseFloat(st.fontSize).toFixed(1)}px < 12px: ${describe(el)}` });
    }
    // Dòng giải thích phụ ngay dưới tiêu đề.
    if (/^H[1-4]$/.test(el.tagName) || el.getAttribute('role') === 'heading') {
      const next = el.nextElementSibling;
      const nt = next && visible(next) && !next.matches(INTERACTIVE) && !next.closest('[role="alert"], [role="status"], [aria-live]')
        ? (next.textContent || '').replace(/\s+/g, ' ').trim() : '';
      if (nt && next.children.length <= 1 && parseFloat(getComputedStyle(next).fontSize) < parseFloat(st.fontSize) &&
          nt.split(' ').length >= 4 && SUBTITLE.test(nt)) {
        warnings.push({ rule: 'subtitle', message: `Dòng giải thích phụ dưới tiêu đề: "${nt.slice(0, 60)}". Bỏ nếu không phải dữ liệu, lỗi hay trạng thái` });
      }
    }
  },

  // Thang chữ (TASTE "Phong cách chung"): cảnh báo nhiều họ chữ trên một màn; trả về kiểu của từng cấp
  // tiêu đề để taste-check.cjs so giữa các màn và các trang (type-drift).
  typeScale(ctx) {
    const { all, warnings } = ctx;
    const families = new Map();
    const headings = [];
    for (const el of all) {
      if (annotated(el) || el.closest('svg, code, pre, kbd, samp, [aria-hidden="true"]')) continue;
      const st = getComputedStyle(el);
      const text = ownText(el);
      const family = st.fontFamily.split(',')[0].replace(/["']/g, '').trim();
      if (text && family && !/mono|icon|symbol|awesome/i.test(family)) {
        const seen = families.get(family.toLowerCase());
        families.set(family.toLowerCase(), seen || { family, where: describe(el) });
      }
      const tag = /^H([1-6])$/.exec(el.tagName);
      const level = tag ? tag[1] : el.getAttribute('role') === 'heading' ? (el.getAttribute('aria-level') || '2') : '';
      if (level && (el.textContent || '').trim()) {
        headings.push({ role: `h${level}`, style: `${Math.round(parseFloat(st.fontSize))}px ${st.fontWeight}`, where: describe(el) });
      }
    }
    if (families.size > 1) {
      const list = [...families.values()].map((f) => `${f.family} (${f.where})`).join(', ');
      warnings.push({ rule: 'font-mix', message: `${families.size} họ chữ trên một màn: ${list}. Dùng một họ chữ, phân cấp bằng cỡ và độ đậm` });
    }
    return headings;
  },

  // Emoji trong chữ
  emoji(ctx) {
    const { root, errors } = ctx;
    const emojiWalker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = emojiWalker.nextNode(); node; node = emojiWalker.nextNode()) {
      const parent = node.parentElement;
      if (!parent || !visible(parent) || annotated(parent) || parent.closest('script, style')) continue;
      const m = node.textContent.match(EMOJI);
      if (m) errors.push({ rule: 'emoji', message: `Emoji "${m[0]}" trong chữ: ${describe(parent)}. Dùng icon cùng bộ hoặc bỏ` });
    }
  },
};
