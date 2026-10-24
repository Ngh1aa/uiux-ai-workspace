#!/usr/bin/env python3
"""Nhúng đúng những icon một trang đang dùng vào chính trang đó.

Trang dùng icon bằng <use href="#ds-i-..."/> hoặc <use href="#app-i-..."/>. Script tìm các id đó
trong components/icons.svg và starter/icons-app.svg, rồi ghi một sprite ẩn vào chỗ đánh dấu
<!--SPRITE--> hoặc thay khối giữa <!-- icons:start --> và <!-- icons:end -->.

Nhúng thẳng vào trang để icon vẫn hiện khi mở file trực tiếp hoặc chép trang sang nơi khác.

Dùng:  python3 design-system/starter/inline-icons.py <trang.html> [...]
       python3 design-system/starter/inline-icons.py --check <trang.html> [...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = [HERE.parent / "components" / "icons.svg", HERE / "icons-app.svg"]
SYMBOL_RE = re.compile(r'<symbol id="([^"]+)".*?</symbol>', re.S)
USE_RE = re.compile(r'<use href="#([a-z0-9-]+)"')
BLOCK_RE = re.compile(r"<!-- icons:start -->.*?<!-- icons:end -->", re.S)


def load_symbols() -> dict[str, str]:
    symbols: dict[str, str] = {}
    for source in SOURCES:
        for match in SYMBOL_RE.finditer(source.read_text(encoding="utf-8")):
            symbols[match.group(1)] = match.group(0)
    return symbols


def render(html: str, symbols: dict[str, str]) -> str:
    used = sorted(set(USE_RE.findall(html)))
    missing = [name for name in used if name not in symbols]
    if missing:
        raise SystemExit(f"không có icon: {', '.join(missing)}")
    body = "\n".join(f"  {symbols[name]}" for name in used)
    block = (
        "<!-- icons:start -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">\n'
        f"{body}\n</svg>\n<!-- icons:end -->"
    )
    if BLOCK_RE.search(html):
        return BLOCK_RE.sub(lambda _: block, html, count=1)
    if "<!--SPRITE-->" in html:
        return html.replace("<!--SPRITE-->", block, 1)
    raise SystemExit("trang chưa có chỗ đánh dấu <!--SPRITE--> hoặc khối icons:start/icons:end")


def main(argv: list[str]) -> int:
    check = "--check" in argv
    pages = [Path(arg) for arg in argv if arg != "--check"]
    if not pages:
        print(__doc__)
        return 2
    symbols = load_symbols()
    stale = []
    for page in pages:
        html = page.read_text(encoding="utf-8")
        new = render(html, symbols)
        if new != html:
            if check:
                stale.append(str(page))
            else:
                page.write_text(new, encoding="utf-8")
                print(f"đã cập nhật icon: {page}")
    if stale:
        print("icon nhúng chưa khớp, chạy lại inline-icons.py cho: " + ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
