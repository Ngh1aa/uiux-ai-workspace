#!/usr/bin/env python3
"""Lightweight structural validator for SKILL.md files.

Uses only the Python standard library so it can run locally or in GitHub Actions.
It intentionally validates structure, not the semantic quality of the instructions.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
RESERVED = ("anthropic", "claude")
MAX_DESCRIPTION = 1024
RECOMMENDED_MAX_BODY_LINES = 500


def parse_frontmatter(text: str) -> tuple[str, str, int]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")

    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing closing YAML frontmatter delimiter") from exc

    fm = lines[1:end]
    name = ""
    description = ""

    for i, line in enumerate(fm):
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"\'')
        if line.startswith("description:"):
            raw = line.split(":", 1)[1].strip()
            if raw in {"|", ">", ""}:
                chunks: list[str] = []
                for follow in fm[i + 1 :]:
                    if follow and not follow[0].isspace():
                        break
                    if follow.strip():
                        chunks.append(follow.strip())
                description = " ".join(chunks)
            else:
                description = raw.strip('"\'')

    if not name:
        raise ValueError("missing name")
    if not description:
        raise ValueError("missing or empty description")

    return name, description, len(lines) - end - 1


def main() -> int:
    skill_files = sorted(ROOT.rglob("SKILL.md"))
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, Path] = {}

    if not skill_files:
        print("No SKILL.md files found", file=sys.stderr)
        return 1

    for path in skill_files:
        rel = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
            name, description, body_lines = parse_frontmatter(text)

            if not NAME_RE.fullmatch(name):
                errors.append(f"{rel}: invalid name '{name}'")
            if any(word in name for word in RESERVED):
                errors.append(f"{rel}: reserved word in name '{name}'")
            if len(description) > MAX_DESCRIPTION:
                errors.append(
                    f"{rel}: description is {len(description)} chars; max {MAX_DESCRIPTION}"
                )
            if body_lines > RECOMMENDED_MAX_BODY_LINES:
                warnings.append(
                    f"{rel}: body is {body_lines} lines; consider progressive disclosure "
                    f"(recommended <= {RECOMMENDED_MAX_BODY_LINES})"
                )
            if path.parent.name != name:
                errors.append(
                    f"{rel}: folder '{path.parent.name}' does not match skill name '{name}'"
                )
            if name in seen:
                errors.append(f"{rel}: duplicate skill name also used by {seen[name]}")
            else:
                seen[name] = rel

        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{rel}: {exc}")

    print(f"Validated {len(skill_files)} skills")

    if warnings:
        print("\nValidation warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("\nValidation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("\nAll required skill structure checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
