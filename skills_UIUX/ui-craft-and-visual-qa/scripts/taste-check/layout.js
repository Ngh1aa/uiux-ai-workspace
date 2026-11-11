/* taste-check: luật bố cục (overflow, table-scroll, icon-missing, target, fixed-overlap, void, coverage, flat-scale, thin-highlight, colors, panel-void, panel-orphan).
 * Chạy trong trang (Playwright evaluate), không phải module Node. taste-check.cjs ghép các file trong
 * thư mục này theo thứ tự shared, text, card, layout, chart, audit vào một hàm rồi chạy một lần mỗi trang.
 * Mỗi luật nhận ctx = { root, all, isPart, rootRect, rootBg, errors, warnings, massOf, highlights }. */
const layoutRules = {
  // Theo từng phần tử: tràn ngang, vùng chạm
  element(ctx, el, st) {
    const { errors, warnings } = ctx;
    // 4. Tràn ngang
    const clips = ['visible', 'clip'].includes(st.overflowX);
    if (clips && !(el instanceof SVGElement) && el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0 && el.textContent.trim()) {
      const inner = [...el.children].some((c) => c.scrollWidth > c.clientWidth + 1 && getComputedStyle(c).overflowX === st.overflowX);
      if (!inner) errors.push({ rule: 'overflow', message: `Nội dung tràn ngang ${el.scrollWidth - el.clientWidth}px: ${describe(el)}` });
    }

    // Bảng cuộn ngang trên màn rộng: luật "clipped" bỏ qua khung cuộn vì người dùng cuộn được,
    // nhưng ở desktop cột cuối (thường là trạng thái hay hành động) bị khuất là lỗi bố cục.
    if (['auto', 'scroll'].includes(st.overflowX) && ctx.rootRect.width >= 1024 && el.querySelector('table') &&
        el.scrollWidth > el.clientWidth + 8 && el.clientWidth > 0) {
      warnings.push({ rule: 'table-scroll', message: `Bảng phải cuộn ngang ${el.scrollWidth - el.clientWidth}px ở màn rộng: ${describe(el)}. Bớt hoặc gộp cột, hoặc cho bảng thêm chỗ` });
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
  },

  // Icon trỏ tới symbol không có trong trang: trình duyệt vẽ ô trống, không báo lỗi.
  iconRefs(ctx) {
    const { root, errors } = ctx;
    const missing = new Set();
    for (const use of root.querySelectorAll('use')) {
      const ref = use.getAttribute('href') || use.getAttribute('xlink:href') || '';
      if (ref.startsWith('#') && !document.getElementById(ref.slice(1))) missing.add(ref);
    }
    for (const ref of missing) errors.push({ rule: 'icon-missing', message: `Icon ${ref} không có trong trang (thiếu <symbol id="${ref.slice(1)}">)` });
  },

  // Cả màn tràn ngang
  rootOverflow(ctx) {
    const { root, errors } = ctx;
    if (root !== document.body && root.scrollWidth > root.clientWidth + 1 && getComputedStyle(root).overflowX !== 'hidden') {
      errors.push({ rule: 'overflow', message: `Màn tràn ngang ${root.scrollWidth - root.clientWidth}px` });
    }
  },

  // 8. Khoảng trống dọc thừa (void) và độ phủ ngang (coverage)
  space(ctx) {
    const { root, all, isPart, rootRect, warnings, massOf } = ctx;
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
  },

  // Thang chữ phẳng: chữ lớn nhất không đủ khác chữ thân
  flatScale(ctx) {
    const { all, isPart, rootRect, warnings } = ctx;
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
  },

  // Card nổi bật quá mỏng: ít nhất 3 dòng ở 2 cỡ chữ, nội dung phủ phần lớn card
  thinHighlight(ctx) {
    const { warnings, highlights } = ctx;
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
  },

  // 7. Số nhóm màu trong một màn
  colors(ctx) {
    const { all, warnings } = ctx;
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
  },

  // Thanh cố định ở đáy (bottom nav, thanh hành động) che nội dung khi đã cuộn hết
  fixedOverlap(ctx) {
    const { root, all, rootRect, errors } = ctx;
    const bars = all.filter((el) => {
      if (el === root || el.closest('[role="dialog"], [aria-modal="true"]')) return false;
      const st = getComputedStyle(el);
      if (!['fixed', 'sticky', 'absolute'].includes(st.position)) return false;
      const r = el.getBoundingClientRect();
      if (r.width < rootRect.width * 0.6 || r.height < 32 || r.height > 160) return false;
      if (toRgba(st.backgroundColor)[3] < 0.9 && !(st.backgroundImage && st.backgroundImage !== 'none')) return false;
      if (st.position === 'fixed') return Math.abs(r.bottom - window.innerHeight) <= 4;
      // sticky: mép đáy vùng cuộn; absolute: mép đáy khối định vị gần nhất (khung điện thoại).
      let port = null;
      for (let n = el.parentElement; n && !port; n = n.parentElement) {
        const ns = getComputedStyle(n);
        if (['auto', 'scroll'].includes(ns.overflowY)) port = n;
        else if (st.position === 'absolute' && ns.position !== 'static') port = n;
      }
      const bottom = port ? Math.min(port.getBoundingClientRect().bottom, port === document.scrollingElement ? window.innerHeight : Infinity) : window.innerHeight;
      return Math.abs(r.bottom - bottom) <= 4;
    });
    if (bars.length) {
      const scrollerOf = (el) => {
        for (let n = el.parentElement; n; n = n.parentElement) {
          const ns = getComputedStyle(n);
          if (['auto', 'scroll'].includes(ns.overflowY) && n.scrollHeight > n.clientHeight + 1) return n;
        }
        return document.scrollingElement;
      };
      const targets = all.filter((el) => el !== root && !bars.some((b) => b.contains(el) || el.contains(b)) &&
        (el.matches(INTERACTIVE) || ownText(el)) && !annotated(el));
      const saved = new Map();
      for (const el of targets) {
        const sc = scrollerOf(el);
        if (!saved.has(sc)) { saved.set(sc, sc.scrollTop); sc.scrollTop = sc.scrollHeight; }
      }
      for (const el of targets) {
        const r = el.getBoundingClientRect();
        if (!(r.width > 0 && r.height > 0)) continue;
        for (const bar of bars) {
          const b = bar.getBoundingClientRect();
          const dy = Math.min(r.bottom, b.bottom) - Math.max(r.top, b.top);
          const dx = Math.min(r.right, b.right) - Math.max(r.left, b.left);
          if (dy > 4 && dx > 4) {
            errors.push({ rule: 'fixed-overlap', message: `${describe(el)} bị ${describe(bar).split(' ')[0]} che ${Math.round(dy)}px khi đã cuộn hết. Thêm khoảng đệm đáy bằng chiều cao thanh` });
            break;
          }
        }
      }
      for (const [sc, top] of saved) sc.scrollTop = top;
    }
  },

  // Panel trong lưới: trống đáy tới đáy hàng (panel-void), panel lẻ ở hàng cuối hay giữa lưới (panel-orphan)
  panels(ctx) {
    const { root, all, rootRect, rootBg, warnings, massOf } = ctx;
    const panelSurface = (el) => {
      // Ảnh/biểu đồ (role="img") và thanh điều hướng phụ (cột nav cao theo nội dung bên cạnh) không phải panel nội dung.
      if (el === root || el.matches(CONTROL) || el.matches(MEDIA) || el.matches('nav, aside, [role="navigation"], [role="complementary"]') || annotated(el)) return false;
      const r = el.getBoundingClientRect();
      if (r.width < 180 || r.height < 120 || r.width >= rootRect.width - 2) return false;
      const { own, hasBg, hasEdge, hasShadow } = surfaceOf(el);
      if (!(hasBg || hasEdge || hasShadow)) return false;
      return !(own[3] >= 0.999 && ratio(own, backdrop(el.parentElement) || rootBg) < 1.02 && !hasEdge && !hasShadow);
    };
    const containers = new Set(all.filter(panelSurface).map((p) => p.parentElement).filter(Boolean));
    for (const box of containers) {
      const bst = getComputedStyle(box);
      const multi = bst.display.includes('grid') || (bst.display.includes('flex') && bst.flexWrap === 'wrap');
      const items = [...box.children].filter((c) => visible(c) && panelSurface(c) && getComputedStyle(c).position !== 'absolute');
      if (!multi || items.length < 2) continue;
      for (const card of items) {
        if (card.hasAttribute('data-whitespace') || card.querySelector('[data-whitespace]')) continue;
        const cr = card.getBoundingClientRect();
        const cs = getComputedStyle(card);
        const parts = [...card.querySelectorAll('*')].filter((n) => visible(n) && !(n.closest('svg') && n.closest('svg') !== n) && (ownText(n) || n.matches(MEDIA) || massOf(n)));
        if (!parts.length) continue;
        const bottom = Math.max(...parts.flatMap((n) => (ownText(n) && !n.matches(MEDIA) ? textRects(n) : [n.getBoundingClientRect()])).map((r) => r.bottom));
        // Card ngắn hơn hàng (align-items: start) cũng để lại khoảng trống tới đáy hàng.
        const rowmates = items.map((c) => c.getBoundingClientRect()).filter((o) => Math.abs(o.top - cr.top) < 6);
        const below = items.map((c) => c.getBoundingClientRect()).filter((o) => o.top >= cr.bottom - 1 && Math.min(o.right, cr.right) - Math.max(o.left, cr.left) > 8);
        const rowBottom = Math.max(cr.bottom, Math.min(Math.max(...rowmates.map((o) => o.bottom)), ...below.map((o) => o.top - parseFloat(bst.rowGap || 0) - 1)));
        const gap = rowBottom - parseFloat(cs.paddingBottom || 0) - parseFloat(cs.borderBottomWidth || 0) - bottom;
        if (gap > Math.max(96, (rowBottom - cr.top) * 0.25)) {
          warnings.push({ rule: 'panel-void', message: `Panel trống ${Math.round(gap)}px ở đáy (${Math.round((gap / cr.height) * 100)}% chiều cao): ${describe(card)}. Cân lại lưới (đổi span, ghép panel, thêm nội dung có ích) thay vì để hàng kéo giãn` });
        }
      }
      if (items.length < 3) continue;
      const rows = [];
      for (const card of items) {
        const r = card.getBoundingClientRect();
        const row = rows.find((x) => Math.abs(x.top - r.top) < 6);
        if (row) row.items.push(r); else rows.push({ top: r.top, items: [r] });
      }
      rows.sort((a, b) => a.top - b.top);
      const last = rows[rows.length - 1];
      const inner = box.getBoundingClientRect().width - parseFloat(bst.paddingLeft || 0) - parseFloat(bst.paddingRight || 0);
      // Panel trải nhiều hàng từ hàng trên xuống (grid-row: span 2) vẫn lấp chỗ ở hàng cuối.
      const spanning = items.map((c) => c.getBoundingClientRect()).filter((r) => r.top < last.top - 6 && r.bottom > last.top + 6);
      const used = last.items[0].width + spanning.reduce((sum, r) => sum + r.width, 0);
      if (rows.length >= 2 && last.items.length === 1 && used < inner * 0.6 && rows.slice(0, -1).some((x) => x.items.length >= 2)) {
        warnings.push({ rule: 'panel-orphan', message: `Panel lẻ một mình ở hàng cuối, bỏ trống ${Math.round(inner - last.items[0].width)}px: ${describe(items.find((c) => Math.abs(c.getBoundingClientRect().top - last.top) < 6))}. Cho panel trải hết hàng hoặc chia lại lưới` });
      }
      // Hàng giữa cũng không được thủng: một panel lẻ chiếm chưa tới 60% hàng.
      for (const row of rows.slice(0, -1)) {
        if (row.items.length !== 1 || !rows.some((x) => x !== row && x.items.length >= 2)) continue;
        const over = items.map((c) => c.getBoundingClientRect()).filter((r) => r.top < row.top - 6 && r.bottom > row.top + 6);
        if (row.items[0].width + over.reduce((sum, r) => sum + r.width, 0) < inner * 0.6) {
          warnings.push({ rule: 'panel-orphan', message: `Panel lẻ một mình giữa lưới, bỏ trống ${Math.round(inner - row.items[0].width)}px bên cạnh: ${describe(items.find((c) => Math.abs(c.getBoundingClientRect().top - row.top) < 6))}. Xếp lại cột hoặc cho panel trải hết hàng` });
        }
      }
    }
  },
};
