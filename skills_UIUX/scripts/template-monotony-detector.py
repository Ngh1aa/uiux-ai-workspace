#!/usr/bin/env python3
"""Cross-page template-monotony detector for skills_UIUX V5.1.

Analyzes HTML output across pages to detect structural repetition that
indicates template monotony (all pages sharing hero+cards+CTA pattern).

Prefers rendered DOM / page manifests over source inspection.  Modern
frameworks may have identical source templates but different rendered
compositions, so the detector normalizes based on observable structure.

V1 uses calibration-first thresholds:
  - identical ALL pages         → HARD FAIL
  - <3 families / ≥5 roles     → CANDIDATE (deterministic finding)
  - ≥80% shared top-3 pattern  → STRONG WARN
  - ≥60% shared top-3 pattern  → WARN
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- Section pattern detection ---

HERO_PATTERNS = re.compile(
    r"(hero|banner|jumbotron|masthead|splash|cover-section|page-header)",
    re.IGNORECASE,
)
CARD_PATTERNS = re.compile(
    r"(card|tile|feature|benefit|service-item|team-member|testimonial)",
    re.IGNORECASE,
)
CTA_PATTERNS = re.compile(
    r"(cta|call-to-action|action-banner|signup|subscribe|newsletter)",
    re.IGNORECASE,
)
GRID_PATTERNS = re.compile(
    r"(grid|row|columns|flex-container|masonry|gallery)",
    re.IGNORECASE,
)
FOOTER_PATTERNS = re.compile(r"(footer|site-footer)", re.IGNORECASE)
NAV_PATTERNS = re.compile(r"(nav|navbar|header|site-header|menu)", re.IGNORECASE)

SECTION_TAG = re.compile(
    r"<(section|div|article|main|aside|header|footer)"
    r'[^>]*(?:class|id)\s*=\s*["\']([^"\']*)["\']',
    re.IGNORECASE,
)
HEADING_TAG = re.compile(r"<h([1-6])[^>]*>", re.IGNORECASE)


def classify_section(classes_or_id: str) -> str:
    """Classify a section by its class/id into a normalized type."""
    text = classes_or_id.lower()
    if NAV_PATTERNS.search(text):
        return "NAV"
    if HERO_PATTERNS.search(text):
        return "HERO"
    if CTA_PATTERNS.search(text):
        return "CTA"
    if CARD_PATTERNS.search(text):
        return "CARDS"
    if GRID_PATTERNS.search(text):
        return "GRID"
    if FOOTER_PATTERNS.search(text):
        return "FOOTER"
    return "SECTION"


def extract_section_sequence(html: str) -> list[str]:
    """Extract a normalized section sequence from HTML content."""
    sections: list[str] = []
    for match in SECTION_TAG.finditer(html):
        tag_name = match.group(1).lower()
        class_or_id = match.group(2)

        section_type = classify_section(class_or_id)

        # Skip nav and footer for composition comparison
        if section_type in ("NAV", "FOOTER"):
            continue

        sections.append(section_type)

    # Collapse consecutive duplicates (e.g., SECTION SECTION → SECTION)
    collapsed: list[str] = []
    for s in sections:
        if not collapsed or collapsed[-1] != s:
            collapsed.append(s)

    return collapsed if collapsed else ["UNKNOWN"]


def extract_heading_structure(html: str) -> list[int]:
    """Extract heading level sequence (h1-h6) for hierarchy comparison."""
    return [int(m.group(1)) for m in HEADING_TAG.finditer(html)]


# --- Similarity metrics ---

def jaccard_similarity(seq_a: list[str], seq_b: list[str]) -> float:
    """Jaccard similarity of two section sequences."""
    set_a, set_b = set(seq_a), set(seq_b)
    if not set_a and not set_b:
        return 1.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 1.0


def sequence_match(seq_a: list[str], seq_b: list[str]) -> float:
    """Exact sequence match ratio (position-aware)."""
    if not seq_a and not seq_b:
        return 1.0
    max_len = max(len(seq_a), len(seq_b))
    if max_len == 0:
        return 1.0
    matches = sum(1 for a, b in zip(seq_a, seq_b) if a == b)
    return matches / max_len


def top_n_match(seq_a: list[str], seq_b: list[str], n: int = 3) -> bool:
    """Check if the top-N sections are identical."""
    return seq_a[:n] == seq_b[:n]


# --- Analysis ---

def analyze_pages(pages: dict[str, str]) -> dict[str, Any]:
    """Analyze a set of pages for template monotony.

    Args:
        pages: dict mapping page role/name to HTML content.

    Returns:
        Analysis report with per-page data, cross-page matrix, and verdict.
    """
    page_data: dict[str, dict[str, Any]] = {}
    sequences: dict[str, list[str]] = {}

    for name, html in pages.items():
        seq = extract_section_sequence(html)
        headings = extract_heading_structure(html)
        page_data[name] = {
            "section_sequence": seq,
            "heading_levels": headings[:10],  # first 10
            "section_count": len(seq),
        }
        sequences[name] = seq

    names = sorted(sequences.keys())
    n_pages = len(names)

    # Cross-page similarity matrix
    matrix: dict[str, dict[str, float]] = {}
    for i, a in enumerate(names):
        matrix[a] = {}
        for j, b in enumerate(names):
            if i <= j:
                sim = sequence_match(sequences[a], sequences[b])
                matrix[a][b] = round(sim, 3)

    # Top-3 section pattern analysis
    top3_patterns: dict[str, list[str]] = {}
    for name in names:
        top3_patterns[name] = sequences[name][:3]

    top3_counter = Counter(tuple(p) for p in top3_patterns.values())
    most_common_top3, most_common_count = top3_counter.most_common(1)[0] if top3_counter else ((), 0)
    top3_shared_ratio = most_common_count / n_pages if n_pages else 0

    # Composition families (unique section sequences)
    unique_sequences = set(tuple(s) for s in sequences.values())
    n_families = len(unique_sequences)

    # Identical check
    all_identical = n_families == 1 and n_pages > 1

    # --- Verdict ---
    verdict: str
    if all_identical:
        verdict = "HARD_FAIL"
    elif n_pages >= 5 and n_families < 3:
        verdict = "CANDIDATE"
    elif top3_shared_ratio >= 0.8:
        verdict = "STRONG_WARN"
    elif top3_shared_ratio >= 0.6:
        verdict = "WARN"
    else:
        verdict = "OK"

    return {
        "pages": page_data,
        "similarity_matrix": matrix,
        "composition_families": n_families,
        "unique_sequences": [list(s) for s in sorted(unique_sequences)],
        "top3_shared_ratio": round(top3_shared_ratio, 3),
        "most_common_top3": list(most_common_top3),
        "most_common_top3_count": most_common_count,
        "total_pages": n_pages,
        "verdict": verdict,
        "verdict_description": {
            "HARD_FAIL": "All pages have identical section structure",
            "CANDIDATE": f"Only {n_families} composition families for {n_pages} page roles",
            "STRONG_WARN": f"{top3_shared_ratio:.0%} of pages share the same top-3 section pattern",
            "WARN": f"{top3_shared_ratio:.0%} of pages share the same top-3 section pattern",
            "OK": "Sufficient structural diversity detected",
        }.get(verdict, verdict),
    }


def load_pages_from_dir(directory: Path) -> dict[str, str]:
    """Load HTML files from a directory as page name → content."""
    pages: dict[str, str] = {}
    for path in sorted(directory.glob("*.html")):
        pages[path.stem] = path.read_text(encoding="utf-8", errors="replace")
    return pages


def load_pages_from_manifest(manifest_path: Path) -> dict[str, str]:
    """Load pages from a JSON manifest: { "pages": { "name": "path_or_html" } }."""
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    pages_spec = data.get("pages", {})
    pages: dict[str, str] = {}
    for name, value in pages_spec.items():
        p = Path(value)
        if p.exists():
            pages[name] = p.read_text(encoding="utf-8", errors="replace")
        else:
            # Treat value as inline HTML
            pages[name] = value
    return pages


def cmd_analyze(args: argparse.Namespace) -> int:
    source = Path(args.source)

    if source.is_dir():
        pages = load_pages_from_dir(source)
    elif source.suffix == ".json":
        pages = load_pages_from_manifest(source)
    else:
        print(f"ERROR: source must be a directory of .html files or a .json manifest", file=sys.stderr)
        return 1

    if len(pages) < 2:
        print(f"ERROR: need at least 2 pages, found {len(pages)}", file=sys.stderr)
        return 1

    report = analyze_pages(pages)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        v = report["verdict"]
        print(f"Template Monotony Analysis")
        print(f"{'=' * 50}")
        print(f"Pages analyzed:        {report['total_pages']}")
        print(f"Composition families:  {report['composition_families']}")
        print(f"Top-3 shared ratio:    {report['top3_shared_ratio']:.0%}")
        print(f"Most common top-3:     {' → '.join(report['most_common_top3'])}")
        print(f"Verdict:               {v}")
        print(f"  {report['verdict_description']}")
        print()

        for name, data in report["pages"].items():
            seq_str = " → ".join(data["section_sequence"])
            print(f"  {name}: {seq_str}")

    return 0 if v in ("OK", "WARN") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        help="Directory of .html files or a .json manifest with page paths/content",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return cmd_analyze(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
