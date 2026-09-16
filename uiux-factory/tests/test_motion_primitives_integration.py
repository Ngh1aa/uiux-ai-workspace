from pathlib import Path

from core.orchestration.intelligent_flow import MOTION_COMPONENT_INTELLIGENCE, ProfessionalWebsiteFlow
from core.orchestration.motion_component_intelligence import MotionPrimitiveCatalog


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def test_motion_intelligence_skill_routes_through_visual_ownership_stages() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    goal = "Redesign an editorial product website with cinematic motion"
    for stage in ("art_direction", "visual_composition", "implementation", "repair"):
        _profile, selected, _mandatory = flow.resolve_skill_names(stage, goal)
        assert MOTION_COMPONENT_INTELLIGENCE in selected


def test_pinned_motion_primitives_corpus_is_discoverable() -> None:
    catalog = MotionPrimitiveCatalog()
    assert catalog.available
    paths = catalog.discover()
    assert len(paths) >= 50
    assert all(path.startswith("src/components/") for path in paths)


def test_motion_catalog_returns_bounded_traceable_candidates() -> None:
    catalog = MotionPrimitiveCatalog()
    results = catalog.search("editorial image reveal scroll", limit=3)
    assert 1 <= len(results) <= 3
    assert all(item.path.startswith("src/components/") for item in results)
    assert all(item.score > 0 for item in results)
    assert all(item.reasons for item in results)


def test_motion_catalog_can_filter_component_categories() -> None:
    catalog = MotionPrimitiveCatalog()
    results = catalog.search("scroll reveal", categories=("scroll",), limit=5)
    assert results
    assert all(item.category == "scroll" for item in results)
