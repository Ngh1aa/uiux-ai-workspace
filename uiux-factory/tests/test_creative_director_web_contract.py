from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"
BRIDGE = ROOT / "apps" / "bridge"


def test_workbench_wires_review_pack_and_stage_aware_directive_import() -> None:
    app = (WEB / "app.js").read_text(encoding="utf-8")

    assert "/review-pack" in app
    assert "/creative-directive" in app
    assert "Export Review Pack" in app
    assert "Import Creative Directive" in app
    assert "source_run_id" in app
    assert "creative_review_ready" in app


def test_auto_inspiration_controls_are_sent_to_design_context() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    app = (WEB / "app.js").read_text(encoding="utf-8")

    assert 'id="auto-inspiration"' in html
    assert 'id="inspiration-target"' in html
    assert "ctx.auto_inspiration" in app
    assert "ctx.inspiration_target" in app


def test_creative_review_panel_preserves_editorial_visual_language() -> None:
    css = (WEB / "creative-review.css").read_text(encoding="utf-8").lower()

    assert "linear-gradient" not in css
    assert "radial-gradient" not in css
    assert "backdrop-filter" not in css
    assert "glassmorphism" not in css
    assert "var(--font-display)" in css
    assert "var(--accent)" in css
    assert "@media" in css


def test_bridge_exposes_review_pack_and_validated_revision_endpoint() -> None:
    server = (BRIDGE / "server.py").read_text(encoding="utf-8")
    pack = (BRIDGE / "creative_review.py").read_text(encoding="utf-8")

    assert "/jobs/([a-f0-9]{12})/review-pack" in server
    assert "/jobs/([a-f0-9]{12})/creative-directive" in server
    assert "CreativeDirective.model_validate" in server
    assert "stage_aware_revision" in server
    assert "path.is_relative_to(run_root)" in pack
