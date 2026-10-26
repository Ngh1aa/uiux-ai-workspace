import importlib.util
import re
import subprocess
import sys
from pathlib import Path

DS = Path(__file__).resolve().parents[1]
SCRIPT = DS / "scripts" / "export-native.py"
spec = importlib.util.spec_from_file_location("export_native", SCRIPT)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def test_committed_native_files_are_current():
    result = subprocess.run([sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_every_semantic_colour_role_is_exported_once_per_platform():
    modes = native.load()
    roles = native.colour_roles(modes)
    swift = native.swift(modes)
    kotlin = native.kotlin(modes)
    names = [native.camel(k) for k, _, _ in roles]
    assert len(names) == len(set(names)), "two roles collapse to the same identifier"
    for name in names:
        assert f"static let {name} = Color(dsLight:" in swift
        assert kotlin.count(f"    {name} = Color(0xFF") == 2  # light and dark
    assert all(re.fullmatch(r"#[0-9a-f]{6}", c) for _, lo, da in roles for c in (lo, da))


def test_material_scheme_slots_point_at_existing_roles():
    roles = {k for k, _, _ in native.colour_roles(native.load())}
    missing = [r for r in native.M3_SCHEME.values() if r not in roles]
    assert not missing


def test_type_roles_keep_scalable_platform_styles():
    swift = native.swift(native.load())
    for role, (ios_style, _) in native.TYPE_ROLES.items():
        assert f"relativeTo: {ios_style})" in swift


def test_material_scheme_maps_component_container_slots():
    # NavigationBar dùng surfaceContainer, Dialog dùng surfaceContainerHigh.
    for slot in ("surfaceContainerLowest", "surfaceContainerLow", "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest"):
        assert slot in native.M3_SCHEME
