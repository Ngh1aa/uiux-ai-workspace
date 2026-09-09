from pathlib import Path

import pytest

from apps.bridge.server import runtime_preset_inventory, validate_runtime_preset


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"
BRIDGE = ROOT / "apps" / "bridge"


def test_bridge_exposes_and_validates_runtime_presets() -> None:
    inventory = runtime_preset_inventory()
    ids = {item["id"] for item in inventory}

    assert {"standard", "visual-first", "research-heavy", "creator"}.issubset(ids)
    assert validate_runtime_preset("visual-first") == "visual-first"
    with pytest.raises(KeyError):
        validate_runtime_preset("does-not-exist")


def test_bridge_passes_runtime_preset_to_factory_process() -> None:
    server = (BRIDGE / "server.py").read_text(encoding="utf-8")

    assert '"--runtime-preset"' in server
    assert 'payload.get("runtime_preset", "standard")' in server
    assert '"runtime_presets": runtime_preset_inventory()' in server
    assert '"runtime_preset": runtime_preset' in server


def test_workbench_runtime_selector_reaches_run_request() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    adapter = (WEB / "runtime-presets.js").read_text(encoding="utf-8")

    assert 'id="runtime-preset"' in html
    assert './runtime-presets.js' in html
    assert 'payload.runtime_preset = currentPreset()' in adapter
    assert 'payload.runtime_presets' in adapter
    assert 'uiux-runtime-preset-v1' in adapter


def test_runtime_evidence_is_exposed_in_bridge_and_workbench() -> None:
    server = (BRIDGE / "server.py").read_text(encoding="utf-8")
    adapter = (WEB / "runtime-presets.js").read_text(encoding="utf-8")

    for name in ("runtime-composition.json", "flow-plan.json", "events.jsonl"):
        assert f'"{name}"' in server
        assert f'"{name}"' in adapter
