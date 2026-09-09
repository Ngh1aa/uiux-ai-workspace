from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"


def test_workbench_router_mirrors_prototype_vertical_and_reference_contracts() -> None:
    router = (WEB / "skills-router.js").read_text(encoding="utf-8")
    app = (WEB / "app.js").read_text(encoding="utf-8")
    html = (WEB / "index.html").read_text(encoding="utf-8")

    assert "prototype-visual-experience-qa/SKILL.md" in router
    assert '"luxury-fragrance"' in router
    assert "inferVertical" in router
    assert "inferMode" in router
    assert "interactive-prototype" in router
    assert "production-candidate" in router

    assert "Math.min(4" in router
    assert "[1, 2, 3, 4]" in router
    assert "Math.min(4" in app
    assert "[1, 2, 3, 4]" in app
    assert '<option value="4" selected>4</option>' in html


def test_workbench_client_does_not_embed_live_search_credentials() -> None:
    client_source = "\n".join(
        (WEB / name).read_text(encoding="utf-8")
        for name in ("index.html", "app.js", "skills-router.js")
    )
    assert "BRAVE_SEARCH_API_KEY" not in client_source
    assert "X-Subscription-Token" not in client_source
