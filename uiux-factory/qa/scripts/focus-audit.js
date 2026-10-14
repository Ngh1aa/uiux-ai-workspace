(async () => {
  // Run after a trusted keyboard event. This is rendered smoke, not WCAG certification.
  const visible = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).display !== 'none'
      && getComputedStyle(el).visibility !== 'hidden';
  };
  const controls = Array.from(document.querySelectorAll(
    'a[href],button,input:not([type="hidden"]),select,textarea,[tabindex],[contenteditable="true"]'
  )).filter(el => el.tabIndex >= 0 && !el.disabled && !el.closest('[inert]') && visible(el));
  const transparent = value => value === 'transparent' || /(?:,|\/)\s*0(?:\.0+)?\s*\)$/.test(value);
  const outlineSignature = s => [s.outlineStyle, s.outlineWidth, s.outlineColor, s.outlineOffset].join('|');
  const visibleShadow = value => value.replace(/\([^)]*\)/g, '').split(',').some(layer => {
    const lengths = (layer.match(/-?[\d.]+px/g) || []).map(parseFloat);
    return lengths.length === 4 && lengths.some(length => length !== 0);
  });
  const checked = [];
  const settleFocus = async el => {
    let previous = '', stableFrames = 0;
    for (let frame = 0; frame < 60; frame++) {
      await new Promise(resolve => requestAnimationFrame(resolve));
      const box = el.getBoundingClientRect(), style = getComputedStyle(el);
      const signature = [box.x, box.y, box.width, box.height, outlineSignature(style),
        style.boxShadow, style.opacity].join('|');
      const animating = el.getAnimations().some(animation => animation.playState === 'running');
      stableFrames = !animating && signature === previous ? stableFrames + 1 : 0;
      if (stableFrames >= 2) return true;
      previous = signature;
    }
    return false;
  };
  for (const [index, el] of controls.slice(0, 120).entries()) {
    el.blur();
    const before = getComputedStyle(el);
    const beforeOther = [before.borderColor, before.backgroundColor, before.color, before.textDecoration].join('|');
    const beforeShadow = before.boxShadow;
    const beforeOutline = outlineSignature(before);
    el.focus();
    const settled = await settleFocus(el);
    const style = getComputedStyle(el), box = el.getBoundingClientRect();
    const point = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
    // Pointer hit testing cannot prove visual occlusion for pointer-events:none.
    const hitTestUnavailable = style.pointerEvents === 'none';
    let hidden = !hitTestUnavailable && (!point || !(point === el || el.contains(point)));
    for (let ancestor = el; ancestor; ancestor = ancestor.parentElement) {
      const s = getComputedStyle(ancestor);
      hidden ||= Number(s.opacity) <= 0.01 || s.visibility === 'hidden' || s.display === 'none';
    }
    const focused = document.activeElement === el && el.matches(':focus-visible');
    const outline = !['none', 'hidden'].includes(style.outlineStyle)
      && parseFloat(style.outlineWidth) > 0 && !transparent(style.outlineColor)
      && outlineSignature(style) !== beforeOutline;
    const shadow = style.boxShadow !== 'none' && style.boxShadow !== beforeShadow
      && !transparent(style.boxShadow) && visibleShadow(style.boxShadow);
    const otherChanged = beforeOther !== [style.borderColor, style.backgroundColor, style.color, style.textDecoration].join('|');
    // Borders/backgrounds/caret/custom indicators need inspection, not automatic rejection or PASS.
    const status = !settled ? 'NEEDS_REVIEW' : !focused || hidden ? 'FAIL' : hitTestUnavailable ? 'NEEDS_REVIEW' : outline || shadow ? 'PASS'
      : otherChanged || el.matches('input,textarea,[contenteditable="true"]') ? 'NEEDS_REVIEW' : 'FAIL';
    checked.push({ index, tag: el.tagName.toLowerCase(), name: (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 160),
      focused, hidden, settled, hitTestUnavailable, bounds: {x: box.x, y: box.y, width: box.width, height: box.height},
      coveringElement: hidden && point ? {tag: point.tagName.toLowerCase(), class: point.getAttribute('class')} : null,
      outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth,
      outlineColor: style.outlineColor, boxShadow: style.boxShadow, status });
  }
  const unsupported = document.querySelector('iframe') !== null
    || Array.from(document.querySelectorAll('*')).some(el => el.shadowRoot);
  const status = checked.some(item => item.status === 'FAIL') ? 'FAIL'
    : unsupported || controls.length > 120 || checked.some(item => item.status !== 'PASS') ? 'NEEDS_REVIEW' : 'PASS';
  return { schema_version: '1.0', status, total: controls.length, checked,
    limitations: ['Computed/rendered smoke only; inspect screenshots, contrast, Tab order, traps and dynamic states separately.',
      ...(unsupported ? ['Shadow DOM or iframe needs dedicated keyboard review.'] : []),
      ...(controls.length > 120 ? ['Control count exceeds bounded inspection; remaining controls need review.'] : [])] };
})()
