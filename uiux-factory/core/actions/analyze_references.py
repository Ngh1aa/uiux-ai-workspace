"""Measure public reference pages and persist source-grounded browser evidence.

The existing ReferenceBoard remains the compact design-analysis contract. In parallel this
module writes `reference-evidence.v1.json`, a deeper machine-readable capture used by the
spec-first pipeline. Browser HTTP traffic is fulfilled through a public-IP-only aiohttp
connector, including redirects and subresources.
"""

from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import aiohttp
from aiohttp.resolver import ThreadedResolver
from metagpt.actions import Action
from PIL import Image
from playwright.async_api import async_playwright

from core.contracts.design_context_schema import (
    DesignContext,
    DesignObservation,
    ReferenceBoard,
    ReferenceDNA,
    public_web_url,
)
from core.contracts.reference_evidence_schema import (
    EvidenceViewport,
    PaletteColorEvidence,
    ReferenceCaptureEvidence,
    ReferenceEvidenceBundle,
    ReferencePageEvidence,
    ScreenshotEvidence,
)


class PublicResolver(ThreadedResolver):
    async def resolve(self, host, port=0, family=socket.AF_INET):
        records = await super().resolve(host, port, family)
        if not records or any(not ipaddress.ip_address(row["host"]).is_global for row in records):
            raise OSError("Reference analysis only connects to public IP addresses.")
        return records


def validate_network_url(url: str) -> str:
    public_web_url(url)
    host = urlsplit(url).hostname
    if not host:
        raise ValueError("Reference URL has no hostname.")
    lowered = host.lower()
    if lowered == "localhost" or lowered.endswith((".localhost", ".local")):
        raise ValueError("Local/private reference addresses are not allowed.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return url
    if not address.is_global:
        raise ValueError("Local/private reference addresses are not allowed.")
    return url


async def fetch_public_response(session, url: str, budget: dict) -> tuple[int, dict, bytes]:
    """Follow redirects here; never delegate an unchecked Location to Chromium."""
    for _ in range(6):
        validate_network_url(url)
        async with session.get(url, allow_redirects=False) as response:
            if response.status in {301, 302, 303, 307, 308}:
                location = response.headers.get("Location")
                if not location:
                    raise ValueError("Reference redirect has no Location.")
                url = urljoin(url, location)
                continue
            body = bytearray()
            async for chunk in response.content.iter_chunked(65536):
                body.extend(chunk)
                budget["bytes"] += len(chunk)
                if len(body) > 4_000_000 or budget["bytes"] > 20_000_000:
                    raise ValueError("Reference response exceeded the capture budget.")
            headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() in {"content-type", "access-control-allow-origin"}
            }
            return response.status, headers, bytes(body)
    raise ValueError("Reference exceeded five redirects.")


# Compact observations retained for ReferenceBoard compatibility.
MEASURE_PAGE = r"""() => {
  const observations = [];
  const visible = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const add = (category, subject, value) => observations.push({ category, subject, value: String(value) });
  for (const selector of ['body', 'h1', 'h2', 'header', 'nav', 'main', 'main > section', 'button', 'a[class*="btn"], a[class*="button"]']) {
    Array.from(document.querySelectorAll(selector)).filter(visible).slice(0, 3).forEach((el, index) => {
      const style = getComputedStyle(el), box = el.getBoundingClientRect(), subject = `${selector}[${index}]`;
      for (const key of ['font-family', 'font-size', 'font-weight', 'line-height']) add('typography', `${subject}.${key}`, style.getPropertyValue(key));
      for (const key of ['color', 'background-color']) add('color', `${subject}.${key}`, style.getPropertyValue(key));
      for (const key of ['display', 'gap', 'padding-top', 'padding-bottom', 'border-radius']) add('layout', `${subject}.${key}`, style.getPropertyValue(key));
      add('layout', `${subject}.width`, `${Math.round(box.width)}px`);
      add('motion', `${subject}.transition-duration`, style.transitionDuration);
      add('motion', `${subject}.animation-name`, style.animationName);
    });
  }
  const h1 = document.querySelector('h1'), nav = document.querySelector('nav');
  add('ux', 'navigation.visible-links', nav ? Array.from(nav.querySelectorAll('a')).filter(visible).length : 0);
  add('ux', 'forms.count', document.forms.length);
  add('ux', 'images.count', document.images.length);
  add('layout', 'document.horizontal-overflow', document.documentElement.scrollWidth > innerWidth);
  const patterns = [];
  if (h1 && parseFloat(getComputedStyle(h1).fontSize) >= 56) patterns.push('Large display heading observed (at least 56px).');
  if (nav && getComputedStyle(nav).display !== 'none') patterns.push('Visible navigation landmark observed.');
  if (document.querySelector('main img, main video')) patterns.push('Media is present within the main content; editorial intent is not established.');
  return { title: document.title, observations, patterns };
}"""


# Deep evidence capture. Values here are browser measurements, not design interpretation.
MEASURE_EVIDENCE = r"""() => {
  const MAX_DOM = 900;
  const MAX_STYLES = 260;
  const STYLE_KEYS = [
    'display','position','top','right','bottom','left','width','height','min-width','min-height','max-width','max-height',
    'margin-top','margin-right','margin-bottom','margin-left','padding-top','padding-right','padding-bottom','padding-left',
    'gap','row-gap','column-gap','grid-template-columns','grid-template-rows','align-items','justify-content',
    'font-family','font-size','font-style','font-weight','line-height','letter-spacing','text-align','text-transform',
    'color','background-color','background-image','border-top-color','border-right-color','border-bottom-color','border-left-color',
    'border-radius','box-shadow','opacity','transform','transform-origin','filter','object-fit','object-position','overflow',
    'overflow-x','overflow-y','z-index','pointer-events','visibility','transition-duration','transition-timing-function',
    'animation-name','animation-duration','animation-timing-function','fill','stroke'
  ];
  const ATTR_ALLOW = new Set(['role','tabindex','href','src','alt','type','name','rel','target','title','aria-label','aria-labelledby','aria-describedby','aria-expanded','aria-current','aria-hidden','aria-controls']);
  const cleanText = value => String(value || '').replace(/\s+/g, ' ').trim().slice(0, 600);
  const round = value => Math.round(value * 100) / 100;
  const isVisible = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden';
  };
  const selectorFor = el => {
    if (!(el instanceof Element)) return '';
    if (el.id) return `#${CSS.escape(el.id)}`;
    const parts = [];
    let current = el;
    for (let depth = 0; current && current !== document.documentElement && depth < 6; depth += 1) {
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

  const cssWarnings = [];
  const customNames = new Set();
  const mediaQueries = new Map();
  const scanRules = rules => {
    if (!rules) return;
    for (const rule of Array.from(rules)) {
      if (rule.style) {
        for (const name of Array.from(rule.style)) if (name.startsWith('--')) customNames.add(name);
      }
      if (rule.conditionText && String(rule.constructor && rule.constructor.name).includes('Media')) {
        const condition = String(rule.conditionText);
        if (!mediaQueries.has(condition)) mediaQueries.set(condition, matchMedia(condition).matches);
      }
      try { if (rule.cssRules) scanRules(rule.cssRules); } catch (_) {}
    }
  };
  for (const sheet of Array.from(document.styleSheets)) {
    try { scanRules(sheet.cssRules); }
    catch (error) { cssWarnings.push(`CSSOM unavailable: ${sheet.href || 'inline'} (${error.name})`); }
  }
  for (const name of Array.from(document.documentElement.style)) if (name.startsWith('--')) customNames.add(name);

  const rootStyle = getComputedStyle(document.documentElement);
  const rootCustom = {};
  Array.from(customNames).slice(0, 160).sort().forEach(name => {
    const value = rootStyle.getPropertyValue(name).trim();
    if (value) rootCustom[name] = value;
  });

  const allElements = Array.from(document.documentElement.querySelectorAll('*'));
  const domElements = allElements.slice(0, MAX_DOM);
  const indexMap = new Map(domElements.map((el, index) => [el, index]));
  const dom = domElements.map((el, index) => {
    const rect = el.getBoundingClientRect();
    const attributes = {};
    for (const attr of Array.from(el.attributes).slice(0, 40)) {
      if (ATTR_ALLOW.has(attr.name) || attr.name.startsWith('aria-') || attr.name === 'data-testid') {
        attributes[attr.name] = String(attr.value).slice(0, 500);
      }
    }
    const shouldKeepText = /^(H[1-6]|A|BUTTON|LABEL|P|LI|DT|DD|FIGCAPTION|TD|TH)$/.test(el.tagName) || el.children.length === 0;
    return {
      index,
      parent_index: indexMap.has(el.parentElement) ? indexMap.get(el.parentElement) : null,
      tag: el.tagName.toLowerCase(),
      selector: selectorFor(el),
      id: el.id || '',
      classes: Array.from(el.classList).slice(0, 64),
      attributes,
      text: shouldKeepText ? cleanText(el.innerText || el.textContent) : '',
      visible: isVisible(el),
      rect: { x: round(rect.x), y: round(rect.y), width: round(rect.width), height: round(rect.height) },
      evidence: 'VERIFIED'
    };
  });

  const visible = domElements.filter(isVisible).slice(0, MAX_STYLES);
  const cssColorCounts = new Map();
  const countColor = value => {
    const normalized = String(value || '').trim().toLowerCase();
    if (!normalized || normalized === 'transparent' || normalized === 'none' || normalized === 'currentcolor' || normalized === 'rgba(0, 0, 0, 0)') return;
    cssColorCounts.set(normalized, (cssColorCounts.get(normalized) || 0) + 1);
  };
  const computed_styles = visible.map(el => {
    const style = getComputedStyle(el);
    const properties = {};
    STYLE_KEYS.forEach(name => {
      const value = style.getPropertyValue(name).trim();
      if (value) properties[name] = value;
    });
    ['color','background-color','border-top-color','border-right-color','border-bottom-color','border-left-color','fill','stroke'].forEach(name => countColor(properties[name]));
    const custom_properties = {};
    for (const name of Object.keys(rootCustom)) {
      const value = style.getPropertyValue(name).trim();
      if (value && value !== rootCustom[name]) custom_properties[name] = value;
    }
    return {
      node_index: indexMap.get(el),
      selector: selectorFor(el),
      properties,
      custom_properties,
      evidence: 'VERIFIED'
    };
  });

  const assets = [];
  const assetSeen = new Set();
  const pushAsset = asset => {
    const key = `${asset.kind}|${asset.url || ''}|${asset.selector || ''}|${asset.family || ''}`;
    if (!assetSeen.has(key)) { assetSeen.add(key); assets.push({ ...asset, evidence: 'VERIFIED' }); }
  };
  for (const img of Array.from(document.images)) {
    pushAsset({ kind: 'image', url: img.currentSrc || img.src || '', declared_url: img.getAttribute('src') || '', selector: selectorFor(img), family: '', natural_width: img.naturalWidth || 0, natural_height: img.naturalHeight || 0, status: img.complete ? 'complete' : 'loading' });
  }
  for (const video of Array.from(document.querySelectorAll('video'))) {
    pushAsset({ kind: 'video', url: video.currentSrc || video.src || '', declared_url: video.getAttribute('src') || '', selector: selectorFor(video), family: '', natural_width: video.videoWidth || 0, natural_height: video.videoHeight || 0, status: String(video.readyState) });
    if (video.poster) pushAsset({ kind: 'image', url: video.poster, declared_url: video.getAttribute('poster') || '', selector: `${selectorFor(video)}[poster]`, family: '', natural_width: null, natural_height: null, status: 'poster' });
  }
  for (const link of Array.from(document.querySelectorAll('link[href]'))) {
    const rel = String(link.rel || '').toLowerCase();
    if (rel.includes('stylesheet')) pushAsset({ kind: 'stylesheet', url: link.href, declared_url: link.getAttribute('href') || '', selector: selectorFor(link), family: '', natural_width: null, natural_height: null, status: 'linked' });
    if (rel.includes('icon')) pushAsset({ kind: 'icon', url: link.href, declared_url: link.getAttribute('href') || '', selector: selectorFor(link), family: '', natural_width: null, natural_height: null, status: rel });
  }
  for (const script of Array.from(document.scripts).filter(node => node.src)) {
    pushAsset({ kind: 'script', url: script.src, declared_url: script.getAttribute('src') || '', selector: selectorFor(script), family: '', natural_width: null, natural_height: null, status: script.type || 'classic' });
  }
  for (const row of computed_styles) {
    const value = row.properties['background-image'] || '';
    const matches = Array.from(value.matchAll(/url\(["']?([^"')]+)["']?\)/g));
    for (const match of matches) pushAsset({ kind: 'background-image', url: new URL(match[1], document.baseURI).href, declared_url: match[1], selector: row.selector, family: '', natural_width: null, natural_height: null, status: 'computed-style' });
  }
  if (document.fonts) {
    for (const font of Array.from(document.fonts)) {
      pushAsset({ kind: 'font', url: '', declared_url: '', selector: '', family: font.family || '', natural_width: null, natural_height: null, status: `${font.status || ''}|${font.style || ''}|${font.weight || ''}|${font.stretch || ''}` });
    }
  }

  const colorTotal = Array.from(cssColorCounts.values()).reduce((sum, value) => sum + value, 0) || 1;
  const css_colors = Array.from(cssColorCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 24)
    .map(([value, count]) => ({ value, weight: count / colorTotal, evidence: 'VERIFIED', source: 'computed-style frequency' }));

  const meta = name => document.querySelector(`meta[name="${name}"]`)?.content || '';
  const documentData = {
    title: document.title || '',
    lang: document.documentElement.lang || '',
    description: meta('description'),
    canonical: document.querySelector('link[rel="canonical"]')?.href || '',
    theme_color: meta('theme-color'),
    doctype: document.doctype ? `<!DOCTYPE ${document.doctype.name}>` : ''
  };

  return {
    document: documentData,
    page_url: location.href,
    scroll_width: document.documentElement.scrollWidth,
    scroll_height: document.documentElement.scrollHeight,
    horizontal_overflow: document.documentElement.scrollWidth > innerWidth + 1,
    dom_truncated: allElements.length > MAX_DOM,
    style_truncated: domElements.filter(isVisible).length > MAX_STYLES,
    dom,
    computed_styles,
    root_custom_properties: rootCustom,
    assets,
    media_queries: Array.from(mediaQueries.entries()).map(([condition, matches]) => ({ condition, matches, source: 'cssom', evidence: 'VERIFIED' })),
    css_colors,
    warnings: cssWarnings
  };
}"""


def screenshot_visual_palette(path: Path, colors: int = 8) -> list[PaletteColorEvidence]:
    """Return screenshot-derived color clusters.

    Pillow median-cut quantization is intentionally labelled INFERRED: screenshot pixels are
    perceptual evidence, not proof of authored CSS/brand tokens.
    """
    try:
        with Image.open(path) as image:
            sample = image.convert("RGB")
            sample.thumbnail((180, 180))
            quantized = sample.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
            palette = quantized.getpalette() or []
            counts = quantized.getcolors(maxcolors=colors) or []
            total = sum(count for count, _ in counts) or 1
            result: list[PaletteColorEvidence] = []
            for count, index in sorted(counts, reverse=True):
                offset = index * 3
                if offset + 2 >= len(palette):
                    continue
                red, green, blue = palette[offset : offset + 3]
                result.append(
                    PaletteColorEvidence(
                        value=f"#{red:02x}{green:02x}{blue:02x}",
                        weight=count / total,
                        evidence="INFERRED",
                        source="screenshot quantization",
                    )
                )
            return result
    except Exception:
        return []


def build_capture_from_measurement(
    measured: dict,
    *,
    label: str,
    width: int,
    height: int,
    screenshot_path: Path,
    screenshot_ref: str,
) -> ReferenceCaptureEvidence:
    digest = hashlib.sha256(screenshot_path.read_bytes()).hexdigest()
    screenshot = ScreenshotEvidence(
        path=screenshot_ref,
        sha256=digest,
        width=width,
        height=height,
        full_page=False,
    )
    return ReferenceCaptureEvidence.model_validate(
        {
            **measured,
            "viewport": EvidenceViewport(label=label, width=width, height=height).model_dump(),
            "visual_palette": [item.model_dump() for item in screenshot_visual_palette(screenshot_path)],
            "screenshot": screenshot.model_dump(),
        }
    )


async def analyze_reference(
    url: str,
    output_dir: Path,
    role: str = "reference",
    *,
    evidence_output: list[ReferencePageEvidence] | None = None,
) -> ReferenceDNA:
    captured_at = datetime.now(timezone.utc).isoformat()
    dna = ReferenceDNA(url=url, role=role, captured_at=captured_at)
    page_evidence = ReferencePageEvidence(url=url, role=role, captured_at=captured_at)
    try:
        validate_network_url(url)
        async with asyncio.timeout(45), async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                context = await browser.new_context(service_workers="block", accept_downloads=False)
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
                    blocked_requests = 0
                    budget = {"bytes": 0}

                    async def route_request(route):
                        nonlocal request_count, blocked_requests
                        request_count += 1
                        if request_count > 100 or budget["bytes"] > 20_000_000 or route.request.method != "GET":
                            blocked_requests += 1
                            await route.abort()
                            return
                        try:
                            status, headers, body = await fetch_public_response(session, route.request.url, budget)
                            await route.fulfill(status=status, headers=headers, body=body)
                        except (ValueError, OSError, aiohttp.ClientError, asyncio.TimeoutError):
                            blocked_requests += 1
                            await route.abort()

                    await context.route("**/*", route_request)
                    page = await context.new_page()
                    page.set_default_timeout(10_000)
                    for label, width, height in (("desktop", 1440, 1000), ("mobile", 390, 844)):
                        await page.set_viewport_size({"width": width, "height": height})
                        if label == "desktop":
                            response = await page.goto(url, wait_until="load", timeout=25_000)
                            if not response or not response.ok:
                                raise ValueError(f"Reference returned HTTP {response.status if response else 'unknown'}.")
                        compact = await page.evaluate(MEASURE_PAGE)
                        deep = await page.evaluate(MEASURE_EVIDENCE)
                        dna.title = compact["title"][:300]
                        source = f"{page.url} @ {width}x{height}, computed style / DOM"
                        dna.observations.extend(
                            DesignObservation(**item, source=source) for item in compact["observations"]
                        )
                        dna.patterns.extend(f"{label}: {pattern}" for pattern in compact["patterns"])
                        output_dir.mkdir(parents=True, exist_ok=True)
                        name = f"reference-{hashlib.sha256(url.encode()).hexdigest()[:12]}-{label}.png"
                        screenshot_path = output_dir / name
                        await page.screenshot(path=str(screenshot_path), full_page=False, timeout=8000)
                        screenshot_ref = f"references/{name}"
                        dna.screenshots.append(screenshot_ref)
                        capture = build_capture_from_measurement(
                            deep,
                            label=label,
                            width=width,
                            height=height,
                            screenshot_path=screenshot_path,
                            screenshot_ref=screenshot_ref,
                        )
                        page_evidence.document = deep["document"]
                        page_evidence.captures.append(capture)

                    dna.status = "observed"
                    page_evidence.status = "observed"
                    if blocked_requests:
                        dna.status = "partial"
                        page_evidence.status = "partial"
                        warning = (
                            f"{blocked_requests} requests failed or exceeded capture limits; "
                            "some page resources may be missing."
                        )
                        dna.warnings.append(warning)
                        page_evidence.warnings.append(warning)
                    dna.warnings.append(
                        "Motion reports CSS declarations only; runtime choreography and unvisited states are unknown."
                    )
                    page_evidence.warnings.append(
                        "NEXT 01 captures initial rendered state only; motion/interaction sampling is handled by a later contract."
                    )
                    await context.unroute_all(behavior="wait")
            finally:
                await browser.close()
    except Exception as error:
        dna.status = "partial" if dna.observations else "unavailable"
        page_evidence.status = "partial" if page_evidence.captures else "unavailable"
        warning = f"{type(error).__name__}: {str(error)[:400]}"
        dna.warnings.append(warning)
        page_evidence.warnings.append(warning)
    finally:
        if evidence_output is not None:
            evidence_output.append(page_evidence)
    return dna


class AnalyzeReferences(Action):
    name: str = "AnalyzeReferences"

    async def run(self, instruction: str) -> str:
        payload = json.loads(instruction)
        design_context = DesignContext.model_validate(payload.get("design_context", {}))
        run_dir = Path(payload["run_dir"])
        output_dir = run_dir / "references"
        targets = [
            (url, "reference")
            for url in design_context.reference_urls
            if url != design_context.existing_website
        ]
        if design_context.existing_website:
            targets.insert(0, (design_context.existing_website, "existing_website"))

        board = ReferenceBoard()
        evidence_pages: list[ReferencePageEvidence] = []
        for url, role in targets:
            board.references.append(
                await analyze_reference(url, output_dir, role, evidence_output=evidence_pages)
            )

        bundle = ReferenceEvidenceBundle(references=evidence_pages)
        (run_dir / "reference-evidence.v1.json").write_text(
            bundle.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return board.model_dump_json(indent=2)
