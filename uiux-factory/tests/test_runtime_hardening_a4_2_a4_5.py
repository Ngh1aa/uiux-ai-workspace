from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors, provider_claim_records
from core.runtime.flow_os.file_tools import WorkspaceFileError, WorkspaceFileTools
from core.runtime.flow_os.target_runner import TargetRunner, TargetRunnerError
from core.runtime.flow_os.workspace import WorkspaceIsolationError, WorktreeManager


FACTORY = Path(__file__).resolve().parents[1]
SKILLS = FACTORY.parent / "skills_UIUX"


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "a4@example.test")
    _git(root, "config", "user.name", "A4 Test")
    (root / "src").mkdir()
    (root / "src" / "app.txt").write_text("source\nneedle\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def test_a4_2_writes_are_isolated_from_source_checkout(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    manager = WorktreeManager(source)
    metadata = manager.ensure("managed123")
    workspace = Path(metadata.workspace_root)

    tools = WorkspaceFileTools(workspace)
    result = tools.write_text("src/app.txt", "workspace-only\n")

    assert (source / "src" / "app.txt").read_text(encoding="utf-8") == "source\nneedle\n"
    assert (workspace / "src" / "app.txt").read_text(encoding="utf-8") == "workspace-only\n"
    assert result["before_sha256"] != result["after_sha256"]
    assert metadata.branch == "uiux-agent/managed123"
    assert _git(workspace, "branch", "--show-current") == metadata.branch


def test_a4_2_requires_real_git_top_level(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(WorkspaceIsolationError):
        WorktreeManager(plain).ensure("managed123")


def test_a4_2_refuses_dirty_project_truth_but_ignores_runtime_checkpoint_state(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    runtime_state = source / ".uiux-agent-runs" / "abc"
    runtime_state.mkdir(parents=True)
    (runtime_state / "checkpoint.json").write_text("{}", encoding="utf-8")
    manager = WorktreeManager(source)
    metadata = manager.ensure("cleanruntime")
    assert Path(metadata.workspace_root).is_dir()

    source2 = _repo(tmp_path / "other")
    (source2 / "uncommitted.txt").write_text("project truth", encoding="utf-8")
    with pytest.raises(WorkspaceIsolationError, match="uncommitted or untracked project changes"):
        WorktreeManager(source2).ensure("dirtyrun")


def test_a4_2_legacy_harness_low_write_uses_worktree_not_source(tmp_path: Path) -> None:
    source = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, source)
    state = harness.create_run(
        "Write a UIUX artifact",
        "implementation",
        "branch_write",
        selected_skills=[],
        explicit_sources=[],
        run_id="legacy123",
    )
    completed = harness.execute_plan(
        state,
        [
            {
                "tool": "write_artifact",
                "args": {"path": "docs/uiux/a4.md", "content": "isolated"},
            }
        ],
    )
    metadata = harness.worktrees.validate_metadata(
        completed.context["workspace"], expected_run_id="legacy123"
    )
    assert not (source / "docs" / "uiux" / "a4.md").exists()
    assert (Path(metadata.workspace_root) / "docs" / "uiux" / "a4.md").read_text(encoding="utf-8") == "isolated"


def test_a4_5_file_tools_bound_search_replace_and_secret_paths(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "a.txt").write_text("Hello Needle\nsecond\n", encoding="utf-8")
    tools = WorkspaceFileTools(root)

    search = tools.search_text("needle", path="src")
    assert search["matches"][0]["path"] == "src/a.txt"
    assert search["matches"][0]["line"] == 1

    replaced = tools.replace_text("src/a.txt", "Needle", "World")
    assert replaced["replacements"] == 1
    assert (root / "src" / "a.txt").read_text(encoding="utf-8") == "Hello World\nsecond\n"

    listing = tools.list_files_recursive("src")
    assert listing["items"] == ["src/a.txt"]

    with pytest.raises(WorkspaceFileError):
        tools.write_text("../escape.txt", "no")
    with pytest.raises(WorkspaceFileError):
        tools.write_text(".env.local", "SECRET=x")


def test_a4_3_runner_is_argv_only_allowlisted_workspace_scoped_and_env_filtered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    policy = {
        "target_runner": {
            "max_seconds": 30,
            "max_output_chars": 4000,
            "env_allowlist": ["PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP", "TEMP"],
            "commands": [
                {"prefix": ["python", "-c"], "allow_extra": True},
            ],
        }
    }
    monkeypatch.setenv("A4_SECRET_SHOULD_NOT_LEAK", "top-secret")
    runner = TargetRunner(root, policy)
    result = runner.run(
        ["python", "-c", "import os; print(os.getenv('A4_SECRET_SHOULD_NOT_LEAK', 'filtered'))"]
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "filtered"
    assert result.cwd == "."

    with pytest.raises(TargetRunnerError, match="not allowlisted"):
        runner.run(["python", "--version"])
    with pytest.raises(TargetRunnerError):
        runner.run(["python", "-c", "print('x')"], cwd="../outside")


def test_a4_4_provider_claims_never_satisfy_typed_gates() -> None:
    gates = [{"id": "implementation-proof", "require": "implementation evidence", "evidence_types": ["file_change"]}]
    claims = provider_claim_records("implementation", ["I changed the file."])
    errors = gate_evidence_errors(gates, "implementation", claims, agent="implementation")
    assert errors == ["gate implementation-proof missing typed evidence: file_change"]

    record = evidence_from_tool(
        "implementation",
        "write_project_file",
        {"path": "src/app.tsx", "bytes": 10, "after_sha256": "abc"},
    )
    assert gate_evidence_errors(
        gates,
        "implementation",
        [*claims, record.to_dict()],
        agent="implementation",
    ) == []


def test_a4_4_legacy_provider_gate_still_requires_runtime_evidence() -> None:
    gate = [{"id": "research-proof", "require": "evidence-backed research"}]
    assert gate_evidence_errors(gate, "research", [], agent="research")
    read_record = evidence_from_tool("research", "read_text", {"path": "README.md", "bytes": 12})
    assert gate_evidence_errors(gate, "research", [read_record.to_dict()], agent="research") == []
