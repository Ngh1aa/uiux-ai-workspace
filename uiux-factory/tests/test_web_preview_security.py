from pathlib import Path


def test_generated_preview_does_not_keep_same_origin() -> None:
    html = (Path(__file__).resolve().parents[1] / "apps" / "web" / "index.html").read_text(
        encoding="utf-8"
    )

    assert 'id="preview-frame"' in html
    assert 'sandbox="allow-scripts"' in html
    assert "allow-same-origin" not in html


def test_generated_preview_is_not_exposed_as_unsandboxed_new_tab_link() -> None:
    html = (Path(__file__).resolve().parents[1] / "apps" / "web" / "index.html").read_text(
        encoding="utf-8"
    )

    assert '<a id="preview-link"' not in html
    assert '<span id="preview-link"' in html
