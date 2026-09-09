#!/usr/bin/env python3
"""Build a deterministic discovery index for root skills_UIUX skill packages.

Adapted from the artifact/digest/discovery pattern reviewed in
vercel-labs/agent-skills. Uses only the Python standard library and does not
publish anything by itself.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
SCHEMA = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"


def parse_frontmatter(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing closing frontmatter") from exc

    fm = lines[1:end]
    name = ""
    description = ""
    for i, line in enumerate(fm):
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"\'')
        elif line.startswith("description:"):
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

    if not NAME_RE.fullmatch(name):
        raise ValueError(f"invalid skill name: {name!r}")
    if not description or len(description) > 1024:
        raise ValueError(f"invalid description for {name}")
    return name, description


def skill_directories() -> list[Path]:
    return sorted(
        path
        for path in ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def package_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*") if path.is_file())


def deterministic_archive(directory: Path, files: list[Path]) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
        for path in files:
            arcname = path.relative_to(directory).as_posix()
            info = tar.gettarinfo(str(path), arcname=arcname)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with path.open("rb") as handle:
                tar.addfile(info, handle)

    gzip_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=gzip_buffer, mode="wb", mtime=0) as zipped:
        zipped.write(tar_buffer.getvalue())
    return gzip_buffer.getvalue()


def artifact_for(directory: Path) -> tuple[bytes, str, str]:
    files = package_files(directory)
    if len(files) == 1 and files[0].name == "SKILL.md":
        return files[0].read_bytes(), "md", "skill-md"
    return deterministic_archive(directory, files), "tar.gz", "archive"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/agent-skills")
    parser.add_argument("--base-url", default="")
    args = parser.parse_args()

    output = (ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    if output == ROOT or ROOT in output.parents and output.name == "":
        raise ValueError("invalid output directory")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    skills: list[dict[str, str]] = []
    names: set[str] = set()
    for directory in skill_directories():
        name, description = parse_frontmatter((directory / "SKILL.md").read_text(encoding="utf-8"))
        if name != directory.name:
            raise ValueError(f"name/folder mismatch: {directory.name} != {name}")
        if name in names:
            raise ValueError(f"duplicate skill name: {name}")
        names.add(name)

        payload, extension, artifact_type = artifact_for(directory)
        filename = f"{name}.{extension}"
        (output / filename).write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        url = f"{args.base_url.rstrip('/')}/{filename}" if args.base_url else filename
        skills.append(
            {
                "name": name,
                "description": description,
                "type": artifact_type,
                "url": url,
                "digest": f"sha256:{digest}",
            }
        )

    skills.sort(key=lambda item: item["name"])
    index = {"$schema": SCHEMA, "skills": skills}
    (output / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built discovery index for {len(skills)} skills at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
