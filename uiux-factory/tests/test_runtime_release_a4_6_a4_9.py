from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.browser_evidence import BrowserEvidenceError, PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.release import DeploymentResult, ProductionReleaseController, ProductionReleaseError
from core.runtime.flow_os.sandbox import ContainerSandbox, SandboxUnavailableError
from core.runtime.flow_os.workspace import WorkspaceIsolationError, WorktreeManager


FACTORY = Path(__file__).resolve().parents[1]
SKILLS = FACTORY.parent / "skills_UIUX"


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True)
    _git(root, "init")
    _git(root, "config", "user.email", "a4-release@example.test")
    _git(root, "config", "user.name", "A4 Release Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def _policy() -> dict:
    return {
        "target_runner": {
            "max_seconds": 30,
            "max_output_chars": 4000,
            "commands": [{"prefix": ["npm", "test"], "allow_extra": False}],
        },
        "sandbox": {
            "required": True,
            "engines": ["docker"],
            "network": "none",
            "read_only_rootfs": True,
            "memory": "512m",
            "cpus": "1",
            "pids_limit": 64,
            "tmpfs_size": "64m",
            "images": {"node": "node:test-local", "python": "python:test-local"},
        },
        "browser_evidence": {
            "allow_remote": False,
            "max_routes": 4,
            "max_artifact_bytes": 1024 * 1024,
            "timeout_seconds": 30,
        },
    }


def test_a4_6_sandbox_builds_networkless_locked_container_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.setattr("core.runtime.flow_os.sandbox.shutil.which", lambda name: "/usr/bin/docker")

    def fake_run(argv, **kwargs):
        if argv[:2] == ["/usr/bin/docker", "version"]:
            return SimpleNamespace(returncode=0, stdout="ok", stderr="")
        if argv[:3] == ["/usr/bin/docker", "image", "inspect"]:
            return SimpleNamespace(returncode=0, stdout="{}", stderr="")
        raise AssertionError(f"unexpected subprocess: {argv}")

    monkeypatch.setattr("core.runtime.flow_os.sandbox.subprocess.run", fake_run)
    sandbox = ContainerSandbox(root, _policy())
    command, timeout, spec = sandbox.build_command(["npm", "test"])

    assert timeout == 30
    assert spec.network == "none"
    assert "--network" in command and command[command.index("--network") + 1] == "none"
    assert "--read-only" in command
    assert ["--cap-drop", "ALL"] == command[command.index("--cap-drop") : command.index("--cap-drop") + 2]
    assert "no-new-privileges" in command
    assert "node:test-local" in command
    assert command[-2:] == ["npm", "test"]


def test_a4_6_sandbox_fails_closed_without_engine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.setattr("core.runtime.flow_os.sandbox.shutil.which", lambda _name: None)
    with pytest.raises(SandboxUnavailableError, match="required container sandbox is unavailable"):
        ContainerSandbox(root, _policy()).build_command(["npm", "test"])


def test_a4_7_finalize_fast_forwards_source_and_cleans_worktree(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    manager = WorktreeManager(source)
    metadata = manager.ensure("finalize123")
    workspace = Path(metadata.workspace_root)
    (workspace / "app.txt").write_text("changed\n", encoding="utf-8")

    result = manager.finalize(metadata, "uiux-agent: test finalize", merge=True, cleanup=True)

    assert result.changed is True
    assert result.merged is True
    assert result.cleaned is True
    assert result.commit
    assert (source / "app.txt").read_text(encoding="utf-8") == "changed\n"
    assert not workspace.exists()
    branches = _git(source, "branch", "--format=%(refname:short)").splitlines()
    assert metadata.branch not in branches


def test_a4_7_finalize_refuses_source_head_drift(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    manager = WorktreeManager(source)
    metadata = manager.ensure("drift123")
    workspace = Path(metadata.workspace_root)
    (workspace / "app.txt").write_text("agent\n", encoding="utf-8")

    (source / "other.txt").write_text("human\n", encoding="utf-8")
    _git(source, "add", "other.txt")
    _git(source, "commit", "-m", "human change")

    with pytest.raises(WorkspaceIsolationError, match="source HEAD moved"):
        manager.finalize(metadata, "uiux-agent: should not merge")


def test_a4_9_browser_adapter_hashes_real_artifacts_and_marks_errors_failed(tmp_path: Path) -> None:
    qa = tmp_path / "qa"
    artifacts = qa / "artifacts"
    artifacts.mkdir(parents=True)
    screenshot = artifacts / "home-render.png"
    screenshot.write_bytes(b"\x89PNG\r\n\x1a\nfixture-png-bytes")
    evidence = {
        "route": "/",
        "url": "http://127.0.0.1:4173/",
        "title": "Home",
        "viewport": {"width": 1440, "height": 900},
        "box": {"x": 0, "y": 0, "width": 100, "height": 30},
        "screenshot": screenshot.name,
        "ariaSnapshot": "- heading Home",
        "consoleMessages": [],
        "pageErrors": [],
        "blockedRequests": [],
    }
    (artifacts / "browser-evidence-home.json").write_text(json.dumps(evidence), encoding="utf-8")

    adapter = PlaywrightBrowserEvidenceAdapter(qa, _policy())
    records = adapter.collect(artifacts)
    assert len(records) == 1
    assert records[0].type == "browser_render"
    assert records[0].status == "PASS"
    assert len(records[0].data["screenshot_sha256"]) == 64

    evidence["pageErrors"] = ["boom"]
    (artifacts / "browser-evidence-home.json").write_text(json.dumps(evidence), encoding="utf-8")
    failed = adapter.collect(artifacts)
    assert failed[0].status == "FAIL"


def test_a4_9_browser_capture_rejects_remote_url_by_default(tmp_path: Path) -> None:
    qa = tmp_path / "qa"
    qa.mkdir()
    adapter = PlaywrightBrowserEvidenceAdapter(qa, _policy())
    with pytest.raises(BrowserEvidenceError, match="remote browser targets are disabled"):
        adapter.capture("https://example.com", ["/"])


class _DeployStub:
    def __init__(self) -> None:
        self.called = False

    def deploy(self, project_root: Path) -> DeploymentResult:
        self.called = True
        return DeploymentResult(adapter="stub", returncode=0, stdout="deployed", stderr="", deployed=True)


def test_a4_8_release_requires_release_authority_confirmation_and_evidence(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, source)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal("Fix button spacing", authority="branch_write", overrides={"change_surface": "MICRO"})
    managed.state = "COMPLETED"
    manager._checkpoint_managed(managed)

    controller = ProductionReleaseController(harness)
    browser = EvidenceRecord(
        id="browser-release",
        type="browser_render",
        stage_id="qa",
        tool="playwright",
        status="PASS",
        summary="rendered",
        data={"route": "/"},
    )
    check = EvidenceRecord(
        id="check-release",
        type="validator_result",
        stage_id="qa",
        tool="run_validator",
        status="PASS",
        summary="validator passed",
        data={"name": "validate-runtime", "returncode": 0},
    )
    controller.attach_release_evidence(managed, [browser, check])

    with pytest.raises(ProductionReleaseError, match="release authority"):
        controller.deploy_production(managed, "external_write", "PRODUCTION", adapter=_DeployStub())
    with pytest.raises(ProductionReleaseError, match="explicit confirmation"):
        controller.deploy_production(managed, "release", "yes", adapter=_DeployStub())

    stub = _DeployStub()
    result = controller.deploy_production(managed, "release", "PRODUCTION", adapter=stub)
    assert result.deployed is True
    assert stub.called is True
    manager_state = harness.resume(managed.manager_run_id)
    assert any(item.get("type") == "deployment_result" for item in manager_state.context["release_evidence"])


def test_a4_8_finalize_requires_completed_managed_flow(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, source)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal("Fix button spacing", authority="branch_write", overrides={"change_surface": "MICRO"})
    with pytest.raises(ProductionReleaseError, match="managed flow COMPLETED"):
        ProductionReleaseController(harness).finalize_workspace(
            managed,
            authority="external_write",
            commit_message="uiux-agent: premature",
        )
