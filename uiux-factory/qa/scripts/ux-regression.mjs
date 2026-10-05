// Rendered safety net. Project style is declared by the target, never inferred from Nova.
const kinds = new Set(['style-range', 'hit-target', 'right-aligned', 'unobscured', 'absent-or-hidden', 'toggle-persistence']);
const properties = new Set(['border-top-left-radius', 'border-top-right-radius', 'border-bottom-left-radius', 'border-bottom-right-radius', 'font-size', 'min-height', 'opacity']);
const keys = new Set(['id', 'kind', 'selector', 'within', 'property', 'min', 'max', 'tolerance', 'route']);

export function qaViewports(payload = '') {
  if (!payload) return [{ name: 'desktop', width: 1440, height: 1000 }, { name: 'mobile', width: 390, height: 844 }];
  const parsed = JSON.parse(payload);
  if (!Array.isArray(parsed) || parsed.length < 1 || parsed.length > 6) throw new Error('QA_VIEWPORTS_JSON must be an array with 1..6 entries');
  const result = parsed.map(raw => {
    if (!raw || typeof raw !== 'object') throw new Error('viewport entry must be an object');
    const name = String(raw.name || '').trim().toLowerCase(), width = Number(raw.width), height = Number(raw.height);
    if (!/^[a-z0-9][a-z0-9_-]{0,31}$/.test(name) || !Number.isInteger(width) || !Number.isInteger(height) || width < 240 || width > 4096 || height < 240 || height > 4096) throw new Error('Invalid viewport name/dimensions');
    return { name, width, height };
  });
  if (new Set(result.map(item => item.name)).size !== result.length) throw new Error('viewport names must be unique');
  return result;
}

export function validateUXContract(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || value.schema_version !== 1) throw new Error('UX contract schema_version must be 1');
  if (Object.keys(value).some(key => !['schema_version', 'checks'].includes(key))) throw new Error('Unknown UX contract field');
  if (!Array.isArray(value.checks) || value.checks.length > 64) throw new Error('UX contract checks must be an array of at most 64 checks');
  const ids = new Set();
  for (const check of value.checks) {
    if (!check || typeof check !== 'object' || Array.isArray(check) || Object.keys(check).some(key => !keys.has(key))) throw new Error('Invalid UX check fields');
    if (typeof check.id !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$/.test(check.id) || ids.has(check.id) || ['UX-FOREGROUND', 'UX-OVERFLOW', 'UX-MEDIA'].includes(check.id)) throw new Error('UX check ids must be unique bounded identifiers and cannot shadow default requirements');
    ids.add(check.id);
    if (!kinds.has(check.kind)) throw new Error(`Unknown UX check kind: ${check.kind}`);
    const kindKeys = { 'style-range': ['property', 'min', 'max'], 'hit-target': ['min'], 'right-aligned': ['within', 'tolerance'], 'unobscured': [], 'absent-or-hidden': [], 'toggle-persistence': [] };
    if (Object.keys(check).some(key => !['id', 'kind', 'selector', 'route', ...kindKeys[check.kind]].includes(key))) throw new Error('Field does not apply to UX check kind');
    for (const key of ['selector', ...(check.kind === 'right-aligned' ? ['within'] : [])]) {
      if (typeof check[key] !== 'string' || !check[key].trim() || check[key].length > 500) throw new Error(`UX ${key} must be a bounded CSS selector`);
    }
    if (check.route !== undefined && (typeof check.route !== 'string' || !check.route.startsWith('/') || check.route.startsWith('//') || check.route.length > 500)) throw new Error('UX route must be a local path');
    for (const key of ['min', 'max', 'tolerance']) {
      if (check[key] !== undefined && (!Number.isFinite(check[key]) || check[key] < 0 || check[key] > 4096)) throw new Error(`Invalid UX ${key}`);
    }
    if (check.min !== undefined && check.max !== undefined && check.min > check.max) throw new Error('UX range min exceeds max');
    if (check.kind === 'style-range' && (!properties.has(check.property) || (check.min === undefined && check.max === undefined))) throw new Error('UX style-range needs an allowed property and range');
  }
  return value;
}

export async function inspectRenderedUX(page) {
  return page.evaluate(() => {
    const failures = [], unknown = [];
    const visible = element => {
      const box = element.getBoundingClientRect();
      if (!box.width || !box.height) return false;
      // Off-canvas skip links and clipped screen-reader text are not visible until
      // activated. Below-fold page content remains in the document-wide scan.
      let fixed = false;
      for (let node = element; node; node = node.parentElement) {
        const style = getComputedStyle(node);
        fixed ||= style.position === 'fixed';
        if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
        if (style.clip === 'rect(0px, 0px, 0px, 0px)' || style.clipPath === 'inset(50%)') return false;
      }
      if (box.bottom + (fixed ? 0 : scrollY) <= 0 || box.right + (fixed ? 0 : scrollX) <= 0) return false;
      return true;
    };
    const rgb = value => {
      const match = value.match(/^rgba?\(([^)]+)\)$/);
      if (!match) return null;
      const numbers = match[1].split(',').map(Number);
      return numbers.length >= 3 ? [...numbers.slice(0, 3), numbers[3] ?? 1] : null;
    };
    const over = (front, back) => {
      const alpha = front[3] + back[3] * (1 - front[3]);
      return alpha ? [...front.slice(0, 3).map((channel, i) => (channel * front[3] + back[i] * back[3] * (1 - front[3])) / alpha), alpha] : [0, 0, 0, 0];
    };
    const luminance = color => color.slice(0, 3).map(channel => {
      const value = channel / 255;
      return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
    }).reduce((sum, value, index) => sum + value * [.2126, .7152, .0722][index], 0);
    const identify = element => element.id ? `#${element.id}` : `${element.tagName.toLowerCase()}${[...element.classList].slice(0, 3).map(name => '.' + name).join('')}`;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const seen = new Set();
    let textNode, inspected = 0, candidates = 0;
    while ((textNode = walker.nextNode())) {
      const element = textNode.parentElement;
      if (!textNode.textContent.trim() || !element || seen.has(element) || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(element.tagName) || !visible(element)) continue;
      seen.add(element); candidates++;
      if (candidates > 5000) { unknown.push({ reason: 'text-scan-budget-exceeded' }); break; }
      const target = identify(element), style = getComputedStyle(element);
      let foreground = rgb(style.webkitTextFillColor || style.color), surface = [0, 0, 0, 0], reason;
      if (element.closest('svg, canvas')) reason = 'vector-or-canvas';
      for (let node = element; node; node = node.parentElement) {
        const computed = getComputedStyle(node);
        if (Number(computed.opacity) < 1 || computed.mixBlendMode !== 'normal' || computed.filter !== 'none') reason = 'compositing-needs-visual-review';
        if (surface[3] >= .999) continue;
        if (computed.backgroundImage !== 'none' || computed.backgroundClip === 'text') reason = 'image-or-gradient-needs-visual-review';
        for (const pseudo of ['::before', '::after']) {
          const overlay = getComputedStyle(node, pseudo);
          const color = rgb(overlay.backgroundColor);
          if (!['none', 'normal'].includes(overlay.content) && (overlay.backgroundImage !== 'none' || (color && color[3] > 0))) reason = 'pseudo-surface-needs-visual-review';
        }
        const background = rgb(computed.backgroundColor);
        if (background) surface = over(surface, background);
        else reason = 'unsupported-color-space';
      }
      if (!foreground || surface[3] < .999) reason ||= 'unknown-rendered-surface';
      if (reason) { if (unknown.length < 80) unknown.push({ target, reason }); continue; }
      foreground = over(foreground, surface);
      const light = luminance(foreground), dark = luminance(surface);
      const ratio = (Math.max(light, dark) + .05) / (Math.min(light, dark) + .05);
      inspected++;
      if (ratio < 1.2) failures.push({ requirement: 'UX-FOREGROUND', target, ratio: Number(ratio.toFixed(3)) });
    }
    if (document.documentElement.scrollWidth > innerWidth + 1) failures.push({ requirement: 'UX-OVERFLOW', width: document.documentElement.scrollWidth, viewport: innerWidth });
    const images = [...document.images].filter(visible);
    for (const image of images) if (!image.complete || image.naturalWidth === 0) failures.push({ requirement: 'UX-MEDIA', target: identify(image) });
    return { failures, unknown, inspected_text: inspected, text_candidates: candidates, images: images.length };
  });
}

async function checkTarget(page, check) {
  const locator = page.locator(check.selector);
  const count = await locator.count();
  if (check.kind === 'absent-or-hidden') {
    for (let i = 0; i < count; i++) if (await locator.nth(i).isVisible()) return 'unexpected visible overlay';
    return null;
  }
  if (!count) return 'required selector is missing';
  if (count > 100) return 'selector exceeds 100-element inspection budget';
  for (let i = 0; i < count; i++) {
    const target = locator.nth(i);
    if (!(await target.isVisible())) return 'required target is hidden';
    await target.scrollIntoViewIfNeeded();
    if (check.kind === 'style-range') {
      const raw = await target.evaluate((element, property) => getComputedStyle(element).getPropertyValue(property), check.property);
      if (check.property !== 'opacity' && !/^[\d.]+px$/.test(raw)) return `uninspectable computed ${check.property}`;
      const value = Number.parseFloat(raw);
      if (!Number.isFinite(value) || value < (check.min ?? 0) || value > (check.max ?? Infinity)) return `computed ${check.property}=${raw} violates declared range`;
    } else if (check.kind === 'hit-target') {
      const box = await target.boundingBox();
      if (!box || box.width < (check.min ?? 44) || box.height < (check.min ?? 44)) return 'declared hit region is too small';
    } else if (check.kind === 'right-aligned') {
      const geometry = await target.evaluate((element, selector) => {
        const parent = element.closest(selector);
        if (!parent) return null;
        const childBox = element.getBoundingClientRect(), parentBox = parent.getBoundingClientRect(), style = getComputedStyle(parent);
        return { actual: childBox.right, expected: parentBox.right - parseFloat(style.paddingRight) - parseFloat(style.borderRightWidth) };
      }, check.within);
      if (!geometry || Math.abs(geometry.actual - geometry.expected) > (check.tolerance ?? 2)) return 'control is not aligned with declared owner right edge';
    } else if (check.kind === 'unobscured') {
      const exposed = await target.evaluate(element => {
        const box = element.getBoundingClientRect();
        const top = document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2);
        return !!top && (top === element || element.contains(top));
      });
      if (!exposed) return 'target center is covered by another element';
    } else if (check.kind === 'toggle-persistence') {
      const state = () => target.evaluate(element => element instanceof HTMLInputElement && element.type === 'checkbox' ? element.checked : element.getAttribute('aria-checked') === 'true' ? true : element.getAttribute('aria-checked') === 'false' ? false : null);
      const before = await state();
      if (before === null) return 'target is not a checkbox or an ARIA checked control';
      let failure;
      try {
        await target.focus();
        await page.keyboard.press('Space');
        if (await state() !== !before) failure = 'Space did not toggle control';
        await page.reload({ waitUntil: 'load' });
        if (await state() !== !before) failure ||= 'toggle state did not persist after reload';
      } finally {
        // Restore the original declared local/demo preference even after a failed assertion.
        if (await state() !== before) { await target.focus(); await page.keyboard.press('Space'); }
        await page.reload({ waitUntil: 'load' });
      }
      if (failure) return failure;
    }
  }
  return null;
}

export async function runUXRegression(page, { route, contract = null } = {}) {
  if (contract) validateUXContract(contract);
  const scan = await inspectRenderedUX(page);
  const checks = [];
  for (const check of contract?.checks ?? []) {
    if (check.route !== undefined && check.route !== route) continue;
    let failure;
    try { failure = await checkTarget(page, check); }
    catch (error) { failure = String(error.message).slice(0, 240); }
    checks.push({ id: check.id, kind: check.kind, selector: check.selector, failure, status: failure ? 'FAIL' : 'PASS' });
  }
  // Interaction/reload checks can change the rendered state: scan again after restoration.
  const finalScan = checks.length ? await inspectRenderedUX(page) : scan;
  const failures = [...scan.failures, ...finalScan.failures.filter(item => !scan.failures.some(before => JSON.stringify(before) === JSON.stringify(item)))];
  const requirements = {};
  for (const id of ['UX-FOREGROUND', 'UX-OVERFLOW', 'UX-MEDIA']) {
    requirements[id] = { outcome: failures.some(item => item.requirement === id) ? 'failed' : id === 'UX-FOREGROUND' && (scan.unknown.length || finalScan.unknown.length) ? 'cantTell' : 'passed', applicable: id === 'UX-MEDIA' ? finalScan.images > 0 : id === 'UX-FOREGROUND' ? finalScan.text_candidates > 0 : true, test_targets: [`${new URL(page.url()).pathname}@${page.viewportSize()?.width ?? 'default'}`] };
  }
  for (const check of checks) requirements[check.id] = { outcome: check.failure ? 'failed' : 'passed', applicable: true, test_targets: [check.id] };
  return {
    schema_version: 1, evaluator: 'uiux-rendered-regression', route,
    viewport: page.viewportSize(), reduced_motion: await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches),
    status: failures.length || checks.some(check => check.failure) ? 'FAIL' : 'PASS',
    scope: 'automated_checks_only', visual_review: 'UNKNOWN',
    inspected_text: finalScan.inspected_text, failures, checks, requirements,
    skipped_checks: (contract?.checks ?? []).filter(check => check.route !== undefined && check.route !== route).map(check => check.id),
    unknown: finalScan.unknown,
    limitations: ['Not WCAG certification or a substitute for inspecting screenshots.', 'Image/gradient/compositing text requires visual review.', 'Unlisted data and interaction states remain unverified.']
  };
}
