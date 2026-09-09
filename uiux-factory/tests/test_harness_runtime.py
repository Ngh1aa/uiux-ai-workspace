from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.creator_mode import RuntimeCreator
from core.runtime.harness_runtime import HarnessInspiredRuntime
from core.runtime.plugin_runtime import PluginActivation, PluginRegistry, PluginSpec
from core.runtime.runtime_presets import RuntimePresetCatalog


ROOT = Path(__file__).resolve().parents[1]


def test_plugin_registry_resolves_capabilities_and_disposes_in_reverse_order() -> None:
    lifecycle: list[str] = []

    def activate_base(_context):
        lifecycle.append("mount:base")
        return PluginActivation(
            services={"base.cap": {"ready": True}},
            dispose=lambda: lifecycle.append("dispose:base"),
        )

    def activate_consumer(context):
        assert context.service("base.cap") == {"ready": True}
        lifecycle.append("mount:consumer")
        return PluginActivation(
            dispose=lambda: lifecycle.append("dispose:consumer")
        )

    registry = PluginRegistry(
        (
            PluginSpec(
                plugin_id="base",
                description="base",
                provides=("base.cap",),
                activate=activate_base,
            ),
            PluginSpec(
                plugin_id="consumer",
                description="consumer",
                provides=("consumer.cap",),
                requires=("base.cap",),
                activate=activate_consumer,
            ),
        )
    )

    composition = registry.mount(("consumer",))
    assert composition.mounted_plugins == ("base", "consumer")
    assert set(composition.capabilities) == {"base.cap", "consumer.cap"}

    registry.unmount_all()
    assert lifecycle == [
        "mount:base",
        "mount:consumer",
        "dispose:consumer",
        "dispose:base",
    ]


def test_plugin_registry_rejects_ambiguous_provider_selection() -> None:
    registry = PluginRegistry(
        (
            PluginSpec("a", "a", ("shared",)),
            PluginSpec("b", "b", ("shared",)),
            PluginSpec("consumer", "consumer", ("out",), requires=("shared",)),
        )
    )
    with pytest.raises(RuntimeError, match="multiple providers"):
        registry.mount(("consumer",))


def test_shipped_runtime_presets_resolve_required_factory_capabilities() -> None:
    runtime = HarnessInspiredRuntime(ROOT)
    expected = {"standard", "visual-first", "research-heavy", "creator"}
    assert expected.issubset({item.preset_id for item in runtime.catalog.list()})

    for preset_id in expected:
        active = runtime.compose(preset_id)
        try:
            capabilities = set(active.composition.capabilities)
            assert "events.session" in capabilities
            assert "artifacts.read" in capabilities
            assert "skills.compose" in capabilities
            assert "research.web" in capabilities
            assert "browser.qa" in capabilities
            assert "visual.qa" in capabilities
            assert {"list_artifacts", "read_artifact", "read_skill_source"}.issubset(
                set(active.composition.tools)
            )
        finally:
            active.registry.unmount_all()


def test_visual_first_composes_runtime_skill_overlays() -> None:
    runtime = HarnessInspiredRuntime(ROOT)
    active = runtime.compose("visual-first")
    try:
        visual_qa = set(active.composition.stage_skills["visual_qa"])
        assert "prototype-visual-experience-qa/SKILL.md" in visual_qa
        assert "upstream/anthropic-skills/skills/frontend-design/SKILL.md" in visual_qa
        assert "visual_review" in active.composition.tools
    finally:
        active.registry.unmount_all()


def test_creator_preset_exposes_authoring_capabilities() -> None:
    creator = RuntimeCreator(ROOT)
    preview = creator.preview("creator")
    assert "creator.inspect" in preview["capabilities"]
    assert "preset.author" in preview["capabilities"]
    assert "runtime_inspect" in preview["tools"]


def test_runtime_preset_catalog_uses_copy_only_user_authoring(tmp_path: Path) -> None:
    shipped = tmp_path / "shipped"
    user = tmp_path / "user"
    shipped.mkdir()
    (shipped / "standard.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": "standard",
                "name": "Standard",
                "description": "base",
                "plugins": ["session-events"],
                "stage_skills": {},
            }
        ),
        encoding="utf-8",
    )

    catalog = RuntimePresetCatalog(shipped, user)
    copied = catalog.copy_preset("standard", "my-preset", name="Mine")
    assert copied.trust == "user"
    assert copied.copied_from == "standard"
    assert copied.plugins == ("session-events",)

    with pytest.raises(FileExistsError):
        catalog.copy_preset("standard", "my-preset")
    with pytest.raises(PermissionError):
        catalog.delete_user_preset("standard")

    catalog.delete_user_preset("my-preset")
    with pytest.raises(KeyError):
        catalog.get("my-preset")


def test_runtime_compose_rejects_missing_skill_paths_before_activation(tmp_path: Path) -> None:
    factory = tmp_path / "workspace" / "uiux-factory"
    preset_root = factory / "config" / "runtime-presets"
    skills = factory.parent / "skills_UIUX"
    preset_root.mkdir(parents=True)
    skills.mkdir(parents=True)

    (preset_root / "broken.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": "broken",
                "name": "Broken",
                "description": "should fail before a run consumes it",
                "plugins": ["session-events"],
                "stage_skills": {
                    "research": ["does-not-exist/SKILL.md"]
                },
            }
        ),
        encoding="utf-8",
    )

    runtime = HarnessInspiredRuntime(factory)
    with pytest.raises(FileNotFoundError, match="does-not-exist/SKILL.md"):
        runtime.compose("broken")


def test_runtime_plugin_selection_changes_model_observation_tool_surface(tmp_path: Path) -> None:
    factory = tmp_path / "workspace" / "uiux-factory"
    preset_root = factory / "config" / "runtime-presets"
    skills = factory.parent / "skills_UIUX"
    preset_root.mkdir(parents=True)
    skills.mkdir(parents=True)

    (preset_root / "skills-only.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": "skills-only",
                "name": "Skills only",
                "description": "No artifact reader plugin",
                "plugins": ["session-events", "skill-composition"],
                "stage_skills": {},
            }
        ),
        encoding="utf-8",
    )

    runtime = HarnessInspiredRuntime(factory)
    active = runtime.compose("skills-only")
    try:
        tools = set(active.composition.tools)
        assert "read_skill_source" in tools
        assert "list_artifacts" not in tools
        assert "read_artifact" not in tools
    finally:
        active.registry.unmount_all()
