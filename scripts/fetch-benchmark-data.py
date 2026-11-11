#!/usr/bin/env python3
"""Lấy dữ liệu bộ đề chuẩn từ nhánh benchmarks-data về cây làm việc.

`main` chỉ giữ code, đề và REPORT.md. Ảnh, điểm và bằng chứng của các lần chạy
(`benchmarks/runs/`, `benchmarks/evidence/`, `benchmarks/trials/`) nằm ở nhánh
`benchmarks-data`. File `benchmarks/data-ref.txt` ghi đúng commit dữ liệu mà `main`
dùng, nên CI và máy cá nhân luôn kiểm cùng một bộ dữ liệu.

Script giải nén đúng từng byte (không đổi xuống dòng theo core.autocrlf), vì
checks.json, review.json và images-archive.json ràng file bằng SHA-256.

Dùng: python3 scripts/fetch-benchmark-data.py [--ref <commit>] [--remote origin]
"""
from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF_FILE = ROOT / "benchmarks" / "data-ref.txt"
BRANCH = "benchmarks-data"
DATA_DIRS = ("benchmarks/runs", "benchmarks/evidence", "benchmarks/trials")


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=check)


def pinned_ref() -> str:
    for line in REF_FILE.read_text(encoding="utf8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    raise SystemExit(f"{REF_FILE.relative_to(ROOT)} không có commit")


def ensure_commit(ref: str, remote: str) -> None:
    if git("cat-file", "-e", f"{ref}^{{commit}}", check=False).returncode == 0:
        return
    for args in (["fetch", "--depth=1", remote, ref], ["fetch", remote, BRANCH]):
        if git(*args, check=False).returncode == 0 and git("cat-file", "-e", f"{ref}^{{commit}}", check=False).returncode == 0:
            return
    raise SystemExit(f"Không lấy được commit {ref} từ {remote} (nhánh {BRANCH})")


def extract(ref: str) -> int:
    archive = git("-c", "core.autocrlf=false", "-c", "core.eol=lf", "archive", "--format=tar", ref, *DATA_DIRS).stdout
    for name in DATA_DIRS:
        shutil.rmtree(ROOT / name, ignore_errors=True)
    count = 0
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            if member.isdir() or member.type == tarfile.XGLTYPE:
                continue
            target = (ROOT / member.name).resolve()
            if not member.name.startswith(tuple(d + "/" for d in DATA_DIRS)) or ROOT.resolve() not in target.parents:
                raise SystemExit(f"Đường dẫn lạ trong dữ liệu: {member.name}")
            if not member.isfile():
                raise SystemExit(f"Dữ liệu chỉ được có file thường: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ref", help="commit dữ liệu; mặc định đọc benchmarks/data-ref.txt")
    parser.add_argument("--remote", default="origin")
    args = parser.parse_args(argv)
    ref = args.ref or pinned_ref()
    ensure_commit(ref, args.remote)
    count = extract(ref)
    print(f"Đã lấy {count} file dữ liệu benchmark từ {ref[:12]} vào {', '.join(DATA_DIRS)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
