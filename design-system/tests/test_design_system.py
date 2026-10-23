"""Regression tests for the design system. Run: python3 -m pytest design-system/tests -q"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

DS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DS / "scripts"))
import dslib  # noqa: E402


def run(script: str, *args: str, cwd: Path = DS) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(cwd / "scripts" / script), *args], capture_output=True, text=True)


def test_generated_files_are_current():
    result = run("build.py", "--check")
    assert result.returncode == 0, result.stderr


def test_validator_passes_on_committed_system():
    result = run("validate.py")
    assert result.returncode == 0, result.stderr


@pytest.fixture()
def sandbox(tmp_path):
    """A disposable copy of the design system for negative tests."""
    copy = tmp_path / "ds"
    shutil.copytree(DS, copy, ignore=shutil.ignore_patterns("review", "fonts", "__pycache__"))
    return copy


def _edit_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _validate(copy: Path) -> subprocess.CompletedProcess:
    subprocess.run([sys.executable, str(copy / "scripts" / "build.py")], capture_output=True, text=True)
    return run("validate.py", cwd=copy)


def test_contrast_regression_is_caught(sandbox):
    # Point body text at a light gray: must fail the 4.5:1 rule in light mode.
    _edit_json(sandbox / "tokens/semantic/color.light.json",
               lambda d: d["text"]["primary"].update({"$value": "{color.neutral.300}"}))
    result = _validate(sandbox)
    assert result.returncode == 1
    assert "contrast text.primary on surface.page" in result.stderr


def test_missing_dark_mode_token_is_caught(sandbox):
    _edit_json(sandbox / "tokens/semantic/color.dark.json", lambda d: d["surface"].pop("sunken"))
    result = _validate(sandbox)
    assert result.returncode == 1
    assert "missing mode token 'surface.sunken'" in result.stderr


def test_component_aliasing_primitive_color_is_caught(sandbox):
    _edit_json(sandbox / "tokens/component/components.json",
               lambda d: d["card"]["bg"].update({"$value": "{color.neutral.0}"}))
    result = _validate(sandbox)
    assert result.returncode == 1
    assert "card.bg: component token aliases primitive" in result.stderr


def test_semantic_literal_color_is_caught(sandbox):
    _edit_json(sandbox / "tokens/semantic/color.light.json",
               lambda d: d["text"]["brand"].update({"$value": {"colorSpace": "srgb", "components": [0, 0.4, 0.3], "hex": "#00664d"}}))
    result = _validate(sandbox)
    assert result.returncode == 1
    assert "text.brand: semantic color holds a literal" in result.stderr


def test_circular_alias_is_caught(sandbox):
    _edit_json(sandbox / "tokens/semantic/layout.json",
               lambda d: (d["spacing"]["stack-xs"].update({"$value": "{spacing.stack-sm}"}),
                          d["spacing"]["stack-sm"].update({"$value": "{spacing.stack-xs}"})))
    result = _validate(sandbox)
    assert result.returncode == 1
    assert "circular reference" in result.stderr


def test_hex_component_mismatch_is_caught(sandbox):
    def corrupt(d):
        d["color"]["jade"]["500"]["$value"]["hex"] = "#ff0000"
    _edit_json(sandbox / "tokens/primitive/color.json", corrupt)
    result = _validate(sandbox)
    assert result.returncode == 1
    assert "color.jade.500: hex #ff0000 disagrees" in result.stderr


@pytest.mark.parametrize("snippet, message", [
    (".x { color: #ff0000; }", "color literal"),
    (".x { color: rgb(0 0 0); }", "color literal"),
    (".x { color: var(--ds-color-jade-500); }", "primitive palette"),
    (".x { color: var(--ds-text-does-not-exist); }", "is not defined"),
])
def test_component_css_lint(sandbox, snippet, message):
    css = sandbox / "components/components.css"
    css.write_text(css.read_text(encoding="utf-8") + "\n" + snippet + "\n", encoding="utf-8")
    result = _validate(sandbox)
    assert result.returncode == 1
    assert message in result.stderr


def test_stale_generated_css_is_caught(sandbox):
    css = sandbox / "generated/tokens.css"
    css.write_text(css.read_text(encoding="utf-8") + "/* hand edit */\n", encoding="utf-8")
    assert run("build.py", "--check", cwd=sandbox).returncode == 1


def test_dark_block_overrides_only_mode_tokens():
    css = (DS / "generated/tokens.css").read_text(encoding="utf-8")
    dark = css.split(':root[data-theme="dark"] {', 1)[1]
    assert "--ds-surface-page:" in dark
    assert "--ds-color-jade-500:" not in dark, "primitives must not be redefined per mode"
    assert "--ds-button-height-md" not in dark, "component tokens follow semantic vars automatically"


def test_every_contrast_pair_meets_minimum_in_both_modes():
    pairs = json.loads((DS / "contrast-pairs.json").read_text(encoding="utf-8"))["pairs"]
    for mode in ("light", "dark"):
        res = dslib.resolve(dslib.mode_tokens(mode))
        for pair in pairs:
            ratio = dslib.contrast(dslib.color_hex(res[pair["fg"]][1]), dslib.color_hex(res[pair["bg"]][1]))
            assert ratio >= pair["min"], (mode, pair, round(ratio, 2))


def test_wcag_contrast_math_matches_known_values():
    assert dslib.contrast("#000000", "#ffffff") == pytest.approx(21.0)
    assert dslib.contrast("#777777", "#ffffff") == pytest.approx(4.48, abs=0.01)


def test_example_uses_only_defined_classes_and_icons():
    html = (DS / "examples/appointment-app/index.html").read_text(encoding="utf-8")
    css = (DS / "components/components.css").read_text(encoding="utf-8")
    sprite = (DS / "components/icons.svg").read_text(encoding="utf-8")
    defined_classes = set(re.findall(r"\.(ds-[a-z0-9_-]+)", css))
    used_classes = set(re.findall(r"\b(ds-[a-z0-9_-]+)", " ".join(re.findall(r'class="([^"]+)"', html))))
    used_classes |= set(re.findall(r"\bclass=\"[^\"]*?(ds-[a-z0-9_-]+)", html))
    # template literals like ds-badge--${tone}: check each tone the data can produce
    tones = set(re.findall(r"tone: '([a-z]+)'", html))
    used_classes |= {f"ds-badge--{t}" for t in tones}
    undefined = {c for c in used_classes if c not in defined_classes and not c.startswith("ds-i-") and not c.endswith("--")}
    assert not undefined, f"example uses undefined classes: {sorted(undefined)}"
    icon_ids = set(re.findall(r'<symbol id="(ds-i-[a-z0-9-]+)"', sprite))
    used_icons = set(re.findall(r'href="#(ds-i-[a-z0-9-]+)"', html)) | {f"ds-i-{m}" for m in re.findall(r"icon\('([a-z0-9-]+)'", html)}
    assert used_icons <= icon_ids, sorted(used_icons - icon_ids)
    assert sprite.strip() in html, "inline sprite in the example drifted from components/icons.svg"


def test_tab_bar_items_have_icon_and_text_label():
    html = (DS / "examples/appointment-app/index.html").read_text(encoding="utf-8")
    items = re.findall(r'<a class="ds-tab-bar__item"[^>]*>(.*?)</a>', html, flags=re.S)
    assert items
    for item in items:
        assert "ds-tab-bar__icon" in item
        label = re.sub(r"<[^>]+>", "", item).strip()
        assert label, "tab item without visible text label"
    for nav in re.findall(r'<nav class="ds-tab-bar".*?</nav>', html, flags=re.S):
        assert nav.count('aria-current="page"') == 1


def test_fonts_are_bundled_with_license():
    fonts = DS / "fonts"
    assert (fonts / "OFL.txt").read_text(encoding="utf-8").count("SIL Open Font License") >= 1
    for ref in re.findall(r'url\("\./([^"]+)"\)', (fonts / "fonts.css").read_text(encoding="utf-8")):
        assert (fonts / ref).is_file(), ref


def test_recorded_browser_report_has_no_axe_violations():
    report = json.loads((DS / "examples/appointment-app/review/browser-report.json").read_text(encoding="utf-8"))
    assert report["axe"] == "RUN"
    assert report["runs"], "no runs recorded"
    for run_ in report["runs"]:
        assert run_["axe"]["violations"] == [], run_
        assert run_["overflow"] == "PASS" and run_["console"] == "PASS"


# ---------- v0.2: money-app reference and app components ----------

MONEY = DS / "examples/money-app/index.html"


def _defined_classes():
    css = (DS / "components/components.css").read_text(encoding="utf-8")
    return set(re.findall(r"\.(ds-[a-z0-9_-]+)", css))


def test_money_app_uses_only_defined_ds_classes_and_icons():
    html = MONEY.read_text(encoding="utf-8")
    sprite = (DS / "components/icons.svg").read_text(encoding="utf-8")
    used = set()
    for attr in re.findall(r'class="([^"]+)"', html):
        used |= set(re.findall(r"\b(ds-[a-z0-9_-]+)", attr))
    undefined = {c for c in used if c not in _defined_classes() and not c.startswith("ds-i-") and not c.endswith("--")}
    assert not undefined, f"money-app uses undefined classes: {sorted(undefined)}"
    icon_ids = set(re.findall(r'<symbol id="(ds-i-[a-z0-9-]+)"', sprite))
    used_icons = set(re.findall(r'href="#(ds-i-[a-z0-9-]+)"', html)) | {f"ds-i-{m}" for m in re.findall(r"icon: '([a-z0-9-]+)'", html)}
    assert used_icons <= icon_ids, sorted(used_icons - icon_ids)
    assert sprite.strip() in html, "inline sprite in money-app drifted from components/icons.svg"


def test_money_app_styles_use_tokens_not_colour_literals():
    html = MONEY.read_text(encoding="utf-8")
    styles = " ".join(re.findall(r"<style>(.*?)</style>", html, flags=re.S))
    styles += " ".join(re.findall(r'style="([^"]+)"', html))
    styles = re.sub(r"/\*.*?\*/", "", styles, flags=re.S)
    literal = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color)\(", re.I)
    assert not literal.search(styles), literal.search(styles).group(0)
    generated = (DS / "generated/tokens.css").read_text(encoding="utf-8")
    defined = set(re.findall(r"(--ds-[a-z0-9-]+):", generated))
    used = set(re.findall(r"var\((--ds-[a-z0-9-]+)", styles))
    assert used <= defined, sorted(used - defined)
    assert not any(v.startswith("--ds-color-") for v in used), "example must use semantic roles"


def test_money_app_tab_bars_and_dialog_semantics():
    html = MONEY.read_text(encoding="utf-8")
    navs = re.findall(r'<nav class="ds-tab-bar".*?</nav>', html, flags=re.S)
    assert len(navs) == 2
    for nav in navs:
        assert nav.count('aria-current="page"') == 1
        for item in re.findall(r'<a class="ds-tab-bar__item"[^>]*>(.*?)</a>', nav, flags=re.S):
            assert "ds-tab-bar__icon" in item and re.sub(r"<[^>]+>", "", item).strip()
    assert 'role="dialog"' in html and 'aria-labelledby="sheet-title"' in html
    for bar in re.findall(r'<div class="ds-progress[^"]*"[^>]*>', html):
        assert 'role="progressbar"' in bar and "aria-valuenow" in bar and "aria-label" in bar
    for sw in re.findall(r'<span class="ds-switch"><input[^>]*>', html):
        assert 'role="switch"' in sw


def test_money_app_recorded_review_is_honestly_labelled():
    report = json.loads((DS / "examples/money-app/review/browser-report.json").read_text(encoding="utf-8"))
    assert report["status"] in {"PASS", "PARTIAL"}
    if report["axe"] != "RUN" or report["engines_skipped"] or len(report["runs"]) != report["expected_runs"]:
        assert report["status"] == "PARTIAL", "incomplete review must not be labelled PASS"
    assert any(run.get("task_recovery") == "PASS" for run in report["runs"])
    for run_ in report["runs"]:
        assert run_["overflow"] == "PASS" and run_["console"] == "PASS" and run_["enlarged_text"] == "PASS"


def test_v02_components_have_contracts_and_reduced_motion():
    contracts = (DS / "docs/component-contracts.md").read_text(encoding="utf-8")
    for name in ("Segmented control", "Switch", "Progress", "Skeleton", "Sheet and scrim", "Section header"):
        assert f"## {name}" in contracts, name
    css = (DS / "components/components.css").read_text(encoding="utf-8")
    for cls in ("ds-segmented", "ds-switch", "ds-progress", "ds-skeleton", "ds-sheet", "ds-scrim", "ds-section-header"):
        assert f".{cls}" in css, cls
    reduced = css.split("prefers-reduced-motion")[1]
    assert ".ds-skeleton { animation: none; }" in reduced


def test_scrim_stays_dark_in_both_modes():
    light = dslib.resolve(dslib.mode_tokens("light"))
    dark = dslib.resolve(dslib.mode_tokens("dark"))
    for res in (light, dark):
        hexv = dslib.color_hex(res["surface.scrim"][1])
        assert dslib.contrast(hexv, "#ffffff") > 12, hexv
