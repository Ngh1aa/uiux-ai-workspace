from pathlib import Path

import pytest

from verify_prototype import latest_quality_pair


def test_latest_quality_pair_selects_latest_complete_iteration(tmp_path: Path):
    run_dir = tmp_path / "run-1"
    first = run_dir / "quality-loop" / "iteration-01"
    second = run_dir / "quality-loop" / "iteration-02"
    incomplete = run_dir / "quality-loop" / "iteration-03"
    for directory in (first, second, incomplete):
        directory.mkdir(parents=True)

    for directory in (first, second):
        (directory / "browser-report.json").write_text("{}", encoding="utf-8")
        (directory / "visual-critic.json").write_text("{}", encoding="utf-8")
    (incomplete / "browser-report.json").write_text("{}", encoding="utf-8")

    browser, critic = latest_quality_pair(run_dir)
    assert browser.parent.name == "iteration-02"
    assert critic.parent.name == "iteration-02"


def test_latest_quality_pair_requires_complete_evidence(tmp_path: Path):
    run_dir = tmp_path / "run-2"
    run_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        latest_quality_pair(run_dir)
