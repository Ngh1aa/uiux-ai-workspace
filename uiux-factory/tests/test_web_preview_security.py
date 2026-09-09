from pathlib import Path


WEB_ROOT = Path(__file__).resolve().parents[1] / "apps" / "web"


def test_generated_preview_does_not_keep_same_origin() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="preview-frame"' in html
    assert 'sandbox="allow-scripts"' in html
    assert "allow-same-origin" not in html


def test_generated_preview_is_not_exposed_as_unsandboxed_new_tab_link() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

    assert '<a id="preview-link"' not in html
    assert '<span id="preview-link"' in html


def test_direct_bridge_configuration_does_not_add_console_api_prefix() -> None:
    javascript = (WEB_ROOT / "app.js").read_text(encoding="utf-8")

    assert 'window.UIUX_BRIDGE_URL.replace(/\\/$/, "") + "/api"' not in javascript
    assert 'if (window.UIUX_BRIDGE_URL) return window.UIUX_BRIDGE_URL.replace(/\\/$/, "");' in javascript
    assert 'return "http://127.0.0.1:8788";' in javascript
