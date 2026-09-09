from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "skills_UIUX" / "upstream" / "anthropic-skills"

REQUIRED = (
    "skills/frontend-design/SKILL.md",
    "skills/frontend-design/LICENSE.txt",
    "skills/webapp-testing/SKILL.md",
    "skills/webapp-testing/LICENSE.txt",
    "skills/webapp-testing/scripts/with_server.py",
    "skills/webapp-testing/examples/console_logging.py",
    "skills/webapp-testing/examples/element_discovery.py",
    "skills/webapp-testing/examples/static_html_automation.py",
    "skills/skill-creator/SKILL.md",
    "skills/skill-creator/LICENSE.txt",
    "skills/skill-creator/agents/analyzer.md",
    "skills/skill-creator/agents/comparator.md",
    "skills/skill-creator/agents/grader.md",
    "skills/skill-creator/references/schemas.md",
    "skills/skill-creator/eval-viewer/generate_review.py",
    "skills/skill-creator/eval-viewer/viewer.html",
    "skills/skill-creator/scripts/run_eval.py",
    "skills/skill-creator/scripts/run_loop.py",
    "skills/skill-creator/scripts/aggregate_benchmark.py",
    "skills/skill-creator/scripts/improve_description.py",
    "skills/skill-creator/scripts/quick_validate.py",
    "skills/web-artifacts-builder/SKILL.md",
    "skills/web-artifacts-builder/LICENSE.txt",
    "skills/web-artifacts-builder/scripts/init-artifact.sh",
    "skills/web-artifacts-builder/scripts/bundle-artifact.sh",
    "skills/web-artifacts-builder/scripts/shadcn-components.tar.gz",
)


def verify() -> list[str]:
    return [relative for relative in REQUIRED if not (UPSTREAM / relative).is_file()]


def main() -> int:
    missing = verify()
    if missing:
        print("Pinned Anthropic skills are incomplete.", file=sys.stderr)
        print(
            "Run: git submodule update --init --recursive",
            file=sys.stderr,
        )
        for item in missing:
            print(f"  missing: {item}", file=sys.stderr)
        return 1

    print(f"Anthropic skills verified: {len(REQUIRED)} required resources")
    print(f"Upstream root: {UPSTREAM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
