"""Free provider transport contracts and AI pipeline regression using explicit fixtures."""

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aiohttp import web

from core.actions.generate_ai_frontend import DesignBrief, DesignPage, validate_bundle, write_bundle
from core.runtime.free_provider import ENDPOINTS, FreeProvider, ProviderConfig, ProviderError


BRIEF = DesignBrief(direction="Editorial studio, existing blue brand", pages=[
    DesignPage(path="index.html", title="Sample Studio", purpose="Explore studio services", sections=["hero", "services"])])
HTML = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Sample Studio</title></head><body><header><a href="#services">Services</a></header><main><h1>Design for thoughtful businesses.</h1><p>A fixture used to test generation plumbing.</p><section id="services"><h2>What we do</h2><p>Research, design and implementation.</p></section></main></body></html>'''
CSS = '''body{margin:0;padding:clamp(20px,6vw,80px);font:18px/1.6 Arial;color:#17222c;background:#fff}h1{font-size:clamp(32px,6vw,72px);max-width:900px;line-height:1.05}a{color:var(--color-brand-primary)}:focus-visible{outline:3px solid currentColor}section{margin-top:80px}@media(max-width:600px){section{margin-top:40px}}'''
BUNDLE = json.dumps({"files": {"index.html": HTML, "styles.css": CSS}})


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.requests = []
        self.status = 429
        self.finish_reason = "stop"
        async def response(request):
            payload = await request.json()
            self.requests.append(payload)
            if request.path == "/first" and self.status != 200:
                return web.json_response({"error": "must-not-be-persisted"}, status=self.status)
            return web.json_response({"choices": [{"message": {"content": '{"ok":true}'}, "finish_reason": self.finish_reason}]})
        app = web.Application()
        app.router.add_post("/{name}", response)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        server = await asyncio.get_running_loop().create_server(self.runner.server, "127.0.0.1", 0)
        self.server = server
        port = server.sockets[0].getsockname()[1]
        self.endpoints = patch.dict(ENDPOINTS, {"groq": f"http://127.0.0.1:{port}/first", "gemini": f"http://127.0.0.1:{port}/second"})
        self.endpoints.start()

    async def asyncTearDown(self):
        self.endpoints.stop()
        self.server.close()
        await self.server.wait_closed()
        await self.runner.cleanup()

    def provider(self):
        return FreeProvider([ProviderConfig("groq", "test-model", "secret-key"), ProviderConfig("gemini", "test-model", "secret-key")])

    async def test_rate_limit_falls_back_only_within_explicit_list(self):
        provider = self.provider()
        self.assertEqual(json.loads(await provider.complete("implementation", "JSON only", "test", json_mode=True)), {"ok": True})
        self.assertEqual(provider.calls, 2)
        self.assertNotIn("secret-key", json.dumps(provider.history))
        self.assertEqual(self.requests[1]["response_format"], {"type": "json_object"})

    async def test_auth_error_does_not_fall_back(self):
        self.status = 401
        provider = self.provider()
        with self.assertRaises(ProviderError) as result:
            await provider.complete("ux_ia", "test", "test")
        self.assertEqual(provider.calls, 1)
        self.assertNotIn("must-not", str(result.exception))

    async def test_budget_and_context_limits(self):
        provider = self.provider()
        provider.calls = 12
        with self.assertRaises(ProviderError):
            await provider.complete("repair", "test", "test")
        with self.assertRaises(ProviderError):
            await self.provider().complete("repair", "test", "x" * 50000)
        self.assertFalse(self.requests)

    async def test_truncated_generation_is_not_accepted(self):
        self.status = 200
        self.finish_reason = "length"
        with self.assertRaises(ProviderError):
            await self.provider().complete("implementation", "test", "test")
        self.assertEqual(len(self.requests), 1)

    def test_no_implicit_cloud_and_no_model_default(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderError):
                FreeProvider.from_env(Path(folder))
            with patch.dict(os.environ, {"UIUX_FREE_TIER_CONFIRMED": "1", "UIUX_CLOUD_PROVIDERS": "groq", "GROQ_API_KEY": "key"}):
                with self.assertRaises(ProviderError):
                    FreeProvider.from_env(Path(folder))


class BundleTests(unittest.TestCase):
    def test_ai_proposals_fill_gaps_and_preserve_supplied_brand(self):
        from core.orchestration.design_brain import apply_proposed_tokens
        from scripts.test_design_intelligence_v3 import base_system
        from core.contracts.design_system_schema import TokenValue
        system = base_system()
        apply_proposed_tokens(system, {"color.brand.primary": "#6E4B32"})
        self.assertEqual(system.foundations.colors["color.brand.primary"].value, "#6E4B32")
        self.assertEqual(system.foundations.colors["color.brand.primary"].status, "derived")
        system.foundations.colors["color.brand.primary"] = TokenValue(value="#003B71", status="confirmed", source="brand")
        apply_proposed_tokens(system, {"color.brand.primary": "#FF0000"})
        self.assertEqual(system.foundations.colors["color.brand.primary"].value, "#003B71")
        with self.assertRaises(ValueError):
            apply_proposed_tokens(system, {"unsafe": "x"})

    def test_canonical_token_override_cannot_write_any_file(self):
        raw = json.loads(BUNDLE)
        raw["files"]["styles.css"] += ":root { --font-family-body: Comic Sans MS; }"
        bundle = validate_bundle(json.dumps(raw), BRIEF)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                write_bundle(Path(folder), "sample", bundle, ":root { --font-family-body: Arial; }")
            self.assertFalse((Path(folder) / "generated").exists())

    def test_rejects_path_escape_missing_routes_and_brand_override(self):
        validate_bundle(BUNDLE, BRIEF)
        for files in [
            {"../outside.txt": "x", "index.html": HTML, "styles.css": CSS},
            {"styles.css": CSS, "app.js": ""},
            {"index.html": HTML, "styles.css": CSS + ":root{--color-brand-primary:red}"},
            {"index.html": HTML.replace("<header>", '<iframe src="http://localhost:8788"></iframe><header>'), "styles.css": CSS},
        ]:
            with self.assertRaises(ValueError):
                validate_bundle(json.dumps({"files": files}), BRIEF)


class BrainIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_skills_browser_qa_and_repair_with_fixture_provider(self):
        from core.manager.development_manager import DevelopmentManager
        from core.contracts.design_context_schema import DesignContext

        class FixtureProvider:
            def __init__(self):
                self.history = []
            async def complete(self, stage, system, prompt, *, json_mode=False):
                self.history.append({"stage": stage, "provider": "fixture", "model": "not-a-real-model"})
                if stage == "research":
                    return "FACT: supplied studio brief. UNKNOWN: portfolio assets. INFERENCE: service discovery is the primary task."
                if stage == "ux_ia":
                    return BRIEF.model_dump_json()
                if stage == "art_direction":
                    return "Editorial typography with restrained blue accents, spacious sections and a compact mobile layout."
                if stage == "implementation":
                    self_outer.assertIn("Original guideline constraint", prompt)
                    return BUNDLE.replace("margin:0;", "margin:0;width:1800px;")
                if stage == "repair":
                    return BUNDLE
                raise AssertionError(stage)

        root = Path(__file__).resolve().parents[1]
        self_outer = self
        from uuid import uuid4
        run_id = "brain-fixture-" + uuid4().hex[:8]
        provider = FixtureProvider()
        with patch.object(FreeProvider, "from_env", return_value=provider):
            context = await DevelopmentManager(root).run("Design a studio landing page", DesignContext(brand_name="Sample Studio", guideline="Original guideline constraint", tokens={"colors":{"primary":"#003B71"}}), run_id, engine="ai")
        self.assertEqual(context.status, "completed")
        report = json.loads(Path(context.artifacts["quality_loop"]).read_text(encoding="utf-8"))
        self.assertEqual(report["attempts"], 2)
        self.assertTrue(report["browser_checks_passed"])
        self.assertIsNone(report["aesthetic_score"])
        document = Path(context.artifacts["design_document"]).read_text(encoding="utf-8")
        self.assertIn("#003B71", document)
        self.assertEqual(document.count("\n## "), 9)
        self.assertIn("repair", [call["stage"] for call in provider.history])
        print("Fixture integration artifacts:", context.run_dir)


if __name__ == "__main__":
    unittest.main()
