"""Test overlay-check.py trên các repo git tạm: một nhánh phủ đè và một nhánh thay thế."""

from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).with_name("overlay-check.py")
spec = importlib.util.spec_from_file_location("overlay_check", SCRIPT)
overlay_check = importlib.util.module_from_spec(spec)
sys.modules["overlay_check"] = overlay_check
spec.loader.exec_module(overlay_check)

OLD_CSS = "\n".join(
    f".row-{i} {{ background: #f{i % 10}e{i % 10}ff; color: #333; padding: 12px; border-radius: {i % 4 + 4}px; }}"
    for i in range(60)
)
PAGE = """<!doctype html><html><head>
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/pastel.css">
{extra}</head><body><main id="main"><div class="hero">Home</div></main>
<script src="assets/render.js"></script>{script}</body></html>
"""


def run(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def write(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


class OverlayCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        run(self.repo, "init", "-q", "-b", "main")
        run(self.repo, "config", "user.email", "t@example.com")
        run(self.repo, "config", "user.name", "Test")
        write(self.repo, "assets/base.css", "body { margin: 0; font-family: system-ui; }\n" + OLD_CSS + "\n")
        write(self.repo, "assets/pastel.css", OLD_CSS.replace("row", "tile") + "\n")
        write(self.repo, "assets/render.js", "export const render = () => '<div class=\"hero\">Home</div>';\n")
        write(self.repo, "app.html", PAGE.format(extra="", script=""))
        run(self.repo, "add", "-A")
        run(self.repo, "commit", "-qm", "base")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def check(self) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out):
            code = overlay_check.main(["--repo", str(self.repo), "--base", "main"])
        return code, out.getvalue()

    def test_overlay_branch_fails(self) -> None:
        layer = "\n".join(f".row-{i} {{ background: #fff !important; border-radius: 12px !important; }}" for i in range(90))
        write(self.repo, "assets/v6.css", "/* final layer */\n" + layer + "\n")
        write(
            self.repo,
            "assets/v6.js",
            "const hero = document.querySelector('.hero');\nhero.insertAdjacentHTML('beforeend', '<i></i>');\n",
        )
        write(
            self.repo,
            "app.html",
            PAGE.format(extra='<link rel="stylesheet" href="assets/v6.css">\n', script='<script src="assets/v6.js"></script>'),
        )
        code, out = self.check()
        self.assertEqual(code, 1)
        for rule in ("overlay-ratio", "new-layer", "important", "dom-patch", "untouched-owners"):
            self.assertIn(f"ERROR   {rule}", out, rule)

    def test_replacement_branch_passes(self) -> None:
        new_css = "\n".join(f".row-{i} {{ background: var(--surface); color: var(--ink); padding: 16px; }}" for i in range(60))
        write(self.repo, "assets/base.css", "body { margin: 0; font-family: var(--font); }\n" + new_css + "\n")
        (self.repo / "assets/pastel.css").unlink()
        write(self.repo, "app.html", PAGE.format(extra="", script="").replace('<link rel="stylesheet" href="assets/pastel.css">\n', ""))
        write(self.repo, "assets/render.js", "export const render = () => '<section class=\"hero\"><h1>Home</h1></section>';\n")
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("ERROR", out)

    def test_allow_marker_downgrades_new_layer(self) -> None:
        layer = "\n".join(f".row-{i} {{ gap: 8px; }}" for i in range(70))
        write(self.repo, "assets/v6.css", "/* brownfield-allow: tạm thời trong lúc chuyển renderer, gỡ ở bước 3 */\n" + layer + "\n")
        write(self.repo, "assets/base.css", "body { margin: 0; }\n" + OLD_CSS.replace("#333", "#222") + "\n")
        write(self.repo, "app.html", PAGE.format(extra='<link rel="stylesheet" href="assets/v6.css">\n', script=""))
        code, out = self.check()
        self.assertIn("WARNING new-layer", out)
        self.assertNotIn("ERROR   new-layer", out)
        self.assertEqual(code, 0, out)

    def test_bad_base_exits_2(self) -> None:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = overlay_check.main(["--repo", str(self.repo), "--base", "khong-co"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
