"""Run with: .venv\Scripts\python.exe -m unittest scripts.test_design_intelligence_v3 -v"""

import asyncio
import base64
import io
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen, Request

from PIL import Image
from pydantic import ValidationError
from playwright.async_api import async_playwright

from core.actions.analyze_references import MEASURE_PAGE, PublicResolver, analyze_reference, validate_network_url, fetch_public_response
from core.actions.create_design_system import CreateDesignSystem
from core.actions.create_design_system_v3 import CreateDesignSystemV3
from core.contracts.design_context_schema import DesignContext, ReferenceBoard, ReferenceDNA, DesignObservation
from core.contracts.design_system_schema import DesignSystemContract, DesignSystemGate
from core.contracts.schema import DesignContract, ProjectContract, UXContract, VisualContract, ImplementationConstraints, EvidenceStatus
from core.runtime.design_tokens import token_css, system_styles
from core.runtime.run_context import RunContext
from core.actions.generate_frontend_project_v2 import GenerateFrontendProjectV2
from core.actions.create_visual_composition_v2 import CreateVisualCompositionV2
from core.contracts.visual_composition_schema import PageSpec


def base_system():
    contract = DesignContract(project=ProjectContract(goal="Bank website", domain="corporate"), ux=UXContract(),
                              visual=VisualContract(), constraints=ImplementationConstraints(), gates=EvidenceStatus(), sources={})
    return DesignSystemContract(source_design_contract_path="fixture.json", source_design_contract_sha256="fixture",
                                foundations=CreateDesignSystem.build_foundations(contract),
                                gates=DesignSystemGate(implementation_ready_with_fallbacks=True),
                                components=CreateDesignSystem.common_components())


class BrandTests(unittest.TestCase):
    def test_composer_v2_home_contract_and_missing_section(self):
        home = PageSpec(path="/", page_role="Home", composition_family="commerce", first_visual_anchor="product",
                        sections=CreateVisualCompositionV2.sections_for("ecommerce", "/", "Home", "editorial"))
        GenerateFrontendProjectV2.require_home_contract(home)
        home.sections = [section for section in home.sections if section.type != "product-hero"]
        with self.assertRaises(RuntimeError):
            GenerateFrontendProjectV2.require_home_contract(home)

    def test_precedence_and_downstream_css(self):
        context = DesignContext(brand_name="Sample Bank", personality=["premium", "trustworthy"], avoid=["stock photos"],
                                existing_code=":root { --brand-primary: #111111; --font-body: Arial; }",
                                guideline="Primary: #006D6A\nBody font: Inter\nCard radius: 16px",
                                tokens={"colors": {"primary": "#003B71", "accent": "#90321E"},
                                        "typography": {"heading": "Inter"}})
        system = CreateDesignSystemV3.enrich(base_system(), context, ReferenceBoard())
        self.assertEqual(system.foundations.colors["color.brand.primary"].value, "#003B71")
        self.assertEqual(system.foundations.colors["color.brand.primary"].status, "confirmed")
        self.assertEqual(system.foundations.typography["font.family.body"].value, "Inter")
        self.assertEqual(len(system.brand.conflicts), 3)
        self.assertIn("--color-brand-primary: #003B71", token_css(system))
        self.assertIn("font-family: var(--font-family-body)", system_styles(system))
        self.assertIn("--radius-lg: 16px", token_css(system))
        self.assertTrue(all(component.states for component in system.components if component.priority == "P0"))
        self.assertFalse(system.gates.final_visual_lock)

    def test_competitor_never_becomes_brand(self):
        board = ReferenceBoard(references=[ReferenceDNA(url="https://reference.example", status="observed", observations=[
            DesignObservation(category="typography", subject="body[0].font-family", value="Competitor Font", source="https://reference.example @ 1440x1000"),
            DesignObservation(category="color", subject="body[0].background-color", value="rgb(255, 0, 0)", source="https://reference.example @ 1440x1000"),
        ], patterns=["Large display heading observed."])])
        system = CreateDesignSystemV3.enrich(base_system(), DesignContext(), board)
        self.assertIsNone(system.foundations.colors["color.brand.primary"].value)
        self.assertIsNone(system.foundations.typography["font.family.body"].value)
        self.assertIn("https://reference.example", system.brand.reference_patterns[0])

    def test_existing_site_typography_is_derived(self):
        board = ReferenceBoard(references=[ReferenceDNA(url="https://brand.example", role="existing_website", observations=[
            DesignObservation(category="typography", subject="body[0].font-family", value="Arial", source="https://brand.example @ 1440x1000")
        ])])
        system = CreateDesignSystemV3.enrich(base_system(), DesignContext(), board)
        self.assertEqual(system.foundations.typography["font.family.body"].status, "derived")

    def test_roundtrip_does_not_promote_defaults(self):
        baseline = base_system()
        system = CreateDesignSystemV3.enrich(base_system(), DesignContext(tokens=json.loads(baseline.model_dump_json())), ReferenceBoard())
        self.assertEqual(system.foundations.colors["color.neutral.0"].status, "factory_default")
        self.assertIsNone(system.foundations.colors["color.brand.primary"].value)
        DesignSystemContract.model_validate_json(system.model_dump_json())

    def test_rejects_css_injection_and_bad_input(self):
        for value in ["red; } body { display:none", "url(https://host)", "#123456</style>", "not-a-color"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                CreateDesignSystemV3.enrich(base_system(), DesignContext(tokens={"colors": {"primary": value}}), ReferenceBoard())
        with self.assertRaises(ValidationError):
            DesignContext(reference_urls=["file:///secret"])
        with self.assertRaises(ValidationError):
            DesignContext(assets=[{"name": "x", "kind": "logo", "data_url": "data:text/html;base64,aGk="}])

    def test_image_palette_is_evidence_only(self):
        buffer = io.BytesIO()
        Image.new("RGB", (16, 16), "#006D6A").save(buffer, format="PNG")
        context = DesignContext(assets=[{"name": "logo.png", "kind": "logo", "data_url": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()}])
        system = CreateDesignSystemV3.enrich(base_system(), context, ReferenceBoard())
        self.assertIn("#006D6A", system.brand.evidence[0].value)
        self.assertIsNone(system.foundations.colors["color.brand.primary"].value)

    def test_unique_run_ids(self):
        self.assertNotEqual(RunContext(root=Path.cwd(), goal="a").run_id, RunContext(root=Path.cwd(), goal="a").run_id)


class ReferenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_redirect_to_private_network_is_blocked(self):
        class Redirect:
            status = 302
            headers = {"Location": "http://127.0.0.1/secret"}

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class Session:
            def __init__(self):
                self.calls = []

            def get(self, url, **kwargs):
                self.calls.append(url)
                return Redirect()

        session = Session()
        with self.assertRaises(ValueError):
            await fetch_public_response(session, "https://public.example", {"bytes": 0})
        self.assertEqual(session.calls, ["https://public.example"])

    async def test_private_network_and_dns_are_blocked(self):
        for url in ["http://127.0.0.1", "http://[::1]", "http://169.254.169.254/", "http://10.0.0.1", "http://localhost", "http://user:pass@host.com", "ftp://example.com"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_network_url(url)
        async def private_resolve(*args, **kwargs):
            return [{"host": "127.0.0.1"}]
        with patch("aiohttp.resolver.ThreadedResolver.resolve", private_resolve):
            with self.assertRaises(OSError):
                await PublicResolver().resolve("rebind.example", 443)
        with tempfile.TemporaryDirectory() as folder:
            result = await analyze_reference("http://127.0.0.1", Path(folder))
            self.assertEqual(result.status, "unavailable")
            self.assertFalse(result.observations)
            self.assertTrue(result.warnings)

    async def test_rendered_measurements_and_token_consumption(self):
        system = CreateDesignSystemV3.enrich(base_system(), DesignContext(tokens={"typography": {"body": "Arial", "heading": "Georgia"}, "radius": {"button": "12px"}}), ReferenceBoard())
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                page = await browser.new_page(viewport={"width": 1440, "height": 1000})
                await page.set_content("<style>h1 { font-size:64px; }" + system_styles(system) + "</style><nav><a href='/'>Home</a></nav><main><h1>Evidence</h1><button class='button'>Apply</button></main>")
                desktop = await page.evaluate(MEASURE_PAGE)
                self.assertTrue(any(item["subject"] == "h1[0].font-size" and item["value"] == "64px" for item in desktop["observations"]))
                self.assertEqual(await page.locator("button").evaluate("el => getComputedStyle(el).borderRadius"), "12px")
                self.assertIn("Georgia", await page.locator("h1").evaluate("el => getComputedStyle(el).fontFamily"))
                await page.set_viewport_size({"width": 390, "height": 844})
                mobile = await page.evaluate(MEASURE_PAGE)
                self.assertTrue(any(item["subject"] == "navigation.visible-links" and item["value"] == "1" for item in mobile["observations"]))
            finally:
                await browser.close()


class BridgeTests(unittest.TestCase):
    def test_validation_and_artifact_scope(self):
        from apps.bridge import server
        from http.server import ThreadingHTTPServer
        with tempfile.TemporaryDirectory() as folder, patch.object(server, "RUNS", Path(folder)):
            job_id = "abcdef123456"
            (Path(folder) / job_id).mkdir()
            (Path(folder) / job_id / "design-system.json").write_text('{"brand": "test"}')
            httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{httpd.server_port}"
            try:
                with self.assertRaises(HTTPError) as error:
                    urlopen(Request(base + "/intelligence", data=b'{"prompt":"test"}', headers={"Origin": "https://untrusted.example"}))
                self.assertEqual(error.exception.code, 403)
                self.assertEqual(json.load(urlopen(base + f"/jobs/{job_id}/artifacts/design-system.json"))["brand"], "test")
                for path in [f"/jobs/{job_id}/artifacts/design-context.json", f"/jobs/{job_id}/artifacts/../../secret", "/jobs/111111111111/artifacts/design-system.json"]:
                    with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                        urlopen(base + path)
                    self.assertEqual(error.exception.code, 404)
                for data in [[], {"prompt": "test", "design_context": {"reference_urls": ["file:///x"]}}]:
                    with self.assertRaises(HTTPError) as error:
                        urlopen(Request(base + "/intelligence", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}))
                    self.assertEqual(error.exception.code, 400)
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
