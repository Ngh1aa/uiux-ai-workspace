from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.runtime.flow_os.target_runner import TargetCommandResult, TargetRunner


class SandboxUnavailableError(RuntimeError):
    """Raised when a required sandbox engine/image is unavailable."""


@dataclass(frozen=True)
class SandboxSpec:
    engine: str
    image: str
    network: str
    read_only_rootfs: bool
    memory: str
    cpus: str
    pids_limit: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContainerSandbox:
    """Execute allowlisted target commands in a locked-down Docker/Podman container.

    Security invariants:
    - no shell interpretation;
    - network is disabled by default and cannot be widened by model arguments;
    - root filesystem is read-only while only the isolated worktree is mounted rw;
    - all Linux capabilities are dropped and no-new-privileges is enabled;
    - process, memory, CPU, timeout and output budgets are bounded;
    - host environment/secrets are not forwarded;
    - images are never pulled implicitly. Missing engine/image fails closed.
    """

    def __init__(self, workspace_root: Path, policy: dict[str, Any]) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.policy = dict(policy)
        self.validator = TargetRunner(self.workspace_root, self.policy)
        config = dict(self.policy.get("sandbox", {}))
        self.required = bool(config.get("required", True))
        self.engines = [str(item) for item in config.get("engines", ["docker", "podman"])]
        self.network = str(config.get("network", "none"))
        self.read_only_rootfs = bool(config.get("read_only_rootfs", True))
        self.memory = str(config.get("memory", "1g"))
        self.cpus = str(config.get("cpus", "2"))
        self.pids_limit = int(config.get("pids_limit", 256))
        self.tmpfs_size = str(config.get("tmpfs_size", "256m"))
        self.images = {
            str(key): str(value)
            for key, value in dict(
                config.get(
                    "images",
                    {
                        "node": "node:22-bookworm-slim",
                        "python": "python:3.13-slim",
                    },
                )
            ).items()
        }
        if self.network != "none":
            raise ValueError("canonical sandbox policy requires network='none'")
        if self.pids_limit <= 0 or self.pids_limit > 2048:
            raise ValueError("sandbox.pids_limit must be between 1 and 2048")

    def _engine(self) -> str:
        for engine in self.engines:
            executable = shutil.which(engine)
            if not executable:
                continue
            probe = subprocess.run(
                [executable, "version"],
                capture_output=True,
                text=True,
                timeout=15,
                shell=False,
            )
            if probe.returncode == 0:
                return executable
        raise SandboxUnavailableError(
            "required container sandbox is unavailable; install/start one of: " + ", ".join(self.engines)
        )

    def _image_for(self, argv: list[str]) -> str:
        family = "python" if argv[0] == "python" else "node"
        image = self.images.get(family, "").strip()
        if not image:
            raise SandboxUnavailableError(f"no sandbox image configured for command family: {family}")
        return image

    @staticmethod
    def _container_argv(argv: list[str]) -> list[str]:
        return ["python3", *argv[1:]] if argv[0] == "python" else list(argv)

    def _ensure_image(self, engine: str, image: str) -> None:
        probe = subprocess.run(
            [engine, "image", "inspect", image],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
        if probe.returncode != 0:
            raise SandboxUnavailableError(
                f"sandbox image is not present locally: {image}; canonical runtime never pulls images implicitly"
            )

    def build_command(self, argv: list[str], cwd: str = ".", timeout_seconds: int | None = None) -> tuple[list[str], int, SandboxSpec]:
        logical_argv, working_directory, timeout = self.validator.validate(argv, cwd, timeout_seconds)
        engine = self._engine()
        image = self._image_for(logical_argv)
        self._ensure_image(engine, image)
        relative_cwd = working_directory.relative_to(self.workspace_root).as_posix()
        container_cwd = "/workspace" if relative_cwd == "." else f"/workspace/{relative_cwd}"
        command = [
            engine,
            "run",
            "--rm",
            "--network",
            "none",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(self.pids_limit),
            "--memory",
            self.memory,
            "--cpus",
            self.cpus,
            "--tmpfs",
            f"/tmp:rw,nosuid,nodev,noexec,size={self.tmpfs_size}",
            "--mount",
            f"type=bind,src={self.workspace_root},dst=/workspace,rw",
            "--workdir",
            container_cwd,
            "--env",
            "CI=1",
            "--env",
            "UIUX_SANDBOX=1",
        ]
        if self.read_only_rootfs:
            command.append("--read-only")
        command.extend([image, *self._container_argv(logical_argv)])
        return command, timeout, SandboxSpec(
            engine=Path(engine).name,
            image=image,
            network="none",
            read_only_rootfs=self.read_only_rootfs,
            memory=self.memory,
            cpus=self.cpus,
            pids_limit=self.pids_limit,
        )

    def run(self, argv: list[str], cwd: str = ".", timeout_seconds: int | None = None) -> TargetCommandResult:
        command, timeout, _spec = self.build_command(argv, cwd, timeout_seconds)
        started = time.monotonic()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={
                    key: value
                    for key, value in os.environ.items()
                    if key in {"PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP", "TEMP"}
                },
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxUnavailableError(f"sandboxed target command exceeded {timeout}s timeout") from exc
        duration_ms = int((time.monotonic() - started) * 1000)
        stdout_raw = result.stdout or ""
        stderr_raw = result.stderr or ""
        limit = self.validator.max_output_chars
        logical_argv, working_directory, _ = self.validator.validate(argv, cwd, timeout_seconds)
        return TargetCommandResult(
            argv=logical_argv,
            cwd=str(working_directory.relative_to(self.workspace_root)) or ".",
            returncode=int(result.returncode),
            stdout=stdout_raw[-limit:],
            stderr=stderr_raw[-limit:],
            duration_ms=duration_ms,
            stdout_truncated=len(stdout_raw) > limit,
            stderr_truncated=len(stderr_raw) > limit,
        )
