from pathlib import Path
import shutil


TARGET = Path(
    "core/actions/generate_frontend_project_v2.py"
)

if not TARGET.exists():
    raise FileNotFoundError(
        f"Target file not found: {TARGET.resolve()}"
    )

# utf-8-sig strips a possible BOM automatically.
text = TARGET.read_text(
    encoding="utf-8-sig",
)

backup = TARGET.with_suffix(
    TARGET.suffix + ".mojibake-backup-2"
)

shutil.copy2(
    TARGET,
    backup,
)

MOJIBAKE_MARKERS = (
    "Ã",
    "Â",
    "â",
    "Æ",
    "áº",
    "á»",
    "ðŸ",
)


def score(value: str) -> int:
    return sum(
        value.count(marker)
        for marker in MOJIBAKE_MARKERS
    )


def is_cp1252_char(char: str) -> bool:
    try:
        char.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def try_repair_chunk(chunk: str) -> str:
    if score(chunk) == 0:
        return chunk

    try:
        repaired = chunk.encode(
            "cp1252"
        ).decode(
            "utf-8"
        )
    except (
        UnicodeEncodeError,
        UnicodeDecodeError,
    ):
        return chunk

    if score(repaired) < score(chunk):
        return repaired

    return chunk


def repair_mixed_unicode(value: str) -> str:
    output = []
    buffer = []

    def flush() -> None:
        if not buffer:
            return

        chunk = "".join(buffer)
        output.append(
            try_repair_chunk(
                chunk
            )
        )
        buffer.clear()

    for char in value:
        if is_cp1252_char(char):
            buffer.append(char)
        else:
            flush()
            output.append(char)

    flush()

    return "".join(output)


before = score(text)
repaired = repair_mixed_unicode(
    text
)
after = score(repaired)

if before == 0:
    print(
        "No mojibake markers detected. "
        "No repair was necessary."
    )
    raise SystemExit(0)

if after >= before:
    raise RuntimeError(
        "Repair did not improve the mojibake score. "
        f"before={before}, after={after}. "
        "No file was changed."
    )

# Validate Python syntax before replacing the file.
compile(
    repaired,
    str(TARGET),
    "exec",
)

# Write UTF-8 without BOM.
TARGET.write_text(
    repaired,
    encoding="utf-8",
)

print(
    "FrontendEngineerV2 Unicode repaired safely."
)
print(
    f"Mojibake markers: {before} -> {after}"
)
print(
    f"Backup: {backup}"
)
