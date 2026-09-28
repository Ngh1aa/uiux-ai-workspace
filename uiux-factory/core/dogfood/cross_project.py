from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from core.runtime.flow_os.adaptive_surface import CHANGE_SURFACES
from core.runtime.flow_os.task_context import GoalInterpreter


CHANGE_BOUNDARIES = {"PRODUCT", "FACTORY"}
NOVA_LEAK_TOKENS = (
    "vcb",
    "fpt",
    "hpg",
    "financial-product-intelligence",
    "consumer_fintech_personal_banking",
    "missing_business_evidence",
)


@dataclass(frozen=True)
class ProjectDogfoodProfile:
    """Observable, data-driven contract for cross-project Factory dogfood.

    `expected_change_boundary` answers *where the implementation change belongs*
    (PRODUCT or FACTORY). The canonical Task Contract's `change_surface` separately
    answers *how broad the UI change is* (MICRO/FOCUSED/PAGE/REDESIGN/PRODUCT).
    Expected surface/flow values are regression assertions only; they never override
    the canonical interpreter or router.
    """

    project_id: str
    repo: str
    repo_ref: str
    archetype: str
    evidence_paths: tuple[str, ...]
    source_truth_candidates: tuple[str, ...]
    default_task: str
    expected_change_boundary: str
    expected_change_surface: str
    expected_flow_id: str
    routing_intent: str
    evidence_model: str

    def validate(self) -> None:
        if self.expected_change_boundary not in CHANGE_BOUNDARIES:
            raise ValueError(f"unsupported change boundary: {self.expected_change_boundary}")
        if self.expected_change_surface not in CHANGE_SURFACES:
            raise ValueError(f"unsupported adaptive change surface: {self.expected_change_surface}")
        if not self.expected_flow_id.strip():
            raise ValueError(f"{self.project_id} must declare an expected flow")
        if not self.evidence_paths:
            raise ValueError(f"{self.project_id} must declare evidence paths")
        if not self.source_truth_candidates:
            raise ValueError(f"{self.project_id} must declare source-truth candidates")


PROJECT_PROFILES: dict[str, ProjectDogfoodProfile] = {
    "nova": ProjectDogfoodProfile(
        project_id="nova",
        repo="Ngh1aa/Nova",
        repo_ref="main",
        archetype="fintech-trust-data",
        evidence_paths=("PROJECT-CONTEXT.md", ".uiux-profile.json", "app.html"),
        source_truth_candidates=("PROJECT-CONTEXT.md", "PROJECT_CONTEXT.md"),
        default_task=(
            "Redesign the whole product trust and data experience for the existing Nova fintech app "
            "while preserving its established product strategy and interaction model."
        ),
        expected_change_boundary="PRODUCT",
        expected_change_surface="PRODUCT",
        expected_flow_id="professional-website-redesign",
        routing_intent="product-trust-data",
        evidence_model="trust-data-regulatory",
    ),
    "lumen": ProjectDogfoodProfile(
        project_id="lumen",
        repo="Ngh1aa/Lumen",
        repo_ref="main",
        archetype="visual-cultural-experience",
        evidence_paths=(
            "AGENTS.md",
            "PROJECT-CONTEXT.md",
            "docs/DESIGN-DIRECTION.md",
            "docs/CULTURAL-EXPERIENCE.md",
            "docs/DISCOVERY-MODES.md",
            "docs/COMPOSITION-PROOFS.md",
        ),
        source_truth_candidates=("PROJECT-CONTEXT.md", "PROJECT_CONTEXT.md", "AGENTS.md"),
        default_task=(
            "Refine Lumen's visual and art direction only without reopening product strategy; "
            "preserve the cultural-experience concept."
        ),
        expected_change_boundary="PRODUCT",
        expected_change_surface="FOCUSED",
        expected_flow_id="existing-ui-improvement",
        routing_intent="visual-art-direction",
        evidence_model="composition-cultural-experience",
    ),
    "cennext": ProjectDogfoodProfile(
        project_id="cennext",
        repo="Ngh1aa/cennext-b2b-prototype",
        repo_ref="main",
        archetype="b2b-enterprise-service",
        evidence_paths=(
            "README.md",
            "BRIEF_COMPLIANCE.md",
            "sitemap.html",
            "design-system.html",
            "component-states.html",
        ),
        source_truth_candidates=("README.md", "BRIEF_COMPLIANCE.md"),
        default_task=(
            "Improve CENNEXT enterprise information architecture and workflow clarity while "
            "preserving brief and compliance constraints."
        ),
        expected_change_boundary="PRODUCT",
        expected_change_surface="FOCUSED",
        expected_flow_id="existing-ui-improvement",
        routing_intent="enterprise-ia-workflow",
        evidence_model="ia-workflow-compliance",
    ),
}


def project_profile(project_id: str) -> ProjectDogfoodProfile:
    try:
        profile = PROJECT_PROFILES[project_id]
    except KeyError as exc:
        raise ValueError(f"unknown dogfood project profile: {project_id}") from exc
    profile.validate()
    return profile


def _normalize_paths(paths: Iterable[str]) -> set[str]:
    return {str(path).replace("\\", "/").lstrip("./") for path in paths if str(path).strip()}


def resolve_source_truth(profile: ProjectDogfoodProfile, available_paths: Iterable[str]) -> str | None:
    available = _normalize_paths(available_paths)
    for candidate in profile.source_truth_candidates:
        if candidate in available:
            return candidate
    return None


def compile_task_contract(
    profile: ProjectDogfoodProfile,
    *,
    task_description: str | None = None,
    change_boundary: str | None = None,
) -> dict[str, Any]:
    """Compile one canonical task without overwriting adaptive UI scope.

    GoalInterpreter owns `change_surface`. Dogfood orchestration owns the orthogonal
    PRODUCT/FACTORY `change_boundary`. Neither is allowed to silently rewrite the other.
    """

    task = (task_description or profile.default_task).strip()
    context = GoalInterpreter().interpret(task).to_context()
    explicit_boundary = (change_boundary or profile.expected_change_boundary).strip().upper()
    if explicit_boundary not in CHANGE_BOUNDARIES:
        raise ValueError(f"unsupported explicit change boundary: {explicit_boundary}")
    if str(context.get("change_surface", "")).upper() not in CHANGE_SURFACES:
        raise ValueError(f"canonical interpreter returned invalid change_surface: {context.get('change_surface')!r}")
    context["change_boundary"] = explicit_boundary
    context["dogfood_profile"] = {
        "project_id": profile.project_id,
        "archetype": profile.archetype,
        "routing_intent": profile.routing_intent,
        "evidence_model": profile.evidence_model,
    }
    return context


def nova_domain_leaks(profile: ProjectDogfoodProfile) -> list[str]:
    haystack = "\n".join(
        (
            profile.project_id,
            profile.repo,
            profile.archetype,
            profile.default_task,
            profile.routing_intent,
            profile.evidence_model,
            *profile.evidence_paths,
            *profile.source_truth_candidates,
        )
    ).lower()
    if profile.project_id == "nova":
        return []
    return [token for token in NOVA_LEAK_TOKENS if token in haystack]


def evaluate_cross_project_contract(
    profile: ProjectDogfoodProfile,
    *,
    available_paths: Iterable[str],
    task_description: str | None = None,
    change_boundary: str | None = None,
) -> dict[str, Any]:
    available = _normalize_paths(available_paths)
    contract = compile_task_contract(
        profile,
        task_description=task_description,
        change_boundary=change_boundary,
    )
    source_truth = resolve_source_truth(profile, available)
    missing_evidence = [path for path in profile.evidence_paths if path not in available]
    leaks = nova_domain_leaks(profile)
    expected_boundary = (change_boundary or profile.expected_change_boundary).strip().upper()
    checks = {
        "explicit_change_boundary_preserved": contract["change_boundary"] == expected_boundary,
        "adaptive_change_surface_valid": contract["change_surface"] in CHANGE_SURFACES,
        "adaptive_change_surface_expected": contract["change_surface"] == profile.expected_change_surface,
        "source_truth_resolved": source_truth is not None,
        "profile_evidence_grounded": not missing_evidence,
        "no_nova_domain_leakage": not leaks,
    }
    return {
        "schema_version": 2,
        "phase": "A14-fix-once-validate-across-projects",
        "project": profile.project_id,
        "repo": profile.repo,
        "repo_ref": profile.repo_ref,
        "archetype": profile.archetype,
        "routing_intent": profile.routing_intent,
        "evidence_model": profile.evidence_model,
        "contract": contract,
        "source_truth": source_truth,
        "missing_evidence": missing_evidence,
        "nova_domain_leaks": leaks,
        "checks": checks,
        "passed": all(checks.values()),
        "truth_boundary": (
            "This lane verifies project-source isolation, execution-boundary propagation and canonical "
            "adaptive UI scope. It does not manufacture browser, provider-quality, aesthetic-human-review, "
            "deploy, or release verdicts."
        ),
    }
