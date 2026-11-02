#!/usr/bin/env python3
"""Đưa ảnh của lần chạy benchmark cũ ra khỏi git, vẫn giữ kiểm chứng được.

Trong repo chỉ giữ ảnh của lần chạy mới nhất. Ảnh lần chạy cũ đóng thành một file zip đính kèm bản
phát hành GitHub (không hết hạn như artifact CI). Lần chạy giữ `images-archive.json`: tên bản phát hành,
SHA-256 của zip và SHA-256 từng ảnh. `report.py --check` và `review-packet.py verify` chấp nhận ảnh vắng
mặt khi hash của nó khớp bản ghi này; `verify` tải zip về và so từng byte.

Dùng:
  python3 benchmarks/archive.py pack <run> --tag benchmark-images-<run>   # tạo zip + images-archive.json, xoá ảnh
  gh release create <tag> <zip> ...                                       # đăng zip (in ra lệnh cụ thể)
  python3 benchmarks/archive.py verify <run> [--zip <file>]               # so hash với zip, bản phát hành, hoặc lịch sử git
  python3 benchmarks/archive.py policy                                     # chỉ lần chạy mới nhất còn ảnh trong git
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "benchmarks" / "runs"
REPO = "Ngh1aa/uiux-ai-workspace"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def images_of(run: Path) -> list[Path]:
    return sorted(p for p in run.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)


def pack(args: argparse.Namespace) -> int:
    run = RUNS / args.run
    images = images_of(run)
    if not images:
        print(f"{run} không còn ảnh nào để đóng gói", file=sys.stderr)
        return 1
    out = Path(args.out or f"/tmp/{args.tag}.zip")
    files = {}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as zf:
        for img in images:
            rel = img.relative_to(run).as_posix()
            data = img.read_bytes()
            files[rel] = sha256(data)
            info = zipfile.ZipInfo(rel, date_time=(2026, 1, 1, 0, 0, 0))
            zf.writestr(info, data)
    index = {
        "note": "Ảnh của lần chạy này nằm trong bản phát hành GitHub, không nằm trong git. Kiểm: python3 benchmarks/archive.py verify " + args.run,
        "release": args.tag,
        "asset": out.name,
        "url": f"https://github.com/{REPO}/releases/download/{args.tag}/{out.name}",
        "asset_sha256": sha256(out.read_bytes()),
        "files": files,
    }
    (run / "images-archive.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not args.keep:
        for img in images:
            img.unlink()
    print(f"{len(files)} ảnh -> {out} ({out.stat().st_size // 1024} KB)")
    print(f"đăng: gh release create {args.tag} {out} --repo {REPO} --title '{args.tag}' --notes 'Ảnh benchmark {args.run}, xem benchmarks/archive.py'")
    return 0


def verify(args: argparse.Namespace) -> int:
    run = RUNS / args.run
    index = json.loads((run / "images-archive.json").read_text(encoding="utf-8"))
    if args.zip:
        data = Path(args.zip).read_bytes()
    elif not index.get("url"):
        return verify_from_git(run, index)
    else:
        with urllib.request.urlopen(index["url"]) as resp:  # noqa: S310 (fixed GitHub release URL)
            data = resp.read()
    errors = []
    if sha256(data) != index["asset_sha256"]:
        errors.append("zip lệch asset_sha256")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
        for rel, digest in index["files"].items():
            if rel not in names:
                errors.append(f"thiếu {rel}")
            elif sha256(zf.read(rel)) != digest:
                errors.append(f"lệch hash {rel}")
    for e in errors:
        print("LỖI:", e, file=sys.stderr)
    print(f"{args.run}: {len(index['files'])} ảnh, {len(errors)} lỗi")
    return 1 if errors else 0


def verify_from_git(run: Path, index: dict) -> int:
    """Chưa đăng bản phát hành: so hash với bản gốc trong lịch sử git (source_commit)."""
    import subprocess
    errors = []
    for rel, digest in index["files"].items():
        path = f"{run.relative_to(ROOT).as_posix()}/{rel}"
        res = subprocess.run(["git", "-C", str(ROOT), "show", f"{index['source_commit']}:{path}"], capture_output=True)
        if res.returncode or sha256(res.stdout) != digest:
            errors.append(f"không lấy được hoặc lệch hash {rel}")
    for e in errors:
        print("LỖI:", e, file=sys.stderr)
    print(f"{run.name}: {len(index['files'])} ảnh (từ git {index['source_commit'][:7]}), {len(errors)} lỗi")
    return 1 if errors else 0


def policy(_: argparse.Namespace) -> int:
    runs = sorted(p for p in RUNS.iterdir() if p.is_dir())
    errors = []
    for run in runs[:-1]:
        if images_of(run):
            errors.append(f"{run.name}: lần chạy cũ còn ảnh trong git; chạy archive.py pack")
    for e in errors:
        print("LỖI:", e, file=sys.stderr)
    print(f"chỉ {runs[-1].name} giữ ảnh trong git" if not errors else f"{len(errors)} lỗi")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pack"); p.add_argument("run"); p.add_argument("--tag", required=True); p.add_argument("--out"); p.add_argument("--keep", action="store_true")
    p.set_defaults(func=pack)
    v = sub.add_parser("verify"); v.add_argument("run"); v.add_argument("--zip"); v.set_defaults(func=verify)
    sub.add_parser("policy").set_defaults(func=policy)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
