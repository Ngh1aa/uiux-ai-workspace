from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import core.dogfood.real_project as real_project_module
from core.dogfood.cross_project import ProjectDogfoodProfile
from core.dogfood.real_project import RealProjectDogfoodRunner


REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY_ROOT = REPO_ROOT / "uiux-factory"
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"


def _synthetic_profile() -> ProjectDogfoodProfile:
    return ProjectDogfoodProfile(
        project_id="synthetic-portfolio",
        repo="example/synthetic-portfolio",
        repo_ref="main",
        archetype="visual-portfolio",
        evidence_paths=("README.md", "index.html"),
        source_truth_candidates=("README.md",),
        default_task="Improve the hero section only while preserving the current structure.",
        expected_change_boundary="PRODUCT",
        expected_change_surface="FOCUSED",
        expected_flow_id="existing-ui-improvement",
        routing_intent="visual-polish",
        evidence_model="source-and-render",
    )


def test_a14_generic_runner_accepts_profile_it_has_never_seen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "synthetic"
    project.mkdir()
    (project / "README.md").write_text("# Synthetic\nSource truth.\n", encoding="utf-8")
    (project / "index.html").write_text("<!doctype html><main>Demo</main>\n", encoding="utf-8")
    monkeypatch.setattr(real_project_module, "_git_sha", lambda _root: "1" * 40)

    report = RealProjectDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
        profile=_synthetic_profile(),
    ).run(expected_target_sha="1" * 40)

    assert report["passed"] is True
    assert report["contract"]["change_boundary"] == "PRODUCT"
    assert report["contract"]["change_surface"] == "FOCUSED"
    assert report["flow"]["id"] == "existing-ui-improvement"
    assert report["source_truth"] == "README.md"


def test_a14_generic_runner_core_contains_no_named_project_or_fintech_exception() -> None:
    source = inspect.getsource(real_project_module).lower()
    for forbidden in ("if project", "nova", "lumen", "cennext", "financial-product-intelligence"):
        assert forbidden not in source


def test_a14_generic_runner_requires_explicit_profile_identity(tmp_path: Path) -> None:
    project = tmp_path / "synthetic"
    project.mkdir()
    with pytest.raises(Exception, match="explicit profile or project_id"):
        RealProjectDogfoodRunner(
            skills_root=SKILLS_ROOT,
            factory_root=FACTORY_ROOT,
            project_root=project,
        )
