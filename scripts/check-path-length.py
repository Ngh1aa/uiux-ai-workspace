#!/usr/bin/env python3
"""Chặn đường dẫn quá dài trong repo.

Windows giới hạn đường dẫn đầy đủ ở 260 ký tự nếu chưa bật long paths. Khi đó `git clone` vẫn chạy
nhưng bỏ qua file dài mà không báo lỗi rõ, và AI đọc repo tưởng skill không tồn tại. Giữ đường dẫn
tương đối trong repo không quá LIMIT ký tự để còn chỗ cho thư mục clone khoảng 150 ký tự.

Dùng: python3 scripts/check-path-length.py [--limit N]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 100


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True).stdout
    return [name for name in out.decode("utf8").split("\0") if name]


def too_long(paths: list[str], limit: int) -> list[str]:
    return sorted((p for p in paths if len(p) > limit), key=len, reverse=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=LIMIT)
    args = parser.parse_args(argv)
    paths = tracked_files()
    errors = too_long(paths, args.limit)
    for path in errors:
        print(f"ERROR: {len(path)} ký tự > {args.limit}: {path}")
    longest = max(paths, key=len) if paths else ""
    print(f"Đã kiểm tra {len(paths)} file, dài nhất {len(longest)} ký tự, {len(errors)} file vượt {args.limit}.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
