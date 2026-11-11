"""inline-icons.py: icon dựng bằng JS cũng được nhúng; tên không có trong sprite thì cảnh báo."""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "design-system" / "starter" / "inline-icons.py"
SPEC = importlib.util.spec_from_file_location("inline_icons", SCRIPT)
icons = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(icons)

PAGE = """<html><body><!-- icons:start -->
<!-- icons:end -->
<svg><use href="#ds-i-home"/></svg>
<script>const icon = done ? '#ds-i-check-circle' : 'ds-i-clock'; const typo = '#ds-i-nope';</script>
</body></html>"""


def test_icons_named_only_in_scripts_are_embedded():
    html = icons.render(PAGE, icons.load_symbols())
    for name in ("ds-i-home", "ds-i-check-circle", "ds-i-clock"):
        assert f'<symbol id="{name}"' in html
    assert 'id="ds-i-nope"' not in html


def test_unknown_scripted_name_is_reported_not_silently_dropped(tmp_path):
    page = tmp_path / "page.html"
    page.write_text(PAGE, encoding="utf-8")
    out = subprocess.run([sys.executable, str(SCRIPT), str(page)], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0
    assert "ds-i-nope" in out.stdout
    assert "ds-i-check-circle" in out.stdout


def test_sprite_ids_in_the_existing_block_are_not_counted_as_usage():
    symbols = icons.load_symbols()
    once = icons.render(PAGE, symbols)
    start = once.index("<script>")
    without_script = once[:start] + once[once.index("</script>") + len("</script>"):]
    again = icons.render(without_script, symbols)
    assert 'id="ds-i-clock"' not in again, "khối sprite cũ không được tự giữ icon không còn dùng"
