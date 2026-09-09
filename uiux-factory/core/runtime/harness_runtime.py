from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.runtime.plugin_runtime import PluginRegistry, PluginSpec, RuntimeComposition
from core.runtime.runtime_presets import RuntimePreset, RuntimePresetCatalog


@dataclass
class ActiveRuntime:
    preset: RuntimePreset
    registry: PluginRegistry
    composition: RuntimeComposition

    def to_dict(self) -> dict[str, Any]:
        payload = self.composition.to_dict()
        payload.update(
            {
                "schema_version": "1.0.0",
                "preset": self.preset.to_dict(),
            }
        )
        return payload


class HarnessInspiredRuntime:
    """Composable runtime layer learned from DeepSeek Harness.

    This is an adaptation, not a port. The Factory keeps MetaGPT roles and its
    Python pipeline while gaining stable capability dependencies, per-run
    compositions, logical tool catalogs, skill overlays, lifecycle events and a
    creator-friendly preset surface.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.workspace_root = self.root.parent
        self.skills_root = self.workspace_root / "skills_UIUX"
        self.catalog = RuntimePresetCatalog(
            shipped_root=self.root / "config" / "runtime-presets",
            user_root=self.root / ".runtime-presets",
        )
        self._active: dict[str, ActiveRuntime] = {}

    @staticmethod
    def builtin_specs() -> tuple[PluginSpec, ...]:
        return (
            PluginSpec(
                plugin_id="session-events",
                description="Append-only run/session event record with replay and projection.",
                provides=("events.session",),
                tools=("session_inspect", "session_replay"),
            ),
            PluginSpec(
                plugin_id="skill-composition",
                description="Compose stage skills from the canonical router plus runtime overlays.",
                provides=("skills.registry", "skills.compose"),
                requires=("events.session",),
                tools=("skill_catalog", "skill_load"),
            ),
            PluginSpec(
                plugin_id="web-research",
                description="Allow evidence-backed live reference/domain research.",
                provides=("research.web",),
                requires=("skills.compose",),
                tools=("web_search", "reference_inspect"),
                stage_skills={
                    "research": (
                        "design-reference-research-and-benchmark/SKILL.md",
                    ),
                },
            ),
            PluginSpec(
                plugin_id="browser-evidence",
                description="Collect rendered browser evidence and interaction/runtime truth.",
                provides=("browser.qa",),
                requires=("events.session",),
                tools=("browser_render", "browser_inspect"),
                stage_skills={
                    "browser_qa": (
                        "upstream/anthropic-skills/skills/webapp-testing/SKILL.md",
                    ),
                },
            ),
            PluginSpec(
                plugin_id="semantic-visual-qa",
                description="Domain/page-role multimodal visual acceptance and anti-generic blocking.",
                provides=("visual.qa",),
                requires=("browser.qa", "skills.compose"),
                tools=("visual_review",),
                stage_skills={
                    "visual_qa": (
                        "upstream/anthropic-skills/skills/frontend-design/SKILL.md",
                        "prototype-visual-experience-qa/SKILL.md",
                    ),
                    "repair": (
                        "upstream/anthropic-skills/skills/frontend-design/SKILL.md",
                    ),
                },
            ),
            PluginSpec(
                plugin_id="creator-inspector",
                description="Inspect runtime composition and safely author presets by copying existing ones.",
                provides=("creator.inspect", "preset.author"),
                requires=("events.session", "skills.compose"),
                tools=("runtime_inspect", "preset_copy", "composition_preview"),
            ),
        )

    def _event_sink(self, context):
        def sink(event_type: str, data: dict[str, Any]) -> None:
            context.event_bus().emit(event_type, data=data)

        return sink

    def compose(self, preset_id: str, *, event_sink=None) -> ActiveRuntime:
        preset = self.catalog.get(preset_id)
        registry = PluginRegistry(self.builtin_specs(), event_sink=event_sink)
        base = registry.mount(
            preset.plugins,
            metadata={"runtime_preset": preset.preset_id},
        )

        merged: dict[str, list[str]] = {
            stage: list(paths)
            for stage, paths in base.stage_skills.items()
        }
        for stage, paths in preset.stage_skills.items():
            bucket = merged.setdefault(stage, [])
            for path in paths:
                if path not in bucket:
                    bucket.append(path)

        composition = RuntimeComposition(
            requested_plugins=base.requested_plugins,
            mounted_plugins=base.mounted_plugins,
            capabilities=base.capabilities,
            tools=base.tools,
            stage_skills={
                stage: tuple(paths)
                for stage, paths in merged.items()
            },
        )
        return ActiveRuntime(preset=preset, registry=registry, composition=composition)

    def activate(self, context, preset_id: str | None = None) -> ActiveRuntime:
        selected = (preset_id or getattr(context, "runtime_preset", "standard")).strip()
        if context.run_id in self._active:
            raise RuntimeError(f"Run already has an active runtime composition: {context.run_id}")

        active = self.compose(selected, event_sink=self._event_sink(context))
        context.runtime_preset = active.preset.preset_id
        self._active[context.run_id] = active
        context.event_bus().emit(
            "runtime.preset_selected",
            data={
                "preset": active.preset.preset_id,
                "plugins": list(active.composition.mounted_plugins),
                "capabilities": list(active.composition.capabilities),
                "tools": list(active.composition.tools),
            },
        )

        artifact = context.run_dir / "runtime-composition.json"
        artifact.write_text(
            json.dumps(active.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        context.add_artifact("runtime_composition", artifact)
        return active

    def active(self, context) -> ActiveRuntime:
        active = self._active.get(context.run_id)
        if active is None:
            raise RuntimeError(f"Run has no active runtime composition: {context.run_id}")
        return active

    def require(self, context, capability: str) -> None:
        self.active(context).registry.require(capability)

    def stage_skill_paths(self, context, stage: str) -> tuple[str, ...]:
        active = self.active(context)
        paths = active.composition.stage_skills.get(stage, ())
        missing = [path for path in paths if not (self.skills_root / path).is_file()]
        if missing:
            raise FileNotFoundError(
                "Runtime composition references missing skills: " + ", ".join(missing)
            )
        return tuple(paths)

    def snapshot(self, context) -> dict[str, Any]:
        return self.active(context).to_dict()

    def deactivate(self, context) -> None:
        active = self._active.pop(context.run_id, None)
        if active is None:
            return
        active.registry.unmount_all()
        context.event_bus().emit(
            "runtime.preset_released",
            data={"preset": active.preset.preset_id},
        )

    def inventory(self) -> dict[str, Any]:
        registry = PluginRegistry(self.builtin_specs())
        return {
            "plugins": registry.inventory(),
            "presets": self.catalog.inventory(),
        }
