from __future__ import annotations

import subprocess
from pathlib import Path

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.evidence import EvidenceRecord, effective_evidence
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.release import ProductionReleaseController


FACTORY = Path(__file__).resolve().parents[1]
SKILLS = FACTORY.parent / "skills_UIUX"


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "release-evidence@example.test")
    _git(root, "config", "user.name", "Release Evidence Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def _record(record_id: str, type_: str, status: str, data: dict) -> EvidenceRecord:
    return EvidenceRecord(
        id=record_id,
        type=type_,
        stage_id="qa",
        tool="run_validator" if type_ == "validator_result" else "playwright",
        status=status,
        summary=f"{record_id}: {status}",
        data=data,
    )


def test_a4_8_later_pass_supersedes_same_failed_release_channel(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, source)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Fix button spacing",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )
    managed.state = "COMPLETED"
    manager._checkpoint_managed(managed)
    release = ProductionReleaseController(harness)

    failed = _record(
        "validator-fail",
        "validator_result",
        "FAIL",
        {"name": "validate-runtime", "returncode": 1},
    )
    repaired = _record(
        "validator-pass",
        "validator_result",
        "PASS",
        {"name": "validate-runtime", "returncode": 0},
    )
    browser = _record(
        "browser-pass",
        "browser_render",
        "PASS",
        {"route": "/", "viewport": {"width": 1440, "height": 900}},
    )
    release.attach_release_evidence(managed, [failed, repaired, browser])

    effective = effective_evidence([failed.to_dict(), repaired.to_dict(), browser.to_dict()])
    assert [item.id for item in effective if item.type == "validator_result"] == ["validator-pass"]
    assert release.validate_release_ready(managed) == []


def test_a4_8_unrelated_pass_cannot_hide_failed_release_channel(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, source)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Fix button spacing",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )
    managed.state = "COMPLETED"
    manager._checkpoint_managed(managed)
    release = ProductionReleaseController(harness)

    failed = _record(
        "validator-fail",
        "validator_result",
        "FAIL",
        {"name": "validate-runtime", "returncode": 1},
    )
    unrelated = _record(
        "validator-other-pass",
        "validator_result",
        "PASS",
        {"name": "validate-flows", "returncode": 0},
    )
    browser = _record(
        "browser-pass",
        "browser_render",
        "PASS",
        {"route": "/", "viewport": {"width": 1440, "height": 900}},
    )
    release.attach_release_evidence(managed, [failed, unrelated, browser])

    errors = release.validate_release_ready(managed)
    assert any("failing result" in error for error in errors)
