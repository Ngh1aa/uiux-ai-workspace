from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from core.runtime.flow_os.agent import build_context_manifest
from core.runtime.flow_os.remote_control import RemoteFactoryControlPlane

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = WORKSPACE_ROOT / "skills_UIUX"


def create_server() -> Any:
    try:
        from mcp.server import MCPServer
    except ImportError as exc:
        raise RuntimeError(
            'Optional MCP adapter requires the current v2 SDK: pip install "mcp[cli]>=2,<3"'
        ) from exc

    mcp = MCPServer("uiux-factory")
    remote = RemoteFactoryControlPlane(SKILLS_ROOT)

    @mcp.resource("uiux://runtime/foundation")
    def runtime_foundation() -> str:
        return (SKILLS_ROOT / "RUNTIME-FOUNDATION.md").read_text(encoding="utf-8")

    @mcp.tool()
    def build_project_context(
        project_root: str,
        selected_skills: list[str] | None = None,
        explicit_sources: list[str] | None = None,
    ) -> dict[str, Any]:
        return build_context_manifest(
            Path(project_root).resolve(),
            SKILLS_ROOT,
            selected_skills=selected_skills or [],
            explicit_sources=explicit_sources or [],
        )

    @mcp.tool()
    def validate_runtime() -> dict[str, Any]:
        result = subprocess.run(
            [sys.executable, "-B", str(SKILLS_ROOT / "scripts" / "validate-runtime-foundation.py")],
            cwd=SKILLS_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-12000:],
            "stderr": result.stderr[-12000:],
        }

    @mcp.tool()
    def remote_health() -> dict[str, Any]:
        return remote.health()

    @mcp.tool()
    def start_managed_run(
        token: str,
        project_root: str,
        goal: str,
        authority: str = "branch_write",
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return remote.start_run(
            token=token,
            project_root=project_root,
            goal=goal,
            authority=authority,
            overrides=overrides,
        )

    @mcp.tool()
    def managed_run_status(token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        return remote.status(token=token, project_root=project_root, manager_run_id=manager_run_id)

    @mcp.tool()
    def managed_run_artifacts(token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        return remote.list_artifacts(token=token, project_root=project_root, manager_run_id=manager_run_id)

    @mcp.tool()
    def read_managed_artifact(
        token: str,
        project_root: str,
        manager_run_id: str,
        path: str,
    ) -> dict[str, Any]:
        return remote.read_artifact(
            token=token,
            project_root=project_root,
            manager_run_id=manager_run_id,
            path=path,
        )

    @mcp.tool()
    def submit_creative_directive(
        token: str,
        project_root: str,
        manager_run_id: str,
        directive: dict[str, Any],
    ) -> dict[str, Any]:
        return remote.submit_creative_directive(
            token=token,
            project_root=project_root,
            manager_run_id=manager_run_id,
            directive=directive,
        )

    @mcp.tool()
    def start_revision_run(
        token: str,
        project_root: str,
        manager_run_id: str,
        goal: str | None = None,
    ) -> dict[str, Any]:
        return remote.start_revision(
            token=token,
            project_root=project_root,
            manager_run_id=manager_run_id,
            goal=goal,
        )

    @mcp.tool()
    def cancel_managed_run(token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        return remote.cancel(token=token, project_root=project_root, manager_run_id=manager_run_id)

    return mcp


def main() -> int:
    create_server().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
