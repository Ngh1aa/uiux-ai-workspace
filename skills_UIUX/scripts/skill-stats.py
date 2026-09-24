#!/usr/bin/env python3
"""Report skill size/resource statistics to guide progressive disclosure refactors."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

rows = []
for skill in sorted(ROOT.glob("*/SKILL.md")):
    folder = skill.parent
    lines = len(skill.read_text(encoding="utf-8").splitlines())
    refs = sum(1 for p in folder.rglob("*") if p.is_file()) - 1
    rows.append((lines, refs, folder.name))

print(f"{'LINES':>6} {'RES':>4} SKILL")
for lines, refs, name in sorted(rows, reverse=True):
    marker = "!" if lines > 500 else " "
    print(f"{lines:>6}{marker} {refs:>4} {name}")
