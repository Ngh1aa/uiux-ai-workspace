#!/usr/bin/env python3
"""Soát một file thương hiệu (brand.css) trước khi dùng cho khách hàng. Chỉ cần thư viện chuẩn.

    python3 design-system/scripts/check-brand.py <brand.css> [<brand.css> ...]

File thương hiệu ghi đè token ngữ nghĩa của design system bằng mã màu riêng của khách, nên
validate.py không nhìn thấy nó. Script này đọc file đó chồng lên generated/tokens.css giống
trình duyệt (sáng: :root; tối: :root + khối tối) rồi kiểm:

LỖI (thoát với mã 1):
  - mọi cặp chữ/nền trong contrast-pairs.json, cộng các cặp riêng của lớp thương hiệu
    (chữ phụ trên nền chìm, chữ trên nút...), dưới ngưỡng ở chế độ sáng hoặc tối
  - khối tối trong @media (prefers-color-scheme: dark) và khối :root[data-theme="dark"]
    khai báo khác nhau (chép lệch hai lần)
  - giá trị không đọc được thành màu, hoặc var() trỏ tới token không có
CẢNH BÁO:
  - ghi đè một token --ds-* không có trong design system (có thể gõ nhầm tên)
  - viền nút phụ dưới 3:1 so với nền trang (trên card thì là lỗi, theo contrast-pairs.json)
  - chữ mờ nhất (text.tertiary) dưới 4.5:1 trên nền chìm: tránh đặt chữ đó lên nền chìm

Tín hiệu tự động, không thay việc nhìn ảnh chụp và không phải bằng chứng đạt WCAG.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dslib import ROOT, contrast  # noqa: E402

DECL = re.compile(r"(--[a-zA-Z0-9-]+)\s*:\s*([^;]+);")
VAR = re.compile(r"^var\(\s*(--[a-zA-Z0-9-]+)\s*(?:,\s*(.+))?\)$")
HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

# Cặp riêng của lớp thương hiệu: những chỗ starter kit thật sự đặt chữ lên nền.
EXTRA_PAIRS = [
    ("text.tertiary", "surface.raised", 4.5, "chữ phụ trên card"),
    ("text.secondary", "surface.sunken", 4.5, "chữ phụ trên nền chìm"),
    ("text.on-brand-strong", "surface.brand-strong", 4.5, "chữ trên card nổi bật"),
    ("text.brand", "surface.brand-subtle", 4.5, "chữ thương hiệu trên nền nhạt"),
    ("action.primary-text", "action.primary-bg", 4.5, "nhãn nút chính"),
    ("action.primary-text", "action.primary-bg-hover", 4.5, "nhãn nút chính khi rê chuột"),
    ("action.primary-text", "action.primary-bg-pressed", 4.5, "nhãn nút chính khi bấm"),
    ("action.secondary-text", "action.secondary-bg", 4.5, "nhãn nút phụ"),
    ("action.tertiary-text", "surface.raised", 4.5, "nút dạng chữ trên card"),
    ("action.selected-text", "action.selected-bg", 4.5, "mục đang chọn"),
    ("feedback.neutral-text", "feedback.neutral-surface", 4.5, "thông báo trung tính"),
    ("border.focus", "surface.page", 3.0, "viền focus trên nền trang"),
    ("border.focus", "surface.raised", 3.0, "viền focus trên card"),
    ("border.control", "surface.raised", 3.0, "viền ô nhập trên card"),
]
SOFT_PAIRS = [
    ("text.tertiary", "surface.sunken", 4.5, "chữ mờ nhất nếu đặt trên nền chìm"),
    ("action.secondary-border", "surface.page", 3.0, "viền nút phụ đặt thẳng trên nền trang"),
]


def css_var(path: str) -> str:
    return "--ds-" + path.replace(".", "-")


def blocks(css: str) -> dict[str, dict[str, str]]:
    """Tách ba khối: sáng (:root), tối theo hệ điều hành (@media), tối ép bằng data-theme."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = {"light": {}, "dark_media": {}, "dark_attr": {}}
    media = re.search(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{(.*?)\}\s*\}", css, re.S)
    if media:
        out["dark_media"] = dict(DECL.findall(media.group(1)))
        css = css[:media.start()] + css[media.end():]
    attr = re.search(r':root\[data-theme="dark"\]\s*\{(.*?)\}', css, re.S)
    if attr:
        out["dark_attr"] = dict(DECL.findall(attr.group(1)))
        css = css[:attr.start()] + css[attr.end():]
    for body in re.findall(r":root\s*\{(.*?)\}", css, re.S):
        out["light"].update(DECL.findall(body))
    return {k: {n: v.strip() for n, v in d.items()} for k, d in out.items()}


def resolve(name: str, env: dict[str, str], seen: tuple = ()) -> str:
    if name in seen:
        raise ValueError(f"{name}: var() vòng lặp")
    if name not in env:
        raise ValueError(f"{name}: không có token này")
    value = env[name].strip()
    m = VAR.match(value)
    if m:
        try:
            return resolve(m.group(1), env, seen + (name,))
        except ValueError:
            if m.group(2):
                return m.group(2).strip()
            raise
    return value


def to_hex(value: str) -> str:
    m = HEX.match(value)
    if not m:
        raise ValueError(f"'{value}' không phải mã màu hex")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.lower()


def check(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    base = blocks((ROOT / "generated" / "tokens.css").read_text(encoding="utf-8"))
    brand = blocks(path.read_text(encoding="utf-8"))

    if brand["dark_media"] or brand["dark_attr"]:
        a, b = brand["dark_media"], brand["dark_attr"]
        for name in sorted(set(a) | set(b)):
            if a.get(name) != b.get(name):
                errors.append(f"khối tối lệch nhau ở {name}: @media = {a.get(name, '(không có)')}, "
                              f"data-theme = {b.get(name, '(không có)')}")

    known = set(base["light"]) | set(base["dark_media"])
    for name in sorted(set(brand["light"]) | set(brand["dark_media"]) | set(brand["dark_attr"])):
        if name.startswith("--ds-") and name not in known:
            warnings.append(f"{name} không có trong design system (gõ nhầm tên?)")

    modes = {
        "sáng": {**base["light"], **brand["light"]},
        # Khối tối của tokens.css có selector mạnh hơn :root, nên thắng khối sáng của brand.css.
        "tối": {**base["light"], **brand["light"], **base["dark_attr"], **brand["dark_attr"]},
    }
    declared = json.loads((ROOT / "contrast-pairs.json").read_text(encoding="utf-8"))["pairs"]
    pairs = [(p["fg"], p["bg"], float(p["min"]), p.get("why", "")) for p in declared] + EXTRA_PAIRS
    for mode, env in modes.items():
        for group, sink in ((pairs, errors), (SOFT_PAIRS, warnings)):
            for fg, bg, minimum, why in group:
                try:
                    ratio = contrast(to_hex(resolve(css_var(fg), env)), to_hex(resolve(css_var(bg), env)))
                except ValueError as exc:
                    errors.append(f"{mode}: {fg} trên {bg}: {exc}")
                    continue
                if ratio + 1e-9 < minimum:
                    sink.append(f"{mode}: {fg} trên {bg} chỉ {ratio:.2f}:1, cần {minimum:g}:1 ({why})")
    return sorted(set(errors)), sorted(set(warnings))


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    total = 0
    for arg in argv:
        path = Path(arg)
        if not path.is_file():
            print(f"check-brand: không có file {arg}", file=sys.stderr)
            return 2
        errors, warnings = check(path)
        total += len(errors)
        print(f"\n{arg}: {'LỖI' if errors else 'ĐẠT'}")
        for e in errors:
            print(f"  lỗi       {e}")
        for w in warnings:
            print(f"  cảnh báo  {w}")
    print(f"\nTổng: {total} lỗi. Vẫn phải nhìn ảnh chụp trước khi giao.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
