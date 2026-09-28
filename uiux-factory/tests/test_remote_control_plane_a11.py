from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.flow_os.remote_control import RemoteControlError, RemoteFactoryControlPlane


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"
BASE_POLICY = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _plane(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[RemoteFactoryControlPlane, Path]:
    projects = tmp_path / "projects"
    project = projects / "site"
    project.mkdir(parents=True)
    monkeypatch.setenv("UIUX_REMOTE_CONTROL_TOKEN", "fixture-token")
    monkeypatch.setenv("UIUX_REMOTE_PROJECT_ROOTS_JSON", json.dumps([str(projects)]))
    policy = json.loads(json.dumps(BASE_POLICY))
    policy["remote_control"] = {
        "enabled": True,
        "max_artifact_chars": 120000,
        "allow_cancel": True,
        "allow_revision": True,
    }
    return RemoteFactoryControlPlane(SKILLS_ROOT, policy), project


def test_a11_remote_control_is_fail_closed_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setenv("UIUX_REMOTE_CONTROL_TOKEN", "fixture-token")
    monkeypatch.setenv("UIUX_REMOTE_PROJECT_ROOTS_JSON", json.dumps([str(tmp_path)]))
    plane = RemoteFactoryControlPlane(SKILLS_ROOT, BASE_POLICY)

    assert plane.health()["enabled"] is False
    with pytest.raises(RemoteControlError, match="disabled by runtime policy"):
        plane.start_run(token="fixture-token", project_root=str(project), goal="Build a SaaS website")


def test_a11_auth_allowlist_and_authority_boundaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plane, project = _plane(monkeypatch, tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()

    with pytest.raises(RemoteControlError, match="authentication failed"):
        plane.start_run(token="wrong", project_root=str(project), goal="Build a SaaS website")
    with pytest.raises(RemoteControlError, match="outside the remote-control allowlist"):
        plane.start_run(token="fixture-token", project_root=str(outside), goal="Build a SaaS website")
    with pytest.raises(RemoteControlError, match="read_only or branch_write"):
        plane.start_run(
            token="fixture-token",
            project_root=str(project),
            goal="Build a SaaS website",
            authority="release",
        )


def test_a11_start_status_directive_revision_and_cancel_use_canonical_managed_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plane, project = _plane(monkeypatch, tmp_path)
    started = plane.start_run(
        token="fixture-token",
        project_root=str(project),
        goal="Build a modern ecommerce website with search",
        authority="branch_write",
        overrides={"website_type": "ecommerce", "features": ["search"], "mode": "interactive-prototype"},
    )
    run_id = started["manager_run_id"]
    assert started["flow_id"] == "professional-website-redesign"
    assert started["authority"] == "branch_write"

    status = plane.status(token="fixture-token", project_root=str(project), manager_run_id=run_id)
    assert status["manager_run_id"] == run_id
    assert status["active_stage"] == started["active_stage"]

    directive = {
        "directives": [
            {
                "verdict": "REVISE",
                "priority": "P1",
                "route": "/",
                "section": "hero",
                "problem": "Hierarchy needs stronger contrast",
                "instruction": "Increase title/CTA separation",
                "success_criteria": "Primary action is unmistakable",
            }
        ]
    }
    saved = plane.submit_creative_directive(
        token="fixture-token",
        project_root=str(project),
        manager_run_id=run_id,
        directive=directive,
    )
    assert (project / saved["path"]).is_file()

    revised = plane.start_revision(
        token="fixture-token",
        project_root=str(project),
        manager_run_id=run_id,
        goal="Revise the ecommerce experience from the approved directive",
    )
    assert revised["manager_run_id"] != run_id
    assert revised["revision_of"] == run_id
    assert revised["authority"] == "branch_write"

    cancelled = plane.cancel(
        token="fixture-token",
        project_root=str(project),
        manager_run_id=revised["manager_run_id"],
    )
    assert cancelled["state"] == "BLOCKED"

    audit = (project / ".uiux-agent-runs" / "remote-control-audit.jsonl").read_text(encoding="utf-8")
    assert "start_run" in audit
    assert "submit_creative_directive" in audit
    assert "start_revision" in audit
    assert "cancel" in audit
    assert "fixture-token" not in audit


def test_a11_health_never_exposes_token_or_project_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plane, _project = _plane(monkeypatch, tmp_path)
    payload = plane.health()
    encoded = json.dumps(payload)

    assert payload["status"] == "ready"
    assert payload["authentication_configured"] is True
    assert payload["allowed_project_roots"] == 1
    assert payload["arbitrary_shell"] is False
    assert payload["release_operations"] is False
    assert "fixture-token" not in encoded
    assert str(tmp_path) not in encoded
