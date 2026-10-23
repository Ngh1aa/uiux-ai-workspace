#!/usr/bin/env python3
"""Kiểm tra link nội bộ trong mọi file Markdown của repo.

Báo lỗi khi một link tương đối trỏ tới file hoặc thư mục không còn tồn tại.
Bỏ qua link web, anchor thuần, code block, thư mục vendor/upstream và lịch sử.

Dùng: python3 scripts/check-links.py [thư-mục-gốc]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
SKIP_PARTS = {".git", "node_modules", "vendor", "upstream", "history", "evidence"}
FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def markdown_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.md")
        if not SKIP_PARTS.intersection(path.relative_to(ROOT).parts)
    )


def broken_links(path: Path) -> list[str]:
    text = INLINE_CODE_RE.sub("", FENCE_RE.sub("", path.read_text(encoding="utf-8")))
    errors = []
    for raw in LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("mailto:", "/")):
            continue
        if any(token in target for token in "<>{}"):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: link hỏng -> {raw}")
    return errors


def main() -> int:
    files = markdown_files()
    errors = [error for path in files for error in broken_links(path)]
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Đã kiểm tra {len(files)} file Markdown, {len(errors)} link hỏng.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
