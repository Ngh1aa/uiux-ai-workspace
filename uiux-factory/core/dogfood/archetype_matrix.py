from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.runtime.flow_os.external_task import build_external_task_manifest


class ArchetypeDogfoodError(RuntimeError):
    """Raised when a pinned P1.1 real-task archetype invariant is not satisfied."""


@dataclass(frozen=True)
class ArchetypeTaskCase:
    case_id: str
    goal: str
    expected_domain: str
    expected_archetype: str
    expected_change_surface: str
    expected_flow_id: str
    required_stage_skills: tuple[tuple[str, tuple[str, ...]], ...]

    def validate(self) -> None:
        if not self.case_id.strip():
            raise ValueError("archetype dogfood case_id is required")
        if not self.goal.strip():
            raise ValueError(f"{self.case_id} goal is required")
        if not self.expected_domain.strip() or not self.expected_archetype.strip():
            raise ValueError(f"{self.case_id} must declare domain + archetype")
        if not self.expected_flow_id.strip():
            raise ValueError(f"{self.case_id} must declare expected flow")
        if not self.required_stage_skills:
            raise ValueError(f"{self.case_id} must declare specialist stage checks")


@dataclass(frozen=True)
class ArchetypeDogfoodProject:
    project_id: str
    repo: str
    evidence_paths: tuple[str, ...]
    cases: tuple[ArchetypeTaskCase, ...]

    def validate(self) -> None:
        if not self.project_id.strip() or not self.repo.strip():
            raise ValueError("archetype dogfood project id + repo are required")
        if not self.evidence_paths:
            raise ValueError(f"{self.project_id} must declare real checkout evidence")
        if not self.cases:
            raise ValueError(f"{self.project_id} must declare at least one task case")
        for case in self.cases:
            case.validate()


PROJECTS: dict[str, ArchetypeDogfoodProject] = {
    "edtech": ArchetypeDogfoodProject(
        project_id="edtech",
        repo="Ngh1aa/EdTech",
        evidence_paths=("index.html", "app.js", "style.css"),
        cases=(
            ArchetypeTaskCase(
                case_id="edtech-learning-experience",
                goal=(
                    "Redesign the whole product learning experience for the PATH EdTech course platform: "
                    "lessons, quizzes, assignments, learning paths and mistake review."
                ),
                expected_domain="education-edtech",
                expected_archetype="learning-experience",
                expected_change_surface="PRODUCT",
                expected_flow_id="professional-website-redesign",
                required_stage_skills=(
                    ("research", ("education-website", "product-discovery")),
                    ("design", ("journey-driven-content-and-layout", "complex-workflow-and-progress-ux")),
                    ("implementation", ("state-feedback-and-error-recovery",)),
                ),
            ),
            ArchetypeTaskCase(
                case_id="edtech-learning-operations",
                goal=(
                    "Build a product for the PATH EdTech LMS admin with an instructor dashboard, "
                    "course management, grading, student management and learning analytics."
                ),
                expected_domain="education-edtech",
                expected_archetype="learning-operations",
                expected_change_surface="PRODUCT",
                expected_flow_id="professional-website-redesign",
                required_stage_skills=(
                    ("design", ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux")),
                    ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
                ),
            ),
        ),
    ),
    "luxroom": ArchetypeDogfoodProject(
        project_id="luxroom",
        repo="Ngh1aa/LuxRoom",
        evidence_paths=("index.html", "detail.html", "cart.html", "checkout.html"),
        cases=(
            ArchetypeTaskCase(
                case_id="luxroom-catalog-commerce",
                goal=(
                    "Redesign the whole product catalog discovery experience for the LuxRoom ecommerce website: "
                    "product listing, category browsing, filters, search and product detail."
                ),
                expected_domain="commerce-retail",
                expected_archetype="catalog-commerce",
                expected_change_surface="PRODUCT",
                expected_flow_id="professional-website-redesign",
                required_stage_skills=(
                    ("research", ("ecommerce-website", "conversion-and-content")),
                    ("design", ("site-search-and-findability", "conversion-and-content")),
                    ("implementation", ("site-search-and-findability",)),
                ),
            ),
            ArchetypeTaskCase(
                case_id="luxroom-checkout-commerce",
                goal="Improve the LuxRoom ecommerce checkout page, cart, payment and order confirmation flow.",
                expected_domain="commerce-retail",
                expected_archetype="checkout-commerce",
                expected_change_surface="PAGE",
                expected_flow_id="page-ui-work",
                required_stage_skills=(
                    ("design", ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency")),
                    ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
                ),
            ),
        ),
    ),
}


def project_ids() -> tuple[str, ...]:
    return tuple(sorted(PROJECTS))


def project_profile(project_id: str) -> ArchetypeDogfoodProject:
    try:
        project = PROJECTS[project_id]
    except KeyError as exc:
        raise ValueError(f"unknown P1.1 archetype dogfood project: {project_id}") from exc
    project.validate()
    return project


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=15,
        shell=False,
    )
    if result.returncode != 0:
        raise ArchetypeDogfoodError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _stage_map(flow: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(stage.get("id", "")): dict(stage)
        for stage in flow.get("stages", [])
        if isinstance(stage, dict) and str(stage.get("id", ""))
    }


def _evaluate_case(
    *,
    skills_root: Path,
    policy_doc: dict[str, Any],
    project: ArchetypeDogfoodProject,
    project_root: Path,
    case: ArchetypeTaskCase,
) -> dict[str, Any]:
    manifest = build_external_task_manifest(
        skills_root,
        policy_doc,
        case.goal,
        project.repo,
        authority="read_only",
        target_root=project_root,
    ).to_dict()
    contract = dict(manifest["task_contract"])
    flow = dict(manifest["resolved_flow"])
    stages = _stage_map(flow)

    specialist_checks: list[dict[str, Any]] = []
    all_required_present = True
    for stage_id, required_skills in case.required_stage_skills:
        stage = stages.get(stage_id, {})
        stage_skills = {str(value) for value in stage.get("skills", [])}
        missing = [skill for skill in required_skills if skill not in stage_skills]
        if missing:
            all_required_present = False
        specialist_checks.append(
            {
                "stage": stage_id,
                "required": list(required_skills),
                "missing": missing,
                "jit_skills": list(stage.get("jit_skills", [])),
                "jit_skill_sources": dict(stage.get("jit_skill_sources", {})),
            }
        )

    provenance = dict(contract.get("routing_provenance", {}))
    checks = {
        "domain_expected": contract.get("domain") == case.expected_domain,
        "archetype_expected": contract.get("product_archetype") == case.expected_archetype,
        "surface_expected": contract.get("change_surface") == case.expected_change_surface,
        "flow_expected": flow.get("id") == case.expected_flow_id,
        "specialist_stage_skills_present": all_required_present,
        "target_truth_probed": manifest.get("evidence_boundary", {}).get("target_truth_probed_before_flow_resolution") is True,
        "target_truth_precedes_flow_resolution": provenance.get("target_truth_applied_before_flow_resolution") is True,
        "read_only_authority_preserved": manifest.get("authority") == "read_only",
    }
    return {
        "case": asdict(case),
        "contract": contract,
        "flow_id": flow.get("id"),
        "specialist_checks": specialist_checks,
        "checks": checks,
        "passed": all(checks.values()),
    }


def evaluate_project(
    *,
    skills_root: Path,
    policy_doc: dict[str, Any],
    project_root: Path,
    project_id: str,
    expected_target_sha: str,
) -> dict[str, Any]:
    project = project_profile(project_id)
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ArchetypeDogfoodError(f"project root does not exist: {root}")

    target_sha = _git(root, "rev-parse", "HEAD")
    clean_before = _git(root, "status", "--porcelain")
    missing_evidence = [path for path in project.evidence_paths if not (root / path).is_file()]

    case_reports = [
        _evaluate_case(
            skills_root=Path(skills_root).resolve(),
            policy_doc=policy_doc,
            project=project,
            project_root=root,
            case=case,
        )
        for case in project.cases
    ]
    clean_after = _git(root, "status", "--porcelain")

    checks = {
        "target_sha_bound": target_sha == expected_target_sha,
        "real_project_evidence_grounded": not missing_evidence,
        "checkout_clean_before": clean_before == "",
        "checkout_clean_after": clean_after == "",
        "all_archetype_cases_passed": all(report["passed"] for report in case_reports),
    }
    return {
        "schema_version": 1,
        "phase": "P1.1-real-task-archetype-dogfood",
        "project": project.project_id,
        "repo": project.repo,
        "target_sha": target_sha,
        "expected_target_sha": expected_target_sha,
        "evidence_paths": list(project.evidence_paths),
        "missing_evidence": missing_evidence,
        "cases": case_reports,
        "checks": checks,
        "passed": all(checks.values()),
        "truth_boundary": (
            "PASS proves canonical goal interpretation, target-truth precedence, FlowPlanner routing and specialist "
            "composition against a pinned real repository checkout. It is read-only routing dogfood, not rendered "
            "UX QA, user validation, deployment verification or a release verdict."
        ),
    }
