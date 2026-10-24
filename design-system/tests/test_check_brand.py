"""Tests for scripts/check-brand.py, the client brand-layer checker. Run: python3 -m pytest design-system/tests -q"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DS = Path(__file__).resolve().parents[1]
SCRIPT = DS / "scripts" / "check-brand.py"
STARTER = DS / "starter" / "brand.css"


def check(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)


def write(tmp_path: Path, css: str) -> Path:
    path = tmp_path / "brand.css"
    path.write_text(css, encoding="utf-8")
    return path


def test_starter_brand_passes():
    result = check(STARTER)
    assert result.returncode == 0, result.stdout + result.stderr


def test_low_contrast_text_fails(tmp_path):
    css = STARTER.read_text(encoding="utf-8").replace(
        "--ds-text-tertiary: #646873;", "--ds-text-tertiary: #a0a4ad;", 1)
    result = check(write(tmp_path, css))
    assert result.returncode == 1
    assert "text.tertiary" in result.stdout


def test_dark_blocks_must_match(tmp_path):
    css = STARTER.read_text(encoding="utf-8").replace(
        "--ds-text-secondary: #b3b7c3;", "--ds-text-secondary: #c0c4cf;", 1)
    result = check(write(tmp_path, css))
    assert result.returncode == 1
    assert "khối tối lệch nhau" in result.stdout


def test_unknown_token_is_a_warning(tmp_path):
    css = STARTER.read_text(encoding="utf-8").replace(
        "/* Màu thương hiệu */", "/* Màu thương hiệu */\n  --ds-text-primay: #000000;", 1)
    result = check(write(tmp_path, css))
    assert result.returncode == 0, result.stdout
    assert "--ds-text-primay" in result.stdout


def test_minimal_brand_file_inherits_system(tmp_path):
    result = check(write(tmp_path, ":root { --ds-shape-card: 12px; }\n"))
    assert result.returncode == 0, result.stdout
