from pathlib import Path
import shutil


TARGET = Path(
    "core/actions/generate_frontend_project_v2.py"
)

if not TARGET.exists():
    raise FileNotFoundError(
        f"Target file not found: {TARGET.resolve()}"
    )

text = TARGET.read_text(
    encoding="utf-8",
)

markers = (
    "Ã",
    "Â",
    "â",
    "Æ",
    "áº",
    "á»",
)

before = sum(
    text.count(marker)
    for marker in markers
)

backup = TARGET.with_suffix(
    TARGET.suffix + ".mojibake-backup"
)

shutil.copy2(
    TARGET,
    backup,
)

try:
    repaired = text.encode(
        "cp1252"
    ).decode(
        "utf-8"
    )
except UnicodeEncodeError as exc:
    raise RuntimeError(
        "Could not safely reverse the mojibake with cp1252. "
        "No file was changed."
    ) from exc

after = sum(
    repaired.count(marker)
    for marker in markers
)

if after >= before and before > 0:
    raise RuntimeError(
        f"Repair did not improve mojibake score: "
        f"before={before}, after={after}. "
        "No file was changed."
    )

compile(
    repaired,
    str(TARGET),
    "exec",
)

TARGET.write_text(
    repaired,
    encoding="utf-8",
)

print(
    "FrontendEngineerV2 Unicode repaired."
)
print(
    f"Mojibake markers: {before} -> {after}"
)
print(
    f"Backup: {backup}"
)
