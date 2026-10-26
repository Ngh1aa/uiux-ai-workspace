import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "oklch-scale.py"
spec = importlib.util.spec_from_file_location("oklch_scale", SCRIPT)
oklch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oklch)


def luminance(rgb):
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def test_scale_is_monotonic_and_in_gamut():
    for hue in (25, 85, 165, 250, 300):
        rows = oklch.scale(hue, 0.2)
        assert [r["step"] for r in rows] == oklch.STEPS
        lum = [luminance(r["rgb"]) for r in rows]
        assert lum == sorted(lum, reverse=True), f"hue {hue} lightness not monotonic"
        assert all(0 <= v <= 1 for r in rows for v in r["rgb"])


def test_extreme_steps_meet_text_contrast():
    rows = oklch.scale(165, 0.14)
    light, dark = luminance(rows[0]["rgb"]), luminance(rows[-1]["rgb"])
    assert (light + 0.05) / (dark + 0.05) >= 7


def test_json_output_is_dtcg_group():
    out = subprocess.run([sys.executable, str(SCRIPT), "--hue", "300", "--json", "violet"],
                         capture_output=True, text=True, check=True).stdout
    group = json.loads(out)["violet"]
    assert set(group) == {str(s) for s in oklch.STEPS}
    assert group["500"]["$value"]["colorSpace"] == "srgb"
    assert group["500"]["$value"]["hex"].startswith("#")
