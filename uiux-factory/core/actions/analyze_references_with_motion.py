from __future__ import annotations

import asyncio
import json
from pathlib import Path

import aiohttp
from metagpt.actions import Action
from playwright.async_api import async_playwright

from core.actions.analyze_references import (
    AnalyzeReferences,
    PublicResolver,
    fetch_public_response,
    validate_network_url,
)
from core.contracts.design_context_schema import DesignContext
from core.contracts.reference_evidence_schema import (
    EvidenceViewport,
    EventListenerEvidence,
    InteractionStateEvidence,
    MotionCheckpointEvidence,
    ReferenceEvidenceBundle,
    ReferenceMotionEvidence,
)


MOTION_INIT_SCRIPT = r"""() => {
  window.__uiuxReferenceListeners = [];
  const originalAdd = EventTarget.prototype.addEventListener;
  const label = target => {
    if (target === window) return 'window';
    if (target === document) return 'document';
    if (!(target instanceof Element)) return target?.constructor?.name || 'EventTarget';
    if (target.id) return `#${CSS.escape(target.id)}`;
    let value = target.tagName.toLowerCase();
    const classes = Array.from(target.classList).filter(Boolean).slice(0, 2);
    if (classes.length) value += classes.map(name => `.${CSS.escape(name)}`).join('');
    return value;
  };
  EventTarget.prototype.addEventListener = function(type, listener, options) {
    try {
      if (window.__uiuxReferenceListeners.length < 300) {
        const objectOptions = options && typeof options === 'object' ? options : {};
        window.__uiuxReferenceListeners.push({
          event_type: String(type),
          target: label(this),
          capture: typeof options === 'boolean' ? options : Boolean(objectOptions.capture),
          once: Boolean(objectOptions.once),
          passive: Boolean(objectOptions.passive),
          evidence: 'VERIFIED'
        });
      }
    } catch (_) {}
    return originalAdd.call(this, type, listener, options);
  };
}"""


MOTION_CHECKPOINT_JS = r"""() => {
  const round = value => Math.round(value * 100) / 100;
  const visible = el => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden';
  };
  const selectorFor = el => {
    if (!(el instanceof Element)) return '';
    if (el.id) return `#${CSS.escape(el.id)}`;
    const parts = [];
    let current = el;
    for (let depth = 0; current && current !== document.documentElement && depth < 5; depth += 1) {
      let part = current.tagName.toLowerCase();
      const classes = Array.from(current.classList).filter(Boolean).slice(0, 2);
      if (classes.length) part += classes.map(name => `.${CSS.escape(name)}`).join('');
      const siblings = current.parentElement ? Array.from(current.parentElement.children).filter(node => node.tagName === current.tagName) : [];
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(current) + 1})`;
      parts.unshift(part);
      current = current.parentElement;
    }
    return parts.join(' > ') || el.tagName.toLowerCase();
  };
  const customNames = new Set();
  const scan = rules => {
    if (!rules) return;
    for (const rule of Array.from(rules)) {
      if (rule.style) for (const name of Array.from(rule.style)) if (name.startsWith('--')) customNames.add(name);
      try { if (rule.cssRules) scan(rule.cssRules); } catch (_) {}
    }
  };
  for (const sheet of Array.from(document.styleSheets)) {
    try { scan(sheet.cssRules); } catch (_) {}
  }
  const rootComputed = getComputedStyle(document.documentElement);
  const root_custom_properties = {};
  Array.from(customNames).slice(0, 120).sort().forEach(name => {
    const value = rootComputed.getPropertyValue(name).trim();
    if (value) root_custom_properties[name] = value;
  });

  const candidates = [];
  for (const el of Array.from(document.querySelectorAll('body *'))) {
    if (!visible(el)) continue;
    const style = getComputedStyle(el);
    const important = (
      style.transform !== 'none' || style.opacity !== '1' || style.filter !== 'none' ||
      style.position === 'fixed' || style.position === 'sticky' ||
      style.animationName !== 'none' ||
      (style.transitionDuration && !/^0s(?:, 0s)*$/.test(style.transitionDuration)) ||
      /^(H1|H2|H3|HEADER|NAV|MAIN|SECTION|ARTICLE)$/.test(el.tagName)
    );
    if (!important) continue;
    const rect = el.getBoundingClientRect();
    const custom_properties = {};
    for (const name of Object.keys(root_custom_properties)) {
      const value = style.getPropertyValue(name).trim();
      if (value && value !== root_custom_properties[name]) custom_properties[name] = value;
    }
    candidates.push({
      selector: selectorFor(el),
      opacity: style.opacity,
      transform: style.transform,
      position: style.position,
      filter: style.filter,
      rect: { x: round(rect.x), y: round(rect.y), width: round(rect.width), height: round(rect.height) },
      custom_properties,
      evidence: 'VERIFIED'
    });
    if (candidates.length >= 90) break;
  }

  const animations = [];
  for (const animation of document.getAnimations().slice(0, 60)) {
    const effect = animation.effect;
    const target = effect && effect.target instanceof Element ? effect.target : null;
    const timing = effect && effect.getTiming ? effect.getTiming() : {};
    animations.push({
      selector: target ? selectorFor(target) : '',
      play_state: animation.playState || '',
      current_time: typeof animation.currentTime === 'number' ? animation.currentTime : null,
      duration: String(timing.duration ?? ''),
      delay: String(timing.delay ?? ''),
      easing: String(timing.easing ?? ''),
      iterations: String(timing.iterations ?? ''),
      evidence: 'VERIFIED'
    });
  }
  return { elements: candidates, animations, root_custom_properties };
}"""


INTERACTION_TARGETS_JS = r"""() => {
  const visible = el => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden';
  };
  const selectorFor = el => {
    if (el.id) return `#${CSS.escape(el.id)}`;
    const parts = [];
    let current = el;
    for (let depth = 0; current && current !== document.documentElement && depth < 5; depth += 1) {
      let part = current.tagName.toLowerCase();
      const classes = Array.from(current.classList).filter(Boolean).slice(0, 2);
      if (classes.length) part += classes.map(name => `.${CSS.escape(name)}`).join('');
      const siblings = current.parentElement ? Array.from(current.parentElement.children).filter(node => node.tagName === current.tagName) : [];
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(current) + 1})`;
      parts.unshift(part);
      current = current.parentElement;
    }
    return parts.join(' > ');
  };
  return Array.from(document.querySelectorAll('a[href],button,input:not([type="hidden"]),select,textarea,[tabindex]:not([tabindex="-1"])'))
    .filter(visible).slice(0, 12).map(selectorFor).filter(Boolean);
}"""


INTERACTION_STYLE_JS = r"""el => {
  const style = getComputedStyle(el);
  const result = {};
  for (const key of ['color','background-color','border-color','box-shadow','opacity','transform','filter','outline-color','outline-style','outline-width','text-decoration-line']) {
    const value = style.getPropertyValue(key).trim();
    if (value) result[key] = value;
  }
  return result;
}"""


async def _sample_interactions(page) -> list[InteractionStateEvidence]:
    results: list[InteractionStateEvidence] = []
    selectors = await page.evaluate(INTERACTION_TARGETS_JS)
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            before = await locator.evaluate(INTERACTION_STYLE_JS)
            await locator.hover(timeout=1200)
            await page.wait_for_timeout(60)
            hover = await locator.evaluate(INTERACTION_STYLE_JS)
            hover_changed = sorted(key for key in set(before) | set(hover) if before.get(key) != hover.get(key))
            results.append(
                InteractionStateEvidence(
                    selector=selector,
                    state="hover",
                    before=before,
                    after=hover,
                    changed_properties=hover_changed,
                )
            )
        except Exception:
            pass
        try:
            await locator.focus(timeout=1200)
            await page.wait_for_timeout(40)
            focus = await locator.evaluate(INTERACTION_STYLE_JS)
            baseline = before if 'before' in locals() else {}
            focus_changed = sorted(key for key in set(baseline) | set(focus) if baseline.get(key) != focus.get(key))
            results.append(
                InteractionStateEvidence(
                    selector=selector,
                    state="focus",
                    before=baseline,
                    after=focus,
                    changed_properties=focus_changed,
                )
            )
        except Exception:
            pass
    return results


async def sample_reference_motion(url: str, role: str = "reference") -> ReferenceMotionEvidence:
    validate_network_url(url)
    viewport = EvidenceViewport(label="desktop-motion", width=1440, height=1000)
    evidence = ReferenceMotionEvidence(viewport=viewport, max_scroll_y=0)
    try:
        async with asyncio.timeout(45), async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                context = await browser.new_context(
                    viewport={"width": viewport.width, "height": viewport.height},
                    service_workers="block",
                    accept_downloads=False,
                )
                await context.add_init_script(MOTION_INIT_SCRIPT)
                if hasattr(context, "route_web_socket"):
                    await context.route_web_socket("**/*", lambda ws: ws.close())
                connector = aiohttp.TCPConnector(resolver=PublicResolver(), limit=12, use_dns_cache=False)
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=aiohttp.ClientTimeout(total=12),
                    trust_env=False,
                    cookie_jar=aiohttp.DummyCookieJar(),
                ) as session:
                    request_count = 0
                    budget = {"bytes": 0}

                    async def route_request(route):
                        nonlocal request_count
                        request_count += 1
                        if request_count > 100 or budget["bytes"] > 20_000_000 or route.request.method != "GET":
                            await route.abort()
                            return
                        try:
                            status, headers, body = await fetch_public_response(session, route.request.url, budget)
                            await route.fulfill(status=status, headers=headers, body=body)
                        except (ValueError, OSError, aiohttp.ClientError, asyncio.TimeoutError):
                            await route.abort()

                    await context.route("**/*", route_request)
                    page = await context.new_page()
                    page.set_default_timeout(6000)
                    response = await page.goto(url, wait_until="load", timeout=25_000)
                    if not response or not response.ok:
                        raise ValueError(f"Reference returned HTTP {response.status if response else 'unknown'}.")
                    max_scroll = int(await page.evaluate("Math.max(0, document.documentElement.scrollHeight - innerHeight)"))
                    evidence.max_scroll_y = max_scroll
                    progress_values = [0.0] if max_scroll == 0 else [0.0, 0.125, 0.25, 0.5, 0.75, 0.875, 1.0]
                    seen_y: set[int] = set()
                    for progress in progress_values:
                        scroll_y = int(round(max_scroll * progress))
                        if scroll_y in seen_y:
                            continue
                        seen_y.add(scroll_y)
                        await page.evaluate("y => window.scrollTo(0, y)", scroll_y)
                        await page.wait_for_timeout(120)
                        measured = await page.evaluate(MOTION_CHECKPOINT_JS)
                        evidence.checkpoints.append(
                            MotionCheckpointEvidence(
                                label=f"scroll-{int(round(progress * 100))}",
                                scroll_y=scroll_y,
                                scroll_progress=progress if max_scroll else 0.0,
                                elements=measured["elements"],
                                animations=measured["animations"],
                                root_custom_properties=measured["root_custom_properties"],
                            )
                        )

                    raw_listeners = await page.evaluate("window.__uiuxReferenceListeners || []")
                    unique: dict[tuple, EventListenerEvidence] = {}
                    for row in raw_listeners:
                        item = EventListenerEvidence.model_validate(row)
                        key = (item.event_type, item.target, item.capture, item.once, item.passive)
                        unique[key] = item
                    evidence.listeners = list(unique.values())[:200]

                    await page.evaluate("window.scrollTo(0, 0)")
                    await page.wait_for_timeout(80)
                    evidence.interactions = await _sample_interactions(page)
                    evidence.warnings.append(
                        "Interaction sampling is non-destructive: hover/focus only; click, submit, drag and destructive controls are not triggered."
                    )
                    await context.unroute_all(behavior="wait")
            finally:
                await browser.close()
    except Exception as error:
        evidence.warnings.append(f"{type(error).__name__}: {str(error)[:400]}")
    return evidence


class AnalyzeReferencesWithMotion(Action):
    """Run the existing deep extractor, then enrich its artifact with runtime motion evidence."""

    name: str = "AnalyzeReferencesWithMotion"

    async def run(self, instruction: str) -> str:
        board_json = await AnalyzeReferences().run(instruction)
        payload = json.loads(instruction)
        design_context = DesignContext.model_validate(payload.get("design_context", {}))
        run_dir = Path(payload["run_dir"])
        evidence_path = run_dir / "reference-evidence.v1.json"
        bundle = ReferenceEvidenceBundle.model_validate_json(evidence_path.read_text(encoding="utf-8"))

        targets = [
            (url, "reference")
            for url in design_context.reference_urls
            if url != design_context.existing_website
        ]
        if design_context.existing_website:
            targets.insert(0, (design_context.existing_website, "existing_website"))

        by_key = {(page.url, page.role): page for page in bundle.references}
        for url, role in targets:
            page = by_key.get((url, role))
            if page is None:
                continue
            page.motion.append(await sample_reference_motion(url, role))
        evidence_path.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
        return board_json
