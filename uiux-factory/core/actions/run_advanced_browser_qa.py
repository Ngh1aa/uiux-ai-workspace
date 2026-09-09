from __future__ import annotations

import json
from pathlib import Path

from core.actions.run_browser_qa import RunBrowserQA, StaticServer
from core.contracts.browser_qa_schema import BrowserQAResult
from core.skills.policy_resolver import SkillPolicyResolver


SANITY_AUDIT = r"""() => {
  const visible = (el) => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0.02 && r.width > 0 && r.height > 0;
  };
  const text = (el) => (el.textContent || '').replace(/\s+/g, ' ').trim();
  const labelled = (el) => {
    const aria = (el.getAttribute('aria-label') || '').trim();
    if (aria) return true;
    const ids = (el.getAttribute('aria-labelledby') || '').trim().split(/\s+/).filter(Boolean);
    if (ids.some(id => text(document.getElementById(id) || document.createElement('span')))) return true;
    if (el.id) {
      const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (label && text(label)) return true;
    }
    const parentLabel = el.closest('label');
    if (parentLabel && text(parentLabel)) return true;
    if ((el.getAttribute('title') || '').trim()) return true;
    if (el.tagName === 'IMG' && el.hasAttribute('alt')) return true;
    if (el.tagName === 'INPUT') {
      const type = (el.getAttribute('type') || 'text').toLowerCase();
      if (['submit', 'reset', 'button'].includes(type) && (el.value || '').trim()) return true;
      if (type === 'image' && (el.getAttribute('alt') || '').trim()) return true;
    }
    return !!text(el);
  };
  const parseRGB = (value) => {
    const m = String(value).match(/rgba?\((\d+(?:\.\d+)?)[, ]+(\d+(?:\.\d+)?)[, ]+(\d+(?:\.\d+)?)(?:[, /]+([\d.]+))?\)/i);
    return m ? [Number(m[1]), Number(m[2]), Number(m[3]), m[4] === undefined ? 1 : Number(m[4])] : null;
  };
  const lum = (rgb) => {
    const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2]);
  };
  const ratio = (a, b) => {
    const l1 = lum(a), l2 = lum(b), hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
  };
  const background = (el) => {
    let node = el;
    while (node && node.nodeType === 1) {
      const s = getComputedStyle(node);
      if (s.backgroundImage && s.backgroundImage !== 'none') return { image: true, rgb: null };
      const rgb = parseRGB(s.backgroundColor);
      if (rgb && rgb[3] > 0.9) return { image: false, rgb };
      node = node.parentElement;
    }
    return { image: false, rgb: [255, 255, 255, 1] };
  };

  const images = Array.from(document.querySelectorAll('img'));
  const missingAlt = images.filter(img => !img.hasAttribute('alt')).length;

  const controls = Array.from(document.querySelectorAll(
    'button,input:not([type="hidden"]),select,textarea,[role="button"],a[href]'
  )).filter(visible);
  const unlabeled = controls.filter(el => !labelled(el)).length;

  const smallTargets = controls.filter(el => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    if (el.tagName === 'A' && s.display === 'inline') return false;
    return r.width < 24 || r.height < 24;
  }).length;

  let focusObscured = 0;
  for (const el of controls.slice(0, 24)) {
    try {
      el.scrollIntoView({ block: 'center', inline: 'nearest' });
      el.focus({ preventScroll: true });
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0 || r.top < 0 || r.left < 0 || r.bottom > innerHeight || r.right > innerWidth) {
        focusObscured += 1;
        continue;
      }
      const x = Math.max(0, Math.min(innerWidth - 1, r.left + r.width / 2));
      const y = Math.max(0, Math.min(innerHeight - 1, r.top + r.height / 2));
      const top = document.elementFromPoint(x, y);
      if (top && !(top === el || el.contains(top) || top.contains(el))) focusObscured += 1;
    } catch (_) {}
  }

  const textNodes = Array.from(document.querySelectorAll('h1,h2,h3,p,li,label,button,a,span'))
    .filter(el => visible(el) && text(el).length >= 2)
    .slice(0, 180);
  let catastrophicContrast = 0;
  for (const el of textNodes) {
    const fg = parseRGB(getComputedStyle(el).color), bg = background(el);
    if (!fg || !bg.rgb || bg.image) continue;
    if (ratio(fg, bg.rgb) < 1.25) catastrophicContrast += 1;
  }

  return {
    missingAlt,
    unlabeled,
    smallTargets,
    focusObscured,
    catastrophicContrast,
  };
}"""


class RunAdvancedBrowserQA(RunBrowserQA):
    """BrowserQA plus skills_UIUX elementary visual/accessibility smoke gates."""

    EXTRA_QA_SKILLS = (
        "ui-craft-and-visual-qa/SKILL.md",
        "inclusive-design-and-cognitive-accessibility/SKILL.md",
        "interaction-patterns-and-form-ux/SKILL.md",
    )

    async def _collect_sanity(self, project_dir: Path, routes, viewports) -> dict[tuple[str, str], dict]:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("Python Playwright is required for advanced BrowserQA.") from exc

        results: dict[tuple[str, str], dict] = {}
        with StaticServer(project_dir) as server:
            base_url = f"http://127.0.0.1:{server.port}"
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                try:
                    for route in routes:
                        for viewport in viewports:
                            context = await browser.new_context(
                                viewport={"width": viewport.width, "height": viewport.height},
                                reduced_motion="reduce",
                                service_workers="block",
                            )
                            if (project_dir / ".uiux-ai.json").exists():
                                async def local_only(request_route):
                                    if request_route.request.url.startswith(base_url + "/"):
                                        await request_route.continue_()
                                    else:
                                        await request_route.abort()
                                await context.route("**/*", local_only)
                            page = await context.new_page()
                            try:
                                await page.goto(
                                    base_url.rstrip("/") + route,
                                    wait_until="networkidle",
                                    timeout=30000,
                                )
                                results[(route, viewport.name)] = await page.evaluate(SANITY_AUDIT)
                            finally:
                                await context.close()
                finally:
                    await browser.close()
        return results

    async def run(self, instruction: str) -> str:
        base = BrowserQAResult.model_validate_json(await super().run(instruction))
        project_dir = Path(base.project_dir).resolve()
        sanity = await self._collect_sanity(project_dir, base.routes, base.viewports)

        for item in base.evidence:
            row = sanity.get((item.route, item.viewport.name), {})
            item.missing_alt_count = int(row.get("missingAlt", 0))
            item.unlabeled_control_count = int(row.get("unlabeled", 0))
            item.small_control_target_count = int(row.get("smallTargets", 0))
            item.focus_obscured_count = int(row.get("focusObscured", 0))
            item.catastrophic_contrast_count = int(row.get("catastrophicContrast", 0))

            hard_failure = any(
                (
                    item.missing_alt_count,
                    item.unlabeled_control_count,
                    item.small_control_target_count,
                    item.focus_obscured_count,
                    item.catastrophic_contrast_count,
                )
            )
            if hard_failure:
                item.status = "failed"

        missing_alt = sum(item.missing_alt_count for item in base.evidence)
        unlabeled = sum(item.unlabeled_control_count for item in base.evidence)
        small_targets = sum(item.small_control_target_count for item in base.evidence)
        focus_obscured = sum(item.focus_obscured_count for item in base.evidence)
        catastrophic = sum(item.catastrophic_contrast_count for item in base.evidence)

        base.gates.image_alt_smoke_passed = missing_alt == 0
        base.gates.accessible_name_smoke_passed = unlabeled == 0
        base.gates.control_target_smoke_passed = small_targets == 0
        base.gates.focus_visibility_smoke_passed = focus_obscured == 0
        base.gates.elementary_visual_sanity_passed = catastrophic == 0

        base.gates.ready_for_visual_critic = bool(
            base.gates.ready_for_visual_critic
            and base.gates.image_alt_smoke_passed
            and base.gates.accessible_name_smoke_passed
            and base.gates.control_target_smoke_passed
            and base.gates.focus_visibility_smoke_passed
            and base.gates.elementary_visual_sanity_passed
        )
        base.status = (
            "passed"
            if base.gates.ready_for_visual_critic and base.gates.no_console_errors
            else "partial"
        )

        base.summary.update(
            {
                "missing_alt_count": missing_alt,
                "unlabeled_control_count": unlabeled,
                "small_control_target_count": small_targets,
                "focus_obscured_count": focus_obscured,
                "catastrophic_contrast_count": catastrophic,
            }
        )

        resolver = SkillPolicyResolver()
        for relative_path in self.EXTRA_QA_SKILLS:
            skill = resolver.load(relative_path)
            if skill.name not in base.skills_used:
                base.skills_used.append(skill.name)

        base.limitations = [
            limitation
            for limitation in base.limitations
            if "not WCAG conformance certification" not in limitation
        ] + [
            "Automated accessibility checks are smoke evidence only; this is not WCAG conformance certification.",
            "Target-size smoke uses a conservative 24 CSS px obvious-control rule and does not model every WCAG spacing exception.",
            "Catastrophic contrast only checks solid computed backgrounds and deliberately skips image-background text for VisualCritic/human review.",
        ]
        base.generated_by = "AdvancedBrowserQAAgent"
        return base.model_dump_json(indent=2)
