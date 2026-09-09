from __future__ import annotations

from pathlib import Path
from typing import Any

from core.runtime.harness_runtime import HarnessInspiredRuntime


class RuntimeCreator:
    """Safe creator surface for inspecting and authoring runtime presets.

    DeepSeek Harness Creator mode can inspect and modify its plugin runtime. The
    UIUX Factory adopts the useful authoring loop while keeping a narrower trust
    boundary: shipped plugins remain code-owned; Creator mode may inspect the
    catalog, preview compositions, and copy/edit JSON presets in the writable
    user preset root. It never evaluates model-written Python.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.runtime = HarnessInspiredRuntime(self.root)

    def inventory(self) -> dict[str, Any]:
        payload = self.runtime.inventory()
        payload["creator_policy"] = {
            "shipped_plugins_mutable": False,
            "shipped_presets_mutable": False,
            "authoring_model": "copy-only preset authoring",
            "arbitrary_python_plugins": False,
            "user_preset_root": str(self.runtime.catalog.user_root),
        }
        return payload

    def preview(self, preset_id: str) -> dict[str, Any]:
        active = self.runtime.compose(preset_id)
        try:
            payload = active.to_dict()
            payload["valid"] = True
            return payload
        finally:
            active.registry.unmount_all()

    def copy_preset(
        self,
        source_id: str,
        new_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        preset = self.runtime.catalog.copy_preset(
            source_id,
            new_id,
            name=name,
            description=description,
        )
        preview = self.preview(preset.preset_id)
        return {
            "preset": preset.to_dict(),
            "composition": preview,
        }

    def delete_preset(self, preset_id: str) -> None:
        self.runtime.catalog.delete_user_preset(preset_id)

    def validate(self, preset_id: str) -> dict[str, Any]:
        return self.preview(preset_id)
