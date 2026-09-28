from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MAX_READ_BYTES = 512 * 1024
BLOCKED_DIRECTORY_NAMES = frozenset({
    ".git",
    ".uiux-agent-runs",
    "node_modules",
})
BLOCKED_FILE_NAMES = frozenset({
    ".env",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
})
SAFE_ENV_TEMPLATE_NAMES = frozenset({".env.example", ".env.sample", ".env.template"})
BLOCKED_FILE_PREFIXES = (".env.",)
BLOCKED_FILE_SUFFIXES = (".p12", ".pfx", ".key")
PRIVATE_KEY_MARKERS = (
    b"-----BEGIN PRIVATE KEY-----",
    b"-----BEGIN RSA PRIVATE KEY-----",
    b"-----BEGIN EC PRIVATE KEY-----",
    b"-----BEGIN OPENSSH PRIVATE KEY-----",
)


class SafeReadError(ValueError):
    """Raised when a path cannot be read without violating the Safe Read contract."""


@dataclass(frozen=True)
class SafeReadResult:
    path: Path
    relative_path: str
    content: str
    bytes_read: int

    def observation(self) -> dict[str, Any]:
        return {
            "path": self.relative_path,
            "content": self.content,
            "bytes": self.bytes_read,
            "encoding": "utf-8",
        }


class SafeReader:
    """Fail-closed UTF-8 reader anchored to one explicit trust root.

    Safe Read deliberately rejects symlinks rather than trying to infer whether a
    link target should inherit trust. This keeps project/source reads deterministic
    and closes the common symlink-escape ambiguity before A4.2 worktree isolation.

    A8.5 adds one narrow exception below `.uiux-agent-runs`: the runtime-generated
    public `skill-section-index.json`. Checkpoints, traces and the private section
    registry remain blocked.
    """

    def __init__(self, root: Path, max_bytes: int = DEFAULT_MAX_READ_BYTES) -> None:
        self.root = Path(root).resolve()
        if not self.root.exists() or not self.root.is_dir():
            raise SafeReadError(f"safe-read root is not a directory: {self.root}")
        if max_bytes <= 0:
            raise SafeReadError("safe-read max_bytes must be positive")
        self.max_bytes = int(max_bytes)

    @staticmethod
    def _is_blocked_file_name(name: str) -> bool:
        lowered = name.lower()
        if lowered in SAFE_ENV_TEMPLATE_NAMES:
            return False
        return (
            lowered in BLOCKED_FILE_NAMES
            or any(lowered.startswith(prefix) for prefix in BLOCKED_FILE_PREFIXES)
            or any(lowered.endswith(suffix) for suffix in BLOCKED_FILE_SUFFIXES)
        )

    @staticmethod
    def _is_public_runtime_skill_index(relative: Path) -> bool:
        parts = relative.parts
        return (
            len(parts) == 3
            and parts[0].lower() == ".uiux-agent-runs"
            and bool(parts[1])
            and parts[2] == "skill-section-index.json"
        )

    @staticmethod
    def _contains_blocked_directory(relative: Path) -> str | None:
        if SafeReader._is_public_runtime_skill_index(relative):
            return None
        for part in relative.parts[:-1]:
            if part.lower() in BLOCKED_DIRECTORY_NAMES:
                return part
        return None

    def _lexical_candidate(self, raw: str | Path) -> tuple[Path, Path]:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        lexical = Path(os.path.abspath(os.fspath(candidate)))
        try:
            relative = lexical.relative_to(self.root)
        except ValueError as exc:
            raise SafeReadError(f"path escapes safe-read root: {raw}") from exc
        return lexical, relative

    def _reject_symlink_chain(self, relative: Path) -> None:
        current = self.root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise SafeReadError(f"safe-read refuses symlink path: {relative.as_posix()}")

    def resolve_file(self, raw: str | Path) -> tuple[Path, Path]:
        lexical, lexical_relative = self._lexical_candidate(raw)
        blocked_dir = self._contains_blocked_directory(lexical_relative)
        if blocked_dir:
            raise SafeReadError(
                f"safe-read refuses blocked directory {blocked_dir!r}: {lexical_relative.as_posix()}"
            )
        if self._is_blocked_file_name(lexical_relative.name):
            raise SafeReadError(f"safe-read refuses credential-bearing path: {lexical_relative.as_posix()}")

        self._reject_symlink_chain(lexical_relative)
        try:
            resolved = lexical.resolve(strict=True)
        except FileNotFoundError as exc:
            raise SafeReadError(f"safe-read file not found: {lexical_relative.as_posix()}") from exc
        try:
            resolved_relative = resolved.relative_to(self.root)
        except ValueError as exc:
            raise SafeReadError(f"resolved path escapes safe-read root: {lexical_relative.as_posix()}") from exc
        if not resolved.is_file():
            raise SafeReadError(f"safe-read requires a regular file: {resolved_relative.as_posix()}")
        return resolved, resolved_relative

    def resolve_directory(self, raw: str | Path = ".") -> tuple[Path, Path]:
        lexical, lexical_relative = self._lexical_candidate(raw)
        for part in lexical_relative.parts:
            if part.lower() in BLOCKED_DIRECTORY_NAMES:
                raise SafeReadError(
                    f"safe-read refuses blocked directory {part!r}: {lexical_relative.as_posix()}"
                )
        self._reject_symlink_chain(lexical_relative)
        try:
            resolved = lexical.resolve(strict=True)
        except FileNotFoundError as exc:
            raise SafeReadError(f"safe-read directory not found: {lexical_relative.as_posix()}") from exc
        try:
            resolved_relative = resolved.relative_to(self.root)
        except ValueError as exc:
            raise SafeReadError(f"resolved directory escapes safe-read root: {lexical_relative.as_posix()}") from exc
        if not resolved.is_dir():
            raise SafeReadError(f"safe-read requires a directory: {resolved_relative.as_posix()}")
        return resolved, resolved_relative

    def read_text(self, raw: str | Path, max_bytes: int | None = None) -> SafeReadResult:
        resolved, relative = self.resolve_file(raw)
        limit = self.max_bytes if max_bytes is None else min(self.max_bytes, int(max_bytes))
        if limit <= 0:
            raise SafeReadError("safe-read max_bytes must be positive")

        size = resolved.stat().st_size
        if size > limit:
            raise SafeReadError(
                f"safe-read file exceeds {limit} byte limit: {relative.as_posix()} ({size} bytes)"
            )
        payload = resolved.read_bytes()
        if len(payload) > limit:
            raise SafeReadError(
                f"safe-read file exceeded {limit} byte limit while reading: {relative.as_posix()}"
            )
        if b"\x00" in payload:
            raise SafeReadError(f"safe-read refuses binary/NUL content: {relative.as_posix()}")
        if any(marker in payload for marker in PRIVATE_KEY_MARKERS):
            raise SafeReadError(f"safe-read refuses private-key material: {relative.as_posix()}")
        try:
            content = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise SafeReadError(f"safe-read requires valid UTF-8 text: {relative.as_posix()}") from exc
        return SafeReadResult(
            path=resolved,
            relative_path=relative.as_posix(),
            content=content,
            bytes_read=len(payload),
        )

    def list_files(self, raw: str | Path = ".") -> list[str]:
        directory, _relative = self.resolve_directory(raw)
        visible: list[str] = []
        for child in directory.iterdir():
            if child.is_symlink():
                continue
            if child.name.lower() in BLOCKED_DIRECTORY_NAMES:
                continue
            if self._is_blocked_file_name(child.name):
                continue
            try:
                visible.append(child.relative_to(self.root).as_posix())
            except ValueError:
                continue
        return sorted(visible)
