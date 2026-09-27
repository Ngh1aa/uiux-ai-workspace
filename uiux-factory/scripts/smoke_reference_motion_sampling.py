from __future__ import annotations

import asyncio
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if "metagpt.actions" not in sys.modules:
    metagpt = types.ModuleType("metagpt")
    actions = types.ModuleType("metagpt.actions")
    actions.Action = object
    metagpt.actions = actions
    sys.modules["metagpt"] = metagpt
    sys.modules["metagpt.actions"] = actions

from playwright.async_api import async_playwright

from core.actions.analyze_references_with_motion import (
    INTERACTION_STYLE_JS,
    MOTION_CHECKPOINT_JS,
    MOTION_INIT_SCRIPT,
    _sample_interactions,
)
from core.contracts.reference_evidence_schema import (
    EventListenerEvidence,
    MotionCheckpointEvidence,
    ReferenceMotionEvidence,
)


HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
:root{--scroll-progress:0;--accent:#d14b32}
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;min-height:3600px}
header{position:sticky;top:0;padding:20px;background:#fff;z-index:3}
#motion-target{position:fixed;right:40px;top:160px;width:220px;height:110px;background:var(--accent);transform:translateX(0px);opacity:1;transition:filter .2s ease-out}
#motion-target.pulse{animation:pulse 1.2s ease-in-out infinite alternate}
#action{margin:420px 40px 0;padding:16px 24px;background:#fff;border:2px solid #111;transition:transform .18s ease-out,background-color .18s ease-out}
#action:hover{transform:translateY(-3px);background:#f2e8d5}
#action:focus-visible{outline:4px solid #2855d9;outline-offset:3px}
@keyframes pulse{from{filter:saturate(1)}to{filter:saturate(1.4)}}
</style></head><body>
<header><h1>Runtime motion fixture</h1></header>
<div id="motion-target" class="pulse"></div>
<button id="action">Focus or hover</button>
<script>
const target=document.querySelector('#motion-target');
window.addEventListener('scroll',()=>{
  const max=Math.max(1,document.documentElement.scrollHeight-innerHeight);
  const p=Math.min(1,scrollY/max);
  document.documentElement.style.setProperty('--scroll-progress',p.toFixed(3));
  target.style.transform=`translateX(${Math.round(p*180)}px)`;
  target.style.opacity=String((1-p*.45).toFixed(3));
},{passive:true});
document.querySelector('#action').addEventListener('mouseenter',()=>{});
</script></body></html>"""


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            context = await browser.new_context(viewport={"width": 1440, "height": 1000})
            await context.add_init_script(MOTION_INIT_SCRIPT)
            page = await context.new_page()
            await page.set_content(HTML, wait_until="load")

            max_scroll = int(await page.evaluate("Math.max(0,document.documentElement.scrollHeight-innerHeight)"))
            checkpoints = []
            for label, progress in (("start", 0.0), ("middle", 0.5), ("end", 1.0)):
                y = int(round(max_scroll * progress))
                await page.evaluate("y => scrollTo(0,y)", y)
                await page.wait_for_timeout(120)
                measured = await page.evaluate(MOTION_CHECKPOINT_JS)
                checkpoints.append(
                    MotionCheckpointEvidence(
                        label=label,
                        scroll_y=y,
                        scroll_progress=progress,
                        elements=measured["elements"],
                        animations=measured["animations"],
                        root_custom_properties=measured["root_custom_properties"],
                    )
                )

            raw = await page.evaluate("window.__uiuxReferenceListeners || []")
            listeners = [EventListenerEvidence.model_validate(row) for row in raw]
            await page.evaluate("scrollTo(0,0)")
            await page.wait_for_timeout(80)
            interactions = await _sample_interactions(page)
            evidence = ReferenceMotionEvidence(
                viewport={"label": "desktop-motion", "width": 1440, "height": 1000},
                max_scroll_y=max_scroll,
                checkpoints=checkpoints,
                listeners=listeners,
                interactions=interactions,
            )

            target_states = []
            for checkpoint in evidence.checkpoints:
                state = next((item for item in checkpoint.elements if item.selector == "#motion-target"), None)
                assert state is not None, checkpoint.label
                target_states.append((checkpoint.label, state.transform, state.opacity))
            assert len({state[1] for state in target_states}) >= 2, target_states
            assert len({state[2] for state in target_states}) >= 2, target_states
            assert evidence.checkpoints[1].root_custom_properties.get("--scroll-progress") not in {None, "0"}
            assert any(item.event_type == "scroll" and item.target == "window" for item in evidence.listeners)
            assert any(item.selector == "#action" and item.state == "hover" and "transform" in item.changed_properties for item in evidence.interactions)
            assert any(item.selector == "#action" and item.state == "focus" and "outline-width" in item.changed_properties for item in evidence.interactions)
            assert any(animation.selector == "#motion-target" and animation.duration in {"1200", "1200.0"} for animation in evidence.checkpoints[0].animations)

            # Prove the style probe itself remains side-effect free.
            before = await page.locator("#action").evaluate(INTERACTION_STYLE_JS)
            after = await page.locator("#action").evaluate(INTERACTION_STYLE_JS)
            assert before == after
            print(json.dumps(evidence.model_dump(), indent=2)[:5000])
            print("reference motion sampling Chromium smoke passed")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
