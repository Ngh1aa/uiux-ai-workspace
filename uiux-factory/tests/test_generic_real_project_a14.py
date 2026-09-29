from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import core.dogfood.real_project as real_project_module
from core.dogfood.cross_project import ProjectDogfoodProfile, evaluate_cross_project_contract, project_profile
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
        isolation_tokens=("synthetic-portfolio",),
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
    for forbidden in (
        "if project",
        "nova",
        "lumen",
        "cennext",
        "luxroom",
        "financial-product-intelligence",
        "luxury-minimal",
    ):
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


def test_a14_cross_profile_isolation_is_not_nova_specific() -> None:
    profile = project_profile("luxroom")
    report = evaluate_cross_project_contract(
        profile,
        available_paths=profile.evidence_paths,
    )
    assert report["checks"]["cross_profile_isolation"] is True
    assert report["cross_profile_leaks"] == []


def test_a14_cross_profile_isolation_detects_foreign_project_marker() -> None:
    original = project_profile("luxroom")
    contaminated = ProjectDogfoodProfile(
        project_id=original.project_id,
        repo=original.repo,
        repo_ref=original.repo_ref,
        archetype=original.archetype,
        evidence_paths=original.evidence_paths,
        source_truth_candidates=original.source_truth_candidates,
        default_task=original.default_task + " Preserve Money Horizon behavior from Nova.",
        expected_change_boundary=original.expected_change_boundary,
        expected_change_surface=original.expected_change_surface,
        expected_flow_id=original.expected_flow_id,
        routing_intent=original.routing_intent,
        evidence_model=original.evidence_model,
        isolation_tokens=original.isolation_tokens,
    )
    report = evaluate_cross_project_contract(
        contaminated,
        available_paths=contaminated.evidence_paths,
    )
    assert report["checks"]["cross_profile_isolation"] is False
    assert any(item.startswith("nova:") for item in report["cross_profile_leaks"])
