"""Cho phép test import `designlib` từ skills_UIUX/."""
from pathlib import Path
import sys

SKILLS_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
for path in (SKILLS_ROOT, TESTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
