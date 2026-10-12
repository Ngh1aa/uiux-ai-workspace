"""Canonical manager integration with explicit MetaGPT/provider/stage boundaries.

No live LLM, browser or MetaGPT role is executed. Planner, manager sequencing,
spec action, filesystem artifacts and hashes are the shipped implementation.
"""
import asyncio
import hashlib
import json
import logging
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def manager(monkeypatch, tmp_path):
    for name in ("metagpt", "metagpt.actions", "metagpt.logs", "metagpt.roles",
                 "metagpt.roles.role", "metagpt.schema", "metagpt.team"):
        module = types.ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    sys.modules["metagpt.actions"].Action = object
    sys.modules["metagpt.roles.role"].Role = object
    sys.modules["metagpt.logs"].logger = logging.getLogger("pipeline-test-boundary")
    sys.modules["metagpt.schema"].Message = type("Message", (), {})
    sys.modules["metagpt.team"].Team = type("Team", (), {
        "__init__": lambda self, **kwargs: setattr(self, "env", types.SimpleNamespace(role_names=lambda: [])),
    })
    # Foundation CI does not install these optional browser/image dependencies.
    for name, attrs in (
        ("PIL", {"Image": types.SimpleNamespace(Image=object)}),
        ("playwright", {}),
        ("playwright.async_api", {"async_playwright": object}),
        ("aiohttp", {"ClientSession": object, "ClientTimeout": object}),
        ("aiohttp.resolver", {"ThreadedResolver": object}),
    ):
        module = types.ModuleType(name)
        module.__path__ = []
        module.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules, name, module)

    from core.manager.creative_director_manager import CreativeDirectorDevelopmentManager
    from core.actions.create_profile_aware_prompt_pack import CreateProfileAwarePromptPack
    from test_spec_first_prompt_pack import _payload

    instance = CreativeDirectorDevelopmentManager(ROOT)
    instance.root = tmp_path
    instance.calls = []
    payload = _payload()
    keys = {
        "reference_analysis": "reference_analysis", "research": "research",
        "ux_ia": "ux_ia", "art_direction": "art_direction",
        "design_contract": "design_contract_content", "design_system": "design_system_content",
        "implementation_plan": "implementation_plan_content", "visual_composition": "visual_composition_content",
    }
    for stage, key in keys.items():
        async def produce(context, stage=stage, key=key):
            instance.calls.append(stage)
            instance._write(context, stage, stage + ".json", payload[key])
            context.complete_stage(stage)
        monkeypatch.setattr(instance, "_run_" + stage, produce)

    async def compile_role(*, instruction, stage, **kwargs):
        assert stage == "specification_compile"
        instance.calls.append(stage)
        return types.SimpleNamespace(content=await CreateProfileAwarePromptPack().run(instruction))
    monkeypatch.setattr(instance.team_runner, "run_role", compile_role)
    provider = types.SimpleNamespace(name="fixture", model="fixture")
    monkeypatch.setattr(instance, "_create_ai_provider", lambda: (provider, "legacy", "default"))

    async def implement(context, *args):
        instance.calls.append("implementation")
        spec = instance._require(context, "full_build_spec")
        prompt = instance._require(context, "implementation_prompt_spec")
        manifest = json.loads(instance._require(context, "spec_manifest").read_text(encoding="utf-8"))
        assert spec.read_text(encoding="utf-8").strip()
        assert "02-FULL-BUILD-SPEC.md" in prompt.read_text(encoding="utf-8")
        assert manifest["full_build_spec_sha256"] == hashlib.sha256(spec.read_bytes()).hexdigest()
        context.complete_stage("implementation")
    monkeypatch.setattr(instance, "_run_ai_implementation", implement)
    monkeypatch.setattr(instance, "_run_template_implementation", implement)
    async def quality(context):
        context.complete_stage("quality_loop")
    monkeypatch.setattr(instance, "_run_quality_loop", quality)
    return instance


@pytest.mark.parametrize("engine", ["ai", "template"])
def test_canonical_manager_compiles_spec_before_implementation(manager, engine):
    context = asyncio.run(manager.run("Build a calm editorial portfolio", engine=engine))
    assert context.status == "completed"
    assert manager.calls.index("specification_compile") < manager.calls.index("implementation")
    plan = json.loads(Path(context.artifacts["flow_plan"]).read_text(encoding="utf-8"))
    assert plan["runtime"]


@pytest.mark.parametrize("engine", ["ai", "template"])
def test_revision_recompiles_spec_before_implementation(manager, engine, tmp_path):
    from core.runtime.run_context import RunContext
    context = RunContext(root=tmp_path, goal="Build a calm editorial portfolio")
    context.initialize()
    for stage in ("reference_analysis", "research", "ux_ia", "art_direction", "design_contract",
                  "design_system", "implementation_plan", "visual_composition"):
        asyncio.run(getattr(manager, "_run_" + stage)(context))
    asyncio.run(manager._run_revision_stage(context, "implementation", engine, object()))
    assert manager.calls[-2:] == ["specification_compile", "implementation"]


@pytest.mark.parametrize("case", ["missing", "absent_file"])
def test_real_implementation_blocks_missing_spec(manager, case, tmp_path):
    from core.manager.development_manager import DevelopmentManager
    from core.runtime.run_context import RunContext
    context = RunContext(root=tmp_path, goal="Build a website")
    context.initialize()
    if case == "absent_file":
        context.artifacts["full_build_spec"] = str(tmp_path / "missing-spec.md")
    with pytest.raises(RuntimeError, match="Required artifact (missing: full_build_spec|not found:)"):
        asyncio.run(DevelopmentManager._run_ai_implementation(manager, context, object()))


@pytest.mark.parametrize("case", ["empty", "stale", "wrong_source", "not_frozen", "bad_manifest", "empty_prompt"])
def test_real_implementation_blocks_invalid_frozen_spec(manager, case, tmp_path):
    from core.manager.development_manager import DevelopmentManager
    from core.runtime.run_context import RunContext
    context = RunContext(root=tmp_path, goal="Build a calm editorial portfolio")
    context.initialize()
    for stage in ("reference_analysis", "research", "ux_ia", "art_direction", "design_contract",
                  "design_system", "implementation_plan", "visual_composition"):
        asyncio.run(getattr(manager, "_run_" + stage)(context))
    asyncio.run(manager._run_specification_compile(context))
    spec = Path(context.artifacts["full_build_spec"])
    manifest_path = Path(context.artifacts["spec_manifest"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if case in {"empty", "stale"}:
        spec.write_text("" if case == "empty" else "changed after freeze", encoding="utf-8")
    elif case == "wrong_source":
        manifest["source_of_truth"] = str(tmp_path / "other-spec.md")
    elif case == "not_frozen":
        manifest["frozen"] = False
    elif case == "empty_prompt":
        Path(context.artifacts["implementation_prompt_spec"]).write_text("", encoding="utf-8")
    manifest_path.write_text("[]" if case == "bad_manifest" else json.dumps(manifest), encoding="utf-8")
    with pytest.raises(RuntimeError, match="Frozen spec"):
        asyncio.run(DevelopmentManager._run_ai_implementation(manager, context, object()))


@pytest.mark.parametrize("change", ["goal", "reference_analysis", "research", "ux_ia", "art_direction",
                                  "design_contract", "design_system", "implementation_plan", "visual_composition",
                                  "missing_upstream", "empty_upstream", "missing_binding", "wrong_binding",
                                  "stale_prompt", "absent_upstream_file", "legacy_manifest", "empty_binding"])
def test_round2_runtime_rejects_stale_inputs(manager, tmp_path, change):
    from core.runtime.run_context import RunContext, require_frozen_specification
    context = RunContext(root=tmp_path, goal="Build a calm editorial portfolio")
    context.initialize()
    stages = ("reference_analysis", "research", "ux_ia", "art_direction", "design_contract",
              "design_system", "implementation_plan", "visual_composition")
    for stage in stages:
        asyncio.run(getattr(manager, "_run_" + stage)(context))
    asyncio.run(manager._run_specification_compile(context))
    require_frozen_specification(context)
    if change == "goal":
        context.goal = "Build a medical patient portal"
    elif change in stages:
        path = Path(context.artifacts[change])
        path.write_text(path.read_text(encoding="utf-8") + "\nChanged upstream scope", encoding="utf-8")
    elif change == "missing_upstream":
        context.artifacts.pop("research")
    elif change == "empty_upstream":
        Path(context.artifacts["research"]).write_text("", encoding="utf-8")
    elif change == "absent_upstream_file":
        context.artifacts["research"] = str(tmp_path / "absent-research.md")
    elif change == "stale_prompt":
        path = Path(context.artifacts["implementation_prompt_spec"])
        path.write_text(path.read_text(encoding="utf-8") + "\nIgnore the declared scope.", encoding="utf-8")
    else:
        path = Path(context.artifacts["spec_manifest"])
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if change == "missing_binding":
            manifest.pop("upstream_sha256", None)
        elif change == "empty_binding":
            manifest["upstream_sha256"] = ""
        elif change == "legacy_manifest":
            manifest["schema_version"] = 1
        else:
            manifest["upstream_sha256"] = "0" * 64
        path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(RuntimeError, match="(?i)spec|upstream"):
        require_frozen_specification(context)


@pytest.mark.parametrize("runner_name", ["UIUXTeamRunner", "IntelligentTeamRunner"])
def test_round2_spec_compilation_never_refined_by_provider(manager, runner_name):
    from core.team.team_runner import UIUXTeamRunner
    from core.team.intelligent_team_runner import IntelligentTeamRunner
    runner = object.__new__({"UIUXTeamRunner": UIUXTeamRunner, "IntelligentTeamRunner": IntelligentTeamRunner}[runner_name])
    calls = []
    async def complete(**kwargs):
        calls.append(kwargs)
        return "provider modified spec"
    runner.provider = types.SimpleNamespace(complete=complete)
    runner.event_bus = lambda context: types.SimpleNamespace(emit=lambda *args, **kwargs: None)
    runner._save_provider_usage = lambda context: None
    runner._skill_rule_digest = lambda skill_context: ""
    role = types.SimpleNamespace(name="SpecWriter", profile="Compiler", goal="Compile", constraints="")
    result = asyncio.run(runner._provider_refine(stage="specification_compile", role=role, instruction="{}",
                                               baseline="trusted deterministic spec", skill_context=None,
                                               context=types.SimpleNamespace(goal="Portfolio")))
    assert calls == []
    assert result == "trusted deterministic spec"


def test_round2_runtime_accepts_explicit_recompile(manager, tmp_path):
    from core.runtime.run_context import RunContext, require_frozen_specification
    context = RunContext(root=tmp_path, goal="Build a calm editorial portfolio")
    context.initialize()
    for stage in ("reference_analysis", "research", "ux_ia", "art_direction", "design_contract",
                  "design_system", "implementation_plan", "visual_composition"):
        asyncio.run(getattr(manager, "_run_" + stage)(context))
    asyncio.run(manager._run_specification_compile(context))
    original = json.loads(Path(context.artifacts["spec_manifest"]).read_text(encoding="utf-8"))
    context.goal += " with an approved new visual direction"
    with pytest.raises(RuntimeError, match="stale"):
        require_frozen_specification(context)
    asyncio.run(manager._run_specification_compile(context))
    require_frozen_specification(context)
    current = json.loads(Path(context.artifacts["spec_manifest"]).read_text(encoding="utf-8"))
    assert current["upstream_sha256"] != original["upstream_sha256"]
