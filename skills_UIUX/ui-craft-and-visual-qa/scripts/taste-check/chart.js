/* taste-check: luật dashboard và biểu đồ (chart-donut, chart-gauge, chart-name, chart-values, chart-legend, status-series).
 * Chạy trong trang (Playwright evaluate), không phải module Node. taste-check.cjs ghép các file trong
 * thư mục này theo thứ tự shared, text, card, layout, chart, audit vào một hàm rồi chạy một lần mỗi trang.
 * Mỗi luật nhận ctx = { root, all, isPart, rootRect, rootBg, errors, warnings, massOf, highlights }. */
// Lớp hoặc data-status báo trạng thái cần chú ý; màu của chúng được giữ riêng cho trạng thái.
const STATUS = /(^|[\s_-])(risk|danger|error|alert|critical|warning|overdue|negative|unusual|late)([\s_-]|$)/i;
// Nhận biểu đồ không cần quy ước riêng: canvas, [data-chart], [role="img"] có vạch, SVG có đường/cột/vòng,
// donut vẽ bằng conic-gradient. Panel là card có nền/viền/bóng nằm trong lưới.
const chartRules = {
  // 10. Dashboard và biểu đồ: donut, gauge, tên, giá trị, chú giải, màu trạng thái
  charts(ctx) {
    const { root, all, errors, warnings } = ctx;
    const leafMarks = (el) => [...el.querySelectorAll('*')].filter((m) => {
      if (!visible(m) || m.children.length || m.textContent.trim()) return false;
      const r = m.getBoundingClientRect();
      if (m instanceof SVGElement) return m.matches('rect') && r.width <= 96 && r.height >= 4 && saturated(toRgba(getComputedStyle(m).fill));
      return r.width <= 96 && r.height >= 8 && saturated(toRgba(getComputedStyle(m).backgroundColor));
    });
    const isDonut = (el) => {
      const st = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const rad = st.borderTopLeftRadius.trim().endsWith('%') ? (parseFloat(st.borderTopLeftRadius) / 100) * r.width : parseFloat(st.borderTopLeftRadius);
      return /conic-gradient/.test(st.backgroundImage) && r.width >= 48 && Math.abs(r.width - r.height) < 4 && rad >= r.width * 0.4;
    };
    const svgChartLike = (svg) => !!svg.querySelector('polyline') ||
      [...svg.querySelectorAll('path, g')].some((p) => /line|area|grid|bar|series|chart|axis/i.test(p.getAttribute('class') || '')) ||
      svg.querySelectorAll('rect').length >= 3 || [...svg.querySelectorAll('circle')].filter((c) => getComputedStyle(c).strokeDasharray !== 'none').length >= 2;
    const charts = all.filter((el) => {
      if (el === root || annotated(el)) return false;
      if (el.matches('[data-chart]')) return true;
      const r = el.getBoundingClientRect();
      if (r.width < 96 || r.height < 48) return false;
      if (el.matches('canvas')) return true;
      if (el.matches('svg')) return el.getAttribute('aria-hidden') !== 'true' && svgChartLike(el) && !el.parentElement.closest('[role="img"], [data-chart]');
      if (isDonut(el)) return !el.parentElement.closest('[role="img"], [data-chart]');
      return el.getAttribute('role') === 'img' && !el.matches('img') && !el.parentElement.closest('[role="img"], [data-chart]') && leafMarks(el).length >= 3;
    });
    const accName = (el) => {
      const ids = (el.getAttribute('aria-labelledby') || '').split(/\s+/).filter(Boolean);
      const byId = ids.map((id) => (document.getElementById(id) || {}).textContent || '').join(' ');
      const title = el.matches('svg') ? (el.querySelector(':scope > title') || {}).textContent || '' : '';
      const caption = (el.closest('figure') && el.closest('figure').querySelector('figcaption')) ? el.closest('figure').querySelector('figcaption').textContent : '';
      return `${el.getAttribute('aria-label') || ''} ${byId} ${title} ${caption}`.replace(/\s+/g, ' ').trim();
    };
    const panelOf = (el) => el.closest('[data-panel], section, article, figure') || el.parentElement;
    const statusColors = [];
    for (const el of all) {
      const cls = `${typeof el.className === 'string' ? el.className : ''} ${el.getAttribute('data-status') || ''}`;
      if (!(STATUS.test(cls) || el.getAttribute('role') === 'alert') || charts.some((c) => c.contains(el))) continue;
      const st = getComputedStyle(el);
      // Chữ mực gần đen hay nền gần trắng không phải màu trạng thái.
      for (const v of [st.color, st.backgroundColor]) { const c = toRgba(v); if (saturated(c) && hsl(c)[1] >= 0.3 && hsl(c)[2] > 0.2) statusColors.push({ c, el }); }
    }
    const markColors = [];
    for (const chart of charts) {
      const name = accName(chart);
      const label = describe(chart).split(' "')[0];
      const donuts = [chart, ...chart.querySelectorAll('*')].filter((n) => visible(n) && isDonut(n));
      const svgArcs = chart.matches('svg') ? [...chart.querySelectorAll('circle')].filter((c) => getComputedStyle(c).strokeDasharray !== 'none') : [];
      const parts = donuts.length ? gradientColors(getComputedStyle(donuts[0]).backgroundImage).length : svgArcs.length;
      const percentInside = /\d\s?%/.test(chart.textContent);
      if (parts > 3) {
        errors.push({ rule: 'chart-donut', message: `Donut/pie ${parts} phần (tối đa 3): ${label} "${name.slice(0, 40)}". Dùng thanh ngang xếp theo giá trị, ghi nhãn trực tiếp` });
      } else if ((donuts.length || svgArcs.length) && parts <= 2 && percentInside) {
        warnings.push({ rule: 'chart-gauge', message: `Vòng tiến độ cho một con số: ${label} "${name.slice(0, 40)}". Dùng số lớn kèm thanh tiến độ ngang` });
      }
      if (!name) errors.push({ rule: 'chart-name', message: `Biểu đồ không có tên cho trình đọc màn hình: ${label}. Thêm aria-label nêu kết luận, hoặc figure + figcaption` });
      const bars = leafMarks(chart);
      const panel = panelOf(chart);
      const hasTable = !!(panel && panel.querySelector('table'));
      if (bars.length >= 3 && !/\d/.test(chart.textContent) && !/\d/.test(name) && !hasTable) {
        warnings.push({ rule: 'chart-values', message: `${bars.length} cột không có giá trị đọc được (không nhãn số, tên biểu đồ không có số, không có bảng): ${label} "${name.slice(0, 40)}". Ghi giá trị trên cột hoặc nêu số trong tóm tắt` });
      }
      if (panel && panel !== root) {
        const swatches = [...panel.querySelectorAll('*')].filter((s) => {
          if (chart.contains(s) || !visible(s) || s.children.length || s.textContent.trim()) return false;
          const r = s.getBoundingClientRect();
          return r.width >= 4 && r.width <= 16 && r.height >= 4 && r.height <= 16 && saturated(toRgba(getComputedStyle(s).backgroundColor)) &&
            s.parentElement && s.parentElement.textContent.trim().length > 0;
        });
        if (swatches.length >= 2) {
          warnings.push({ rule: 'chart-legend', message: `Chú giải ${swatches.length} ô màu tách khỏi biểu đồ ${label} "${name.slice(0, 40)}". Ghi nhãn trực tiếp lên vạch hoặc đầu dòng, bỏ chú giải` });
        }
        for (const s of swatches) markColors.push({ c: toRgba(getComputedStyle(s).backgroundColor), chart });
      }
      for (const m of bars) markColors.push({ c: toRgba(m instanceof SVGElement ? getComputedStyle(m).fill : getComputedStyle(m).backgroundColor), chart });
      for (const d of donuts) for (const v of gradientColors(getComputedStyle(d).backgroundImage)) markColors.push({ c: toRgba(v), chart });
    }
    const clashed = new Set();
    for (const mark of markColors) {
      if (!saturated(mark.c) || clashed.has(mark.chart)) continue;
      const hit = statusColors.find((s) => hueGap(s.c, mark.c) < 15);
      if (hit) {
        clashed.add(mark.chart);
        warnings.push({ rule: 'status-series', message: `Màu dữ liệu ${hex(mark.c)} trùng sắc màu trạng thái ${hex(hit.c)} của ${describe(hit.el)}. Giữ màu trạng thái cho trạng thái, đổi màu series` });
      }
    }
  },
};
