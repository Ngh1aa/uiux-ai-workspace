from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"


def test_workbench_exposes_visual_brain_and_reference_controls() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    assert "Visual Intelligence Workbench" in html
    assert 'id="auto-inspiration"' in html
    assert 'id="inspiration-target"' in html
    assert "Build with Visual Brain" in html
    assert "Visual Brain" in html
    assert 'sandbox="allow-scripts"' in html
    assert "allow-same-origin" not in html


def test_workbench_visual_signature_is_not_old_gradient_card_theme() -> None:
    css = (WEB / "styles.css").read_text(encoding="utf-8")
    assert "--accent: #d45f32" in css
    assert ".workspace-shell" in css
    assert ".composer-rail" in css
    assert ".studio-canvas" in css
    assert "White background + Red-Orange gradient highlight" not in css
    assert "glassmorphism" not in css.lower()


def test_routing_preview_uses_the_five_visual_skills() -> None:
    router = (WEB / "skills-router.js").read_text(encoding="utf-8")
    required = (
        "visual-design-direction/SKILL.md",
        "brand-distinctiveness-and-visual-signature/SKILL.md",
        "visual-taste-calibration/SKILL.md",
        "interaction-patterns-and-form-ux/SKILL.md",
        "ui-craft-and-visual-qa/SKILL.md",
    )
    for skill in required:
        assert skill in router
    assert "auto_inspiration" in router
    assert "inspiration_target" in router
    assert "portfolio" in router
    assert "hospitality" in router
    assert "real-estate" in router


def test_factory_entrypoint_keeps_visual_brain_under_creative_director_manager() -> None:
    run_py = (ROOT / "run.py").read_text(encoding="utf-8")
    creative_manager = (
        ROOT / "core" / "manager" / "creative_director_manager.py"
    ).read_text(encoding="utf-8")

    assert "CreativeDirectorDevelopmentManager" in run_py
    assert "VisualBrainDevelopmentManager" in creative_manager
    assert "class CreativeDirectorDevelopmentManager(VisualBrainDevelopmentManager)" in creative_manager
    assert "ProviderIntelligentDevelopmentManager(root=ROOT)" not in run_py
