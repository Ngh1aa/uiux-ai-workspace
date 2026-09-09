import json
import threading
from http.server import (
    SimpleHTTPRequestHandler,
    ThreadingHTTPServer,
)
from pathlib import Path
from typing import ClassVar
from urllib.parse import (
    unquote,
    urljoin,
    urlparse,
)

from metagpt.actions import Action

from core.contracts.browser_qa_schema import (
    BrowserQAGate,
    BrowserQAResult,
    RouteViewportEvidence,
    ViewportSpec,
)
from core.skills.policy_resolver import SkillPolicyResolver


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


class StaticServer:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.httpd = None
        self.thread = None
        self.port = None

    def __enter__(self):
        handler = lambda *args, **kwargs: QuietHandler(
            *args,
            directory=str(self.root),
            **kwargs,
        )

        self.httpd = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            handler,
        )

        self.port = self.httpd.server_port

        self.thread = threading.Thread(
            target=self.httpd.serve_forever,
            daemon=True,
        )

        self.thread.start()

        return self

    def __exit__(self, exc_type, exc, tb):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()

        if self.thread:
            self.thread.join(timeout=2)


class RunBrowserQA(Action):
    name: str = "RunBrowserQA"

    desc: str = (
        "Serve the generated static site, inspect routes across "
        "desktop/tablet/mobile in Chromium, capture screenshots and "
        "record browser/runtime evidence."
    )

    VIEWPORTS: ClassVar[tuple[tuple[str, int, int], ...]] = (
        ("desktop-1440", 1440, 1000),
        ("tablet-768", 768, 1024),
        ("mobile-390", 390, 844),
    )

    QA_SKILLS: ClassVar[tuple[str, ...]] = (
        "testing-strategy/SKILL.md",
        "ui-craft-and-visual-qa/SKILL.md",
        "accessibility/SKILL.md",
        "visual-regression-and-design-drift/SKILL.md",
    )

    @staticmethod
    def discover_routes(
        project_dir: Path,
    ) -> list[str]:
        routes = []

        for index_file in sorted(
            project_dir.rglob("index.html")
        ):
            relative_parts = tuple(
                part.lower()
                for part in index_file.relative_to(
                    project_dir
                ).parts
            )

            # Do not treat deployment/error documents as product routes.
            # They are useful GitHub Pages fallbacks, but they are not
            # part of the application's route coverage gate.
            if (
                "next-app" in relative_parts
                or "404" in relative_parts
            ):
                continue

            relative_parent = (
                index_file.parent.relative_to(project_dir)
            )

            if str(relative_parent) == ".":
                route = "/"
            else:
                route = (
                    "/"
                    + relative_parent.as_posix().strip("/")
                    + "/"
                )

            routes.append(route)

        return sorted(
            set(routes),
            key=lambda value: (
                value != "/",
                value.count("/"),
                value,
            ),
        )

    @staticmethod
    def url_to_local_target(
        href: str,
        current_url: str,
        project_dir: Path,
        base_url: str,
    ) -> Path | None:
        if not href:
            return None

        if href.startswith(
            (
                "mailto:",
                "tel:",
                "javascript:",
                "#",
            )
        ):
            return None

        absolute = urljoin(
            current_url,
            href,
        )

        parsed = urlparse(absolute)
        base = urlparse(base_url)

        if (
            parsed.scheme not in ("http", "https")
            or parsed.netloc != base.netloc
        ):
            return None

        path = unquote(parsed.path)
        relative = path.lstrip("/")

        candidate = project_dir / relative

        if path.endswith("/"):
            candidate = candidate / "index.html"
        elif not candidate.suffix:
            candidate = candidate / "index.html"

        return candidate.resolve()

    @classmethod
    async def inspect_page(
        cls,
        browser,
        route: str,
        viewport: ViewportSpec,
        project_dir: Path,
        evidence_dir: Path,
        base_url: str,
    ) -> RouteViewportEvidence:
        context = await browser.new_context(
            viewport={
                "width": viewport.width,
                "height": viewport.height,
            },
            reduced_motion="reduce",
        )

        page = await context.new_page()

        console_errors = []
        page_errors = []

        page.on(
            "console",
            lambda message: (
                console_errors.append(message.text)
                if message.type == "error"
                else None
            ),
        )

        page.on(
            "pageerror",
            lambda error: page_errors.append(str(error)),
        )

        url = base_url.rstrip("/") + route

        response = await page.goto(
            url,
            wait_until="networkidle",
            timeout=30000,
        )

        if (
            response is None
            or response.status >= 400
        ):
            page_errors.append(
                "Navigation failed or returned HTTP "
                f"{response.status if response else 'NO_RESPONSE'}"
            )

        metrics = await page.evaluate(
            """() => {
                const root = document.documentElement;
                const body = document.body;

                const scrollWidth = Math.max(
                    root.scrollWidth,
                    body ? body.scrollWidth : 0
                );

                const clientWidth = root.clientWidth;

                const hrefs = Array.from(
                    document.querySelectorAll('a[href]')
                ).map(
                    (node) => node.getAttribute('href')
                );

                return {
                    scrollWidth,
                    clientWidth,
                    h1Count:
                        document.querySelectorAll('h1').length,
                    mainCount:
                        document.querySelectorAll('main').length,
                    navCount:
                        document.querySelectorAll('nav').length,
                    hrefs,
                };
            }"""
        )

        overflow_amount = max(
            0,
            int(
                metrics["scrollWidth"]
                - metrics["clientWidth"]
            ),
        )

        broken_links = []

        for href in metrics["hrefs"]:
            target = cls.url_to_local_target(
                href,
                url,
                project_dir,
                base_url,
            )

            if (
                target is not None
                and target.is_relative_to(project_dir.resolve())
                and not target.exists()
            ):
                broken_links.append(href)

        safe_route = (
            "home"
            if route == "/"
            else route.strip("/").replace("/", "__")
        )

        screenshot_path = (
            evidence_dir
            / viewport.name
            / f"{safe_route}.png"
        )

        screenshot_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        await page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        status = (
            "passed"
            if (
                not console_errors
                and not page_errors
                and overflow_amount <= 2
                and not broken_links
                and metrics["mainCount"] == 1
                and metrics["h1Count"] == 1
            )
            else "failed"
        )

        evidence = RouteViewportEvidence(
            route=route,
            viewport=viewport,
            screenshot=str(screenshot_path),
            status=status,
            console_errors=console_errors,
            page_errors=page_errors,
            horizontal_overflow=overflow_amount > 2,
            overflow_amount_px=overflow_amount,
            h1_count=metrics["h1Count"],
            main_count=metrics["mainCount"],
            nav_count=metrics["navCount"],
            broken_internal_links=sorted(
                set(broken_links)
            ),
        )

        await context.close()

        return evidence

    async def run(
        self,
        instruction: str,
    ) -> str:
        payload = json.loads(instruction)

        project_dir = Path(
            payload.get("project_dir", "")
        ).resolve()

        output_dir = Path(
            payload.get("output_dir", "")
        ).resolve()

        project_slug = payload.get(
            "project_slug",
            project_dir.name,
        )

        if not project_dir.exists():
            raise FileNotFoundError(
                "Browser QA project directory not found: "
                f"{project_dir}"
            )

        if not (project_dir / "index.html").exists():
            raise FileNotFoundError(
                "Browser QA requires root index.html: "
                f"{project_dir}"
            )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        evidence_dir = (
            output_dir / "browser-screenshots"
        )

        resolver = SkillPolicyResolver()
        skills_used = []

        for relative_path in self.QA_SKILLS:
            skill = resolver.load(relative_path)
            skills_used.append(skill.name)

        try:
            from playwright.async_api import (
                async_playwright,
            )
        except ImportError as exc:
            raise RuntimeError(
                "Python Playwright is not installed. "
                "Run: python -m pip install playwright "
                "then: python -m playwright install chromium"
            ) from exc

        routes = self.discover_routes(project_dir)

        if not routes:
            raise RuntimeError(
                "Browser QA discovered no static routes."
            )

        viewports = [
            ViewportSpec(
                name=name,
                width=width,
                height=height,
            )
            for name, width, height in self.VIEWPORTS
        ]

        evidence = []

        with StaticServer(project_dir) as server:
            base_url = (
                f"http://127.0.0.1:{server.port}"
            )

            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True
                )

                try:
                    for route in routes:
                        for viewport in viewports:
                            item = await self.inspect_page(
                                browser,
                                route,
                                viewport,
                                project_dir,
                                evidence_dir,
                                base_url,
                            )

                            evidence.append(item)
                finally:
                    await browser.close()

        no_page_errors = all(
            not item.page_errors
            for item in evidence
        )

        no_console_errors = all(
            not item.console_errors
            for item in evidence
        )

        no_overflow = all(
            not item.horizontal_overflow
            for item in evidence
        )

        links_valid = all(
            not item.broken_internal_links
            for item in evidence
        )

        semantic_smoke = all(
            item.main_count == 1
            and item.h1_count == 1
            for item in evidence
        )

        screenshots_created = all(
            Path(item.screenshot).exists()
            for item in evidence
        )

        ready = (
            bool(routes)
            and screenshots_created
            and no_page_errors
            and no_overflow
            and links_valid
            and semantic_smoke
        )

        clean_pass = (
            ready
            and no_console_errors
        )

        failed_items = sum(
            item.status == "failed"
            for item in evidence
        )

        result = BrowserQAResult(
            status=(
                "passed"
                if clean_pass
                else (
                    "partial"
                    if screenshots_created
                    else "failed"
                )
            ),
            project_slug=project_slug,
            project_dir=str(project_dir),
            base_url=base_url,
            routes=routes,
            viewports=viewports,
            evidence=evidence,
            skills_used=skills_used,
            gates=BrowserQAGate(
                routes_discovered=bool(routes),
                screenshots_created=screenshots_created,
                no_page_errors=no_page_errors,
                no_console_errors=no_console_errors,
                no_horizontal_overflow=no_overflow,
                internal_links_valid=links_valid,
                semantic_smoke_passed=semantic_smoke,
                ready_for_visual_critic=ready,
            ),
            summary={
                "routes": len(routes),
                "viewports": len(viewports),
                "screenshots": len(evidence),
                "failed_checks": failed_items,
                "console_error_count": sum(
                    len(item.console_errors)
                    for item in evidence
                ),
                "page_error_count": sum(
                    len(item.page_errors)
                    for item in evidence
                ),
                "overflow_count": sum(
                    int(item.horizontal_overflow)
                    for item in evidence
                ),
                "broken_link_count": sum(
                    len(item.broken_internal_links)
                    for item in evidence
                ),
            },
            limitations=[
                (
                    "This is browser/runtime and layout smoke QA, "
                    "not WCAG conformance certification."
                ),
                (
                    "Visual quality is not judged here; screenshots "
                    "are passed to VisualCritic."
                ),
                (
                    "Mock/static commerce behavior is not treated "
                    "as real backend integration."
                ),
            ],
        )

        return result.model_dump_json(
            indent=2
        )
