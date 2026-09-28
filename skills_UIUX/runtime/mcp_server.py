"""Deprecated MCP entrypoint forwarding to the canonical Factory runtime."""

from pathlib import Path
import sys

_FACTORY_ROOT = Path(__file__).resolve().parents[2] / "uiux-factory"
if str(_FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_FACTORY_ROOT))

from core.runtime.flow_os.mcp_server import create_server, main  # noqa: F401,E402


if __name__ == "__main__":
    raise SystemExit(main())
