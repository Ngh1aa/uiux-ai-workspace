#!/usr/bin/env python3
"""Đóng gói hồ sơ cho người duyệt độc lập: chỉ ảnh chụp, brief và rubric, không có code.

Người duyệt (người ngoài hoặc một agent ở phiên mới) chỉ được mở thư mục hồ sơ. Không thấy HTML, CSS,
ghi chú của người làm hay điểm tự chấm, nên không bị neo theo lập luận của người làm.

Tạo hồ sơ:
    python3 scripts/review-packet.py make --shots qa/ --brief brief.md --size M --out review/
Kiểm kết quả người duyệt trả về:
    python3 scripts/review-packet.py verify review/

Thư mục hồ sơ gồm:
    images/                ảnh chụp (png, jpg, webp), tên giữ nguyên
    brief.md               bản sao brief
    rubric.md              bản sao rubric chất lượng
    REVIEWER.md            hướng dẫn hai vòng: đọc lạnh (chỉ ảnh), rồi chấm theo brief và rubric
    manifest.json          SHA-256 từng ảnh, cỡ việc, thời điểm tạo
    review.template.json   mẫu kết quả cần điền thành review.json

Chỉ dùng thư viện chuẩn của Python.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / "skills_UIUX" / "design-critique-and-rationale" / "references" / "quality-bar-rubric.md"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
SIZES = ("XS", "S", "M", "L", "XL")
THRESHOLDS = {"XS": (0, 0), "S": (0, 3), "M": (3.5, 3), "L": (4.0, 3.5), "XL": (4.0, 3.5)}
# Ngưỡng riêng theo chiều (quality-bar-rubric.md): XL cần chiều 6 ≥ 4.
DIMENSION_FLOORS = {"XL": {"6": 4}}
DIMENSIONS = [str(i) for i in range(1, 11)]
HARD_FAILS = {f"HF-{i}" for i in range(1, 11)}
COLD_QUESTIONS = [
    "Màn này để làm gì?",
    "Bạn sẽ bấm vào đâu đầu tiên?",
    "Điều gì trông sai, rối hoặc thiếu?",
]

REVIEWER = """# Hướng dẫn người duyệt

Bạn duyệt một thiết kế mà không biết người làm nghĩ gì. Chỉ dùng các file trong thư mục này.
**Không mở** repo, mã HTML hay CSS, ghi chú hay điểm tự chấm của người làm, kể cả khi có quyền.

## Vòng 1: đọc lạnh (chưa mở brief)

Mở lần lượt các ảnh trong `images/`. Với mỗi ảnh, trả lời ba câu, mỗi câu một đến hai dòng:

{questions}

Ghi câu trả lời vào `cold` trong `review.json` trước khi đọc brief. Không sửa lại sau khi đọc brief.

## Vòng 2: chấm theo brief và rubric

1. Đọc `brief.md`, rồi `rubric.md`.
2. Soát từng hard fail (HF-1 tới HF-10). Hard fail nào thấy được trên ảnh thì ghi mã, ảnh, và điều thấy.
   Điều không kiểm được từ ảnh (bàn phím, trình đọc màn hình, chữ phóng to) ghi vào `not_checked`.
3. Chấm 10 chiều, từ 1 tới 5. Mỗi điểm dưới 4 cần ít nhất một ghi nhận: chiều, ảnh, phần tử, cách sửa.
4. Ngưỡng của cỡ việc **{size}**: {threshold}.

## Trả về

Chép `review.template.json` thành `review.json`, điền đủ, rồi người làm chạy:

```sh
python3 scripts/review-packet.py verify <thư mục này>
```

Ghi `reviewer.kind` là `expert-review` nếu bạn là người ngoài nhóm làm, `agent-heuristic` nếu bạn là
agent. Agent ở phiên độc lập vẫn là `agent-heuristic`, nhưng được ghi `independent: true`.
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def threshold_text(size: str) -> str:
    avg, floor = THRESHOLDS[size]
    if size == "XS":
        return "không hard fail trên màn bị ảnh hưởng"
    if size == "S":
        return "không hard fail, các chiều liên quan ≥ 3"
    extra = "".join(f", chiều {d} ≥ {v}" for d, v in DIMENSION_FLOORS.get(size, {}).items())
    return f"không hard fail, trung bình ≥ {avg}, không chiều nào < {floor}{extra}"


def make(args: argparse.Namespace) -> int:
    shots = Path(args.shots)
    images = sorted(p for p in shots.rglob("*") if p.suffix.lower() in IMAGE_EXT)
    if not images:
        print(f"không tìm thấy ảnh trong {shots}", file=sys.stderr)
        return 1
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        if not args.force:
            print(f"{out} đã có nội dung; thêm --force để ghi đè", file=sys.stderr)
            return 1
        if not (out / "manifest.json").exists():
            print(f"{out} không phải hồ sơ duyệt (thiếu manifest.json); không xoá", file=sys.stderr)
            return 1
        # Xoá sạch hồ sơ cũ: người duyệt mới không được thấy review.json hay ảnh của lượt trước.
        shutil.rmtree(out)
    (out / "images").mkdir(parents=True, exist_ok=True)
    manifest = {"created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "size": args.size, "images": {}}
    for img in images:
        # Tên theo đường dẫn tương đối để ảnh cùng tên ở thư mục con khác nhau không đè nhau.
        base = "-".join(img.relative_to(shots).parts)
        name, n = base, 2
        while name in manifest["images"]:
            name, n = f"{Path(base).stem}-{n}{Path(base).suffix}", n + 1
        shutil.copy2(img, out / "images" / name)
        manifest["images"][name] = sha256(out / "images" / name)
    shutil.copy2(args.brief, out / "brief.md")
    shutil.copy2(RUBRIC, out / "rubric.md")
    questions = "\n".join(f"{i}. {q}" for i, q in enumerate(COLD_QUESTIONS, 1))
    (out / "REVIEWER.md").write_text(REVIEWER.format(questions=questions, size=args.size, threshold=threshold_text(args.size)), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template = {
        "reviewer": {"id": "", "kind": "agent-heuristic | expert-review", "independent": True},
        "cold": {name: {q: "" for q in COLD_QUESTIONS} for name in manifest["images"]},
        "hard_fails": [{"code": "HF-n", "image": "", "observation": ""}],
        "scores": {d: 0 for d in DIMENSIONS},
        "observations": [{"dimension": "1-10", "image": "", "element": "", "fix": ""}],
        "not_checked": ["bàn phím", "trình đọc màn hình", "chữ phóng 200%"],
    }
    (out / "review.template.json").write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"đã tạo hồ sơ {out} với {len(images)} ảnh, cỡ {args.size}")
    return 0


def verify(args: argparse.Namespace) -> int:
    packet = Path(args.packet)
    errors: list[str] = []
    try:
        manifest = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))
        review = json.loads((packet / "review.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"không đọc được hồ sơ: {exc}", file=sys.stderr)
        return 1
    images = manifest.get("images", {})
    for name, digest in images.items():
        path = packet / "images" / name
        if not path.exists() or sha256(path) != digest:
            errors.append(f"ảnh {name} bị đổi hoặc mất sau khi tạo hồ sơ")

    reviewer = review.get("reviewer", {})
    if not reviewer.get("id"):
        errors.append("thiếu reviewer.id")
    if reviewer.get("kind") not in {"agent-heuristic", "expert-review"}:
        errors.append("reviewer.kind phải là agent-heuristic hoặc expert-review")
    if not isinstance(reviewer.get("independent"), bool):
        errors.append("reviewer.independent phải là true hoặc false")

    cold = review.get("cold", {})
    for name in images:
        answers = cold.get(name, {})
        if any(not str(answers.get(q, "")).strip() for q in COLD_QUESTIONS):
            errors.append(f"vòng đọc lạnh thiếu câu trả lời cho {name}")

    hard = review.get("hard_fails", [])
    if not isinstance(hard, list):
        errors.append("hard_fails phải là danh sách (rỗng nếu không có)")
        hard = []
    for item in hard:
        if item.get("code") not in HARD_FAILS or item.get("image") not in images or not str(item.get("observation", "")).strip():
            errors.append(f"hard fail không hợp lệ: {item}")

    scores = review.get("scores", {})
    if set(scores) != set(DIMENSIONS) or any(not isinstance(v, (int, float)) or not 1 <= v <= 5 for v in scores.values()):
        errors.append("scores cần đủ 10 chiều, mỗi chiều từ 1 tới 5")
    else:
        notes = review.get("observations", [])
        for dim, value in scores.items():
            if value < 4 and not any(str(o.get("dimension")) == dim and o.get("image") in images and str(o.get("fix", "")).strip() for o in notes):
                errors.append(f"chiều {dim} được {value} điểm nhưng không có ghi nhận kèm ảnh và cách sửa")

    if errors:
        for e in errors:
            print(f"LỖI: {e}")
        return 1

    size = manifest.get("size", "M")
    avg = sum(scores.values()) / len(scores)
    need_avg, floor = THRESHOLDS[size]
    dims_ok = all(scores[d] >= v for d, v in DIMENSION_FLOORS.get(size, {}).items())
    passed = not hard and avg >= need_avg and min(scores.values()) >= floor and dims_ok
    print(f"hồ sơ hợp lệ: {len(images)} ảnh, {len(hard)} hard fail, trung bình {avg:.2f}, thấp nhất {min(scores.values())}")
    print(f"ngưỡng cỡ {size}: {'ĐẠT' if passed else 'CHƯA ĐẠT'}  (người duyệt: {reviewer['kind']}, độc lập: {reviewer['independent']})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="tạo hồ sơ duyệt")
    m.add_argument("--shots", required=True, help="thư mục ảnh chụp, ví dụ đầu ra --screenshot của taste-check")
    m.add_argument("--brief", required=True, help="file brief")
    m.add_argument("--size", choices=SIZES, default="M", help="cỡ việc theo WORKFLOWS.md")
    m.add_argument("--out", required=True, help="thư mục hồ sơ")
    m.add_argument("--force", action="store_true", help="ghi vào thư mục đã có nội dung")
    v = sub.add_parser("verify", help="kiểm review.json trong hồ sơ")
    v.add_argument("packet")
    args = ap.parse_args()
    return make(args) if args.cmd == "make" else verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
