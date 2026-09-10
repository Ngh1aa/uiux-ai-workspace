from __future__ import annotations

import hashlib
from pathlib import Path

from core.contracts.prototype_acceptance_schema import EvidenceRef


_EXCLUDED_PARTS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "browser-screenshots",
    "quality-loop",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_digest(project_dir: Path) -> str:
    root = Path(project_dir).resolve()
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        if any(part in _EXCLUDED_PARTS for part in relative.parts):
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def evidence_ref(
    path: Path,
    *,
    kind: str,
    evaluator: str,
    source_digest: str,
    route: str | None = None,
    viewport: str | None = None,
) -> EvidenceRef:
    target = Path(path).resolve()
    return EvidenceRef(
        kind=kind,
        path=str(target),
        sha256=sha256_file(target),
        evaluator=evaluator,
        source_digest=source_digest,
        route=route,
        viewport=viewport,
    )
