from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from core.runtime.flow_os.agent import build_context_manifest

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

    return mcp


def main() -> int:
    create_server().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
