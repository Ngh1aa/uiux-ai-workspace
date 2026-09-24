#!/usr/bin/env python3
"""Visual quality deterministic grader for skills_UIUX V5.1.

Two-stage grading:
  1. Deterministic gates (pass/fail) — machine verifiable.
  2. Rubric template output — for model/human scoring.

Does NOT judge typography, hierarchy, brand or composition quality.
Those dimensions require rendered evidence + model/human judgment.
See evals/visual-quality-rubric.md for the full 7-dimension rubric.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

VIEWPORT_META = re.compile(
    r'<meta[^>]*name\s*=\s*["\']viewport["\'][^>]*>',
    re.IGNORECASE,
)
IMG_SRC = re.compile(r'<img[^>]*src\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
OVERFLOW_HINT = re.compile(
    r'overflow-x\s*:\s*hidden|overflow\s*:\s*hidden',
    re.IGNORECASE,
)


def check_page(name: str, html: str, page_dir: Path | None = None) -> dict[str, Any]:
    """Run deterministic gates on a single page."""
    gates: dict[str, bool] = {}
    issues: list[str] = []

    # Gate: page has content
    stripped = re.sub(r'<[^>]+>', '', html).strip()
    has_content = len(stripped) > 50
    gates["has_content"] = has_content
    if not has_content:
        issues.append(f"{name}: page appears empty or near-empty")

    # Gate: viewport meta
    has_viewport = bool(VIEWPORT_META.search(html))
    gates["viewport_meta"] = has_viewport
    if not has_viewport:
        issues.append(f"{name}: missing viewport meta tag")

    # Gate: no obvious broken images (src="" or src="#")
    img_srcs = IMG_SRC.findall(html)
    broken_srcs = [s for s in img_srcs if not s or s == "#" or s == "about:blank"]
    gates["no_broken_img_src"] = len(broken_srcs) == 0
    if broken_srcs:
        issues.append(f"{name}: {len(broken_srcs)} image(s) with empty/broken src")

    # Gate: basic HTML structure
    has_html_tag = "<html" in html.lower()
    has_body_tag = "<body" in html.lower()
    gates["html_structure"] = has_html_tag and has_body_tag
    if not (has_html_tag and has_body_tag):
        issues.append(f"{name}: missing basic HTML structure")

    all_passed = all(gates.values())
    return {
        "page": name,
        "gates": gates,
        "all_passed": all_passed,
        "issues": issues,
    }


def generate_rubric_template(pages: list[str]) -> dict[str, Any]:
    """Generate a rubric scoring template for model/human evaluation."""
    dimensions = [
        {"name": "hierarchy_and_ia", "label": "Hierarchy & information architecture", "weight": 0.20},
        {"name": "typography", "label": "Typography system", "weight": 0.15},
        {"name": "media_art_direction", "label": "Media & art direction", "weight": 0.15},
        {"name": "page_role_diversity", "label": "Page-role diversity", "weight": 0.15},
        {"name": "responsive", "label": "Responsive transformation", "weight": 0.10},
        {"name": "brand_distinctiveness", "label": "Brand distinctiveness", "weight": 0.15},
        {"name": "anti_generic_ai", "label": "Anti-generic-AI", "weight": 0.10},
    ]

    hard_fails = [
        "all_pages_same_silhouette",
        "watermarked_stock_photos",
        "mobile_pure_column_stack",
        "critical_content_unreachable",
        "blank_page",
        "wrong_brand_assets",
    ]

    return {
        "rubric_ref": "evals/visual-quality-rubric.md",
        "pages_to_score": pages,
        "dimensions": dimensions,
        "scores": {d["name"]: {"score": None, "confidence": None, "notes": ""} for d in dimensions},
        "hard_fail_checks": {hf: None for hf in hard_fails},
        "composite_score": None,
        "grader": None,
        "graded_at": None,
    }


def cmd_grade(args: argparse.Namespace) -> int:
    source = Path(args.source)

    # Load pages
    pages: dict[str, str] = {}
    if source.is_dir():
        for path in sorted(source.glob("*.html")):
            pages[path.stem] = path.read_text(encoding="utf-8", errors="replace")
    elif source.suffix == ".json":
        manifest = json.loads(source.read_text(encoding="utf-8"))
        for name, value in manifest.get("pages", {}).items():
            p = Path(value)
            if p.exists():
                pages[name] = p.read_text(encoding="utf-8", errors="replace")
            else:
                pages[name] = value
    else:
        print("ERROR: source must be a directory of .html files or a .json manifest", file=sys.stderr)
        return 1

    if not pages:
        print("ERROR: no pages found", file=sys.stderr)
        return 1

    # Stage 1: Deterministic gates
    page_results: list[dict[str, Any]] = []
    all_issues: list[str] = []
    for name, html in sorted(pages.items()):
        result = check_page(name, html, source if source.is_dir() else None)
        page_results.append(result)
        all_issues.extend(result["issues"])

    deterministic_passed = all(r["all_passed"] for r in page_results)
    pages_with_issues = [r["page"] for r in page_results if not r["all_passed"]]

    # Stage 2: Rubric template
    rubric_template = generate_rubric_template(sorted(pages.keys()))

    report = {
        "deterministic": {
            "passed": deterministic_passed,
            "pages_checked": len(page_results),
            "pages_with_issues": pages_with_issues,
            "all_issues": all_issues,
            "per_page": page_results,
        },
        "rubric_template": rubric_template,
        "note": "Deterministic gates are machine-verified. Rubric dimensions require model/human scoring with rendered screenshots.",
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Visual Quality Grader — Deterministic Gates")
        print(f"{'=' * 50}")
        status = "✅ PASSED" if deterministic_passed else "❌ FAILED"
        print(f"Overall: {status} ({len(page_results)} pages checked)")

        if all_issues:
            print(f"\nIssues found:")
            for issue in all_issues:
                print(f"  - {issue}")

        print(f"\nRubric template generated for model/human scoring:")
        for dim in rubric_template["dimensions"]:
            print(f"  - {dim['label']} ({dim['weight']:.0%}): [score 0-4]")

    return 0 if deterministic_passed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        help="Directory of .html files or a .json manifest",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return cmd_grade(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
