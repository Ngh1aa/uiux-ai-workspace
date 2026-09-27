from __future__ import annotations

import asyncio
import json
import shutil
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# This smoke tests the extractor, not MetaGPT orchestration.
if "metagpt.actions" not in sys.modules:
    metagpt = types.ModuleType("metagpt")
    actions = types.ModuleType("metagpt.actions")
    actions.Action = object
    metagpt.actions = actions
    sys.modules["metagpt"] = metagpt
    sys.modules["metagpt.actions"] = actions

from playwright.async_api import async_playwright

from core.actions.analyze_references import MEASURE_EVIDENCE, build_capture_from_measurement
from core.contracts.reference_evidence_schema import ReferenceEvidenceBundle, ReferencePageEvidence


HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Reference evidence smoke fixture">
<meta name="theme-color" content="#14213d">
<style>
:root{--accent:#fca311;--paper:#fefae0}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:#14213d;font-family:Georgia,serif}
header{display:flex;justify-content:space-between;padding:24px 40px;border-bottom:1px solid #14213d}
main{display:grid;grid-template-columns:1fr 1fr;gap:32px;padding:48px 40px}
h1{font-size:72px;line-height:.9;margin:0;color:#14213d}
.card{background:#fff;padding:24px;border-radius:18px;transition:transform .2s ease-out}
.card:hover{transform:translateY(-2px)}
.hero-image{width:100%;height:240px;object-fit:cover;background:#fca311}
@media (max-width:600px){main{grid-template-columns:1fr;padding:24px 18px}h1{font-size:44px}}
@media (prefers-reduced-motion:reduce){*{transition-duration:.01ms!important}}
</style>
</head>
<body>
<header><strong>Evidence Lab</strong><nav><a href="#work">Work</a><a href="#about">About</a></nav></header>
<main id="work"><section><h1>Measured, not guessed.</h1><p>Fixture copy for deterministic evidence extraction.</p></section><article class="card"><img class="hero-image" alt="Orange sample" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect width='640' height='360' fill='%23fca311'/%3E%3C/svg%3E"><button aria-expanded="false">Inspect</button></article></main>
</body>
</html>"""


async def main() -> None:
    tmp = ROOT / ".tmp" / "reference-evidence-smoke"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)

    captures = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            page = await browser.new_page()
            await page.set_content(HTML, wait_until="load")
            for label, width, height in (("desktop", 1440, 900), ("mobile", 390, 844)):
                await page.set_viewport_size({"width": width, "height": height})
                measured = await page.evaluate(MEASURE_EVIDENCE)
                screenshot = tmp / f"{label}.png"
                await page.screenshot(path=str(screenshot), full_page=False)
                capture = build_capture_from_measurement(
                    measured,
                    label=label,
                    width=width,
                    height=height,
                    screenshot_path=screenshot,
                    screenshot_ref=f"references/{label}.png",
                )
                captures.append(capture)
        finally:
            await browser.close()

    page_evidence = ReferencePageEvidence(
        url="https://example.invalid/reference-smoke",
        role="reference",
        status="observed",
        captured_at="2026-09-27T00:00:00+00:00",
        document={
            "title": "",
            "lang": "en",
            "description": "Reference evidence smoke fixture",
            "canonical": "",
            "theme_color": "#14213d",
            "doctype": "<!DOCTYPE html>",
        },
        captures=captures,
    )
    bundle = ReferenceEvidenceBundle(references=[page_evidence])
    output = tmp / "reference-evidence.v1.json"
    output.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
    restored = ReferenceEvidenceBundle.model_validate_json(output.read_text(encoding="utf-8"))

    assert restored.schema_version == "reference-evidence.v1"
    assert len(restored.references) == 1
    desktop, mobile = restored.references[0].captures
    assert desktop.viewport.width == 1440 and mobile.viewport.width == 390
    assert any(node.tag == "h1" and "Measured, not guessed." in node.text for node in desktop.dom)
    assert desktop.root_custom_properties["--accent"] == "#fca311"
    assert any(row.properties.get("font-size") == "72px" for row in desktop.computed_styles if "h1" in row.selector)
    assert any(row.properties.get("font-size") == "44px" for row in mobile.computed_styles if "h1" in row.selector)
    desktop_mq = {row.condition: row.matches for row in desktop.media_queries}
    mobile_mq = {row.condition: row.matches for row in mobile.media_queries}
    assert desktop_mq.get("(max-width: 600px)") is False
    assert mobile_mq.get("(max-width: 600px)") is True
    assert any(asset.kind == "image" and asset.url.startswith("data:image/svg+xml") for asset in desktop.assets)
    assert desktop.css_colors and all(color.evidence == "VERIFIED" for color in desktop.css_colors)
    assert desktop.visual_palette and all(color.evidence == "INFERRED" for color in desktop.visual_palette)
    assert desktop.screenshot and len(desktop.screenshot.sha256) == 64
    assert desktop.horizontal_overflow is False
    print(json.dumps({
        "schema": restored.schema_version,
        "desktop_dom": len(desktop.dom),
        "desktop_styles": len(desktop.computed_styles),
        "assets": len(desktop.assets),
        "media_queries": len(desktop.media_queries),
        "visual_palette": [row.value for row in desktop.visual_palette],
    }, indent=2))
    print("reference evidence extractor Chromium smoke passed")


if __name__ == "__main__":
    asyncio.run(main())
