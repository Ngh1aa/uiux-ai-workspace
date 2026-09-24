"""Measure reference pages in an isolated browser using existing dependencies.

Browser HTTP traffic is fulfilled through a public-IP-only aiohttp connector.
This checks DNS at connection time, including redirects and subresources.
"""

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
from playwright.async_api import async_playwright

from core.contracts.design_context_schema import (
    DesignContext, DesignObservation, ReferenceBoard, ReferenceDNA, public_web_url,
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
    if host.lower() == "localhost" or host.lower().endswith((".localhost", ".local")):
        raise ValueError("Local/private reference addresses are not allowed.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return url
    if not address.is_global:
        raise ValueError("Local/private reference addresses are not allowed.")
    return url


async def fetch_public_response(session, url: str, budget: dict) -> tuple[int, dict, bytes]:
    """Follow redirects here, never delegate an unchecked Location to Chromium."""
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
            headers = {key: value for key, value in response.headers.items()
                       if key.lower() in {"content-type", "access-control-allow-origin"}}
            return response.status, headers, bytes(body)
    raise ValueError("Reference exceeded five redirects.")


# Computed evidence, not assumptions inferred from a site's name or search snippet.
MEASURE_PAGE = r"""() => {
  const observations = [];
  const visible = el => el.getBoundingClientRect().width > 0 && el.getBoundingClientRect().height > 0;
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


async def analyze_reference(url: str, output_dir: Path, role: str = "reference") -> ReferenceDNA:
    dna = ReferenceDNA(url=url, role=role, captured_at=datetime.now(timezone.utc).isoformat())
    try:
        validate_network_url(url)
        async with asyncio.timeout(45), async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                context = await browser.new_context(service_workers="block", accept_downloads=False)
                if hasattr(context, "route_web_socket"):
                    await context.route_web_socket("**/*", lambda ws: ws.close())
                connector = aiohttp.TCPConnector(resolver=PublicResolver(), limit=12, use_dns_cache=False)
                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=12),
                                                trust_env=False, cookie_jar=aiohttp.DummyCookieJar()) as session:
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
                        measured = await page.evaluate(MEASURE_PAGE)
                        dna.title = measured["title"][:300]
                        source = f"{page.url} @ {width}x{height}, computed style / DOM"
                        dna.observations.extend(DesignObservation(**item, source=source) for item in measured["observations"])
                        dna.patterns.extend(f"{label}: {pattern}" for pattern in measured["patterns"])
                        output_dir.mkdir(parents=True, exist_ok=True)
                        name = f"reference-{hashlib.sha256(url.encode()).hexdigest()[:12]}-{label}.png"
                        await page.screenshot(path=str(output_dir / name), full_page=False, timeout=8000)
                        dna.screenshots.append(f"references/{name}")
                    dna.status = "observed"
                    if blocked_requests:
                        dna.status = "partial"
                        dna.warnings.append(f"{blocked_requests} requests failed or exceeded capture limits; some page resources may be missing.")
                    dna.warnings.append("Motion reports CSS declarations only; timing quality and unvisited states are unknown.")
                    await context.unroute_all(behavior="wait")
            finally:
                await browser.close()
    except Exception as error:
        # A blocked/unavailable reference is evidence of a gap, not a fabricated result.
        dna.status = "partial" if dna.observations else "unavailable"
        dna.warnings.append(f"{type(error).__name__}: {str(error)[:400]}")
    return dna


class AnalyzeReferences(Action):
    name: str = "AnalyzeReferences"

    async def run(self, instruction: str) -> str:
        payload = json.loads(instruction)
        design_context = DesignContext.model_validate(payload.get("design_context", {}))
        output_dir = Path(payload["run_dir"]) / "references"
        targets = [(url, "reference") for url in design_context.reference_urls
                   if url != design_context.existing_website]
        if design_context.existing_website:
            targets.insert(0, (design_context.existing_website, "existing_website"))
        board = ReferenceBoard()
        for url, role in targets:
            board.references.append(await analyze_reference(url, output_dir, role))
        return board.model_dump_json(indent=2)
