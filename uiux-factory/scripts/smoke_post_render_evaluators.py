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

# The smoke exercises the evaluator suite, not MetaGPT role orchestration.
if "metagpt.actions" not in sys.modules:
    metagpt = types.ModuleType("metagpt")
    actions = types.ModuleType("metagpt.actions")
    actions.Action = object
    metagpt.actions = actions
    sys.modules["metagpt"] = metagpt
    sys.modules["metagpt.actions"] = actions

from core.contracts.browser_qa_schema import (
    BrowserQAGate,
    BrowserQAResult,
    ViewportSpec,
)
from core.verification.evidence_contract import EvidenceContractEvaluator
from core.verification.post_render_evaluators_final import PostRenderEvaluatorSuite


STYLE = """
body{font-family:Arial,sans-serif;font-size:16px;line-height:1.6;margin:0;padding:32px;max-width:900px}
button,.toggle,select{min-width:48px;min-height:48px;padding:12px;border:2px solid #222;background:#fff}
button:hover,.toggle:hover{background:#eee}
button:focus-visible,.toggle:focus-visible,input:focus-visible,a:focus-visible{outline:3px solid #005fcc;outline-offset:2px}
button:active,.toggle:active{transform:scale(.98)}
.panel{display:none}.panel[data-open="true"]{display:block}
.no-results{display:none}[data-empty="true"] .no-results{display:block}
input{min-height:44px;padding:8px}form{display:grid;gap:12px;max-width:480px}
.tip{display:none;position:absolute;right:24px;top:24px;max-width:260px;padding:12px;background:#fff;border:2px solid #222;z-index:5}
#help:hover + .tip,#help:focus + .tip,.tip:hover{display:block}
a{display:inline-block;padding:12px;min-height:24px}
@media (prefers-reduced-motion: reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}
"""

HTML = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{STYLE}</style></head>
<body><main>
<h1>Smoke evaluator</h1>
<p>Trang thử nghiệm dùng để chứng minh các evaluator V1 có thể chạy trên DOM thật và không suy diễn PASS từ file tồn tại.</p>
<button id="help" aria-describedby="help-tip">Trợ giúp</button>
<div id="help-tip" role="tooltip" class="tip"><button aria-label="Đóng">×</button> Nội dung trợ giúp có thể được rê chuột vào.</div>
<button id="toggle" aria-expanded="false">Mở chi tiết</button><div class="panel" id="panel">Nội dung chi tiết</div>
<label class="toggle"><input type="checkbox"> Chọn tùy chọn</label>
<section id="search-area"><label>Tìm kiếm <input type="search" id="search"></label><p class="no-results">Không có kết quả</p></section>
<form><label>Email <input required type="email"></label><button type="submit">Gửi</button><p role="status">Sẵn sàng</p></form>
<a href="/details.html">Xem sản phẩm thử nghiệm</a>
</main><script>
const toggle=document.querySelector('#toggle'), panel=document.querySelector('#panel');
toggle.addEventListener('click',()=>{{const next=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(next));panel.dataset.open=String(next)}});
const search=document.querySelector('#search'), area=document.querySelector('#search-area');search.addEventListener('input',()=>{{area.dataset.empty=String(search.value.includes('987654321'))}});
document.querySelector('form').addEventListener('submit',e=>e.preventDefault());
</script></body></html>"""

DETAILS = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{STYLE}</style></head>
<body><main><h1>Chi tiết thử nghiệm</h1><p>Đây là route thứ hai để Chromium smoke chứng minh demo path được hoàn thành bằng liên kết UI thật.</p><a href="/">Quay về trang chủ</a></main></body></html>"""


async def main() -> None:
    smoke_root = ROOT / ".tmp" / "post-render-evaluator-smoke"
    if smoke_root.exists():
        shutil.rmtree(smoke_root)
    project = smoke_root / "project"
    run_dir = smoke_root / "run"
    output = smoke_root / "output"
    project.mkdir(parents=True)
    run_dir.mkdir(parents=True)
    output.mkdir(parents=True)
    (project / "index.html").write_text(HTML, encoding="utf-8")
    (project / "details.html").write_text(DETAILS, encoding="utf-8")

    (run_dir / "design-system.json").write_text(json.dumps({
        "foundations": {
            "typography": {
                "font.family.body": {"value": None, "status": "unresolved"},
                "font.family.display": {"value": None, "status": "unresolved"}
            },
            "semantic_colors": {"text.primary": "color.neutral.950", "state.success": "color.state.success"}
        },
        "components": []
    }, indent=2), encoding="utf-8")
    (run_dir / "implementation-plan.json").write_text(json.dumps({
        "routes": [
            {"path": "/", "page_role": "Home", "priority": "P0"},
            {"path": "/details.html", "page_role": "Product Detail", "priority": "P0"}
        ]
    }, indent=2), encoding="utf-8")
    (run_dir / "art-direction.md").write_text(
        "# Art Direction\n\n## First Impression\n\nA clear test experience.\n\n## Style Adjectives\n\n- Clear\n- Structured\n- Purposeful\n\n## Visual Signature\n\nA visible test signature.\n",
        encoding="utf-8",
    )

    browser = BrowserQAResult(
        status="passed",
        project_slug="smoke",
        project_dir=str(project),
        base_url="http://127.0.0.1",
        routes=["/", "/details.html"],
        viewports=[
            ViewportSpec(name="desktop-1440", width=1440, height=1000),
            ViewportSpec(name="tablet-768", width=768, height=1024),
            ViewportSpec(name="mobile-390", width=390, height=844),
        ],
        evidence=[],
        gates=BrowserQAGate(
            routes_discovered=True,
            screenshots_created=True,
            no_page_errors=True,
            no_console_errors=True,
            no_horizontal_overflow=True,
            internal_links_valid=True,
            semantic_smoke_passed=True,
            ready_for_visual_critic=True,
        ),
    )
    browser_path = output / "browser-report.json"
    browser_path.write_text(browser.model_dump_json(indent=2), encoding="utf-8")

    suite = PostRenderEvaluatorSuite(
        run_dir=run_dir,
        project_dir=project,
        browser_report_path=browser_path,
        evidence_dir=output / "evidence",
    )
    outputs = await suite.run()

    required = {
        "interaction_state", "touch_targets", "content_stress", "squint", "blind_five_second",
        "design_system_metrics", "typography_metrics", "motion_metrics", "journey",
        "decoration_review", "style_word_review", "reference_comparison", "v1_readiness",
    }
    assert required <= set(outputs), outputs
    for path in outputs.values():
        assert Path(path).is_file(), path

    digest = EvidenceContractEvaluator.project_digest(project)
    interaction = json.loads((run_dir / "interaction-state-report.json").read_text(encoding="utf-8"))
    touch = json.loads((run_dir / "touch-target-metrics.json").read_text(encoding="utf-8"))
    stress = json.loads((run_dir / "content-stress-report.json").read_text(encoding="utf-8"))
    design = json.loads((run_dir / "design-system-metrics.json").read_text(encoding="utf-8"))
    typography = json.loads((run_dir / "typography-metrics.json").read_text(encoding="utf-8"))
    journey = json.loads((run_dir / "journey-report.json").read_text(encoding="utf-8"))
    readiness = json.loads((run_dir / "v1-verification-readiness.json").read_text(encoding="utf-8"))
    for payload in (interaction, touch, stress, design, typography, journey):
        assert payload["project_digest"] == digest

    assert "wcag_focus_hover_semantics" in interaction
    assert interaction["wcag_focus_hover_semantics"]["focus_visible_and_not_obscured"]
    assert interaction["wcag_focus_hover_semantics"]["content_on_hover_or_focus"]
    assert touch["requirements"]["RESPONSIVE-003"]["outcome"] == "passed"
    assert {row["id"] for row in stress["pseudo_localization"]["profiles"]} == {"expanded-accented-40", "vietnamese-heavy", "accented-density", "rtl-bidi"}
    assert design["requirements"]["VISUAL-005"]["outcome"] == "passed"
    assert typography["requirements"]["VISUAL-006"]["outcome"] == "passed"
    assert journey["requirements"]["CRITIQUE-006"]["outcome"] == "passed", journey
    assert readiness["v1_evaluator_coverage_complete"] is True, readiness
    assert readiness["missing_evaluator_implementations"] == [], readiness

    traces = list((output / "evidence" / "interaction").glob("*-trace.zip"))
    assert traces and all(path.stat().st_size > 0 for path in traces)
    pseudo_screens = list((output / "evidence" / "pseudo-localization").glob("*.png"))
    assert len(pseudo_screens) >= 24
    journey_traces = list((output / "evidence" / "journey").glob("*-trace.zip"))
    assert journey_traces and all(path.stat().st_size > 0 for path in journey_traces)
    print("final V1 post-render evaluator Chromium smoke passed")


if __name__ == "__main__":
    asyncio.run(main())
