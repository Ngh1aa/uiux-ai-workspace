from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def create_server() -> Any:
    try:
        from mcp.server import MCPServer
    except ImportError as exc:
        raise RuntimeError(
            'Optional MCP adapter requires the current v2 SDK: pip install "mcp[cli]>=2,<3"'
        ) from exc

    from runtime.agent import build_context_manifest

    mcp = MCPServer("skills_UIUX")

    @mcp.resource("uiux://runtime/foundation")
    def runtime_foundation() -> str:
        return (ROOT / "RUNTIME-FOUNDATION.md").read_text(encoding="utf-8")

    @mcp.tool()
    def build_project_context(
        project_root: str,
        selected_skills: list[str] | None = None,
        explicit_sources: list[str] | None = None,
    ) -> dict[str, Any]:
        return build_context_manifest(
            Path(project_root).resolve(),
            ROOT,
            selected_skills=selected_skills or [],
            explicit_sources=explicit_sources or [],
        )

    @mcp.tool()
    def validate_runtime() -> dict[str, Any]:
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / "validate-runtime-foundation.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {"returncode": result.returncode, "stdout": result.stdout[-12000:], "stderr": result.stderr[-12000:]}

    return mcp


def main() -> int:
    create_server().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
