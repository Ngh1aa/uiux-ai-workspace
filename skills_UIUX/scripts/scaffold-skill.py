#!/usr/bin/env python3
"""Create a V2 skill package scaffold. Standard library only."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")

SKILL_TMPL = '''---
name: {name}
description: |
  TODO: Third-person description of what this skill does and when to use it.
---

# {title}

## Goal
TODO

## Workflow
1. TODO
2. TODO
3. TODO

## Progressive resources
- [Reference](references/reference.md)
- [Quality gate](checklists/gate.md)
- [Example](examples/example.md)

## Output
TODO

## Acceptance criteria
- [ ] TODO
'''


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    if not NAME_RE.fullmatch(args.name):
        raise SystemExit("name must be lowercase letters/numbers/hyphens and <=64 chars")
    root = ROOT / args.name
    if root.exists() and not args.force:
        raise SystemExit(f"{root} already exists; use --force only if intentional")
    for sub in ["references", "checklists", "examples"]:
        (root / sub).mkdir(parents=True, exist_ok=True)
    title = " ".join(w.capitalize() for w in args.name.split("-"))
    (root / "SKILL.md").write_text(SKILL_TMPL.format(name=args.name, title=title), encoding="utf-8")
    (root / "references" / "reference.md").write_text("# Reference\n\nTODO\n", encoding="utf-8")
    (root / "checklists" / "gate.md").write_text("# Quality Gate\n\n- [ ] TODO\n", encoding="utf-8")
    (root / "examples" / "example.md").write_text("# Example\n\nTODO\n", encoding="utf-8")
    print(f"Created {root.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
