from __future__ import annotations

from pathlib import Path

from core.dogfood.cross_project import compile_task_contract, project_ids, project_profile
from core.runtime.flow_os.flow import FlowResolver
from core.runtime.flow_os.task_context import GoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
FLOWS = ROOT.parent / "skills_UIUX" / "flows"


def _flow_for(goal: str) -> tuple[str, str]:
    context = GoalInterpreter().interpret(goal).to_context()
    _path, document, _score = FlowResolver(FLOWS).resolve(context)
    return str(context["change_surface"]), str(document["id"])


def test_a14_lumen_focused_art_direction_does_not_expand_to_full_redesign() -> None:
    surface, flow_id = _flow_for(
        "Refine the visual and art direction only. Preserve the cultural experience and do not reopen product strategy."
    )
    assert surface == "FOCUSED"
    assert flow_id == "existing-ui-improvement"


def test_a14_cennext_focused_ia_workflow_does_not_expand_to_full_redesign() -> None:
    surface, flow_id = _flow_for(
        "Improve enterprise information architecture and workflow clarity while preserving brief and compliance constraints."
    )
    assert surface == "FOCUSED"
    assert flow_id == "existing-ui-improvement"


def test_a14_luxroom_checkout_stays_page_bounded() -> None:
    surface, flow_id = _flow_for(
        "Improve the LuxRoom checkout experience while preserving the current luxury-minimal visual direction and the rest of the ecommerce structure."
    )
    assert surface == "PAGE"
    assert flow_id == "page-ui-work"


def test_a14_nova_dashboard_task_stays_page_bounded_without_full_redesign() -> None:
    surface, flow_id = _flow_for(
        "Improve trust and data clarity in the dashboard only while preserving the existing product strategy."
    )
    assert surface == "PAGE"
    assert flow_id == "page-ui-work"


def test_a14_true_whole_site_redesign_still_routes_to_professional_flow() -> None:
    surface, flow_id = _flow_for("Redesign the whole website end to end")
    assert surface == "REDESIGN"
    assert flow_id == "professional-website-redesign"


def test_a14_true_whole_product_redesign_still_routes_to_professional_flow() -> None:
    surface, flow_id = _flow_for("Redesign the whole product experience for a fintech app")
    assert surface == "PRODUCT"
    assert flow_id == "professional-website-redesign"


def test_a14_execution_boundary_is_orthogonal_to_ui_change_surface() -> None:
    profile = project_profile("cennext")
    task = "Improve enterprise information architecture and workflow clarity while preserving compliance constraints."
    product = compile_task_contract(profile, task_description=task, change_boundary="PRODUCT")
    factory = compile_task_contract(profile, task_description=task, change_boundary="FACTORY")

    assert product["change_surface"] == "FOCUSED"
    assert factory["change_surface"] == "FOCUSED"
    assert product["change_boundary"] == "PRODUCT"
    assert factory["change_boundary"] == "FACTORY"


def test_a14_project_profiles_do_not_control_canonical_surface() -> None:
    task = "Improve the hero section only while preserving the current structure."
    surfaces = set()
    for project_id in project_ids():
        contract = compile_task_contract(project_profile(project_id), task_description=task)
        assert contract["change_boundary"] == "PRODUCT"
        surfaces.add(str(contract["change_surface"]))

    assert surfaces == {"FOCUSED"}


def test_a14_registry_spans_distinct_product_archetypes() -> None:
    profiles = [project_profile(project_id) for project_id in project_ids()]
    assert set(project_ids()) >= {"nova", "lumen", "cennext", "luxroom"}
    assert len({profile.archetype for profile in profiles}) == len(profiles)
    assert len({profile.evidence_model for profile in profiles}) == len(profiles)
