from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_PRESET_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,63}$")


@dataclass(frozen=True)
class RuntimePreset:
    preset_id: str
    name: str
    description: str
    plugins: tuple[str, ...]
    stage_skills: dict[str, tuple[str, ...]] = field(default_factory=dict)
    source_path: Path | None = None
    trust: str = "system"
    copied_from: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "id": self.preset_id,
            "name": self.name,
            "description": self.description,
            "plugins": list(self.plugins),
            "stage_skills": {
                stage: list(paths)
                for stage, paths in sorted(self.stage_skills.items())
            },
            "trust": self.trust,
            "copied_from": self.copied_from,
            "source_path": str(self.source_path) if self.source_path else None,
        }


class RuntimePresetCatalog:
    """Discover shipped and user runtime compositions.

    Shipped presets win duplicate ids, mirroring the safety property used by
    DeepSeek Harness: local authoring can copy a shipped composition but cannot
    silently shadow or mutate the built-in definition.
    """

    def __init__(
        self,
        shipped_root: Path,
        user_root: Path | None = None,
    ) -> None:
        self.shipped_root = Path(shipped_root).resolve()
        self.user_root = Path(user_root).resolve() if user_root else None

    @staticmethod
    def validate_id(preset_id: str) -> str:
        value = preset_id.strip()
        if not _PRESET_ID.fullmatch(value):
            raise ValueError(
                "Runtime preset id must match [a-z0-9][a-z0-9-]{0,63}."
            )
        return value

    @classmethod
    def _load_file(cls, path: Path, trust: str) -> RuntimePreset:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Runtime preset must be a JSON object: {path}")

        preset_id = cls.validate_id(str(payload.get("id", "")))
        if path.stem != preset_id:
            raise ValueError(
                f"Preset filename/id mismatch: {path.name} declares {preset_id!r}."
            )

        plugins = payload.get("plugins", [])
        if not isinstance(plugins, list) or not plugins or not all(
            isinstance(item, str) and item.strip() for item in plugins
        ):
            raise ValueError(f"Preset {preset_id} requires a non-empty plugins list.")

        raw_stage_skills = payload.get("stage_skills", {})
        if not isinstance(raw_stage_skills, dict):
            raise ValueError(f"Preset {preset_id} stage_skills must be an object.")
        stage_skills: dict[str, tuple[str, ...]] = {}
        for stage, paths in raw_stage_skills.items():
            if not isinstance(stage, str) or not isinstance(paths, list):
                raise ValueError(f"Preset {preset_id} has invalid stage_skills entry.")
            if not all(isinstance(item, str) and item.strip() for item in paths):
                raise ValueError(
                    f"Preset {preset_id} stage {stage!r} contains an invalid skill path."
                )
            stage_skills[stage] = tuple(dict.fromkeys(paths))

        return RuntimePreset(
            preset_id=preset_id,
            name=str(payload.get("name") or preset_id),
            description=str(payload.get("description") or ""),
            plugins=tuple(dict.fromkeys(item.strip() for item in plugins)),
            stage_skills=stage_skills,
            source_path=path.resolve(),
            trust=trust,
            copied_from=(
                str(payload.get("copied_from"))
                if payload.get("copied_from")
                else None
            ),
        )

    def _scan_root(self, root: Path | None, trust: str) -> list[RuntimePreset]:
        if root is None or not root.exists():
            return []
        result: list[RuntimePreset] = []
        for path in sorted(root.glob("*.json")):
            if path.is_file():
                result.append(self._load_file(path, trust))
        return result

    def list(self) -> list[RuntimePreset]:
        merged: dict[str, RuntimePreset] = {}
        for preset in self._scan_root(self.shipped_root, "system"):
            merged[preset.preset_id] = preset
        for preset in self._scan_root(self.user_root, "user"):
            merged.setdefault(preset.preset_id, preset)
        return list(merged.values())

    def get(self, preset_id: str) -> RuntimePreset:
        wanted = self.validate_id(preset_id)
        for preset in self.list():
            if preset.preset_id == wanted:
                return preset
        raise KeyError(f"Unknown runtime preset: {wanted}")

    def copy_preset(
        self,
        source_id: str,
        new_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> RuntimePreset:
        if self.user_root is None:
            raise RuntimeError("This deployment has no writable runtime preset root.")
        source = self.get(source_id)
        target_id = self.validate_id(new_id)
        if any(item.preset_id == target_id for item in self.list()):
            raise FileExistsError(f"Runtime preset already exists: {target_id}")

        self.user_root.mkdir(parents=True, exist_ok=True)
        target = self.user_root / f"{target_id}.json"
        payload = {
            "schema_version": 1,
            "id": target_id,
            "name": name or target_id,
            "description": description if description is not None else source.description,
            "plugins": list(source.plugins),
            "stage_skills": {
                stage: list(paths)
                for stage, paths in source.stage_skills.items()
            },
            "copied_from": source.preset_id,
        }
        target.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return self._load_file(target, "user")

    def delete_user_preset(self, preset_id: str) -> None:
        preset = self.get(preset_id)
        if preset.trust != "user" or self.user_root is None:
            raise PermissionError("Shipped runtime presets are immutable.")
        path = preset.source_path
        if path is None or path.parent.resolve() != self.user_root.resolve():
            raise PermissionError("Preset is outside the writable runtime preset root.")
        path.unlink()

    def inventory(self) -> list[dict[str, Any]]:
        return [preset.to_dict() for preset in self.list()]
