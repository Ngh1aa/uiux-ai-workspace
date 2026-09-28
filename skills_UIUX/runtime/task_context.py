"""Deprecated compatibility import for the canonical Factory Task Contract compiler."""

from pathlib import Path
import sys

_FACTORY_ROOT = Path(__file__).resolve().parents[2] / "uiux-factory"
if str(_FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_FACTORY_ROOT))

from core.runtime.flow_os.task_context import *  # noqa: F401,F403,E402
