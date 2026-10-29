#!/usr/bin/env python3
"""Soát một nhánh redesign xem có đang "phủ đè" lên code cũ thay vì thay thế nó.

Đọc `git diff` giữa nhánh gốc và nhánh redesign của dự án (không phải repo này) và báo:

- `overlay-ratio`  thêm nhiều CSS nhưng gần như không xoá hay sửa dòng CSS cũ nào;
- `new-layer`      file CSS mới lớn được nạp sau các file cũ (lớp đè cuối);
- `important`      tăng ròng nhiều `!important`;
- `dom-patch`      JS mới tìm phần tử đã render rồi chèn hoặc sửa HTML (vá DOM sau render);
- `generated`      sửa file sinh tự động mà không sửa nguồn của nó;
- `untouched-owners` có file CSS cũ trong dự án nhưng không file nào được sửa.

Chỉ dùng thư viện chuẩn. Thoát mã 1 khi có lỗi, 2 khi không chạy được.
Đánh dấu `brownfield-allow: <lý do>` trong file mới để hạ `new-layer`, `dom-patch` xuống cảnh báo.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

STYLE_EXT = {".css", ".scss", ".sass", ".less"}
SCRIPT_EXT = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
MARKUP_EXT = {".html", ".htm", ".vue", ".svelte", ".astro", ".jsx", ".tsx"}
GENERATED_RE = re.compile(r"(?:<!--|/\*|//|^\s*#)[^\n]*(?:generated|do not edit|auto-?generated|không sửa tay)", re.I | re.M)
ALLOW_RE = re.compile(r"brownfield-allow:\s*\S")
DOM_QUERY_RE = re.compile(r"querySelector(All)?\(|getElementsBy\w+\(|getElementById\(")
DOM_WRITE_RE = re.compile(
    r"\.innerHTML\s*=|insertAdjacentHTML\(|\.outerHTML\s*=|MutationObserver|"
    r"\.(appendChild|prepend|append|insertBefore|replaceWith|replaceChildren)\("
)
LINK_RE = re.compile(r"""<link[^>]+href=["']([^"'?#]+)""", re.I)
IMPORT_RE = re.compile(r"""@import\s+(?:url\()?["']?([^"')\s;]+)|import\s+["']([^"']+\.(?:css|scss|less))["']""")


@dataclass
class FileChange:
    path: str
    status: str
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)

    @property
    def ext(self) -> str:
        return Path(self.path).suffix.lower()


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} thất bại")
    return result.stdout


def diff_range(base: str, head: str | None) -> list[str]:
    return [base, head] if head else [base]


def collect(repo: Path, base: str, head: str | None) -> dict[str, FileChange]:
    changes: dict[str, FileChange] = {}
    for line in git(repo, "diff", "--name-status", "--no-renames", *diff_range(base, head)).splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            changes[parts[-1]] = FileChange(parts[-1], parts[0][0])
    current: FileChange | None = None
    patch = git(repo, "diff", "--no-renames", "--unified=0", "--no-color", *diff_range(base, head))
    for line in patch.splitlines():
        if line.startswith("+++ "):
            name = line[4:]
            current = changes.get(name[2:]) if name.startswith("b/") else None
        elif line.startswith("--- "):
            name = line[4:]
            if name.startswith("a/") and name[2:] in changes and changes[name[2:]].status == "D":
                current = changes[name[2:]]
        elif current is not None and line.startswith("+"):
            current.added.append(line[1:])
        elif current is not None and line.startswith("-"):
            current.removed.append(line[1:])
    if head is None:
        # So với cây làm việc: file mới chưa `git add` không có trong diff, tính cả vào.
        for path in git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
            text = (repo / path).read_text(encoding="utf-8", errors="replace")
            changes[path] = FileChange(path, "A", added=text.splitlines())
    return changes


def file_text(repo: Path, rev: str | None, path: str) -> str:
    if rev is None:
        target = repo / path
        return target.read_text(encoding="utf-8", errors="replace") if target.exists() else ""
    try:
        return git(repo, "show", f"{rev}:{path}")
    except RuntimeError:
        return ""


def tracked_files(repo: Path, rev: str) -> list[str]:
    return git(repo, "ls-tree", "-r", "--name-only", rev).splitlines()


def count_important(lines: list[str]) -> int:
    return sum(line.count("!important") for line in lines)


def is_meaningful(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith(("/*", "*", "//"))


def check(repo: Path, base: str, head: str | None, opts: argparse.Namespace) -> list[dict]:
    changes = collect(repo, base, head)
    total_changes = len(changes)
    includes = getattr(opts, "include", [])
    if includes:
        changes = {name: change for name, change in changes.items()
                   if any(name == prefix or name.startswith(prefix.rstrip('/') + '/') for prefix in includes)}
    findings: list[dict] = []

    def add(level: str, rule: str, message: str, path: str | None = None) -> None:
        findings.append({"level": level, "rule": rule, "path": path, "message": message})

    if includes:
        add("info", "scope", f"Chỉ soát {includes}: {len(changes)}/{total_changes} file thay đổi. Không kết luận cho phần ngoài scope.")

    styles = [c for c in changes.values() if c.ext in STYLE_EXT]
    css_added = sum(1 for c in styles for line in c.added if is_meaningful(line))
    css_removed = sum(1 for c in styles if c.status != "A" for line in c.removed if is_meaningful(line))

    # 1. Tỉ lệ thay thế: thêm nhiều mà gần như không xoá/sửa CSS cũ.
    if css_added >= opts.min_added:
        ratio = css_removed / css_added if css_added else 1.0
        if ratio < opts.min_ratio:
            add(
                "error",
                "overlay-ratio",
                f"Thêm {css_added} dòng CSS nhưng chỉ xoá hoặc sửa {css_removed} dòng CSS cũ "
                f"(tỉ lệ {ratio:.2f}, cần ≥ {opts.min_ratio:.2f}). Sửa thẳng ở file đang sở hữu style "
                "và xoá quy tắc bị thay thế thay vì viết lớp mới đè lên.",
            )

    # 2. File CSS mới lớn được nạp sau các file cũ.
    markup_links: dict[str, list[str]] = {}
    head_rev = head
    for path in tracked_files(repo, head_rev or "HEAD") if head_rev else _worktree_files(repo):
        if Path(path).suffix.lower() in MARKUP_EXT | STYLE_EXT | SCRIPT_EXT:
            text = file_text(repo, head_rev, path)
            refs = [m for m in LINK_RE.findall(text)] + [a or b for a, b in IMPORT_RE.findall(text)]
            if refs:
                markup_links[path] = refs
    for change in styles:
        if change.status != "A":
            continue
        size = sum(1 for line in change.added if is_meaningful(line))
        if size < opts.layer_lines:
            continue
        name = Path(change.path).name
        loaders = [
            (src, refs) for src, refs in markup_links.items() if any(Path(r).name == name for r in refs)
        ]
        loaded_last = any(Path(refs[-1]).name == name and len(refs) > 1 for _, refs in loaders if refs)
        allowed = bool(ALLOW_RE.search("\n".join(change.added)))
        if loaded_last:
            add(
                "warning" if allowed else "error",
                "new-layer",
                f"File CSS mới {size} dòng được nạp sau cùng ({', '.join(src for src, _ in loaders)}). "
                "Đây là lớp đè cuối: đưa từng quy tắc về file nguồn đang sở hữu thành phần đó, "
                "hoặc thay hẳn file cũ và gỡ thẻ nạp file cũ.",
                change.path,
            )
        else:
            add(
                "warning",
                "new-layer",
                f"File CSS mới {size} dòng. Ghi trong kế hoạch thay thế file này thay cho file cũ nào.",
                change.path,
            )

    # 3. Tăng ròng !important.
    imp_added = sum(count_important(c.added) for c in styles)
    imp_removed = sum(count_important(c.removed) for c in styles)
    net = imp_added - imp_removed
    if net > opts.max_important:
        add(
            "error",
            "important",
            f"Tăng ròng {net} `!important` (thêm {imp_added}, bỏ {imp_removed}; tối đa {opts.max_important}). "
            "`!important` để thắng cascade cũ là dấu hiệu đang đè chứ không sửa nguồn.",
        )

    # 4. JS mới vá DOM đã render.
    for change in changes.values():
        if change.ext not in SCRIPT_EXT or change.status != "A":
            continue
        body = "\n".join(change.added)
        if DOM_QUERY_RE.search(body) and DOM_WRITE_RE.search(body) and not _looks_like_test(change.path):
            allowed = bool(ALLOW_RE.search(body))
            add(
                "warning" if allowed else "error",
                "dom-patch",
                "File JS mới tìm phần tử đã render rồi chèn hoặc sửa HTML. Sửa ở renderer, template "
                "hoặc component đang sinh ra phần tử đó để markup đúng ngay từ đầu.",
                change.path,
            )

    # 5. Sửa file sinh tự động.
    for change in changes.values():
        if change.status == "A" or not (change.added or change.removed):
            continue
        head_text = file_text(repo, head_rev, change.path)[:600]
        if GENERATED_RE.search(head_text) or any(g in change.path for g in opts.generated):
            add(
                "warning",
                "generated",
                "File này là file sinh tự động. Kiểm tra đã sửa ở nguồn và chạy lại generator, "
                "không sửa tay bản sinh ra.",
                change.path,
            )

    # 6. Có CSS cũ nhưng không đụng vào file nào.
    base_styles = [p for p in tracked_files(repo, base) if Path(p).suffix.lower() in STYLE_EXT]
    touched_old = [c for c in styles if c.status in {"M", "D"}]
    if base_styles and css_added >= opts.min_added and not touched_old:
        add(
            "error",
            "untouched-owners",
            f"Dự án có {len(base_styles)} file CSS cũ nhưng nhánh này không sửa hay xoá file nào. "
            "Redesign phải thay đổi ở nơi đang sở hữu giao diện.",
        )

    findings.append(
        {
            "level": "info",
            "rule": "summary",
            "path": None,
            "message": (
                f"CSS: +{css_added} / -{css_removed} dòng; file CSS sửa {len(touched_old)}, "
                f"thêm {sum(1 for c in styles if c.status == 'A')}, xoá {sum(1 for c in styles if c.status == 'D')}; "
                f"!important ròng {net:+d}."
            ),
        }
    )
    return findings


def _looks_like_test(path: str) -> bool:
    lowered = path.lower()
    return any(part in lowered for part in ("test", "spec", "/qa/", "e2e"))


def _worktree_files(repo: Path) -> list[str]:
    return git(repo, "ls-files", "--cached", "--others", "--exclude-standard").splitlines()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".", help="thư mục git của dự án (mặc định: thư mục hiện tại)")
    parser.add_argument("--base", default="origin/main", help="nhánh hoặc commit gốc trước redesign")
    parser.add_argument("--head", default=None, help="nhánh redesign (bỏ trống: so với cây làm việc hiện tại)")
    parser.add_argument("--include", action="append", default=[], help="scope file/thư mục sản phẩm trong monorepo; lặp để thêm scope, không đổi ngưỡng")
    parser.add_argument("--min-added", type=int, default=80, help="chỉ xét tỉ lệ khi thêm ít nhất N dòng CSS")
    parser.add_argument("--min-ratio", type=float, default=0.3, help="tỉ lệ xoá/thêm CSS tối thiểu")
    parser.add_argument("--layer-lines", type=int, default=60, help="file CSS mới từ N dòng bị xét là lớp")
    parser.add_argument("--max-important", type=int, default=5, help="số !important tăng ròng tối đa")
    parser.add_argument("--generated", action="append", default=[], help="mẫu đường dẫn file sinh tự động")
    parser.add_argument("--json", dest="json_out", help="ghi kết quả JSON ra file")
    opts = parser.parse_args(argv)
    if any(not value or value.startswith(('/', '\\')) or '..' in Path(value).parts or ':' in value for value in opts.include):
        parser.error("--include cần đường dẫn tương đối trong repo")

    repo = Path(opts.repo).resolve()
    try:
        git(repo, "rev-parse", "--verify", opts.base)
        if opts.head:
            git(repo, "rev-parse", "--verify", opts.head)
        findings = check(repo, opts.base, opts.head, opts)
    except RuntimeError as exc:
        print(f"Không chạy được: {exc}", file=sys.stderr)
        return 2

    for item in findings:
        where = f" {item['path']}:" if item["path"] else ""
        print(f"{item['level'].upper():7} {item['rule']}:{where} {item['message']}")
    errors = sum(1 for f in findings if f["level"] == "error")
    warnings = sum(1 for f in findings if f["level"] == "warning")
    print(f"\n{errors} lỗi, {warnings} cảnh báo.")
    if opts.json_out:
        Path(opts.json_out).write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
