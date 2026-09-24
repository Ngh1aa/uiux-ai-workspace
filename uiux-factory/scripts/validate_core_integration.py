import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS_ROOT = WORKSPACE / "skills_UIUX"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.skills.router import AdaptiveSkillRouter


def code_skill_refs() -> dict[str, list[str]]:
    pattern = re.compile(
        r'["\']([A-Za-z0-9_.\-/]+/SKILL\.md)["\']'
    )
    found: dict[str, list[str]] = {}

    for source in sorted((ROOT / "core").rglob("*.py")):
        text = source.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            relative = match.group(1)
            found.setdefault(relative, []).append(
                str(source.relative_to(ROOT))
            )

    return found


def main():
    print()
    print("=" * 72)
    print("UIUX FACTORY - CORE INTEGRATION VALIDATION")
    print("=" * 72)

    if not SKILLS_ROOT.exists():
        raise FileNotFoundError(
            f"skills_UIUX sibling repository missing: {SKILLS_ROOT}"
        )

    router_missing = AdaptiveSkillRouter.validate_declared_paths(
        SKILLS_ROOT
    )
    refs = code_skill_refs()
    code_missing = [
        relative
        for relative in sorted(refs)
        if not (SKILLS_ROOT / relative).exists()
    ]

    print(f"[Skills Root] {SKILLS_ROOT}")
    print(
        "[Router Declared Paths] "
        f"{len(AdaptiveSkillRouter.all_declared_paths())}"
    )
    print(f"[Code Skill References] {len(refs)}")
    print(f"[Router Missing] {len(router_missing)}")
    print(f"[Code Missing] {len(code_missing)}")

    if router_missing or code_missing:
        if router_missing:
            print("\nMISSING ROUTER SKILLS:")
            for item in router_missing:
                print(f"  - {item}")

        if code_missing:
            print("\nMISSING CODE-REFERENCED SKILLS:")
            for item in code_missing:
                print(f"  - {item}")
                for owner in refs[item]:
                    print(f"      {owner}")

        raise SystemExit(1)

    print()
    print(
        "PASS: every routed/referenced skill exists as a real "
        "skills_UIUX SKILL.md file."
    )


if __name__ == "__main__":
    main()
