from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest


WORKSPACE = Path(__file__).resolve().parents[2]
BASH = shutil.which('bash') or str(Path('C:/Program Files/Git/bin/bash.exe'))


@pytest.fixture()
def gate_project(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    root = tmp_path / 'fixture'
    for name in ('skills_UIUX', 'uiux-factory', 'design-system/tests', '.github/workflows'):
        (root / name).mkdir(parents=True)
    (root / '.github/workflows/uiux-factory-ci.yml').write_text('', encoding='utf-8')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    for name in ('python3', 'node'):
        executable = bin_dir / name
        executable.write_text(
            '#!/usr/bin/env bash\n'
            'echo "$*" >> "$GATE_TRACE"\n'
            'if [[ -n "${GATE_FAIL:-}" && "$*" == *"$GATE_FAIL"* ]]; then\n'
            '  echo "fixture output before failure"\n  exit 7\nfi\n'
            'echo "fixture success"\n', encoding='utf-8', newline='\n',
        )
        executable.chmod(0o755)
    env = {**os.environ, 'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'],
           'GATE_TRACE': str(tmp_path / 'trace.txt')}
    return root, env


def run_gate(root: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([BASH, str(WORKSPACE / 'scripts/check-all.sh'), str(root)],
                          env=env, text=True, capture_output=True, timeout=60)


def test_successful_checks_exit_zero(gate_project) -> None:
    root, env = gate_project
    result = run_gate(root, env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'FAIL ' not in result.stdout
    assert 'PASS  skills:pytest' in result.stdout


def test_failure_is_nonzero_and_later_checks_still_run(gate_project) -> None:
    root, env = gate_project
    result = run_gate(root, {**env, 'GATE_FAIL': 'validate-skills.py'})
    assert result.returncode == 1
    assert 'FAIL  validate-skills' in result.stdout
    assert 'PASS  factory:pytest' in result.stdout
    assert 'PASS  skills:pytest' in result.stdout


def test_failed_producer_cannot_hide_behind_nonempty_output(gate_project) -> None:
    root, env = gate_project
    result = run_gate(root, {**env, 'GATE_FAIL': 'query.py'})
    assert result.returncode == 1
    assert 'FAIL  design-intelligence-smoke' in result.stdout


def test_invalid_root_fails_before_checks(gate_project) -> None:
    root, env = gate_project
    result = run_gate(root / 'missing', env)
    assert result.returncode != 0
    assert not Path(env['GATE_TRACE']).exists()
