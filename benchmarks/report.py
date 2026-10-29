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
import hashlib
import subprocess
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
    reviewer_ids = protocol.get("reviewer_ids")
    if reviewer_ids is not None:
        if not isinstance(reviewer_ids, dict) or set(reviewer_ids) != set(scores.get("briefs", {})) or any(not isinstance(v, str) or not v.strip() or v == protocol.get("author_id") for v in reviewer_ids.values()):
            errors.append(f"{run.name}: reviewer_ids phải ghi đúng người duyệt độc lập cho từng đề")
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
            if check.get("status") not in {"PASS", "FAIL", "MISSING", "CHECK_FAILED", "UNKNOWN"}:
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
    if checks.get("version") == 2:
        errors.extend(validate_evidence(run, scores, checks))
    return errors


def checked_file(run: Path, record: dict, path_key="path") -> Path | None:
    """No traversal or claimed hash without its actual evidence file."""
    raw = record.get(path_key)
    if not isinstance(raw, str):
        return None
    file = (run / raw).resolve()
    if not file.is_relative_to(run.resolve()) or not file.is_file():
        return None
    return file if hashlib.sha256(file.read_bytes()).hexdigest() == record.get("sha256") else None


def validate_evidence(run: Path, scores: dict, checks: dict) -> list[str]:
    errors = []
    source = checks.get("source", {})
    for field in ("patch", "manifest"):
        if not checked_file(run, source.get(field, {})):
            errors.append(f"{run.name}: thiếu hoặc lệch hash provenance {field}")
    manifest_path = checked_file(run, source.get("manifest", {}))
    if manifest_path:
        manifest = load(manifest_path)
        if manifest.get("baseline_commit") != source.get("repo_commit") or manifest.get("patch_sha256") != source.get("patch", {}).get("sha256") or not manifest.get("files"):
            errors.append(f"{run.name}: manifest không gắn với baseline/patch/toolkit files")
    if set(source.get("checkers", {})) != {"render", "static", "flow"} or any(not re.fullmatch(r"[0-9a-f]{64}", str(v)) for v in source.get("checkers", {}).values()):
        errors.append(f"{run.name}: cần hash ba checker riêng")
    script = run / "flow.browser.cjs"
    if not script.exists() or hashlib.sha256(script.read_bytes()).hexdigest() != source.get("browser_test_sha256"):
        errors.append(f"{run.name}: thiếu hoặc lệch hash source test hành vi")
    for name, digest in {**source.get("run_files", {}), **source.get("images", {})}.items():
        if not checked_file(run, {"path": name, "sha256": digest}):
            errors.append(f"{run.name}: source/ảnh đã đổi sau kiểm: {name}")
    for brief, check in checks.get("briefs", {}).items():
        if check.get("status") == "MISSING":
            continue
        where = f"{run.name}/{brief}"
        render, flow = check.get("render", {}), check.get("flow", {})
        if not checked_file(run, render, "evidence"):
            errors.append(f"{where}: render thiếu hoặc lệch hash evidence")
        static = flow.get("static", {})
        static_path = checked_file(run, static, "evidence")
        if not static_path:
            errors.append(f"{where}: static flow thiếu hoặc lệch hash evidence")
        elif static.get("status") == "PASS" and load(static_path).get("errorCount") != 0:
            errors.append(f"{where}: static flow có lỗi nhưng khai PASS")
        browser = flow.get("browser", {})
        if browser.get("status") == "PASS":
            if not checked_file(run, browser, "evidence"):
                errors.append(f"{where}: browser PASS thiếu hoặc lệch hash evidence")
            scenarios = browser.get("scenarios", [])
            if not scenarios or any(item.get("status") != "PASS" for item in scenarios):
                errors.append(f"{where}: browser PASS nhưng scenario thiếu/chưa đạt")
            runtime_path = checked_file(run, browser, "evidence")
            if runtime_path:
                actual = load(runtime_path).get("briefs", {}).get(brief, {})
                if actual.get("status") != "PASS" or actual.get("scenarios") != scenarios:
                    errors.append(f"{where}: browser status/scenarios không khớp kết quả thật")
        expected_flow = "FAIL" if "FAIL" in (flow.get("static", {}).get("status"), browser.get("status")) else "PASS" if flow.get("static", {}).get("status") == browser.get("status") == "PASS" else "UNKNOWN"
        if flow.get("status") != expected_flow:
            errors.append(f"{where}: flow status không khớp các lớp")
        if check.get("status") == "PASS" and (flow.get("status") != "PASS" or render.get("status") != "PASS"):
            errors.append(f"{where}: không được PASS khi flow/render chưa đạt")
        sample = check.get("sample", {})
        if not sample.get("source") or not sample.get("files"):
            errors.append(f"{where}: cần nguồn mẫu và hash files")
        for name, digest in sample.get("files", {}).items():
            if not checked_file(run, {"path": name, "sha256": digest}):
                errors.append(f"{where}: mẫu đã đổi sau đánh giá: {name}")
        if brief == "05-native" and flow.get("native_status") != "UNKNOWN":
            errors.append(f"{where}: trình duyệt không chứng minh native")
        if scores.get("protocol", {}).get("independent_review"):
            entry = scores.get("briefs", {}).get(brief, {})
            review_path = checked_file(run, entry.get("review", {}))
            if not review_path:
                errors.append(f"{where}: độc lập cần review.json có hash")
                continue
            review = load(review_path)
            packet_manifest = load(review_path.parent / "manifest.json")
            evaluated_images = set(source.get("images", {}).values())
            if not packet_manifest.get("images") or not set(packet_manifest["images"].values()) <= evaluated_images:
                errors.append(f"{where}: review ảnh không thuộc lần render đã kiểm")
            # Snapshot integrity remains byte-hashed; canonical Git checkouts may
            # use LF while the reviewed Windows snapshot used CRLF. Only universal
            # newline conversion is allowed here, never whitespace/content edits.
            if (review_path.parent / "brief.md").read_text(encoding="utf8") != (ROOT / "briefs" / (brief + ".md")).read_text(encoding="utf8"):
                errors.append(f"{where}: review dùng sai brief")
            identity = review.get("reviewer", {})
            if identity.get("id") != scores["protocol"].get("reviewer_ids", {}).get(brief, scores["protocol"].get("reviewer_id")) or identity.get("independent") is not True or entry.get("scores") != review.get("scores") or entry.get("hard_fails") != [item["code"] for item in review.get("hard_fails", [])]:
                errors.append(f"{where}: reviewer/điểm/hard-fails không khớp review thật")
            verification = subprocess.run([sys.executable, str(ROOT.parent / "scripts/review-packet.py"), "verify", str(review_path.parent)], capture_output=True, encoding="utf8")
            if verification.returncode:
                errors.append(f"{where}: review packet không hợp lệ: {verification.stdout.strip()}")
    return errors


def row(run: str, brief: str, entry: dict, check: dict, protocol: dict) -> str:
    values = list(entry["scores"].values())
    avg = sum(values) / len(values)
    low = min(values)
    need_avg, need_min = THRESHOLDS[entry["size"]]
    hard = entry.get("hard_fails", [])
    flow_status = check.get("flow", {}).get("status", "UNKNOWN")
    render_status = check.get("render", {}).get("status", check.get("status", "UNKNOWN"))
    rubric_ok = not hard and avg >= need_avg and low >= need_min
    ok = rubric_ok and render_status == flow_status == "PASS"
    verdict = ("Đạt (browser)" if brief == "05-native" else "Đạt") if ok else "UNKNOWN" if flow_status == "UNKNOWN" and rubric_ok and render_status == "PASS" else "Chưa đạt"
    weakest = "mọi chiều" if len(set(values)) == 1 else ", ".join(DIMENSIONS[k] for k, v in entry["scores"].items() if v == low)
    sample_source = check.get("sample", {}).get("source", {})
    kind_label = "Đề mới (tái dùng)" if isinstance(sample_source, dict) and sample_source.get("kind") == "reuse-new-brief" else RUN_KINDS[protocol['kind']]
    return (
        f"| {run} | {kind_label} | {'Có' if protocol['independent_review'] else 'Không'} | {brief} | {entry['size']} | {check.get('errors', '?')} | {check.get('warnings', '?')} | "
        f"{flow_status} | {len(hard)} | {avg:.2f} | {low} ({weakest}) | {verdict} |"
    )


def build() -> tuple[str, list[str]]:
    lines = [
        "# Kết quả bộ đề chuẩn",
        "",
        "Sinh tự động bởi `python3 benchmarks/report.py`. Không sửa tay.",
        f"Generator SHA256: `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`.",
        "",
        "Điểm rubric từ 1 tới 5 theo [quality-bar-rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md).",
        "Cột *Soát* là lỗi/cảnh báo render; lượt mới kiểm 390/1024/1280/1440px sáng/tối và reflow 320px. Đề 04 thêm layout strict.",
        "Lượt sửa tiếp đo khả năng cải tiến mẫu có sẵn; chỉ lượt làm mới mới dùng để đánh giá chất lượng bản đầu.",
        "Review độc lập lượt mới gắn với packet/ảnh/điểm có hash; agent độc lập vẫn là heuristic, không phải người dùng thật.",
        "",
        "| Lần chạy | Kiểu lượt | Review độc lập | Đề | Cỡ | Lỗi soát | Cảnh báo | Luồng | Hard fail | TB | Thấp nhất | Ngưỡng |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
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
        if checks.get("version") != 2:
            notes.append(f"- **{run.name}**: bằng chứng luồng/provenance/review lịch sử `UNKNOWN`; giữ nguyên điểm và kết luận gốc trong scores.json, bảng hiện tại không suy Đạt.")
        else:
            patch_hash = checks.get("source", {}).get("manifest", {}).get("sha256", "UNKNOWN")
            notes.append(f"- **{run.name}**: code local chưa commit, manifest `{patch_hash}`; native của đề 05 `UNKNOWN` (browser-only).")
        label = "Ghi chú gốc lịch sử, chưa tái kiểm" if checks.get("version") != 2 else "Ghi chú lượt mới"
        notes.append(f"- **{run.name}** ({scores['reviewer']}, repo `{scores.get('repo_commit') or 'UNKNOWN'}`), {label}: {scores.get('summary', '')}")
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
