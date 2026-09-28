from __future__ import annotations

from pathlib import Path

from core.dogfood.cross_project import compile_task_contract, project_profile
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


def test_a14_nova_focused_trust_data_task_does_not_expand_to_full_redesign() -> None:
    surface, flow_id = _flow_for(
        "Improve trust and data clarity in the dashboard only while preserving the existing product strategy."
    )
    assert surface == "FOCUSED"
    assert flow_id == "existing-ui-improvement"


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
    tasks = {
        "nova": "Improve trust and data clarity in the dashboard only.",
        "lumen": "Refine the hero art direction only.",
        "cennext": "Improve navigation only while preserving compliance constraints.",
    }
    for project_id, task in tasks.items():
        contract = compile_task_contract(project_profile(project_id), task_description=task)
        assert contract["change_boundary"] == "PRODUCT"
        assert contract["change_surface"] == "FOCUSED"
