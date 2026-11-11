/* taste-check: chạy các nhóm luật trên từng màn, đúng thứ tự cũ để kết quả không đổi.
 * Chạy trong trang (Playwright evaluate), không phải module Node. taste-check.cjs ghép các file trong
 * thư mục này theo thứ tự shared, text, card, layout, chart, audit vào một hàm rồi chạy một lần mỗi trang.
 * Mỗi luật nhận ctx = { root, all, isPart, rootRect, rootBg, errors, warnings, massOf, highlights }. */
function auditScreens() {
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
    const ctx = { root, all, isPart, rootRect, rootBg, errors, warnings, massOf: makeMassOf(root, rootBg), highlights: [] };

    textRules.dots(ctx);
    for (const el of all) {
      const st = getComputedStyle(el);
      textRules.element(ctx, el, st);
      layoutRules.element(ctx, el, st);
    }
    layoutRules.rootOverflow(ctx);
    layoutRules.iconRefs(ctx);
    ctx.highlights = cardRules.highlightAndRadius(ctx);
    layoutRules.space(ctx);
    layoutRules.flatScale(ctx);
    layoutRules.thinHighlight(ctx);
    layoutRules.colors(ctx);
    textRules.markers(ctx);
    for (const el of all) {
      if (annotated(el)) continue;
      const st = getComputedStyle(el);
      textRules.markup(ctx, el, st);
      cardRules.decor(ctx, el, st);
    }
    layoutRules.fixedOverlap(ctx);
    chartRules.charts(ctx);
    layoutRules.panels(ctx);
    cardRules.paddingAndWidth(ctx);
    cardRules.aiLook(ctx);
    cardRules.tileRainbow(ctx);
    cardRules.eyebrow(ctx);
    textRules.emoji(ctx);

    const dedupe = (items) => {
      const seen = new Set();
      return items.filter((item) => (seen.has(item.message) ? false : seen.add(item.message)));
    };
    return { name, errors: dedupe(errors), warnings: dedupe(warnings) };
  });
}
