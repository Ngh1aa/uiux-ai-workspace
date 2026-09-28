from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from core.runtime.flow_os.safe_read import SafeReadError, SafeReader


MAX_WRITE_BYTES = 1024 * 1024
MAX_SEARCH_FILES = 300
MAX_SEARCH_MATCHES = 200
BLOCKED_WRITE_DIRS = frozenset({".git", ".uiux-agent-runs", "node_modules", ".next", "dist", "build"})
BLOCKED_WRITE_NAMES = frozenset({
    ".env",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
})
BLOCKED_WRITE_PREFIXES = (".env.",)
BLOCKED_WRITE_SUFFIXES = (".key", ".p12", ".pfx")
SAFE_ENV_TEMPLATE_NAMES = frozenset({".env.example", ".env.sample", ".env.template"})


class WorkspaceFileError(ValueError):
    """Raised when a model-facing file operation violates workspace policy."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class WorkspaceFileTools:
    """Bounded text search/edit tools anchored to one isolated workspace."""

    def __init__(self, root: Path, max_write_bytes: int = MAX_WRITE_BYTES) -> None:
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise WorkspaceFileError(f"workspace root is not a directory: {self.root}")
        self.reader = SafeReader(self.root)
        self.max_write_bytes = int(max_write_bytes)
        if self.max_write_bytes <= 0:
            raise WorkspaceFileError("max_write_bytes must be positive")

    @staticmethod
    def _blocked_name(name: str) -> bool:
        lowered = name.lower()
        if lowered in SAFE_ENV_TEMPLATE_NAMES:
            return False
        return (
            lowered in BLOCKED_WRITE_NAMES
            or any(lowered.startswith(prefix) for prefix in BLOCKED_WRITE_PREFIXES)
            or any(lowered.endswith(suffix) for suffix in BLOCKED_WRITE_SUFFIXES)
        )

    def _resolve_write_path(self, raw: str | Path) -> tuple[Path, Path]:
        candidate = Path(raw)
        if candidate.is_absolute():
            raise WorkspaceFileError("absolute write paths are not allowed")
        lexical = Path(os.path.abspath(os.fspath(self.root / candidate)))
        try:
            relative = lexical.relative_to(self.root)
        except ValueError as exc:
            raise WorkspaceFileError(f"write path escapes isolated workspace: {raw}") from exc
        if not relative.parts:
            raise WorkspaceFileError("write path must reference a file")
        if any(part.lower() in BLOCKED_WRITE_DIRS for part in relative.parts[:-1]):
            raise WorkspaceFileError(f"write path targets generated/internal directory: {relative.as_posix()}")
        if self._blocked_name(relative.name):
            raise WorkspaceFileError(f"write path is credential-bearing: {relative.as_posix()}")

        current = self.root
        for part in relative.parts:
            current = current / part
            if current.exists() and current.is_symlink():
                raise WorkspaceFileError(f"workspace writes refuse symlink paths: {relative.as_posix()}")
        return lexical, relative

    def _atomic_write(self, path: Path, payload: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".uiux-write-", dir=str(path.parent))
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def write_text(self, path: str, content: str) -> dict[str, Any]:
        resolved, relative = self._resolve_write_path(path)
        payload = str(content).encode("utf-8")
        if len(payload) > self.max_write_bytes:
            raise WorkspaceFileError(
                f"workspace write exceeds {self.max_write_bytes} byte limit: {relative.as_posix()}"
            )
        before = resolved.read_bytes() if resolved.is_file() else b""
        self._atomic_write(resolved, payload)
        return {
            "path": relative.as_posix(),
            "bytes": len(payload),
            "created": not bool(before),
            "before_sha256": _sha256(before) if before else None,
            "after_sha256": _sha256(payload),
        }

    def replace_text(
        self,
        path: str,
        old: str,
        new: str,
        expected_count: int = 1,
    ) -> dict[str, Any]:
        if expected_count <= 0:
            raise WorkspaceFileError("expected_count must be positive")
        resolved, relative = self._resolve_write_path(path)
        try:
            loaded = self.reader.read_text(relative)
        except SafeReadError as exc:
            raise WorkspaceFileError(str(exc)) from exc
        actual = loaded.content.count(old)
        if actual != expected_count:
            raise WorkspaceFileError(
                f"replace_text expected {expected_count} occurrence(s), found {actual}: {relative.as_posix()}"
            )
        updated = loaded.content.replace(old, new, expected_count)
        result = self.write_text(relative.as_posix(), updated)
        result["replacements"] = expected_count
        return result

    def list_files_recursive(self, path: str = ".", max_files: int = 200) -> dict[str, Any]:
        if max_files <= 0 or max_files > 1000:
            raise WorkspaceFileError("max_files must be between 1 and 1000")
        directory, relative = self.reader.resolve_directory(path)
        items: list[str] = []
        for current, dirnames, filenames in os.walk(directory, followlinks=False):
            dirnames[:] = sorted(
                name
                for name in dirnames
                if name.lower() not in BLOCKED_WRITE_DIRS and not (Path(current) / name).is_symlink()
            )
            for name in sorted(filenames):
                if self._blocked_name(name):
                    continue
                candidate = Path(current) / name
                if candidate.is_symlink():
                    continue
                try:
                    rel = candidate.relative_to(self.root).as_posix()
                except ValueError:
                    continue
                items.append(rel)
                if len(items) >= max_files:
                    return {"path": relative.as_posix() or ".", "items": items, "truncated": True}
        return {"path": relative.as_posix() or ".", "items": items, "truncated": False}

    def search_text(
        self,
        query: str,
        path: str = ".",
        regex: bool = False,
        case_sensitive: bool = False,
        max_files: int = MAX_SEARCH_FILES,
        max_matches: int = MAX_SEARCH_MATCHES,
    ) -> dict[str, Any]:
        if not query:
            raise WorkspaceFileError("search query must not be empty")
        if max_files <= 0 or max_files > 1000:
            raise WorkspaceFileError("max_files must be between 1 and 1000")
        if max_matches <= 0 or max_matches > 1000:
            raise WorkspaceFileError("max_matches must be between 1 and 1000")
        directory, relative = self.reader.resolve_directory(path)
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(query if regex else re.escape(query), flags)
        matches: list[dict[str, Any]] = []
        scanned = 0
        truncated = False

        for current, dirnames, filenames in os.walk(directory, followlinks=False):
            dirnames[:] = sorted(
                name
                for name in dirnames
                if name.lower() not in BLOCKED_WRITE_DIRS and not (Path(current) / name).is_symlink()
            )
            for name in sorted(filenames):
                if scanned >= max_files:
                    truncated = True
                    break
                candidate = Path(current) / name
                if candidate.is_symlink() or self._blocked_name(name):
                    continue
                try:
                    loaded = self.reader.read_text(candidate)
                except SafeReadError:
                    continue
                scanned += 1
                for line_number, line in enumerate(loaded.content.splitlines(), start=1):
                    if pattern.search(line):
                        matches.append(
                            {
                                "path": loaded.relative_path,
                                "line": line_number,
                                "text": line[:1000],
                            }
                        )
                        if len(matches) >= max_matches:
                            truncated = True
                            break
                if len(matches) >= max_matches:
                    break
            if truncated or len(matches) >= max_matches:
                break
        return {
            "path": relative.as_posix() or ".",
            "query": query,
            "regex": bool(regex),
            "scanned_files": scanned,
            "matches": matches,
            "truncated": truncated,
        }
