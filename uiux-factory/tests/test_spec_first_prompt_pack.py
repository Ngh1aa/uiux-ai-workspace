import asyncio
import json
from pathlib import Path

from core.actions.create_spec_first_prompt_pack import CreateSpecFirstPromptPack
from core.contracts.prompt_pack_schema import PromptPack
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def _payload() -> dict:
    design_contract = {
        "project": {"goal": "Build a calm editorial portfolio", "domain": "portfolio"},
        "ux": {
            "principles": ["Clarity before decoration"],
            "page_roles": [{"name": "Home", "role": "Orient and showcase"}],
            "primary_journey": ["Land on home", "Open case study"],
        },
        "visual": {
            "signature": "Editorial index with asymmetric project storytelling",
            "attributes": ["editorial", "quiet", "precise"],
            "layout_rules": ["Use asymmetric composition rather than a universal card grid"],
            "typography_rules": ["Display serif for project titles"],
            "media_rules": ["Project media must carry the main visual weight"],
            "motion_rules": ["Use restrained transition timing"],
        },
        "constraints": {
            "preserve_page_role_diversity": True,
            "avoid_shared_hero_everywhere": True,
        },
        "unresolved_items": [],
    }
    design_system = {
        "domain": "portfolio",
        "foundations": {
            "colors": {
                "ink": {"value": "#111111", "status": "derived", "source": "art direction"}
            },
            "semantic_colors": {},
            "typography": {
                "display.size": {"value": "clamp(64px, 8vw, 132px)", "status": "derived", "source": "art direction"}
            },
            "spacing": {},
            "radius": {},
            "border": {},
            "elevation": {},
            "motion": {},
            "layout": {},
        },
        "components": [
            {
                "name": "ProjectLink",
                "accessibility": ["Visible focus state"],
                "responsive_behavior": ["Stack label below title on narrow viewports"],
            }
        ],
        "unresolved_items": [],
        "gates": {"responsive_contracts_defined": True},
    }
    implementation_plan = {
        "framework": "Static HTML",
        "language": "JavaScript",
        "styling": "CSS",
        "output_dir": "generated/editorial-portfolio",
        "routes": [
            {"path": "/", "page_role": "Home", "priority": "P0"},
            {"path": "/case-study", "page_role": "Case Study", "priority": "P0"},
        ],
        "files": [
            {"path": "index.html", "purpose": "Home route"},
            {"path": "case-study/index.html", "purpose": "Case study route"},
        ],
        "implementation_order": ["tokens", "home", "case study", "qa"],
        "unresolved_items": [],
    }
    visual_composition = {
        "domain": "portfolio",
        "project_slug": "editorial-portfolio",
        "visual_signature": "Asymmetric editorial index",
        "pages": [
            {
                "path": "/",
                "page_role": "Home",
                "composition_family": "editorial-index",
                "first_visual_anchor": "Oversized title and project media",
                "sections": [
                    {
                        "type": "project-index",
                        "purpose": "Expose work quickly",
                        "composition": "asymmetric two-column",
                        "visual_anchor": "project image",
                        "density": "medium",
                        "mobile_behavior": ["stack image after title"],
                    }
                ],
                "anti_monotony_rules": ["Do not repeat identical card shells"],
            }
        ],
        "unresolved_items": [],
    }
    return {
        "goal": "Build a calm editorial portfolio and implement it only after compiling a detailed spec.",
        "reference_analysis": "{}",
        "research": "Research already completed.",
        "ux_ia": "Home → Case study.",
        "art_direction": "Editorial / quiet / precise.",
        "design_contract_content": json.dumps(design_contract),
        "design_system_content": json.dumps(design_system),
        "implementation_plan_content": json.dumps(implementation_plan),
        "visual_composition_content": json.dumps(visual_composition),
    }


def test_spec_first_compiler_builds_standalone_pack_without_example_leakage() -> None:
    raw = asyncio.run(CreateSpecFirstPromptPack().run(json.dumps(_payload())))
    pack = PromptPack.model_validate_json(raw)

    assert pack.gates.passed is True
    assert "## 13. Deployment" in pack.full_build_spec
    assert "## 12. Accessibility / performance / SEO" in pack.full_build_spec
    assert "## 14. QA checklist" in pack.full_build_spec
    assert "## 15. Deliverables" in pack.full_build_spec
    assert "02-FULL-BUILD-SPEC.md" in pack.implementation_prompt
    assert "02-FULL-BUILD-SPEC.md" in pack.qa_remediation_prompt
    assert "Mostar" not in pack.full_build_spec


def test_development_manager_places_specification_before_implementation() -> None:
    manager = (ROOT / "core" / "manager" / "development_manager.py").read_text(encoding="utf-8")
    flow_start = manager.index("FLOW = [")
    flow_end = manager.index("]", flow_start)
    flow_block = manager[flow_start:flow_end]

    assert '"specification_compile"' in flow_block
    assert flow_block.index('"specification_compile"') < flow_block.index('"implementation"')
    assert "await self._run_specification_compile(context)" in manager


def test_specification_stage_routes_prompt_compiler_skill() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    _profile, skills, _mandatory = flow.resolve_skill_names(
        "specification_compile",
        "Build a responsive portfolio website",
    )
    assert "prompt-compiler" in skills
