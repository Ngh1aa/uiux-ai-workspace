from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TargetRunnerError(ValueError):
    """Raised when a target command falls outside the bounded runner contract."""


@dataclass(frozen=True)
class TargetCommandResult:
    argv: list[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    duration_ms: int
    stdout_truncated: bool
    stderr_truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "argv": list(self.argv),
            "cwd": self.cwd,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "stdout_truncated": self.stdout_truncated,
            "stderr_truncated": self.stderr_truncated,
        }


class TargetRunner:
    """Run explicitly allowlisted argv commands inside an isolated workspace.

    This is command-policy isolation, not an OS/container sandbox. Project test/build
    commands can execute project code; the contract only removes shell interpretation,
    constrains cwd, filters environment variables and bounds time/output.
    """

    def __init__(self, workspace_root: Path, policy: dict[str, Any]) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        if not self.workspace_root.is_dir():
            raise TargetRunnerError(f"workspace root is not a directory: {self.workspace_root}")
        config = dict(policy.get("target_runner", {}))
        self.commands = list(config.get("commands", []))
        self.max_seconds = int(config.get("max_seconds", 180))
        self.max_output_chars = int(config.get("max_output_chars", 16000))
        self.env_allowlist = set(
            config.get(
                "env_allowlist",
                ["PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP", "TEMP", "LANG", "LC_ALL"],
            )
        )
        if self.max_seconds <= 0 or self.max_seconds > 600:
            raise TargetRunnerError("target_runner.max_seconds must be between 1 and 600")
        if self.max_output_chars <= 0 or self.max_output_chars > 100000:
            raise TargetRunnerError("target_runner.max_output_chars must be between 1 and 100000")

    @staticmethod
    def _normalize_argv(argv: list[str]) -> list[str]:
        if not isinstance(argv, list) or not argv or len(argv) > 32:
            raise TargetRunnerError("argv must be a non-empty array with at most 32 items")
        normalized: list[str] = []
        for raw in argv:
            if not isinstance(raw, str) or not raw or "\x00" in raw or "\n" in raw or "\r" in raw:
                raise TargetRunnerError("argv items must be non-empty single-line strings")
            normalized.append(raw)
        return normalized

    def _match_policy(self, argv: list[str]) -> None:
        for rule in self.commands:
            if not isinstance(rule, dict):
                continue
            prefix = [str(item) for item in rule.get("prefix", [])]
            if not prefix or argv[: len(prefix)] != prefix:
                continue
            if len(argv) == len(prefix) or bool(rule.get("allow_extra", False)):
                return
        raise TargetRunnerError(f"target command is not allowlisted: {' '.join(argv)}")

    def _cwd(self, raw: str) -> Path:
        relative = Path(raw or ".")
        if relative.is_absolute():
            raise TargetRunnerError("target runner cwd must be workspace-relative")
        lexical = Path(os.path.abspath(os.fspath(self.workspace_root / relative)))
        try:
            lexical_relative = lexical.relative_to(self.workspace_root)
        except ValueError as exc:
            raise TargetRunnerError(f"target runner cwd escapes workspace: {raw}") from exc

        current = self.workspace_root
        for part in lexical_relative.parts:
            current = current / part
            if current.is_symlink():
                raise TargetRunnerError(f"target runner refuses symlink cwd: {raw}")

        try:
            resolved = lexical.resolve(strict=True)
        except FileNotFoundError as exc:
            raise TargetRunnerError(f"target runner cwd is not a directory: {raw}") from exc
        try:
            resolved.relative_to(self.workspace_root)
        except ValueError as exc:
            raise TargetRunnerError(f"target runner cwd resolves outside workspace: {raw}") from exc
        if not resolved.is_dir():
            raise TargetRunnerError(f"target runner cwd is not a directory: {raw}")
        return resolved

    def _environment(self) -> dict[str, str]:
        environment = {key: value for key, value in os.environ.items() if key in self.env_allowlist}
        environment["CI"] = "1"
        environment["UIUX_ISOLATED_TARGET_RUN"] = "1"
        return environment

    @staticmethod
    def _executable(argv: list[str]) -> list[str]:
        if argv[0] == "python":
            return [sys.executable, *argv[1:]]
        return argv

    def run(self, argv: list[str], cwd: str = ".", timeout_seconds: int | None = None) -> TargetCommandResult:
        logical_argv = self._normalize_argv(argv)
        self._match_policy(logical_argv)
        working_directory = self._cwd(cwd)
        timeout = self.max_seconds if timeout_seconds is None else int(timeout_seconds)
        if timeout <= 0 or timeout > self.max_seconds:
            raise TargetRunnerError(f"timeout_seconds must be between 1 and {self.max_seconds}")

        started = time.monotonic()
        try:
            result = subprocess.run(
                self._executable(logical_argv),
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._environment(),
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TargetRunnerError(f"target command exceeded {timeout}s timeout") from exc
        duration_ms = int((time.monotonic() - started) * 1000)
        stdout_raw = result.stdout or ""
        stderr_raw = result.stderr or ""
        stdout_truncated = len(stdout_raw) > self.max_output_chars
        stderr_truncated = len(stderr_raw) > self.max_output_chars
        stdout = stdout_raw[-self.max_output_chars :]
        stderr = stderr_raw[-self.max_output_chars :]
        return TargetCommandResult(
            argv=logical_argv,
            cwd=str(working_directory.relative_to(self.workspace_root)) or ".",
            returncode=int(result.returncode),
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            stdout_truncated=stdout_truncated,
            stderr_truncated=stderr_truncated,
        )
