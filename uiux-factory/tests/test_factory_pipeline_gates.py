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
