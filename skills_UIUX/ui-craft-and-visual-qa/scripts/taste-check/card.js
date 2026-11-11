/* taste-check: luật card (highlight, radius, left-bar, decor-overlap, decor-texture, card-spill, card-padding, card-inset, card-wide, gradient-surface, glow, tile-rainbow, eyebrow).
 * Chạy trong trang (Playwright evaluate), không phải module Node. taste-check.cjs ghép các file trong
 * thư mục này theo thứ tự shared, text, card, layout, chart, audit vào một hàm rồi chạy một lần mỗi trang.
 * Mỗi luật nhận ctx = { root, all, isPart, rootRect, rootBg, errors, warnings, massOf, highlights }. */
const LANDMARK = 'main, header, footer, nav, figure, [role="main"], [role="banner"], [role="contentinfo"], [role="navigation"], [role="tablist"]';
const cardRules = {
  // 5. Card nổi bật (tối đa một) và 6. bo góc đồng nhất. Trả về danh sách card nổi bật.
  highlightAndRadius(ctx) {
    const { root, all, rootRect, rootBg, errors, warnings } = ctx;
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
    return highlights;
  },

  // Thanh màu bên trái và hoạ tiết ::before/::after đè chữ
  decor(ctx, el, st) {
    const { warnings } = ctx;
    const { root, errors } = ctx;
    if (el === root || el.matches(CONTROL) || el.closest('nav, [role="navigation"], [role="tablist"]') || el.matches('blockquote') || el.querySelector(':scope > blockquote')) return;
    // Thanh màu bên trái card hay dòng: viền trái dày có màu, hoặc ::before/::after dạng vạch dọc sát mép trái.
    const r = el.getBoundingClientRect();
    if (r.height >= 24 && el.textContent.trim()) {
      const lw = parseFloat(st.borderLeftWidth) || 0;
      const rw = parseFloat(st.borderRightWidth) || 0;
      const lc = toRgba(st.borderLeftColor);
      const coloured = (c) => c[3] > 0.3 && hsl(c)[1] >= 0.2;
      let bar = st.borderLeftStyle !== 'none' && lw >= 3 && rw <= lw / 2 && coloured(lc);
      for (const pseudo of ['::before', '::after']) {
        if (bar) break;
        const ps = getComputedStyle(el, pseudo);
        if (!ps.content || ps.content === 'none' || ps.display === 'none' || ps.position !== 'absolute') continue;
        const w = parseFloat(ps.width) || 0;
        const h = parseFloat(ps.height) || 0;
        const left = parseFloat(ps.left);
        bar = w > 0 && w <= 8 && h >= r.height * 0.6 && Number.isFinite(left) && left <= 4 && coloured(toRgba(ps.backgroundColor));
      }
      if (bar) errors.push({ rule: 'left-bar', message: `Thanh màu bên trái: ${describe(el)}. Dùng nhãn chữ, chip hoặc icon cho trạng thái` });
    }
    // Hoạ tiết ::before/::after định vị tuyệt đối chạy qua dòng chữ bên trong khối.
    if (['relative', 'absolute', 'fixed', 'sticky'].includes(st.position)) {
      const lines = [...el.querySelectorAll('*')].filter((c) => visible(c) && ownText(c) && !annotated(c)).flatMap((c) => textRects(c));
      if (!lines.length) return;
      for (const pseudo of ['::before', '::after']) {
        const ps = getComputedStyle(el, pseudo);
        if (!ps.content || ps.content === 'none' || ps.display === 'none' || ps.position !== 'absolute') continue;
        if (ps.content !== '""' && ps.content !== "''") continue; // ký tự trang trí như dấu ngoặc kép là chữ, không phải hoạ tiết
        const painted = (toRgba(ps.backgroundColor)[3] > 0.05 || ps.backgroundImage !== 'none' ||
          ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(ps[`border${s}Width`]) > 0 && ps[`border${s}Style`] !== 'none'));
        if (!painted || Number(ps.opacity) < 0.03) continue;
        const bl = parseFloat(st.borderLeftWidth) || 0;
        const bt = parseFloat(st.borderTopWidth) || 0;
        const w = parseFloat(ps.width) || 0;
        const h = parseFloat(ps.height) || 0;
        const px = r.left + bl + (Number.isFinite(parseFloat(ps.left)) ? parseFloat(ps.left) : (r.width - bl - (parseFloat(st.borderRightWidth) || 0)) - w - (parseFloat(ps.right) || 0));
        const py = r.top + bt + (Number.isFinite(parseFloat(ps.top)) ? parseFloat(ps.top) : (r.height - bt - (parseFloat(st.borderBottomWidth) || 0)) - h - (parseFloat(ps.bottom) || 0));
        // Vân nền phủ kín cả khối (background-image, không viền) là bề mặt, không phải hoạ tiết đặt lên chữ.
        const noBorder = ['Top', 'Right', 'Bottom', 'Left'].every((s) => !(parseFloat(ps[`border${s}Width`]) > 0) || ps[`border${s}Style`] === 'none');
        if (noBorder && ps.backgroundImage !== 'none' && w * h >= r.width * r.height * 0.9) {
          // Vân nền là bề mặt, nhưng vân có nét (gradient lặp, sọc) chạy qua chữ cỡ lớn làm số khó đọc.
          const big = [...el.querySelectorAll('*')].find((c) => visible(c) && ownText(c) && !annotated(c) && parseFloat(getComputedStyle(c).fontSize) >= 24);
          if (big && /repeating-|linear-gradient/.test(ps.backgroundImage)) {
            warnings.push({ rule: 'decor-texture', message: `Vân nền ${pseudo} của ${describe(el)} chạy qua chữ lớn ${describe(big)}. Mở ảnh kiểm độ đọc, hoặc để vân tránh vùng số` });
          }
          continue;
        }
        const hit = lines.find((t) => Math.min(t.right, px + w) - Math.max(t.left, px) > 4 && Math.min(t.bottom, py + h) - Math.max(t.top, py) > 2);
        if (hit) errors.push({ rule: 'decor-overlap', message: `Hoạ tiết ${pseudo} của ${describe(el)} đè lên chữ. Dời hoạ tiết ra vùng không có chữ` });
      }
    }
  },

  // Card: padding đều, lề trong đều, không rộng quá nội dung
  paddingAndWidth(ctx) {
    const { root, all, rootRect, rootBg, errors, warnings, massOf } = ctx;
    const isCard = (el) => {
      if (el === root || el.matches(CONTROL) || el.matches(MEDIA) || el.matches(LANDMARK) || el.querySelector(LANDMARK) || annotated(el)) return false;
      if (el.closest('svg') || el.closest('[data-artwork]')) return false;
      const st = getComputedStyle(el);
      if (st.display.startsWith('inline') && st.display !== 'inline-block' && st.display !== 'inline-flex' && st.display !== 'inline-grid') return false;
      const r = el.getBoundingClientRect();
      const radius = parseFloat(st.borderTopLeftRadius) || 0;
      if (r.width < 120 || r.height < 72 || radius < 8 || radius >= Math.min(r.width, r.height) / 2 - 1 || r.width >= rootRect.width - 2) return false;
      const { own, hasBg, hasEdge, hasShadow } = surfaceOf(el);
      if (!(hasBg || hasEdge || hasShadow)) return false;
      return !(own[3] >= 0.999 && ratio(own, backdrop(el.parentElement) || rootBg) < 1.02 && !hasEdge && !hasShadow);
    };
    const cardList = all.filter(isCard);
    const cardSet = new Set(cardList);
    const contentRects = (card) => {
      const rects = [...textRects(card)];
      for (const n of card.querySelectorAll('*')) {
        if (!visible(n) || (n.closest('svg') && n.closest('svg') !== n)) continue;
        const sf = surfaceOf(n);
        if (n.matches(MEDIA) || n.matches(CONTROL) || (n.matches(INTERACTIVE) && getComputedStyle(n).display !== 'inline') || cardSet.has(n) || massOf(n) || sf.hasBg || sf.hasEdge) rects.push(n.getBoundingClientRect());
        else if (ownText(n)) rects.push(...textRects(n));
      }
      return rects.filter((x) => x.width >= 1 && x.height >= 1);
    };
    // Nội dung tràn khỏi card (card không cắt): chữ hay nút nằm ngoài khung nhìn thấy được.
    for (const card of cardList) {
      const cs = getComputedStyle(card);
      if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') continue; // card tự cắt hoặc cuộn
      const r = card.getBoundingClientRect();
      for (const n of card.querySelectorAll('*')) {
        if (!visible(n) || !(ownText(n) || n.matches(CONTROL))) continue;
        let clipped = false;
        for (let a = n.parentElement; a && a !== card; a = a.parentElement) {
          const as = getComputedStyle(a);
          if (as.overflowX !== 'visible' || as.overflowY !== 'visible' || ['absolute', 'fixed'].includes(as.position)) { clipped = true; break; }
        }
        if (clipped || ['absolute', 'fixed'].includes(getComputedStyle(n).position)) continue;
        const nr = n.getBoundingClientRect();
        const out = Math.max(nr.bottom - r.bottom, nr.right - r.right);
        // Hộp chữ inline nhô vài px khỏi dòng là bình thường; tràn thật thì lệch cả dòng chữ trở lên.
        if (out > 4) {
          errors.push({ rule: 'card-spill', message: `Nội dung tràn ra ngoài card ${Math.round(out)}px: ${describe(n)} trong ${describe(card)}. Thu nội dung, cho card cao hơn hoặc cho phép cuộn` });
          break;
        }
      }
    }
    for (const card of cardList) {
      const st = getComputedStyle(card);
      const r = card.getBoundingClientRect();
      const pad = ['Top', 'Right', 'Bottom', 'Left'].map((s) => parseFloat(st[`padding${s}`]) || 0);
      const bw = ['Top', 'Right', 'Bottom', 'Left'].map((s) => parseFloat(st[`border${s}Width`]) || 0);
      if (Math.min(...pad) > 0 && Math.max(...pad) - Math.min(...pad) > 2) {
        errors.push({ rule: 'card-padding', message: `Padding card không đều (${pad.map((p) => Math.round(p)).join(' ')} px): ${describe(card)}. Dùng một giá trị cho cả bốn cạnh` });
      }
      const rects = contentRects(card);
      if (!rects.length) continue;
      const left = Math.min(...rects.map((x) => x.left));
      const right = Math.max(...rects.map((x) => x.right));
      const top = Math.min(...rects.map((x) => x.top));
      const bottom = Math.max(...rects.map((x) => x.bottom));
      const insetTop = top - r.top - bw[0];
      const insetLeft = left - r.left - bw[3];
      const insetRight = r.right - bw[1] - right;
      const insetBottom = r.bottom - bw[2] - bottom;
      // Nội dung căn giữa (ngang hoặc dọc) là bố cục có chủ đích, không so lề trên với lề trái.
      const centred = Math.abs(insetLeft - insetRight) < 8 || Math.abs(insetTop - insetBottom) < 8;
      if (!centred && insetTop >= 0 && insetLeft >= 0 && Math.abs(insetTop - insetLeft) > 8) {
        warnings.push({ rule: 'card-inset', message: `Lề trong card lệch: trên ${Math.round(insetTop)}px, trái ${Math.round(insetLeft)}px: ${describe(card)}. Khoảng từ mép card tới nội dung phải bằng nhau ở mọi cạnh` });
      } else if (!centred && insetTop >= 0) {
        // Lề đáy đo ở chiều cao tự nhiên của card (bỏ kéo giãn theo hàng lưới, đã có panel-void lo).
        const saved = card.getAttribute('style');
        card.style.setProperty('height', 'auto', 'important');
        card.style.setProperty('min-height', '0', 'important');
        const pst = card.parentElement ? getComputedStyle(card.parentElement) : null;
        // Chỉ bỏ kéo giãn theo trục dọc; trong flex dọc, align-self đổi bề ngang nên không đụng.
        if (pst && (pst.display.includes('grid') || (pst.display.includes('flex') && !pst.flexDirection.startsWith('column')))) card.style.setProperty('align-self', 'flex-start', 'important');
        card.style.setProperty('flex-grow', '0', 'important');
        const natural = card.getBoundingClientRect();
        const naturalRects = contentRects(card);
        const naturalBottom = naturalRects.length ? Math.max(...naturalRects.map((x) => x.bottom)) : natural.bottom;
        const naturalInset = natural.bottom - bw[2] - naturalBottom;
        if (saved === null) card.removeAttribute('style'); else card.setAttribute('style', saved);
        if (naturalInset - insetTop > 8) {
          warnings.push({ rule: 'card-inset', message: `Lề trong card lệch: trên ${Math.round(insetTop)}px, đáy ${Math.round(naturalInset)}px: ${describe(card)}. Dòng cuối sát padding như dòng đầu` });
        }
      }
      const innerW = r.width - pad[1] - pad[3] - bw[1] - bw[3];
      if (r.width >= 360 && innerW > 0 && Math.abs(insetLeft - insetRight) >= 8 && !card.hasAttribute('data-whitespace') && (right - left) / innerW < 0.55) {
        warnings.push({ rule: 'card-wide', message: `Card rộng ${Math.round(r.width)}px mà nội dung chỉ chiếm ${Math.round(((right - left) / innerW) * 100)}% bề ngang: ${describe(card)}. Thu card về cỡ nội dung, ghép với card khác trên cùng hàng, hoặc xếp nội dung ngang` });
      }
    }
  },

  // Dấu hiệu "AI hoá": nền hay chữ gradient, bóng phát sáng màu
  aiLook(ctx) {
    const { root, all, warnings } = ctx;
    for (const el of all) {
      if (el === root || el.matches(MEDIA) || el.closest('svg, [data-artwork], [role="img"], [data-chart]') || annotated(el)) continue;
      const st = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const bgImage = st.backgroundImage || '';
      const loading = el.closest('[aria-busy="true"]') || /skeleton|shimmer/i.test(typeof el.className === 'string' ? el.className : '');
      if (!loading && /(linear|radial)-gradient/.test(bgImage) && r.width >= 120 && r.height >= 48) {
        const stops = gradientColors(bgImage).map(toRgba).filter((c) => c[3] > 0.05);
        const tinted = stops.some((c) => saturated(c)) && new Set(stops.map((c) => hex(c))).size > 1;
        if (tinted) warnings.push({ rule: 'gradient-surface', message: `Nền gradient trên khối ${Math.round(r.width)}×${Math.round(r.height)}: ${describe(el)}. Dùng một màu phẳng theo vai trò; ảnh minh hoạ thật thì đánh dấu data-artwork` });
      }
      if (/text/.test(st.webkitBackgroundClip || st.backgroundClip || '') && /gradient/.test(bgImage) && ownText(el)) {
        warnings.push({ rule: 'gradient-surface', message: `Chữ tô gradient: ${describe(el)}. Dùng màu chữ phẳng` });
      }
      if (st.boxShadow && st.boxShadow !== 'none') {
        for (const layer of st.boxShadow.split(/,(?![^(]*\))/)) {
          const color = (layer.match(/rgba?\([^)]*\)|#[0-9a-f]{3,8}/i) || [])[0];
          const nums = layer.replace(/rgba?\([^)]*\)/g, '').match(/-?\d+(\.\d+)?px/g) || [];
          const blur = nums.length >= 3 ? parseFloat(nums[2]) : 0;
          const c = color ? toRgba(color) : null;
          if (c && !/inset/.test(layer) && blur >= 12 && c[3] >= 0.2 && saturated(c) && hsl(c)[1] >= 0.4) {
            warnings.push({ rule: 'glow', message: `Bóng phát sáng màu ${hex(c)}: ${describe(el)}. Bỏ glow, dùng bóng trung tính hoặc không bóng` });
            break;
          }
        }
      }
    }
  },

  // Ô icon hay ô nhỏ cùng loại tô nhiều màu khác nhau (icon cầu vồng)
  tileRainbow(ctx) {
    const { root, all, warnings } = ctx;
    const tileGroups = new Map();
    const parentIds = new Map();
    for (const el of all) {
      if (el === root || annotated(el) || el.closest('svg, [role="img"], [data-chart]')) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 20 || r.height < 20 || r.width > 160 || r.height > 160) continue;
      const c = toRgba(getComputedStyle(el).backgroundColor);
      if (c[3] < 0.05 || !saturated(c) || hsl(c)[1] < 0.25) continue;
      const cls = typeof el.className === 'string' && el.className.trim() ? el.className.trim().split(/\s+/)[0] : '';
      if (!parentIds.has(el.parentElement)) parentIds.set(el.parentElement, parentIds.size);
      const key = cls ? `c:${cls}` : `p:${parentIds.get(el.parentElement)}`;
      if (!tileGroups.has(key)) tileGroups.set(key, []);
      tileGroups.get(key).push({ el, c });
    }
    for (const group of tileGroups.values()) {
      if (group.length < 3) continue;
      const hueList = [];
      for (const { c } of group) if (!hueList.some((h) => hueGap(h, c) < 30)) hueList.push(c);
      if (hueList.length >= 3) {
        warnings.push({ rule: 'tile-rainbow', message: `${group.length} ô cùng loại tô ${hueList.length} màu khác nhau (${hueList.map(hex).join(', ')}): ${describe(group[0].el)}. Dùng một màu nền chung; màu chỉ để báo trạng thái` });
      }
    }
  },

  // Overline: nhãn ngắn, nhỏ đặt ngay trên tiêu đề, lặp lại ở nhiều khối
  eyebrow(ctx) {
    const { all, warnings } = ctx;
    const overlines = all.filter((el) => {
      const text = ownText(el);
      const next = el.nextElementSibling;
      if (!text || el.children.length || annotated(el) || !next || !visible(next) || !next.matches('h1, h2, h3, h4, [role="heading"]')) return false;
      if (text.split(/\s+/).length > 4 || /\d/.test(text)) return false;
      const st = getComputedStyle(el);
      return parseFloat(st.fontSize) <= parseFloat(getComputedStyle(next).fontSize) - 2;
    });
    if (overlines.length >= 2) {
      warnings.push({ rule: 'eyebrow', message: `${overlines.length} tiêu đề có nhãn nhỏ phía trên (${overlines.slice(0, 4).map((el) => `"${ownText(el)}"`).join(', ')}). Bỏ overline, để tiêu đề tự nói` });
    }
  },
};
