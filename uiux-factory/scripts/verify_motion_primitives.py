from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills_UIUX"
META_PATH = SKILLS / "motion-component-intelligence" / "upstream.json"


def _git_head(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    upstream = ROOT / metadata["path"]
    component_root = upstream / metadata["component_root"]

    if not upstream.is_dir():
        raise SystemExit(
            f"Motion Primitives submodule missing: {upstream}. "
            "Run: git submodule update --init --recursive"
        )

    actual_head = _git_head(upstream)
    expected_head = metadata["pinned_commit"]
    if actual_head != expected_head:
        raise SystemExit(f"Motion Primitives pin mismatch: expected {expected_head}, got {actual_head}")

    required = [
        upstream / "README.md",
        upstream / "PROMPTING.md",
        upstream / "package.json",
        upstream / "CONTRIBUTING.md",
        component_root,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Motion Primitives upstream is incomplete: " + ", ".join(missing))

    source_files = [
        path
        for path in component_root.rglob("*")
        if path.is_file() and path.suffix in {".tsx", ".ts"}
    ]
    if len(source_files) < 50:
        raise SystemExit(
            f"Motion Primitives corpus unexpectedly small: found {len(source_files)} TypeScript component files"
        )

    expected_categories = {"backgrounds", "buttons", "cards", "effects", "interactive", "navigation", "scroll"}
    present_categories = {path.name for path in component_root.iterdir() if path.is_dir()}
    missing_categories = sorted(expected_categories - present_categories)
    if missing_categories:
        raise SystemExit("Motion Primitives categories missing: " + ", ".join(missing_categories))

    print(
        "Motion Primitives verified:",
        actual_head,
        f"({len(source_files)} TypeScript component files, {len(present_categories)} categories)",
    )


if __name__ == "__main__":
    main()
