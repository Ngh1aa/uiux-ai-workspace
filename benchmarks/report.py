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
import math
import re
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
RUN_KINDS = {"fresh": "Làm mới", "iterative-repair": "Sửa tiếp", "legacy-unknown": "Chưa rõ"}
BRIEFS = {path.stem for path in (ROOT / "briefs").glob("*.md")}
# Đề thêm sau ghi "**Thêm vào:** YYYY-MM-DD"; lần chạy trước ngày đó không bắt buộc có đề này.
BRIEF_SINCE = {
    path.stem: (m.group(1) if (m := re.search(r"\*\*Thêm vào:\*\*\s*(\d{4}-\d{2}-\d{2})", path.read_text(encoding="utf-8"))) else "0000-00-00")
    for path in (ROOT / "briefs").glob("*.md")
}


def required_briefs(run_name: str) -> set[str]:
    day = run_name[:10]
    return {b for b in BRIEFS if BRIEF_SINCE[b] <= day}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(run: Path, scores: dict, checks: dict) -> list[str]:
    errors = []
    if scores.get("run") != run.name or checks.get("run") != run.name:
        errors.append(f"{run.name}: run phải khớp tên thư mục trong cả scores và checks")
    if scores.get("reviewer") not in REVIEWERS:
        errors.append(f"{run.name}: reviewer phải là một trong {sorted(REVIEWERS)}")
    protocol = scores.get("protocol", {})
    if not isinstance(protocol, dict):
        return errors + [f"{run.name}: protocol phải là object"]
    kind = protocol.get("kind")
    if kind not in RUN_KINDS:
        errors.append(f"{run.name}: protocol.kind phải là fresh, iterative-repair hoặc legacy-unknown")
    if kind == "iterative-repair" and not protocol.get("parent_run"):
        errors.append(f"{run.name}: sửa tiếp phải ghi parent_run")
    if protocol.get("parent_run") == run.name:
        errors.append(f"{run.name}: parent_run không được trỏ tới chính nó")
    if kind == "fresh" and protocol.get("parent_run"):
        errors.append(f"{run.name}: lượt fresh không được sửa tiếp từ parent_run")
    if not isinstance(protocol.get("independent_review"), bool):
        errors.append(f"{run.name}: independent_review phải là boolean")
    for identity in ("author_id", "reviewer_id"):
        if not isinstance(protocol.get(identity), str) or not protocol[identity].strip():
            errors.append(f"{run.name}: protocol.{identity} không được để trống")
    if protocol.get("independent_review") and protocol.get("author_id") == protocol.get("reviewer_id"):
        errors.append(f"{run.name}: người làm không thể tự khai là review độc lập")
    commit = scores.get("repo_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        if not (commit is None and kind != "fresh" and protocol.get("legacy_note")):
            errors.append(f"{run.name}: repo_commit cần SHA đầy đủ; lịch sử thiếu SHA phải ghi null và legacy_note")
    source = checks.get("source")
    if kind == "fresh" and not isinstance(source, dict):
        errors.append(f"{run.name}: lượt fresh cần source do run.cjs ghi trong checks.json")
    if isinstance(source, dict):
        if source.get("repo_commit") != commit:
            errors.append(f"{run.name}: SHA trong scores và checks không khớp")
        if not isinstance(source.get("dirty"), bool):
            errors.append(f"{run.name}: source.dirty phải là boolean")
        if not isinstance(source.get("checker_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", source["checker_sha256"]):
            errors.append(f"{run.name}: cần hash SHA256 của checker đã chạy")
    need = required_briefs(run.name)
    got_scores, got_checks = set(scores.get("briefs", {})), set(checks.get("briefs", {}))
    if not need <= got_scores or not got_scores <= BRIEFS or got_scores != got_checks:
        errors.append(f"{run.name}: scores và checks phải có đủ, đúng bộ đề {sorted(need)}")
    for brief, entry in scores.get("briefs", {}).items():
        where = f"{run.name}/{brief}"
        if entry.get("size") not in THRESHOLDS:
            errors.append(f"{where}: size phải là một trong {list(THRESHOLDS)}")
        got = entry.get("scores", {})
        if set(got) != set(DIMENSIONS):
            errors.append(f"{where}: cần đủ điểm 10 chiều, khoá '1' tới '10'")
        if any(type(v) not in (int, float) or not math.isfinite(v) or not 1 <= v <= 5 for v in got.values()):
            errors.append(f"{where}: mỗi điểm phải từ 1 tới 5")
        if not isinstance(entry.get("hard_fails", []), list):
            errors.append(f"{where}: hard_fails phải là danh sách")
        if brief not in checks.get("briefs", {}):
            errors.append(f"{where}: chưa có trong checks.json, chạy lại run.cjs")
        else:
            check = checks["briefs"][brief]
            if check.get("status") not in {"PASS", "FAIL", "MISSING", "CHECK_FAILED"}:
                errors.append(f"{where}: trạng thái kiểm tra không hợp lệ")
            if check.get("status") in {"PASS", "FAIL"}:
                for count in ("errors", "warnings"):
                    value = check.get(count)
                    if type(value) is not int or value < 0:
                        errors.append(f"{where}: {count} phải là số nguyên không âm")
            if check.get("status") == "PASS" and check.get("errors") != 0:
                errors.append(f"{where}: không được PASS khi có lỗi")
            if source and check.get("status") == "PASS" and check.get("checker_exit_code") != 0:
                errors.append(f"{where}: không được PASS nếu checker chưa thoát thành công")
    return errors


def row(run: str, brief: str, entry: dict, check: dict, protocol: dict) -> str:
    values = list(entry["scores"].values())
    avg = sum(values) / len(values)
    low = min(values)
    need_avg, need_min = THRESHOLDS[entry["size"]]
    hard = entry.get("hard_fails", [])
    ok = not hard and avg >= need_avg and low >= need_min and check.get("status") == "PASS"
    weakest = "mọi chiều" if len(set(values)) == 1 else ", ".join(DIMENSIONS[k] for k, v in entry["scores"].items() if v == low)
    return (
        f"| {run} | {RUN_KINDS[protocol['kind']]} | {'Có' if protocol['independent_review'] else 'Không'} | {brief} | {entry['size']} | {check.get('errors', '?')} | {check.get('warnings', '?')} | "
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
        "Lượt sửa tiếp đo khả năng cải tiến mẫu có sẵn; chỉ lượt làm mới mới dùng để đánh giá chất lượng bản đầu.",
        "Review độc lập là khai báo về người chấm; agent độc lập vẫn là heuristic, không phải người dùng thật.",
        "",
        "| Lần chạy | Kiểu lượt | Review độc lập | Đề | Cỡ | Lỗi soát | Cảnh báo | Hard fail | TB | Thấp nhất | Ngưỡng |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
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
        run_problems = validate(run, scores, checks)
        problems += run_problems
        if run_problems:
            continue
        for brief, entry in sorted(scores["briefs"].items()):
            lines.append(row(run.name, brief, entry, checks["briefs"][brief], scores["protocol"]))
        notes.append(f"- **{run.name}** ({scores['reviewer']}, repo `{scores.get('repo_commit') or 'UNKNOWN'}`): {scores.get('summary', '')}")
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
