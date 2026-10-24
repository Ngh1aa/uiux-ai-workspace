#!/usr/bin/env python3
"""Gom kết quả mọi lần chạy bộ đề chuẩn thành benchmarks/REPORT.md.

Mỗi lần chạy là một thư mục benchmarks/runs/<lần-chạy>/ có:
  checks.json   do run.cjs sinh ra (lỗi, cảnh báo của taste-check)
  scores.json   điểm rubric 10 chiều do người chấm ghi

Dùng:  python3 benchmarks/report.py           ghi lại REPORT.md
       python3 benchmarks/report.py --check   báo lỗi nếu REPORT.md chưa khớp hoặc dữ liệu sai
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
REPORT = ROOT / "REPORT.md"
DIMENSIONS = {
    "1": "Rõ việc",
    "2": "Phân cấp",
    "3": "Bố cục, khoảng cách",
    "4": "Chữ",
    "5": "Màu, tương phản",
    "6": "Nhất quán",
    "7": "Tương tác, phản hồi",
    "8": "Nội dung, câu chữ",
    "9": "Hợp nền tảng, co giãn",
    "10": "Tay nghề, dấu ấn",
}
THRESHOLDS = {"XS": (0, 0), "S": (0, 3), "M": (3.5, 3), "L": (4.0, 3.5), "XL": (4.0, 3.5)}
REVIEWERS = {"agent-heuristic", "expert-review"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(run: Path, scores: dict, checks: dict) -> list[str]:
    errors = []
    if scores.get("reviewer") not in REVIEWERS:
        errors.append(f"{run.name}: reviewer phải là một trong {sorted(REVIEWERS)}")
    for brief, entry in scores.get("briefs", {}).items():
        where = f"{run.name}/{brief}"
        if entry.get("size") not in THRESHOLDS:
            errors.append(f"{where}: size phải là một trong {list(THRESHOLDS)}")
        got = entry.get("scores", {})
        if set(got) != set(DIMENSIONS):
            errors.append(f"{where}: cần đủ điểm 10 chiều, khoá '1' tới '10'")
        if any(not isinstance(v, (int, float)) or not 1 <= v <= 5 for v in got.values()):
            errors.append(f"{where}: mỗi điểm phải từ 1 tới 5")
        if not isinstance(entry.get("hard_fails", []), list):
            errors.append(f"{where}: hard_fails phải là danh sách")
        if brief not in checks.get("briefs", {}):
            errors.append(f"{where}: chưa có trong checks.json, chạy lại run.cjs")
    return errors


def row(run: str, brief: str, entry: dict, check: dict) -> str:
    values = list(entry["scores"].values())
    avg = sum(values) / len(values)
    low = min(values)
    need_avg, need_min = THRESHOLDS[entry["size"]]
    hard = entry.get("hard_fails", [])
    ok = not hard and avg >= need_avg and low >= need_min and check.get("status") == "PASS"
    weakest = ", ".join(DIMENSIONS[k] for k, v in entry["scores"].items() if v == low)
    return (
        f"| {run} | {brief} | {entry['size']} | {check.get('errors', '?')} | {check.get('warnings', '?')} | "
        f"{len(hard)} | {avg:.1f} | {low} ({weakest}) | {'Đạt' if ok else 'Chưa đạt'} |"
    )


def build() -> tuple[str, list[str]]:
    lines = [
        "# Kết quả bộ đề chuẩn",
        "",
        "Sinh tự động bởi `python3 benchmarks/report.py`. Không sửa tay.",
        "",
        "Điểm rubric từ 1 tới 5 theo [quality-bar-rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md).",
        "Cột *Soát* là số lỗi và cảnh báo của `taste-check` trên 390px, 1024px và 1280px, sáng và tối.",
        "",
        "| Lần chạy | Đề | Cỡ | Lỗi soát | Cảnh báo | Hard fail | TB | Thấp nhất | Ngưỡng |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    problems: list[str] = []
    notes: list[str] = []
    runs = sorted(p for p in RUNS.iterdir() if p.is_dir()) if RUNS.exists() else []
    for run in runs:
        scores_path, checks_path = run / "scores.json", run / "checks.json"
        if not scores_path.exists() or not checks_path.exists():
            problems.append(f"{run.name}: cần cả scores.json và checks.json")
            continue
        scores, checks = load(scores_path), load(checks_path)
        problems += validate(run, scores, checks)
        if problems:
            continue
        for brief, entry in sorted(scores["briefs"].items()):
            lines.append(row(run.name, brief, entry, checks["briefs"][brief]))
        notes.append(f"- **{run.name}** ({scores['reviewer']}, repo `{scores.get('repo_commit', '?')}`): {scores.get('summary', '')}")
    if not runs:
        lines.append("| (chưa có lần chạy) | | | | | | | | |")
    lines += ["", "## Ghi chú từng lần chạy", ""] + (notes or ["(chưa có)"]) + [""]
    return "\n".join(lines), problems


def main(argv: list[str]) -> int:
    text, problems = build()
    for problem in problems:
        print(f"ERROR: {problem}")
    if problems:
        return 1
    if "--check" in argv:
        if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != text:
            print("ERROR: REPORT.md chưa khớp dữ liệu, chạy python3 benchmarks/report.py")
            return 1
        print("REPORT.md khớp dữ liệu các lần chạy")
        return 0
    REPORT.write_text(text, encoding="utf-8")
    print(f"đã ghi {REPORT.relative_to(ROOT.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
