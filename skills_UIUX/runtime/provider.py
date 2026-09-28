"""Deprecated compatibility import for canonical Factory provider adapters."""

from pathlib import Path
import sys

_FACTORY_ROOT = Path(__file__).resolve().parents[2] / "uiux-factory"
if str(_FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_FACTORY_ROOT))

from core.runtime.flow_os.provider import *  # noqa: F401,F403,E402
