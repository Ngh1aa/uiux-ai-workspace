"""Pure compiler and static frontend contracts; no live provider or browser."""
import asyncio
import ast
import copy
import json
import sys
import types
from pathlib import Path

import pytest

# Same optional MetaGPT Action boundary as foundation evaluator tests.
if "metagpt.actions" not in sys.modules:
    actions = types.ModuleType("metagpt.actions")
    actions.Action = object
    sys.modules.setdefault("metagpt", types.ModuleType("metagpt"))
    sys.modules["metagpt.actions"] = actions

from core.actions.create_spec_first_prompt_pack import CreateSpecFirstPromptPack
from core.actions.generate_ai_frontend import DesignBrief, DesignPage, validate_bundle
from core.contracts.prompt_pack_schema import PromptPack
from test_spec_first_prompt_pack import _payload
from test_factory_pipeline_gates import manager


def _valid_payload():
    payload = _payload()
    visual = json.loads(payload["visual_composition_content"])
    if len(visual["pages"]) == 1:
        visual["pages"].append({
            "path": "/case-study", "page_role": "Case Study", "composition_family": "case-story",
            "first_visual_anchor": "Project narrative",
            "sections": [{"type": "case-story", "purpose": "Explain decisions", "composition": "long-form",
                          "visual_anchor": "project evidence", "density": "medium", "mobile_behavior": ["single column"]}],
        })
    payload["visual_composition_content"] = json.dumps(visual)
    return payload


@pytest.mark.parametrize("case", ["bare_goal", "missing_research", "invalid_contract", "empty_plan",
                                 "scope_mismatch", "preserve_mismatch", "missing_mobile", "hidden_chat"])
def test_compiler_never_passes_missing_or_inconsistent_upstream(case):
    payload = _valid_payload()
    if case == "bare_goal":
        payload = {"goal": payload["goal"]}
    elif case == "missing_research":
        payload.pop("research")
    elif case == "invalid_contract":
        payload["design_contract_content"] = "not JSON"
    elif case == "empty_plan":
        payload["implementation_plan_content"] = "{}"
    elif case in {"scope_mismatch", "preserve_mismatch", "missing_mobile"}:
        visual = json.loads(payload["visual_composition_content"])
        if case == "scope_mismatch":
            visual["pages"][0]["path"] = "/unplanned"
        elif case == "preserve_mismatch":
            visual["pages"][1] = copy.deepcopy(visual["pages"][0])
            visual["pages"][1].update(path="/case-study", page_role="Case Study")
        else:
            visual["pages"][0]["sections"][0]["mobile_behavior"] = []
        payload["visual_composition_content"] = json.dumps(visual)
    else:
        payload["ux_ia"] = "Use the structure from the previous message."
    pack = PromptPack.model_validate_json(asyncio.run(CreateSpecFirstPromptPack().run(json.dumps(payload))))
    assert not pack.gates.passed
    assert pack.blocking_unknowns


def test_complete_consistent_upstream_passes_compiler():
    pack = PromptPack.model_validate_json(asyncio.run(CreateSpecFirstPromptPack().run(json.dumps(_valid_payload()))))
    assert pack.gates.passed


@pytest.mark.parametrize("case", ["qa_routes_missing", "undeclared_example", "spec_role_changed"])
def test_refined_pack_gates_are_recomputed_from_contents(case):
    payload = _valid_payload()
    pack = PromptPack.model_validate_json(asyncio.run(CreateSpecFirstPromptPack().run(json.dumps(payload))))
    if case == "qa_routes_missing":
        pack.qa_remediation_prompt = pack.qa_remediation_prompt.split("Declared route checks")[0]
    elif case == "undeclared_example":
        pack.full_build_spec += "\nBuild the Mostar example.com project."
    else:
        pack.full_build_spec = pack.full_build_spec.replace("### / — Home", "### / — Checkout")
    assert pack.gates.passed  # The supplied flags are deliberately stale PASS.
    assert not CreateSpecFirstPromptPack.evaluate_consistency(payload, pack).passed


def test_compiler_rejects_provider_refinement_even_with_all_pass_flags(manager, monkeypatch, tmp_path):
    from core.runtime.run_context import RunContext
    context = RunContext(root=tmp_path, goal="Build a calm editorial portfolio")
    context.initialize()
    for stage in ("reference_analysis", "research", "ux_ia", "art_direction", "design_contract",
                  "design_system", "implementation_plan", "visual_composition"):
        asyncio.run(getattr(manager, "_run_" + stage)(context))
    async def refine(*, instruction, **kwargs):
        pack = PromptPack.model_validate_json(await CreateSpecFirstPromptPack().run(instruction))
        pack.full_build_spec = pack.full_build_spec.replace("### / — Home", "### / — Checkout")
        assert pack.gates.passed
        return types.SimpleNamespace(content=pack.model_dump_json())
    monkeypatch.setattr(manager.team_runner, "run_role", refine)
    with pytest.raises(RuntimeError, match="consistency gate failed:.*goal_scope_consistent"):
        asyncio.run(manager._run_specification_compile(context))
    assert "full_build_spec" not in context.artifacts


HTML = ('<!doctype html><html lang="en"><head><title>Home</title>'
        '<meta name="viewport" content="width=device-width"></head>'
        '<body><main><h1>Industrial solutions</h1><button>Contact</button>{copy}</main></body></html>')
CSS = ('body{color:var(--color-brand-primary)} :focus-visible{outline:2px solid #145}'
       '@media(max-width:600px){main{padding:1rem}}')


def _bundle(css=CSS, text=""):
    brief = DesignBrief(direction="Industrial automation", pages=[DesignPage(
        path="index.html", title="Home", purpose="Describe solutions", sections=["Services"])])
    return json.dumps({"files": {"index.html": HTML.replace("{copy}", text), "styles.css": css}}), brief


@pytest.mark.parametrize("css,text", [
    (CSS.replace("outline:2px solid #145", "outline:none"), ""),
    (CSS.replace("outline:2px solid #145", "outline:0"), ""),
    (CSS.replace("outline:2px solid #145", "outline:2px solid transparent"), ""),
    (CSS.replace("outline:2px solid #145", "outline:2px solid #145;opacity:0"), ""),
    (CSS.replace("outline:2px solid #145", "outline:2px solid #145;outline-color:transparent"), ""),
    (CSS.replace("outline:2px solid #145", "outline:2px solid #145;outline-width:0"), ""),
    (CSS.replace("outline:2px solid #145", "box-shadow:0 0 0 3px rgba(0,0,0,0)"), ""),
    (CSS + ":focus-visible{outline:none}", ""),
    (CSS.replace("main{padding:1rem}", ""), ""),
    (CSS.replace("main{padding:1rem}", "main{/* empty */}"), ""),
    (CSS, "<p>Implemented using TypeScript and UIUX Factory.</p>"),
])
def test_static_frontend_contract_rejects_invalid_focus_responsive_or_copy(css, text):
    raw, brief = _bundle(css, text)
    with pytest.raises(ValueError):
        validate_bundle(raw, brief)


@pytest.mark.parametrize("css", [CSS, CSS.replace("outline:2px solid #145", "outline:none;box-shadow:0 0 0 3px #145"),
                                CSS + "button:focus-visible{transform:translateY(-1px)}",
                                CSS.replace("@media(max-width:600px)", "@media(width < 600px)"),
                                CSS.replace("outline:2px solid #145", "outline:none") + ":focus-visible{outline:2px solid #145}"])
def test_valid_focus_and_responsive_contract_is_accepted(css):
    raw, brief = _bundle(css)
    assert validate_bundle(raw, brief).files["index.html"]


def test_ai_builder_quality_flags_are_not_constant_pass():
    root = Path(__file__).resolve().parents[1]
    source = ast.parse((root / "core/orchestration/ai_frontend_builder.py").read_text(encoding="utf-8"))
    flags = {"semantic_html_passed", "responsive_contract_passed", "focus_contract_passed", "technical_copy_gate_passed"}
    assert not [node.arg for node in ast.walk(source) if isinstance(node, ast.keyword)
                and node.arg in flags and isinstance(node.value, ast.Constant) and node.value.value is True]
