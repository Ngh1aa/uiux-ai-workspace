import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS_ROOT = WORKSPACE / "skills_UIUX"

if not SKILLS_ROOT.exists():
    raise FileNotFoundError(
        f"skills_UIUX clone not found: {SKILLS_ROOT}"
    )

pattern = re.compile(
    r'["\']([A-Za-z0-9_.\-/]+/SKILL\.md)["\']'
)

references = {}

for source in sorted(
    (ROOT / "core").rglob("*.py")
):
    text = source.read_text(
        encoding="utf-8"
    )

    for match in pattern.finditer(
        text
    ):
        relative = match.group(1)

        references.setdefault(
            relative,
            [],
        ).append(
            str(
                source.relative_to(
                    ROOT
                )
            )
        )

missing = []
valid = []

for relative, owners in sorted(
    references.items()
):
    target = (
        SKILLS_ROOT
        / relative
    )

    row = (
        relative,
        owners,
    )

    if target.exists():
        valid.append(row)
    else:
        missing.append(row)

print()
print("=" * 68)
print("UIUX FACTORY - REAL SKILL REFERENCE VALIDATION")
print("=" * 68)
print(
    f"[Skills Root] {SKILLS_ROOT}"
)
print(
    f"[Referenced Skill Paths] {len(references)}"
)
print(
    f"[Valid] {len(valid)}"
)
print(
    f"[Missing] {len(missing)}"
)

if missing:
    print()
    print("INVALID / INVENTED SKILL REFERENCES:")

    for relative, owners in missing:
        print(
            f"  - {relative}"
        )

        for owner in owners:
            print(
                f"      {owner}"
            )

    print()
    print(
        "FAIL: every */SKILL.md reference must resolve "
        "to a real file in skills_UIUX."
    )

    raise SystemExit(1)

print()
print(
    "PASS: every discovered */SKILL.md reference "
    "maps to a real skills_UIUX file."
)
